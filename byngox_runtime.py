# Byngox Runtime
# Starts and manages all swarm agents via NATS

import asyncio
import logging
from agents.health_agent import HealthAgent
from agents.drug_agent import DrugAgent
from agents.context_agent import ContextAgent
from agents.network_agent import NetworkAgent
from agents.learning_agent import LearningAgent
from agents.population_agent import PopulationAgent

log = logging.getLogger(__name__)

class ByngoxRuntime:
    def __init__(self, nodeid: str, nats_url: str = "nats://localhost:4222"):
        self.nodeid = nodeid
        self.nats_url = nats_url
        self.agents = []

    async def start(self):
        log.info(f"Byngox starting on node {self.nodeid}")
        self.agents = [
            HealthAgent(self.nodeid),
            DrugAgent(self.nodeid),
            ContextAgent(self.nodeid),
            NetworkAgent(self.nodeid),
            LearningAgent(self.nodeid),
            PopulationAgent(self.nodeid),
        ]
        await asyncio.gather(*[agent.start() for agent in self.agents])
        log.info("All Byngox agents started.")

if __name__ == "__main__":
    nodeid = open("/proc/sorabbyngo/nodeid").read().strip()
    runtime = ByngoxRuntime(nodeid=nodeid)
    asyncio.run(runtime.start())
