"""Tests for health schemas — serialization, defaults, field types."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.health import (
    RawHealthEvent, NormalizedEvent, TwinState,
    HealthInsight, HealthRecommendation, HealthAction,
)


def test_raw_health_event_to_dict():
    e = RawHealthEvent(source="novela", patient_ref="PAT-001", data_type="vitals")
    d = e.to_dict()
    assert d["source"] == "novela"
    assert d["patient_ref"] == "PAT-001"
    assert "timestamp" in d


def test_normalized_event_to_dict():
    e = NormalizedEvent(
        patient_ref="PAT-001", data_type="glucose",
        unit="mg/dL", value=126.0, normal_range="70-100 mg/dL"
    )
    d = e.to_dict()
    assert d["value"] == 126.0
    assert d["unit"] == "mg/dL"


def test_twin_state_defaults():
    t = TwinState(patient_ref="PAT-001")
    assert t.vitals == {}
    assert t.conditions == []
    assert t.medications == []
    assert t.risk_score == 0.0
    assert t.baseline_set is False


def test_twin_state_to_dict_roundtrip():
    t = TwinState(
        patient_ref="PAT-001",
        vitals={"heart_rate": 78, "spo2": 97},
        risk_score=0.15,
        baseline_set=True,
    )
    d = t.to_dict()
    assert d["risk_score"] == 0.15
    assert d["vitals"]["heart_rate"] == 78
    assert d["baseline_set"] is True


def test_health_insight_to_dict():
    i = HealthInsight(
        patient_ref="PAT-001", insight_type="risk",
        severity="high", description="Tachycardia detected",
        confidence=0.87,
    )
    d = i.to_dict()
    assert d["severity"] == "high"
    assert d["confidence"] == 0.87


def test_health_recommendation_defaults():
    r = HealthRecommendation(
        patient_ref="PAT-001", category="treatment",
        recommendation="Consult physician"
    )
    assert r.priority == "medium"
    assert r.rationale == ""
    assert r.expires_at is None


def test_health_action_to_dict():
    a = HealthAction(
        patient_ref="PAT-001", action_type="alert",
        target="doctor", message="Patient deteriorating",
        urgency="urgent"
    )
    d = a.to_dict()
    assert d["action_type"] == "alert"
    assert d["urgency"] == "urgent"
    assert d["completed"] is False


def test_twin_state_vitals_update():
    t = TwinState(patient_ref="PAT-001")
    t.vitals["heart_rate"] = 95
    t.vitals["spo2"]       = 94
    assert len(t.vitals) == 2


def test_all_schemas_have_timestamp():
    schemas = [
        RawHealthEvent(source="x", patient_ref="p", data_type="d"),
        NormalizedEvent(patient_ref="p", data_type="d", unit="u", value=1),
        TwinState(patient_ref="p"),
        HealthInsight(patient_ref="p", insight_type="t", severity="low", description="d"),
        HealthRecommendation(patient_ref="p", category="c", recommendation="r"),
        HealthAction(patient_ref="p", action_type="a", target="t", message="m"),
    ]
    for s in schemas:
        d = s.to_dict()
        assert "timestamp" in d, f"{type(s).__name__} missing timestamp"
        assert d["timestamp"] <= time.time() + 1


if __name__ == "__main__":
    fns = [v for k, v in globals().items() if k.startswith("test_")]
    passed = failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
