"""
learning_agent.py — Learning Agent
Collects feedback from clinical decisions.
Subscribes to byngox.learn.feedback on NATS.
Logs feedback for future LoRA adapter fine-tuning.
"""
import asyncio
import json
import logging
import os
import time

import nats

from .base_agent import BaseAgent

log = logging.getLogger(__name__)

NATS_URL       = os.environ.get("NATS_URL", "nats://localhost:4223")
AGENT_SUBJECT  = os.environ.get("LEARN_SUBJECT", "byngox.learn.feedback")
FEEDBACK_LOG   = os.environ.get("FEEDBACK_LOG",
    os.path.expanduser("~/.sorabbyngo/byngox/feedback.jsonl"))


class LearningAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "LearningAgent")
        self._count = 0

    def _log_feedback(self, entry: dict):
        try:
            os.makedirs(os.path.dirname(FEEDBACK_LOG), exist_ok=True)
            entry["logged_at"] = time.time()
            with open(FEEDBACK_LOG, "a") as f:
                f.write(json.dumps(entry) + "\n")
            self._count += 1
        except Exception as e:
            log.error("[LearningAgent] log failed: %s", e)

    async def run(self):
        log.info("[LearningAgent] connecting to NATS %s", NATS_URL)
        nc = await nats.connect(NATS_URL)

        async def handler(msg):
            try:
                payload = json.loads(msg.data.decode())
                # Expected fields:
                #   patient_ref, model, tier, prediction, actual_outcome,
                #   clinician_override (bool), notes
                self._log_feedback(payload)
                log.info(
                    "[LearningAgent] feedback logged #%d model=%s",
                    self._count, payload.get("model", "unknown")
                )
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps({
                        "logged": True, "count": self._count
                    }).encode())
            except Exception as e:
                log.error("[LearningAgent] handler error: %s", e)

        await nc.subscribe(AGENT_SUBJECT, cb=handler)
        log.info("[LearningAgent] subscribed to %s", AGENT_SUBJECT)
        # Periodic summary log every 5 minutes
        while True:
            await asyncio.sleep(300)
            log.info("[LearningAgent] feedback collected: %d entries", self._count)


if __name__ == "__main__":
    import hashlib, socket
    try:
        nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
    asyncio.run(LearningAgent(nodeid).run())
