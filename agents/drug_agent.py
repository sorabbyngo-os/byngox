"""
drug_agent.py — Drug Agent
Medication verification and counterfeit detection.
Subscribes to byngox.drug.verify on NATS.
Delegates analysis to Novela counterfeit endpoint via HTTP.
"""
import asyncio
import json
import logging
import os
import urllib.request
import urllib.error

import nats

from .base_agent import BaseAgent

log = logging.getLogger(__name__)

NATS_URL       = os.environ.get("NATS_URL",       "nats://localhost:4223")
AGENT_SUBJECT  = os.environ.get("DRUG_AGENT_SUBJECT", "byngox.drug.verify")
NOVELA_URL     = os.environ.get("NOVELA_URL",     "http://localhost:8001")
NOVELA_TOKEN   = os.environ.get("NOVELA_SERVICE_TOKEN", "")


class DrugAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "DrugAgent")

    async def run(self):
        log.info("[DrugAgent] connecting to NATS %s", NATS_URL)
        nc = await nats.connect(NATS_URL)

        async def handler(msg):
            try:
                payload = json.loads(msg.data.decode())
                result  = await self.verify(
                    medication_name=payload.get("medication_name", ""),
                    barcode=payload.get("barcode", ""),
                    image_url=payload.get("image_url", ""),
                )
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps(result).encode())
            except Exception as e:
                log.error("[DrugAgent] handler error: %s", e)
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps({
                        "status": "UNKNOWN", "confidence": 0.0,
                        "reasoning": f"Agent error: {e}",
                    }).encode())

        await nc.subscribe(AGENT_SUBJECT, cb=handler)
        log.info("[DrugAgent] subscribed to %s", AGENT_SUBJECT)
        while True:
            await asyncio.sleep(1)

    async def verify(self, medication_name: str = "", barcode: str = "",
                     image_url: str = "") -> dict:
        """
        Verify medication authenticity via Novela counterfeit endpoint.
        Falls back to UNKNOWN if Novela is unreachable.
        """
        try:
            body = json.dumps({
                "medication_name": medication_name,
                "barcode":         barcode,
                "image_url":       image_url,
            }).encode()
            headers = {"Content-Type": "application/json"}
            if NOVELA_TOKEN:
                headers["Authorization"] = f"Bearer {NOVELA_TOKEN}"
            req = urllib.request.Request(
                f"{NOVELA_URL}/api/v1/counterfeit/verify/",
                data=body, headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
                return data.get("data", {})
        except urllib.error.URLError:
            log.warning("[DrugAgent] Novela unreachable — returning UNKNOWN")
            return {
                "status": "UNKNOWN", "confidence": 0.0,
                "reasoning": "Novela service unreachable.",
                "risk_indicators": [],
            }
        except Exception as e:
            log.error("[DrugAgent] verify error: %s", e)
            return {
                "status": "UNKNOWN", "confidence": 0.0,
                "reasoning": f"Verification failed: {e}",
                "risk_indicators": [],
            }


if __name__ == "__main__":
    import hashlib, socket
    try:
        nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
    asyncio.run(DrugAgent(nodeid).run())
