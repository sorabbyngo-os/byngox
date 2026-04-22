"""
population_agent.py — Population Agent
Epidemiology, outbreak detection, and heatmap aggregation.
Subscribes to byngox.population.ping on NATS.
Aggregates anonymous health signals for population health intelligence.
"""
import asyncio
import collections
import json
import logging
import os
import time

import nats

from .base_agent import BaseAgent

log = logging.getLogger(__name__)

NATS_URL      = os.environ.get("NATS_URL", "nats://localhost:4222")
PING_SUBJECT  = os.environ.get("POPULATION_PING_SUBJECT", "byngox.population.ping")
QUERY_SUBJECT = os.environ.get("POPULATION_QUERY_SUBJECT","byngox.population.query")
STATS_LOG     = os.environ.get("POPULATION_STATS_LOG",
    os.path.expanduser("~/.sorabbyngo/byngox/population_stats.jsonl"))

# Outbreak detection thresholds — cases per county per 24h
OUTBREAK_THRESHOLDS = {
    "malaria":    10,
    "cholera":    5,
    "typhoid":    8,
    "covid":      20,
    "default":    15,
}


class PopulationAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "PopulationAgent")
        # county → condition → list of timestamps
        self._signals: dict = collections.defaultdict(
            lambda: collections.defaultdict(list)
        )
        self._alerts_sent: set = set()

    def _record_signal(self, county: str, condition: str):
        now = time.time()
        self._signals[county][condition].append(now)
        # Prune signals older than 24h
        cutoff = now - 86400
        self._signals[county][condition] = [
            t for t in self._signals[county][condition] if t > cutoff
        ]

    def _check_outbreak(self, county: str, condition: str) -> bool:
        count     = len(self._signals[county][condition])
        threshold = OUTBREAK_THRESHOLDS.get(condition.lower(),
                    OUTBREAK_THRESHOLDS["default"])
        return count >= threshold

    def _get_stats(self, county: str = None) -> dict:
        result = {}
        counties = [county] if county else list(self._signals.keys())
        for c in counties:
            result[c] = {
                cond: len(timestamps)
                for cond, timestamps in self._signals[c].items()
            }
        return result

    def _log_stats(self, entry: dict):
        try:
            os.makedirs(os.path.dirname(STATS_LOG), exist_ok=True)
            entry["logged_at"] = time.time()
            with open(STATS_LOG, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            log.error("[PopulationAgent] log failed: %s", e)

    async def run(self):
        log.info("[PopulationAgent] connecting to NATS %s", NATS_URL)
        nc = await nats.connect(NATS_URL)

        async def ping_handler(msg):
            """
            Receive anonymous population health signal.
            Expected: {"county": "Kisii", "condition": "malaria", "count": 1}
            PII is never included — county-level aggregation only.
            """
            try:
                payload   = json.loads(msg.data.decode())
                county    = payload.get("county", "unknown")
                condition = payload.get("condition", "unknown")
                count     = int(payload.get("count", 1))

                for _ in range(count):
                    self._record_signal(county, condition)

                # Check outbreak threshold
                if self._check_outbreak(county, condition):
                    alert_key = f"{county}:{condition}"
                    if alert_key not in self._alerts_sent:
                        self._alerts_sent.add(alert_key)
                        alert = {
                            "type":      "outbreak_alert",
                            "county":    county,
                            "condition": condition,
                            "count":     len(self._signals[county][condition]),
                            "threshold": OUTBREAK_THRESHOLDS.get(
                                condition.lower(), OUTBREAK_THRESHOLDS["default"]),
                            "timestamp": time.time(),
                        }
                        await nc.publish(
                            "sorabbyngo.byngox.risk",
                            json.dumps({
                                "source":    "byngox.population",
                                "message":   f"Outbreak alert: {condition} in {county} ({alert['count']} cases/24h)",
                                "severity":  "critical",
                                "confidence":0.85,
                                **alert,
                            }).encode()
                        )
                        self._log_stats(alert)
                        log.warning(
                            "[PopulationAgent] OUTBREAK ALERT: %s in %s (%d cases)",
                            condition, county, alert["count"]
                        )
            except Exception as e:
                log.error("[PopulationAgent] ping error: %s", e)

        async def query_handler(msg):
            """Return current population stats for a county."""
            try:
                payload = json.loads(msg.data.decode())
                county  = payload.get("county")
                stats   = self._get_stats(county)
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps(stats).encode())
            except Exception as e:
                log.error("[PopulationAgent] query error: %s", e)

        await nc.subscribe(PING_SUBJECT,  cb=ping_handler)
        await nc.subscribe(QUERY_SUBJECT, cb=query_handler)
        log.info("[PopulationAgent] subscribed to %s, %s", PING_SUBJECT, QUERY_SUBJECT)

        # Periodic stats flush every 10 minutes
        while True:
            await asyncio.sleep(600)
            stats = self._get_stats()
            if stats:
                self._log_stats({"type": "periodic_stats", "stats": stats})
                log.info("[PopulationAgent] stats: %s", json.dumps(stats))
            # Reset alert dedup every 6 hours
            self._alerts_sent.clear()


if __name__ == "__main__":
    import hashlib, socket
    try:
        nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
    asyncio.run(PopulationAgent(nodeid).run())
