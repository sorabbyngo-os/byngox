#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json, logging
from core.base_agent import BaseAgent
from schemas.health import TwinState

logging.basicConfig(level=logging.INFO, format="[TWIN] %(asctime)s %(message)s", datefmt="%H:%M:%S")
TWIN_STORE = os.path.expanduser("~/.sorabbyngo/byngox/twins.json")


class TwinAgent(BaseAgent):
    def __init__(self):
        super().__init__("health.twin.agent")
        self._twins: dict = {}
        self._load()

    def _load(self):
        try:
            with open(TWIN_STORE) as f:
                data = json.load(f)
                for ref, state in data.items():
                    known = set(TwinState.__dataclass_fields__.keys())
                    self._twins[ref] = TwinState(**{k: v for k, v in state.items() if k in known})
            self.logger.info(f"Loaded {len(self._twins)} twins")
        except Exception:
            pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(TWIN_STORE), exist_ok=True)
            with open(TWIN_STORE, "w") as f:
                json.dump({k: v.to_dict() for k, v in self._twins.items()}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Save failed: {e}")

    def _subscribe(self):
        self.subscribe("health.normalized.>", 1)
        self.subscribe("sorabbyngo.byngox.twins.>", 2)

    def on_message(self, subject: str, data: dict):
        patient_ref = data.get("patient_ref", data.get("twin_id", "unknown"))
        if patient_ref == "unknown":
            return
        if patient_ref not in self._twins:
            self._twins[patient_ref] = TwinState(patient_ref=patient_ref)
        twin = self._twins[patient_ref]
        data_type = data.get("data_type", "")
        value     = data.get("value")
        if data_type and value is not None:
            twin.vitals[data_type] = value
        for c in data.get("conditions", []):
            if c not in twin.conditions:
                twin.conditions.append(c)
        for m in data.get("medications", []):
            if m not in twin.medications:
                twin.medications.append(m)
        twin.risk_score   = self._risk(twin)
        twin.baseline_set = len(twin.vitals) >= 3
        self._save()
        self.logger.info(f"Twin updated: {patient_ref[:12]} risk={twin.risk_score:.2f}")
        self.publish("health.twin.updated", twin.to_dict())

    def _risk(self, twin: TwinState) -> float:
        score = 0.0
        try:
            if float(twin.vitals.get("glucose", 0)) > 126: score += 0.3
            if float(twin.vitals.get("heart_rate", 0)) > 100: score += 0.2
        except (ValueError, TypeError):
            pass
        score += len(twin.conditions) * 0.1
        return min(round(score, 2), 1.0)


if __name__ == "__main__":
    TwinAgent().start()
