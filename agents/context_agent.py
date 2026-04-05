# Context Agent
# Patient history and episodic memory

from .base_agent import BaseAgent
import logging
log = logging.getLogger(__name__)

class ContextAgent(BaseAgent):
    def __init__(self, nodeid: str):
        super().__init__(nodeid, "ContextAgent")

    async def run(self):
        log.info("ContextAgent ready — episodic memory active")
        # TODO Phase 4: Connect to LanceDB vector store
        # TODO Phase 4: Connect to Neo4j knowledge graph
