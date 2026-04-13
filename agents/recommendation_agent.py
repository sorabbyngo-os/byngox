#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import logging
from core.base_agent import BaseAgent
from schemas.health import HealthRecommendation

logging.basicConfig(level=logging.INFO, format="[RECOMMEND] %(asctime)s %(message)s", datefmt="%H:%M:%S")

RECS = {
    "hyperglycemia": [("treatment","high","Consult physician for diabetes screening and HbA1c test"),
                      ("lifestyle","medium","Reduce refined carbohydrates, increase physical activity")],
    "hypoglycemia":  [("treatment","urgent","Consume 15-20g fast-acting carbohydrates immediately")],
    "tachycardia":   [("treatment","medium","Rest and monitor — seek care if persistent")],
    "high_risk":     [("treatment","urgent","Schedule comprehensive health review with physician")],
}
DEFAULT = [("preventive","low","Maintain regular health monitoring and hydration")]


class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.recommendation.agent")

    def _subscribe(self):
        self.subscribe("health.insights.>", 1)

    def on_message(self, subject: str, data: dict):
        patient_ref = data.get("patient_ref", "unknown")
        description = data.get("description", "").lower()
        matched = []
        for key, recs in RECS.items():  # match on key or description
            if key in description:
                matched.extend(recs)
        if not matched:
            matched = DEFAULT
        for category, priority, text in matched:
            rec = HealthRecommendation(patient_ref=patient_ref, category=category,
                                       recommendation=text, priority=priority,
                                       rationale=f"Based on: {description[:80]}")
            self.logger.info(f"Recommendation [{priority}]: {patient_ref[:12]} — {text[:50]}")
            self.publish(f"health.recommendations.{priority}", rec.to_dict())


if __name__ == "__main__":
    RecommendationAgent().start()
