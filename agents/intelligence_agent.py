#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging
from core.base_agent import BaseAgent
from schemas.health import HealthInsight

logging.basicConfig(level=logging.INFO, format="[INTELLIGENCE] %(asctime)s %(message)s", datefmt="%H:%M:%S")

RULES = [
    ("hyperglycemia", lambda v, r: float(v.get("glucose", 0)) > 126,
     "Fasting glucose above 126 mg/dL — diabetes indicator", "high", 0.85),
    ("hypoglycemia",  lambda v, r: 0 < float(v.get("glucose", 999)) < 70,
     "Glucose below 70 mg/dL — hypoglycemia risk", "high", 0.90),
    ("tachycardia",   lambda v, r: float(v.get("heart_rate", 0)) > 100,
     "Heart rate above 100 bpm — tachycardia detected", "medium", 0.80),
    ("high_risk",     lambda v, r: r >= 0.7,
     "Multiple risk factors — comprehensive review recommended", "critical", 0.75),
]


class IntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.intelligence.agent")

    def _subscribe(self):
        self.subscribe("health.twin.updated", 1)

    def on_message(self, subject: str, data: dict):
        patient_ref = data.get("patient_ref", "unknown")
        vitals      = data.get("vitals", {})
        risk        = float(data.get("risk_score", 0.0))
        for name, condition, description, severity, confidence in RULES:
            try:
                if not condition(vitals, risk):
                    continue
            except (ValueError, TypeError):
                continue
            insight = HealthInsight(patient_ref=patient_ref, insight_type="risk",
                                    severity=severity, description=description,
                                    confidence=confidence)
            self.logger.info(f"Insight [{severity}]: {patient_ref[:12]} — {name}")
            self.publish(f"health.insights.{severity}", insight.to_dict())
            if severity == "critical":
                self.publish("sorabbyngo.byngox.risk", {
                    "source": "byngox.intelligence", "patient_ref": patient_ref,
                    "message": description, "confidence": confidence, "severity": severity,
                })


if __name__ == "__main__":
    IntelligenceAgent().start()
