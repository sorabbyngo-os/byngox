#!/usr/bin/env python3
"""byngox.py — Byngox Orchestrator — starts all 6 health agents"""

import os, sys, logging, threading
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
sys.path.insert(0, os.path.dirname(__file__))

from agents.ingestion_agent      import IngestionAgent
from agents.normalization_agent  import NormalizationAgent
from agents.twin_agent           import TwinAgent
from agents.intelligence_agent   import IntelligenceAgent
from agents.recommendation_agent import RecommendationAgent
from agents.coordination_agent   import CoordinationAgent

log = logging.getLogger("byngox")

def main():
    log.info("╔══════════════════════════════════════╗")
    log.info("║  BYNGOX — Health Intelligence Layer  ║")
    log.info("║  6 agents | NATS | Africa-first      ║")
    log.info("╚══════════════════════════════════════╝")
    agents  = [IngestionAgent(), NormalizationAgent(), TwinAgent(),
               IntelligenceAgent(), RecommendationAgent(), CoordinationAgent()]
    threads = []
    for agent in agents:
        t = threading.Thread(target=agent.start, name=agent.name, daemon=True)
        threads.append(t)
        t.start()
        log.info(f"Started: {agent.name}")
    log.info("All 6 agents running.")
    try:
        for t in threads: t.join()
    except KeyboardInterrupt:
        log.info("Byngox shutting down.")

if __name__ == "__main__":
    main()
