#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging
from core.base_agent import BaseAgent
from schemas.health import HealthAction

logging.basicConfig(level=logging.INFO, format="[COORDINATE] %(asctime)s %(message)s", datefmt="%H:%M:%S")


class CoordinationAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.coordination.agent")

    def _subscribe(self):
        self.subscribe("health.recommendations.urgent", 1)
        self.subscribe("health.recommendations.high",   2)
        self.subscribe("health.recommendations.medium", 3)

    def on_message(self, subject: str, data: dict):
        patient_ref    = data.get("patient_ref", "unknown")
        recommendation = data.get("recommendation", "")
        priority       = data.get("priority", "medium")
        category       = data.get("category", "general")
        action_type    = "alert" if priority == "urgent" else ("referral" if category == "treatment" else "reminder")
        target         = "doctor" if action_type in ("alert","referral") else "patient"
        action = HealthAction(patient_ref=patient_ref, action_type=action_type,
                              target=target, message=recommendation, urgency=priority)
        self.logger.info(f"Action [{action_type}→{target}]: {patient_ref[:12]} — {recommendation[:50]}")
        self.publish(f"health.actions.{action_type}", action.to_dict())
        if priority in ("urgent", "high"):
            self.publish("sorabbyngo.byngox.update", {
                "source": "byngox.coordination", "patient_ref": patient_ref,
                "message": f"Health action required: {recommendation[:80]}",
                "action_type": action_type, "urgency": priority,
            })


if __name__ == "__main__":
    CoordinationAgent().start()
