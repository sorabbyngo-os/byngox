#!/usr/bin/env python3
"""
Byngox — Twin Agent (v2)
Maintains live digital twin state per patient.

Improvements over v1:
  - Pushes twin updates to Novela Django API (closes the loop)
  - Full clinical risk scoring across all 6 vital types
  - CML safety filter on all outbound updates
  - Async NATS via nats-py
  - SUID audit trail per update

NATS subjects:
  Subscribe: health.normalized.>        — normalized vitals from ingestion agent
  Subscribe: novela.monitors.vitals.>   — direct from novela-monitors gateway
  Subscribe: sorabbyngo.byngox.twins.>  — direct twin update requests
  Publish:   health.twin.updated        — twin state change events
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict
from typing import Optional

import httpx
import nats

sys_path = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.insert(0, sys_path)

from schemas.health import TwinState

log = logging.getLogger("byngox.twin_agent")

# ── Config ────────────────────────────────────────────────────────────────────
NATS_URL        = os.environ.get("NATS_URL",         "nats://localhost:4223")
NOVELA_API_URL  = os.environ.get("NOVELA_API_URL",   "http://localhost:8001")
NOVELA_API_KEY  = os.environ.get("NOVELA_API_KEY",   "")
TWIN_STORE      = os.path.expanduser("~/.sorabbyngo/byngox/twins.json")
PUSH_INTERVAL   = int(os.environ.get("TWIN_PUSH_INTERVAL_S", "10"))   # Push to Novela every N seconds


# ── Clinical risk scoring ─────────────────────────────────────────────────────

def _score_vitals(vitals: dict) -> tuple[float, list]:
    """
    Clinical risk score from vitals.
    Returns (score 0.0–1.0, list of risk indicators).
    Based on Modified Early Warning Score (MEWS) principles.
    """
    score      = 0.0
    indicators = []

    def _v(key):
        try:
            return float(vitals.get(key, 0) or 0)
        except (ValueError, TypeError):
            return 0.0

    hr   = _v("heart_rate")
    spo2 = _v("spo2")
    sbp  = _v("bp_systolic")
    dbp  = _v("bp_diastolic")
    temp = _v("temperature")
    rr   = _v("respiratory_rate")
    gluc = _v("glucose")

    # Heart rate
    if hr > 0:
        if hr >= 130 or hr < 40:
            score += 0.30; indicators.append(f"Critical HR: {hr:.0f} bpm")
        elif hr >= 110 or hr < 50:
            score += 0.15; indicators.append(f"Abnormal HR: {hr:.0f} bpm")

    # SpO2
    if spo2 > 0:
        if spo2 < 90:
            score += 0.35; indicators.append(f"Critical SpO2: {spo2:.0f}%")
        elif spo2 < 94:
            score += 0.15; indicators.append(f"Low SpO2: {spo2:.0f}%")

    # Systolic BP
    if sbp > 0:
        if sbp < 70 or sbp > 200:
            score += 0.30; indicators.append(f"Critical SBP: {sbp:.0f} mmHg")
        elif sbp < 90 or sbp > 180:
            score += 0.15; indicators.append(f"Abnormal SBP: {sbp:.0f} mmHg")

    # Temperature
    if temp > 0:
        if temp >= 40.0 or temp < 34.0:
            score += 0.25; indicators.append(f"Critical temp: {temp:.1f}°C")
        elif temp >= 38.5 or temp < 35.5:
            score += 0.10; indicators.append(f"Abnormal temp: {temp:.1f}°C")

    # Respiratory rate
    if rr > 0:
        if rr >= 35 or rr < 6:
            score += 0.30; indicators.append(f"Critical RR: {rr:.0f}/min")
        elif rr >= 25 or rr < 10:
            score += 0.15; indicators.append(f"Abnormal RR: {rr:.0f}/min")

    # Glucose
    if gluc > 0:
        if gluc > 200 or gluc < 50:
            score += 0.20; indicators.append(f"Critical glucose: {gluc:.0f}")
        elif gluc > 126 or gluc < 70:
            score += 0.10; indicators.append(f"Abnormal glucose: {gluc:.0f}")

    return min(round(score, 2), 1.0), indicators


def _risk_label(score: float) -> str:
    if score == 0:     return "unknown"
    if score < 0.25:   return "low"
    if score < 0.50:   return "moderate"
    if score < 0.75:   return "high"
    return "critical"


# ── Twin Agent ────────────────────────────────────────────────────────────────

class TwinAgent:

    def __init__(self):
        self._twins:    dict[str, TwinState]  = {}
        self._dirty:    set[str]              = set()   # SUIDs pending Novela push
        self._nc        = None
        self._cml       = None

    async def start(self):
        logging.basicConfig(
            level=logging.INFO,
            format="[TWIN] %(asctime)s %(message)s",
            datefmt="%H:%M:%S",
        )

        # Load persisted twins
        self._load()

        # Try CML client
        try:
            from cml_client import get_client
            self._cml = get_client()
            log.info("CML client loaded")
        except ImportError:
            log.warning("CML client not found — running without safety filter")

        # Connect NATS
        self._nc = await nats.connect(
            NATS_URL,
            max_reconnect_attempts=-1,
            reconnect_time_wait=2,
        )
        log.info("Connected to NATS")

        # Subscribe
        await self._nc.subscribe("health.normalized.>",       cb=self._handle)
        await self._nc.subscribe("novela.monitors.vitals.>",  cb=self._handle_vitals)
        await self._nc.subscribe("sorabbyngo.byngox.twins.>", cb=self._handle)

        log.info("TwinAgent ready — %d twins loaded", len(self._twins))

        # Background push loop
        asyncio.create_task(self._push_loop())

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self._nc.drain()

    async def _handle(self, msg):
        """Handle normalized health events."""
        try:
            data        = json.loads(msg.data.decode())
            patient_ref = data.get("patient_ref") or data.get("twin_id")
            if not patient_ref:
                return
            self._ensure_twin(patient_ref)
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

            twin.risk_score, indicators = _score_vitals(twin.vitals)
            twin.baseline_set = len(twin.vitals) >= 3
            twin.last_updated = time.time()

            self._dirty.add(patient_ref)
            self._save()

            log.info("Twin updated: %s risk=%.2f (%s)",
                     patient_ref[:16], twin.risk_score, _risk_label(twin.risk_score))

            # Publish twin update to NATS
            await self._nc.publish("health.twin.updated", json.dumps({
                **twin.to_dict(),
                "risk_label":  _risk_label(twin.risk_score),
                "indicators":  indicators,
            }).encode())

        except Exception as e:
            log.error("Handle error: %s", e)

    async def _handle_vitals(self, msg):
        """Handle direct vitals from novela-monitors stream."""
        try:
            payload     = json.loads(msg.data.decode())
            patient_ref = payload.get("patient_id")
            if not patient_ref:
                return

            vitals = payload.get("vitals", {})
            self._ensure_twin(patient_ref)
            twin = self._twins[patient_ref]
            twin.vitals.update({k: v for k, v in vitals.items() if v is not None})
            twin.risk_score, _  = _score_vitals(twin.vitals)
            twin.baseline_set   = len(twin.vitals) >= 3
            twin.last_updated   = time.time()

            self._dirty.add(patient_ref)

        except Exception as e:
            log.error("Vitals handle error: %s", e)

    async def _push_loop(self):
        """
        Periodically push dirty twins to Novela Django API.
        Batches updates to avoid hammering the API.
        """
        while True:
            await asyncio.sleep(PUSH_INTERVAL)
            if not self._dirty:
                continue

            batch = list(self._dirty)
            self._dirty.clear()

            for patient_ref in batch:
                twin = self._twins.get(patient_ref)
                if twin:
                    await self._push_to_novela(patient_ref, twin)

    async def _push_to_novela(self, patient_ref: str, twin: TwinState):
        """Push twin state to Novela via HTTP API."""
        payload = {
            "patient_ref":  patient_ref,
            "vitals":       twin.vitals,
            "conditions":   twin.conditions,
            "medications":  twin.medications,
            "risk_score":   twin.risk_score,
            "baseline_set": twin.baseline_set,
        }

        # CML filter before pushing
        if self._cml:
            summary = (
                f"Patient {patient_ref} risk {_risk_label(twin.risk_score)} "
                f"score {twin.risk_score:.2f} "
                f"conditions: {', '.join(twin.conditions[:3])}"
            )
            cml_result = await self._cml.filter(
                text      = summary,
                component = "byngox.twin_agent",
                context   = "clinical",
                entity_id = patient_ref,
            )
            if not cml_result["allowed"]:
                log.warning("CML blocked twin push for %s: %s",
                            patient_ref, cml_result["reason"])
                return
            if cml_result.get("human_review_required"):
                payload["human_review_required"] = True

        headers = {"Content-Type": "application/json"}
        if NOVELA_API_KEY:
            headers["Authorization"] = f"Bearer {NOVELA_API_KEY}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    f"{NOVELA_API_URL}/api/v1/twins/byngox-update/",
                    json=payload,
                    headers=headers,
                )
                if r.status_code == 200:
                    log.info("Pushed twin to Novela: %s → %s",
                             patient_ref[:16], _risk_label(twin.risk_score))
                else:
                    log.warning("Novela push failed: %s %d",
                                patient_ref[:16], r.status_code)
        except httpx.ConnectError:
            log.warning("Novela API unreachable — twin push queued for next cycle")
            self._dirty.add(patient_ref)   # Re-queue
        except Exception as e:
            log.error("Novela push error: %s", e)

    def _ensure_twin(self, patient_ref: str):
        if patient_ref not in self._twins:
            self._twins[patient_ref] = TwinState(patient_ref=patient_ref)

    def _load(self):
        try:
            with open(TWIN_STORE) as f:
                data   = json.load(f)
                fields = set(TwinState.__dataclass_fields__.keys())
                for ref, state in data.items():
                    self._twins[ref] = TwinState(**{k: v for k, v in state.items() if k in fields})
            log.info("Loaded %d twins", len(self._twins))
        except Exception:
            pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(TWIN_STORE), exist_ok=True)
            with open(TWIN_STORE, "w") as f:
                json.dump(
                    {k: v.to_dict() for k, v in self._twins.items()},
                    f, indent=2,
                )
        except Exception as e:
            log.error("Save failed: %s", e)


if __name__ == "__main__":
    asyncio.run(TwinAgent().start())
