"""Tests for CMLClient — passthrough, stats, offline behaviour."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cml_client as _mod


def fresh():
    _mod._client = None
    return _mod.get_client()


def test_get_client_singleton():
    _mod._client = None
    a = _mod.get_client()
    b = _mod.get_client()
    assert a is b


def test_passthrough_when_offline():
    client = fresh()
    result = asyncio.run(client.filter("Patient glucose 126 mg/dL", component="test"))
    assert result["allowed"] is True
    assert result["cml_online"] is False
    assert result["text"] == "Patient glucose 126 mg/dL"


def test_passthrough_empty_text():
    client = fresh()
    result = asyncio.run(client.filter("", component="test"))
    assert result["allowed"] is True


def test_stats_increment_on_fallback():
    client = fresh()
    asyncio.run(client.filter("some text", component="test"))
    asyncio.run(client.filter("more text", component="test"))
    stats = client.stats()
    assert stats["fallbacks"] == 2
    assert stats["filtered"]  == 0
    assert stats["blocked"]   == 0


def test_is_online_false_before_connect():
    client = fresh()
    assert client.is_online() is False


def test_passthrough_preserves_text():
    client = fresh()
    text   = "HR: 120 bpm, SpO2: 88% — patient critical"
    result = asyncio.run(client.filter(text, component="health_agent"))
    assert result["text"] == text


def test_warnings_present_in_passthrough():
    client = fresh()
    result = asyncio.run(client.filter("test", component="test"))
    assert len(result["warnings"]) > 0
    assert "cml_offline" in result["warnings"][0] or "CML not applied" in result["warnings"][0]


def test_clinical_flags_empty_when_offline():
    client = fresh()
    result = asyncio.run(client.filter("critical patient data", component="test"))
    assert result["clinical_flags"] == []


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
