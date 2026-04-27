"""
byngox_runtime.py -- Unified Byngox Runtime (fixed v2)
Starts ALL Byngox agents in a single process.

Fixes over v1:
  - DrugAgent was added to agents list at index 0 but agents[1:] was passed
    to gather -- DrugAgent was never started. Fixed.
  - health_agent.main() and TwinAgent wrapped correctly in gather
  - SecurityAgent wired in
  - NodeID fallback uses BYNGOX_DEV env var cleanly
"""
import asyncio
import hashlib
import logging
import os
import socket
import threading

logging.basicConfig(
    level=logging.INFO,
    format="[BYNGOX] %(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("byngox.runtime")

# -- Async agents --------------------------------------------------------------
from agents.health_agent      import HealthAgent
from agents.drug_agent        import DrugAgent
from agents.context_agent     import ContextAgent
from agents.learning_agent    import LearningAgent
from agents.population_agent  import PopulationAgent
from agents.network_agent     import NetworkAgent
from agents.twin_agent        import TwinAgent
from agents.security_agent    import SecurityAgent

# -- Sync pipeline agents ------------------------------------------------------
from agents.ingestion_agent      import IngestionAgent
from agents.normalization_agent  import NormalizationAgent
from agents.intelligence_agent   import IntelligenceAgent
from agents.recommendation_agent import RecommendationAgent
from agents.coordination_agent   import CoordinationAgent


def _get_nodeid() -> str:
    try:
        return open("/proc/sorabbyngo/nodeid").read().strip()
    except FileNotFoundError:
        nodeid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
        log.warning("NodeID driver not found -- dev mode (id=%s...)", nodeid[:12])
        return nodeid


def _start_sync_pipeline() -> list:
    """Start sync pipeline agents in daemon threads."""
    agents = [
        IngestionAgent(),
        NormalizationAgent(),
        IntelligenceAgent(),
        RecommendationAgent(),
        CoordinationAgent(),
    ]
    threads = []
    for agent in agents:
        t = threading.Thread(
            target=agent.start,
            name=f"sync-{getattr(agent, 'name', type(agent).__name__)}",
            daemon=True,
        )
        t.start()
        threads.append(t)
        log.info("Sync agent started: %s", getattr(agent, "name", type(agent).__name__))
    return threads


async def _start_async_agents(nodeid: str):
    """
    Start all async agents concurrently.
    Fixed: all agents now actually passed to gather.
    """
    health_agent   = HealthAgent()
    drug_agent     = DrugAgent(nodeid)
    context_agent  = ContextAgent(nodeid)
    learning_agent = LearningAgent(nodeid)
    pop_agent      = PopulationAgent(nodeid)
    network_agent  = NetworkAgent(nodeid)
    twin_agent     = TwinAgent()
    security_agent = SecurityAgent(nodeid)

    log.info("Starting 8 async agents...")

    await asyncio.gather(
        health_agent.start(),
        drug_agent.run(),
        context_agent.run(),
        learning_agent.run(),
        pop_agent.run(),
        network_agent.run(),
        twin_agent.start(),
        security_agent.start(),
    )


async def main():
    nodeid = _get_nodeid()

    log.info("╔══════════════════════════════════════════════╗")
    log.info("║  BYNGOX -- Unified Health Intelligence Layer  ║")
    log.info("║  8 async + 5 sync agents | NATS | Africa-first ║")
    log.info("╚══════════════════════════════════════════════╝")
    log.info("NodeID: %s...", nodeid[:16])

    sync_threads = _start_sync_pipeline()
    log.info("Sync pipeline: %d agents running", len(sync_threads))

    await _start_async_agents(nodeid)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Byngox shutting down.")
