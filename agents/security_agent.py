"""
Byngox — Security Agent (Cyberwall-wired)
Subscribes to cyberwall threat events via NATS JetStream.
Every AI analysis passes through CML before publishing.
Correlates security threats with health and population agents.
Escalates coordinated attacks to coordination_agent.
"""
import asyncio
import json
import logging
import os
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Optional

import httpx
import nats
from nats.js.api import ConsumerConfig, DeliverPolicy

log = logging.getLogger("byngox.security_agent")

NATS_URL        = os.environ.get("NATS_URL",    "nats://localhost:4223")
OLLAMA_URL      = os.environ.get("OLLAMA_URL",  "http://localhost:11434")
SECURITY_MODEL  = os.environ.get("SECURITY_MODEL", "phi4-mini")

# NATS subjects
CYBERWALL_ALERT     = "sorabbyngo.cyberwall.alert"
CYBERWALL_BLOCK     = "sorabbyngo.cyberwall.block"
SENTINEL_ESCALATION = "sorabbyngo.sentinel.escalation"
SENTINEL_HEALTH     = "sorabbyngo.sentinel.health"
SECURITY_SUMMARY    = "sorabbyngo.security.summary"

# ACP routing
ACP_PREFIX = "sorabbyngo.byngox.acp"

# Threat routing rules
HEALTH_THREATS = {
    "data_exfil", "ransomware", "webshell",
    "backdoor", "malware_detected", "file_tamper",
}
POPULATION_THREATS = {
    "port_scan", "syn_flood", "ddos",
    "lateral_movement", "botnet", "xmas_scan",
}

# AI analysis threshold
AI_SCORE_THRESHOLD = 8.0

# Memory
THREAT_BUFFER_SIZE     = 200
COORDINATION_THRESHOLD = 5   # same src_ip hitting N+ times = coordinated

SYSTEM_PROMPT = """You are the Sorabbyngo security intelligence analyst.
RULES:
- Analyse threats on an Africa-native AI OS (Sorabbyngo)
- Consider offline-first, edge clinic context
- Flag patient data threats as highest priority
- Output JSON only — no markdown, no preamble

Output format:
{
  "attack_classification": "",
  "likely_actor": "",
  "severity_assessment": "low|medium|high|critical",
  "recommended_response": "",
  "patient_data_risk": true|false,
  "africa_context": "",
  "confidence": 0.0
}"""


class SecurityAgent:
    def __init__(self, nodeid: str):
        self.nodeid  = nodeid
        self._nc     = None
        self._js     = None
        self._model  = SECURITY_MODEL
        self._cml    = None

        # State
        self._threat_buffer: deque = deque(maxlen=THREAT_BUFFER_SIZE)
        self._attack_map: dict     = defaultdict(int)   # src_ip → hit count
        self._blocked_ips: set     = set()
        self._node_threats: dict   = defaultdict(list)  # node_id → threats

    async def start(self):
        # Load CML client
        try:
            from cml_client import get_client
            self._cml = get_client()
            log.info("[SecurityAgent] CML client loaded")
        except ImportError:
            log.warning("[SecurityAgent] CML client not found — running without safety filter")

        self._nc = await nats.connect(NATS_URL)
        self._js = self._nc.jetstream()
        self._model = await self._select_model()
        log.info("[SecurityAgent] Model: %s", self._model)

        # Subscribe to cyberwall subjects
        await self._nc.subscribe(CYBERWALL_ALERT,     cb=self._on_alert)
        await self._nc.subscribe(CYBERWALL_BLOCK,     cb=self._on_block)
        await self._nc.subscribe(SENTINEL_ESCALATION, cb=self._on_escalation)
        await self._nc.subscribe(SENTINEL_HEALTH,     cb=self._on_health)

        # Subscribe to inbound ACP (other agents querying security)
        await self._nc.subscribe(
            f"{ACP_PREFIX}.security_agent",
            cb=self._on_acp,
        )

        log.info("[SecurityAgent] Ready — watching cyberwall + sentinel")

        # Background tasks
        await asyncio.gather(
            self._correlation_loop(),
            self._summary_loop(),
        )

    # ── Model Selection ───────────────────────────────────────────────────────

    async def _select_model(self) -> str:
        candidates = [
            os.environ.get("TIER2_REASONING_MODEL", "deepseek-r1:70b"),
            os.environ.get("TIER1_MODEL",            "phi4-mini"),
        ]
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{OLLAMA_URL}/api/tags")
                available = {m["name"] for m in r.json().get("models", [])}
                for model in candidates:
                    if model in available:
                        return model
        except Exception:
            pass
        return SECURITY_MODEL

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def _on_alert(self, msg):
        try:
            data = json.loads(msg.data.decode())
        except Exception:
            return

        node_id     = data.get("node_id", "unknown")
        threat_type = data.get("threat_type", "unknown")
        level       = data.get("level", "INFO")
        score       = float(data.get("score", 0))
        src_ip      = data.get("data", {}).get("src_ip", "")

        log.warning(
            "[SecurityAgent] THREAT [%s] score=%.1f | %s | node=%s | src=%s",
            level, score, threat_type, node_id[:12], src_ip,
        )

        # Record
        self._threat_buffer.append(data)
        self._node_threats[node_id].append(data)
        if len(self._node_threats[node_id]) > THREAT_BUFFER_SIZE:
            self._node_threats[node_id].pop(0)

        # Track attack sources
        if src_ip:
            self._attack_map[src_ip] += 1

        # Cross-agent routing
        if threat_type in HEALTH_THREATS:
            await self._acp("health_agent", "security_threat_health_data", {
                "threat_type": threat_type,
                "level":       level,
                "score":       score,
                "description": data.get("description", ""),
                "node_id":     node_id,
                "timestamp":   data.get("timestamp", ""),
            })

        if threat_type in POPULATION_THREATS:
            await self._acp("population_agent", "network_threat_detected", {
                "threat_type": threat_type,
                "src_ip":      src_ip,
                "score":       score,
                "node_id":     node_id,
                "timestamp":   data.get("timestamp", ""),
            })

        # AI deep analysis for high-score threats
        if score >= AI_SCORE_THRESHOLD:
            asyncio.create_task(self._analyse(data))

    async def _on_block(self, msg):
        try:
            data = json.loads(msg.data.decode())
            ip   = data.get("data", {}).get("ip", "")
            if ip:
                self._blocked_ips.add(ip)
                log.warning("[SecurityAgent] BLOCK confirmed: %s", ip)
        except Exception as e:
            log.error("[SecurityAgent] Block handler error: %s", e)

    async def _on_escalation(self, msg):
        try:
            data    = json.loads(msg.data.decode())
            reason  = data.get("reason", "")
            node_id = data.get("node_id", "unknown")
            log.critical("[SecurityAgent] ESCALATION from %s: %s", node_id[:12], reason)
            await self._acp("coordination_agent", "security_escalation", {
                "reason":    reason,
                "node_id":   node_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data":      data,
            })
        except Exception as e:
            log.error("[SecurityAgent] Escalation handler error: %s", e)

    async def _on_health(self, msg):
        try:
            data = json.loads(msg.data.decode())
            dead = data.get("dead", [])
            if "cyberwall" in dead or "cml" in dead:
                log.critical(
                    "[SecurityAgent] Security service down on %s: %s",
                    data.get("node_id", "?")[:12], dead,
                )
                await self._acp("coordination_agent", "security_service_down", {
                    "dead_services": dead,
                    "node_id":       data.get("node_id"),
                    "timestamp":     datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            log.error("[SecurityAgent] Health handler error: %s", e)

    async def _on_acp(self, msg):
        """Handle inbound ACP queries from other agents."""
        try:
            req    = json.loads(msg.data.decode())
            action = req.get("action", "")
            result = {}

            if action == "query_threat_summary":
                result = self._build_summary()
            elif action == "query_node_threats":
                node_id = req.get("payload", {}).get("node_id", "")
                result  = {"threats": self._node_threats.get(node_id, [])}
            elif action == "query_top_attackers":
                result = {
                    "top_attackers": sorted(
                        self._attack_map.items(),
                        key=lambda x: x[1], reverse=True
                    )[:10]
                }
            elif action == "is_blocked":
                ip     = req.get("payload", {}).get("ip", "")
                result = {"blocked": ip in self._blocked_ips}

            if msg.reply:
                await self._nc.publish(msg.reply, json.dumps(result).encode())

        except Exception as e:
            log.error("[SecurityAgent] ACP handler error: %s", e)

    # ── AI Analysis ───────────────────────────────────────────────────────────

    async def _analyse(self, threat: dict):
        prompt = (
            f"Threat event on Sorabbyngo node {threat.get('node_id','?')[:12]}:\n"
            f"{json.dumps(threat, indent=2)}\n"
            f"Analyse and respond in JSON only."
        )
        raw = await self._run_inference(prompt)
        result = self._parse(raw)

        # CML filter on AI output
        if self._cml and result.get("recommended_response"):
            cml_result = await self._cml.filter(
                text      = result["recommended_response"],
                component = "byngox.security_agent",
                context   = "security",
                entity_id = threat.get("node_id"),
            )
            if not cml_result["allowed"]:
                log.warning("[SecurityAgent] CML filtered AI response")
                result["recommended_response"] = "Manual security review required."
                result["cml_blocked"] = True

        if result:
            log.info(
                "[SecurityAgent] AI: %s | patient_data_risk=%s | confidence=%.2f",
                result.get("attack_classification", "?"),
                result.get("patient_data_risk", False),
                result.get("confidence", 0.0),
            )
            # Attach to threat record
            node_id  = threat.get("node_id", "unknown")
            node_log = self._node_threats.get(node_id, [])
            if node_log:
                node_log[-1]["ai_analysis"] = result

            # Publish AI result
            await self._nc.publish(
                "sorabbyngo.security.ai_analysis",
                json.dumps({
                    "node_id":   node_id,
                    "threat":    threat,
                    "analysis":  result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model":     self._model,
                }).encode()
            )

    async def _run_inference(self, prompt: str) -> str:
        payload = {
            "model":  self._model,
            "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 512},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "").strip()

    def _parse(self, raw: str) -> dict:
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception:
            return {
                "attack_classification": "parse_error",
                "recommended_response":  "Manual security review required.",
                "confidence":            0.0,
                "patient_data_risk":     False,
                "flags":                 ["parse_error"],
            }

    # ── Correlation Loop ──────────────────────────────────────────────────────

    async def _correlation_loop(self):
        while True:
            await asyncio.sleep(60)
            coordinated = {
                ip: count
                for ip, count in self._attack_map.items()
                if count >= COORDINATION_THRESHOLD
            }
            if not coordinated:
                continue
            log.warning(
                "[SecurityAgent] COORDINATED ATTACK — %d sources: %s",
                len(coordinated), list(coordinated)[:5],
            )
            await self._acp("coordination_agent", "coordinated_attack_detected", {
                "sources":   coordinated,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            # Publish to mesh for other nodes
            await self._nc.publish(
                "sorabbyngo.security.coordinated_attack",
                json.dumps({
                    "node_id":   self.nodeid,
                    "sources":   coordinated,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }).encode()
            )

    # ── Summary Loop ─────────────────────────────────────────────────────────

    async def _summary_loop(self):
        while True:
            await asyncio.sleep(300)
            summary = self._build_summary()
            log.info("[SecurityAgent] SUMMARY: %s", summary)
            await self._nc.publish(
                SECURITY_SUMMARY,
                json.dumps(summary).encode(),
            )

    def _build_summary(self) -> dict:
        total = len(self._threat_buffer)
        by_level: dict = {}
        for t in self._threat_buffer:
            lvl = t.get("level", "INFO")
            by_level[lvl] = by_level.get(lvl, 0) + 1
        return {
            "timestamp":      datetime.now(timezone.utc).isoformat(),
            "node_id":        self.nodeid,
            "total_threats":  total,
            "by_level":       by_level,
            "nodes_affected": len(self._node_threats),
            "blocked_ips":    len(self._blocked_ips),
            "top_attackers":  sorted(
                self._attack_map.items(),
                key=lambda x: x[1], reverse=True
            )[:5],
            "agent": "security_agent",
        }

    # ── ACP Helper ────────────────────────────────────────────────────────────

    async def _acp(self, target: str, action: str, payload: dict):
        msg = {
            "from":      "security_agent",
            "to":        target,
            "action":    action,
            "payload":   payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            await self._nc.publish(
                f"{ACP_PREFIX}.{target}",
                json.dumps(msg).encode(),
            )
        except Exception as e:
            log.error("[SecurityAgent] ACP publish failed → %s: %s", target, e)

    async def stop(self):
        if self._nc:
            await self._nc.drain()
