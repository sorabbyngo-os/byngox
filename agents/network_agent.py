"""
network_agent.py — Network Agent
Byngonet coordination and distributed task dispatch.
Phase 5: full mesh dispatch via byngonet kernel module.
Phase 4: NATS keepalive + mesh peer discovery.
"""
import asyncio
import json
import logging
import os

import nats

from .base_agent import BaseAgent

log = logging.getLogger(__name__)

NATS_URL      = os.environ.get("NATS_URL",    "nats://localhost:4223")
MESH_SUBJECT  = os.environ.get("MESH_SUBJECT","byngox.network.mesh")


class NetworkAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "NetworkAgent")
        self._peers: dict = {}

    async def run(self):
        log.info("[NetworkAgent] connecting to NATS %s", NATS_URL)
        nc = await nats.connect(NATS_URL)

        async def mesh_handler(msg):
            """Track peer nodes from Byngonet mesh events."""
            try:
                payload = json.loads(msg.data.decode())
                peer_id = payload.get("mesh_id", "")
                if peer_id:
                    self._peers[peer_id] = {
                        "last_seen": payload.get("timestamp"),
                        "hostname":  payload.get("hostname"),
                        "sealed":    payload.get("sealed", False),
                    }
                    log.debug("[NetworkAgent] peer seen: %s...", peer_id[:12])
            except Exception as e:
                log.error("[NetworkAgent] mesh handler error: %s", e)

        await nc.subscribe(MESH_SUBJECT, cb=mesh_handler)
        # Also listen to byngonet mesh events from kernel driver
        await nc.subscribe("sorabbyngo.byngonet.mesh.>", cb=mesh_handler)
        log.info("[NetworkAgent] subscribed — tracking mesh peers")
        log.info("[NetworkAgent] Phase 5 TODO: ioctl dispatch via byngonet kernel module")

        while True:
            await asyncio.sleep(60)
            active = len(self._peers)
            log.info("[NetworkAgent] mesh peers tracked: %d", active)


if __name__ == "__main__":
    import hashlib, socket
    try:
        nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
    asyncio.run(NetworkAgent(nodeid).run())
