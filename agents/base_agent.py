# Base Agent
# All Byngox agents inherit from this

import logging
log = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, nodeid: str, name: str):
        self.nodeid = nodeid
        self.name = name

    async def start(self):
        log.info(f"{self.name} started on node {self.nodeid}")
        await self.run()

    async def run(self):
        raise NotImplementedError(f"{self.name} must implement run()")

    async def handle(self, message):
        raise NotImplementedError(f"{self.name} must implement handle()")
