#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging
from core.base_agent import BaseAgent
from schemas.health import RawHealthEvent

logging.basicConfig(level=logging.INFO, format="[INGESTION] %(asctime)s %(message)s", datefmt="%H:%M:%S")


class IngestionAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.ingestion.agent")

    def _subscribe(self):
        self.subscribe("sorabbyngo.byngox.twins.>", 1)
        self.subscribe("health.input.>", 2)
        self.subscribe("health.wearable.>", 3)

    def on_message(self, subject: str, data: dict):
        source      = "novela.twins" if "twins" in subject else "manual"
        patient_ref = data.get("patient_ref", data.get("twin_id", "unknown"))
        data_type   = data.get("data_type", "general")
        event = RawHealthEvent(source=source, patient_ref=patient_ref, data_type=data_type, payload=data)
        self.logger.info(f"Ingested [{source}] patient={patient_ref[:12]} type={data_type}")
        self.publish("health.raw.ingested", event.to_dict())


if __name__ == "__main__":
    IngestionAgent().start()
