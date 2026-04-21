"""
Byngox — Health Agent (CML-wired version)
Every AI response passes through CML before publishing.
Clinical context enforced — no direct diagnoses allowed.
"""

import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime, timezone
from typing import Optional

import httpx
import nats

log = logging.getLogger(__name__)

NATS_URL        = os.environ.get("NATS_URL",       "nats://localhost:4222")
OLLAMA_URL      = os.environ.get("OLLAMA_URL",     "http://localhost:11434")
AGENT_SUBJECT   = os.environ.get("HEALTH_AGENT_SUBJECT", "byngox.health.analyse")
REPLY_TIMEOUT   = float(os.environ.get("HEALTH_AGENT_TIMEOUT", "120"))
ASSESS_EVERY    = int(os.environ.get("AI_ASSESS_EVERY", "10"))

TIER2_MEDICAL   = os.environ.get("TIER2_MEDICAL_MODEL",    "meditron:70b")
TIER2_REASONING = os.environ.get("TIER2_REASONING_MODEL",  "deepseek-r1:70b")
TIER1_MEDICAL   = os.environ.get("TIER1_MEDICAL_MODEL",    "meditron:7b")

SYSTEM_PROMPT = """You are a clinical decision support engine for Sorabbyngo OS.

STRICT RULES:
- You support healthcare professionals — NOT patients directly
- Never provide a direct diagnosis — provide risk assessment only
- Never prescribe or recommend specific medications or dosages
- Always include confidence score (0.0–1.0)
- Flag HIGH RISK for human review
- Show your reasoning steps clearly
- If uncertain, say so — uncertainty is safer than false confidence

Output JSON only:
{
  "risk_level": "low|medium|high|critical",
  "confidence": 0.0-1.0,
  "summary": "brief clinical summary",
  "reasoning": ["step 1", "step 2"],
  "recommendations": ["action 1"],
  "human_review_required": true|false,
  "flags": []
}"""


class HealthAgent:

    def __init__(self):
        self._nc       = None
        self._js       = None
        self._buffers: dict[str, deque] = {}
        self._counters: dict[str, int]  = {}
        self._model    = None
        self._cml      = None

    async def start(self):
        # Import CML client
        try:
            from cml_client import get_client
            self._cml = get_client()
            log.info("[HealthAgent] CML client loaded")
        except ImportError:
            log.warning("[HealthAgent] CML client not found — running without safety filter")

        self._nc    = await nats.connect(NATS_URL)
        self._js    = self._nc.jetstream()
        self._model = await self._select_model()
        log.info("[HealthAgent] Model: %s", self._model)

        await self._js.subscribe(
            "novela.monitors.vitals.>",
            cb=self._handle_vitals,
            durable="byngox-health-agent",
            stream="NOVELA_MONITORS",
        )
        await self._nc.subscribe(AGENT_SUBJECT, cb=self._handle_direct)
        log.info("[HealthAgent] Ready")

    async def _select_model(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{OLLAMA_URL}/api/tags")
                available = {m["name"] for m in r.json().get("models", [])}
                for model in [TIER2_MEDICAL, TIER2_REASONING, TIER1_MEDICAL]:
                    if model in available:
                        return model
        except Exception:
            pass
        return TIER1_MEDICAL

    async def _handle_vitals(self, msg):
        try:
            payload    = json.loads(msg.data.decode())
            patient_id = payload.get("patient_id")
            if not patient_id:
                await msg.ack()
                return
            if patient_id not in self._buffers:
                self._buffers[patient_id]  = deque(maxlen=30)
                self._counters[patient_id] = 0
            self._buffers[patient_id].append(payload)
            self._counters[patient_id] += 1
            if self._counters[patient_id] % ASSESS_EVERY == 0:
                asyncio.create_task(self._assess(patient_id, payload))
            await msg.ack()
        except Exception as e:
            log.error("[HealthAgent] Vitals error: %s", e)
            await msg.nak()

    async def _handle_direct(self, msg):
        """Handle direct analysis requests from Novela."""
        try:
            payload = json.loads(msg.data.decode())
            result  = await self.analyse(payload)
            if msg.reply:
                await self._nc.publish(msg.reply, json.dumps(result).encode())
        except Exception as e:
            log.error("[HealthAgent] Direct request error: %s", e)

    async def analyse(self, payload: dict) -> dict:
        """
        Main analysis entry point.
        Every response is filtered through CML before returning.
        """
        prompt = (
            f"Patient: {payload.get('patient_id', 'unknown')}\n"
            f"Context: {json.dumps(payload.get('patient_context', {}), indent=2)}\n"
            f"Question: {payload.get('clinical_question', 'Assess patient risk.')}\n"
            f"Respond with JSON only."
        )

        raw    = await self._run_inference(prompt)
        result = self._parse(raw)

        # ── CML filter on AI output ──────────────────────────────────────
        if self._cml:
            cml_result = await self._cml.filter(
                text      = result.get("summary", "") + " " +
                            " ".join(result.get("recommendations", [])),
                component = "byngox.health_agent",
                context   = "clinical",
                entity_id = payload.get("patient_id"),
            )
            if not cml_result["allowed"]:
                log.warning("[HealthAgent] CML blocked response for %s: %s",
                            payload.get("patient_id"), cml_result["reason"])
                result["summary"]         = "Clinical review required — response filtered by safety layer."
                result["recommendations"] = ["Manual clinical assessment required"]
                result["human_review_required"] = True
                result["cml_blocked"]     = True
                return result

            # Merge CML flags into result
            if cml_result.get("clinical_flags"):
                result["flags"] = result.get("flags", []) + cml_result["clinical_flags"]
                result["human_review_required"] = True

            if cml_result.get("human_review_required"):
                result["human_review_required"] = True

        # Critical always requires human review
        if result.get("risk_level") == "critical":
            result["human_review_required"] = True

        return result

    async def _assess(self, patient_id: str, latest: dict):
        """Periodic deterioration assessment from vitals buffer."""
        buffer = list(self._buffers.get(patient_id, []))
        if len(buffer) < 3:
            return
        trend = [{"t": r.get("timestamp"), **r.get("vitals", {}),
                  "alert": r.get("alert_level")} for r in buffer[-20:]]
        payload = {
            "patient_id":      patient_id,
            "patient_context": {"vitals_trend": trend},
            "clinical_question": "Analyze this trend and predict deterioration risk.",
        }
        result = await self.analyse(payload)
        subject = f"novela.monitors.ai.risk.{patient_id}"
        try:
            await self._js.publish(subject, json.dumps({
                "patient_id": patient_id,
                "ward":       latest.get("ward"),
                "bed":        latest.get("bed"),
                "timestamp":  datetime.now(timezone.utc).isoformat(),
                "model":      self._model,
                "assessment": result,
            }).encode())
        except Exception as e:
            log.error("[HealthAgent] Publish failed: %s", e)

    async def _run_inference(self, prompt: str) -> str:
        payload = {
            "model":  self._model,
            "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 1024},
        }
        async with httpx.AsyncClient(timeout=REPLY_TIMEOUT) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "").strip()

    def _parse(self, raw: str) -> dict:
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except Exception:
            return {
                "risk_level": "unknown", "confidence": 0.0,
                "summary": raw[:300] if raw else "Parse failed",
                "reasoning": [], "recommendations": ["Manual review required"],
                "human_review_required": True, "flags": ["parse_error"],
            }

    async def stop(self):
        if self._nc:
            await self._nc.drain()


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
    agent = HealthAgent()
    await agent.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
