"""
context_agent.py — Context Agent
Patient history and episodic memory.
Subscribes to byngox.context.fetch and byngox.context.update on NATS.
Stores/retrieves patient context in LanceDB (vector) + JSON file fallback.
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
FETCH_SUBJECT  = os.environ.get("CONTEXT_FETCH_SUBJECT",  "byngox.context.fetch")
UPDATE_SUBJECT = os.environ.get("CONTEXT_UPDATE_SUBJECT", "byngox.context.update")
STORE_PATH     = os.environ.get("CONTEXT_STORE_PATH",
    os.path.expanduser("~/.sorabbyngo/byngox/context_store.json"))


class ContextAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "ContextAgent")
        self._store: dict = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self):
        try:
            with open(STORE_PATH) as f:
                self._store = json.load(f)
            log.info("[ContextAgent] loaded %d patient contexts", len(self._store))
        except (FileNotFoundError, json.JSONDecodeError):
            self._store = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
            with open(STORE_PATH, "w") as f:
                json.dump(self._store, f, indent=2)
        except Exception as e:
            log.error("[ContextAgent] save failed: %s", e)

    # ── Context operations ────────────────────────────────────────────────────

    def get_context(self, patient_ref: str) -> dict:
        return self._store.get(patient_ref, {
            "patient_ref":  patient_ref,
            "vitals":       {},
            "conditions":   [],
            "medications":  [],
            "history":      [],
            "last_updated": None,
        })

    def update_context(self, patient_ref: str, update: dict) -> dict:
        ctx = self.get_context(patient_ref)
        # Merge vitals
        if "vitals" in update:
            ctx["vitals"].update(update["vitals"])
        # Append conditions/medications (deduplicate)
        for field in ("conditions", "medications"):
            if field in update:
                existing = set(ctx[field])
                for item in update[field]:
                    if item not in existing:
                        ctx[field].append(item)
                        existing.add(item)
        # Append history entry
        if "event" in update:
            ctx["history"].append({
                "event":     update["event"],
                "timestamp": time.time(),
            })
            # Keep last 100 history entries
            ctx["history"] = ctx["history"][-100:]
        ctx["last_updated"] = time.time()
        self._store[patient_ref] = ctx
        self._save()
        return ctx

    # ── NATS subscriber ───────────────────────────────────────────────────────

    async def run(self):
        log.info("[ContextAgent] connecting to NATS %s", NATS_URL)
        nc = await nats.connect(NATS_URL)

        async def fetch_handler(msg):
            try:
                payload     = json.loads(msg.data.decode())
                patient_ref = payload.get("patient_ref", "")
                context     = self.get_context(patient_ref)
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps(context).encode())
            except Exception as e:
                log.error("[ContextAgent] fetch error: %s", e)

        async def update_handler(msg):
            try:
                payload     = json.loads(msg.data.decode())
                patient_ref = payload.get("patient_ref", "")
                if not patient_ref:
                    return
                updated = self.update_context(patient_ref, payload)
                log.info("[ContextAgent] updated context for %s", patient_ref[:12])
                if msg.reply:
                    await nc.publish(msg.reply, json.dumps(updated).encode())
            except Exception as e:
                log.error("[ContextAgent] update error: %s", e)

        await nc.subscribe(FETCH_SUBJECT,  cb=fetch_handler)
        await nc.subscribe(UPDATE_SUBJECT, cb=update_handler)
        log.info("[ContextAgent] subscribed to %s, %s", FETCH_SUBJECT, UPDATE_SUBJECT)
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    import hashlib, socket
    try:
        nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
    asyncio.run(ContextAgent(nodeid).run())
