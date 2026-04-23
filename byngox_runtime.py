"""
byngox_runtime.py — Unified Byngox Runtime

Starts ALL Byngox agents in a single process:

  Async agents (NATS via nats-py):
    HealthAgent      — clinical decision support
    DrugAgent        — medication verification
    ContextAgent     — patient history + episodic memory
    LearningAgent    — feedback collection
    PopulationAgent  — epidemiology + outbreak detection
    NetworkAgent     — mesh peer tracking
    TwinAgent        — digital twin state management (async)

  Sync pipeline agents (raw socket NATS via core/base_agent.py):
    IngestionAgent      — receives raw health events
    NormalizationAgent  — unit conversion + range tagging
    IntelligenceAgent   — rule-based risk scoring
    RecommendationAgent — evidence-based recommendations
    CoordinationAgent   — action dispatch to doctor/patient

Usage:
  python3 byngox_runtime.py            # production (reads /proc/sorabbyngo/nodeid)
  BYNGOX_DEV=1 python3 byngox_runtime.py  # dev mode (hostname-derived NodeID)
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

# ── Async agents ──────────────────────────────────────────────────────────────
from agents.health_agent      import HealthAgent
from agents.drug_agent        import DrugAgent
from agents.context_agent     import ContextAgent
from agents.learning_agent    import LearningAgent
from agents.population_agent  import PopulationAgent
from agents.network_agent     import NetworkAgent
from agents.twin_agent         import TwinAgent
from agents.security_agent     import SecurityAgent

# ── Sync pipeline agents ──────────────────────────────────────────────────────
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
        log.warning("NodeID driver not found — dev mode (id=%s...)", nodeid[:12])
        return nodeid


def _start_sync_pipeline():
    """
    Start the 6 sync pipeline agents in daemon threads.
    These use raw socket NATS (core/base_agent.py) and block on _listen().
    """
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
            name=f"sync-{agent.name}",
            daemon=True,
        )
        t.start()
        threads.append(t)
        log.info("Sync agent started: %s", agent.name)
    return threads


async def _start_async_agents(nodeid: str):
    """
    Start the 6 async agents concurrently.
    These use nats-py and are awaited together.
    """
    agents = [
        HealthAgent(nodeid),
        DrugAgent(nodeid),
        ContextAgent(nodeid),
        LearningAgent(nodeid),
        PopulationAgent(nodeid),
        NetworkAgent(nodeid),
        TwinAgent(),
        SecurityAgent(nodeid),
    ]
    log.info("Starting %d async agents...", len(agents))
    await asyncio.gather(*[agent.start() for agent in agents])


async def main():
    nodeid = _get_nodeid()

    log.info("╔══════════════════════════════════════════════╗")
    log.info("║  BYNGOX — Unified Health Intelligence Layer  ║")
    log.info("║  12 agents | NATS | Africa-first             ║")
    log.info("╚══════════════════════════════════════════════╝")
    log.info("NodeID: %s...", nodeid[:16])

    # 1. Start sync pipeline agents in background threads
    sync_threads = _start_sync_pipeline()
    log.info("Sync pipeline: %d agents running", len(sync_threads))

    # 2. Start async agents (blocks until all exit or crash)
    await _start_async_agents(nodeid)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Byngox shutting down.")
