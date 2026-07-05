#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging
from core.base_agent import BaseAgent
from schemas.health import NormalizedEvent

logging.basicConfig(level=logging.INFO, format="[NORMALIZE] %(asctime)s %(message)s", datefmt="%H:%M:%S")

UNIT_CONVERSIONS = {
    "glucose":     {"mmol/L": lambda x: x * 18.0, "mg/dL": lambda x: x},
    "temperature": {"F": lambda x: (x - 32) * 5/9, "C": lambda x: x},
    "weight":      {"lbs": lambda x: x * 0.453592, "kg": lambda x: x},
}
NORMAL_RANGES = {
    "glucose": "70-100 mg/dL", "blood_pressure": "90/60-120/80 mmHg",
    "heart_rate": "60-100 bpm", "temperature": "36.1-37.2 C", "oxygen_sat": "95-100%",
}


class NormalizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.normalization.agent")

    def _subscribe(self):
        self.subscribe("health.raw.>", 1)

    def on_message(self, subject: str, data: dict):
        payload     = data.get("payload", data)
        patient_ref = data.get("patient_ref", "unknown")
        data_type   = data.get("data_type", "general")
        value       = payload.get("value")
        unit        = payload.get("unit", "")
        if data_type in UNIT_CONVERSIONS and unit in UNIT_CONVERSIONS[data_type]:
            try:
                value = round(UNIT_CONVERSIONS[data_type][unit](float(value)), 2)
            except (ValueError, TypeError):
                pass
        event = NormalizedEvent(patient_ref=patient_ref, data_type=data_type,
                                unit=unit, value=value,
                                normal_range=NORMAL_RANGES.get(data_type),
                                source=data.get("source", ""))
        self.logger.info(f"Normalized [{data_type}] patient={patient_ref[:12]} value={value}")
        self.publish("health.normalized.event", event.to_dict())


if __name__ == "__main__":
    NormalizationAgent().start()
