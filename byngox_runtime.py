"""
byngox_runtime.py — Unified Byngox Runtime
Starts ALL Byngox agents in a single process.
13 agents total: 8 async + 5 sync pipeline.
Graceful shutdown: all async agents drained on SIGINT/SIGTERM.
"""
import asyncio
import hashlib
import logging
import os
import signal
import socket
import threading

logging.basicConfig(
    level=logging.INFO,
    format="[BYNGOX] %(asctime)s %(levelname)s %(name)s — %(message)s",
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
from agents.twin_agent        import TwinAgent
from agents.security_agent    import SecurityAgent

# ── Sync pipeline agents ──────────────────────────────────────────────────────
from agents.ingestion_agent      import IngestionAgent
from agents.normalization_agent  import NormalizationAgent
from agents.intelligence_agent   import IntelligenceAgent
from agents.recommendation_agent import RecommendationAgent
from agents.coordination_agent   import CoordinationAgent


def _get_nodeid() -> str:
    try:
        nid = open("/proc/sorabbyngo/nodeid").read().strip()
        log.info("NodeID read from HAL: %s...", nid[:16])
        return nid
    except FileNotFoundError:
        nid = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
        log.warning("NodeID driver not found — dev mode (id=%s...)", nid[:12])
        return nid


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
        name = getattr(agent, "name", type(agent).__name__)
        t = threading.Thread(target=agent.start, name=f"sync-{name}", daemon=True)
        t.start()
        threads.append(t)
        log.info("Sync agent started: %s", name)
    return threads


class ByngoxRuntime:
    """
    Manages lifecycle of all 13 Byngox agents.
    Handles graceful shutdown via SIGINT/SIGTERM.
    """

    def __init__(self, nodeid: str):
        self.nodeid        = nodeid
        self._shutdown     = asyncio.Event()
        self._async_agents = []

    def _register_signals(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_signal)

    def _handle_signal(self):
        log.info("Shutdown signal received — draining agents...")
        self._shutdown.set()

    async def start(self):
        self._register_signals()

        # Build async agents
        health_agent   = HealthAgent()
        drug_agent     = DrugAgent(self.nodeid)
        context_agent  = ContextAgent(self.nodeid)
        learning_agent = LearningAgent(self.nodeid)
        pop_agent      = PopulationAgent(self.nodeid)
        network_agent  = NetworkAgent(self.nodeid)
        twin_agent     = TwinAgent()
        security_agent = SecurityAgent(self.nodeid)

        self._async_agents = [
            health_agent, drug_agent, context_agent,
            learning_agent, pop_agent, network_agent,
            twin_agent, security_agent,
        ]

        log.info("Starting 8 async agents...")

        agent_tasks = asyncio.gather(
            health_agent.start(),
            drug_agent.run(),
            context_agent.run(),
            learning_agent.run(),
            pop_agent.run(),
            network_agent.run(),
            twin_agent.start(),
            security_agent.start(),
            return_exceptions=True,
        )

        # Wait for shutdown signal or agent crash
        shutdown_task = asyncio.create_task(self._shutdown.wait())
        done, pending = await asyncio.wait(
            [agent_tasks, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Drain
        await self._drain()

        for task in pending:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

    async def _drain(self):
        log.info("Draining async agents...")
        for agent in self._async_agents:
            try:
                if hasattr(agent, "stop"):
                    await agent.stop()
                elif hasattr(agent, "drain"):
                    await agent.drain()
            except Exception as e:
                log.debug("Drain error for %s: %s", type(agent).__name__, e)
        log.info("All agents drained.")


async def main():
    nodeid = _get_nodeid()

    log.info("╔══════════════════════════════════════════════════╗")
    log.info("║   BYNGOX — Unified Health Intelligence Layer     ║")
    log.info("║   8 async + 5 sync agents | NATS | Africa-first  ║")
    log.info("╚══════════════════════════════════════════════════╝")
    log.info("NodeID: %s...", nodeid[:16])

    # Start sync pipeline in daemon threads
    sync_threads = _start_sync_pipeline()
    log.info("Sync pipeline: %d agents running", len(sync_threads))

    # Start async runtime
    runtime = ByngoxRuntime(nodeid)
    await runtime.start()

    log.info("Byngox shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
