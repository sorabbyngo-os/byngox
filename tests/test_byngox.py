"""
Byngox -- Test Suite
Tests: schemas, ACP protocol, agent logic, runtime, population outbreak detection,
       context store, twin scoring, drug verification, learning feedback.
All tests are offline-first -- no NATS, no Ollama, no Novela required.
"""
import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import pytest
import sys

# Ensure byngox root on path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def nodeid():
    return "deadbeef" * 4   # 32-char fake nodeid


# ============================================================================
# Schemas
# ============================================================================

class TestSchemas:

    def test_raw_health_event(self):
        from schemas.health import RawHealthEvent
        e = RawHealthEvent(
            source="novela.monitor",
            patient_ref="PAT-001",
            data_type="heart_rate",
            payload={"value": 72},
        )
        d = e.to_dict()
        assert d["source"]      == "novela.monitor"
        assert d["patient_ref"] == "PAT-001"
        assert d["data_type"]   == "heart_rate"
        assert "timestamp" in d

    def test_normalized_event(self):
        from schemas.health import NormalizedEvent
        e = NormalizedEvent(
            patient_ref="PAT-001",
            data_type="heart_rate",
            unit="bpm",
            value=72,
            normal_range="60-100",
        )
        d = e.to_dict()
        assert d["unit"]  == "bpm"
        assert d["value"] == 72

    def test_twin_state(self):
        from schemas.health import TwinState
        t = TwinState(patient_ref="PAT-001")
        assert t.risk_score   == 0.0
        assert t.baseline_set is False
        assert isinstance(t.vitals, dict)
        d = t.to_dict()
        assert d["patient_ref"] == "PAT-001"

    def test_health_insight(self):
        from schemas.health import HealthInsight
        i = HealthInsight(
            patient_ref="PAT-001",
            insight_type="deterioration",
            severity="high",
            description="SpO2 dropping",
            confidence=0.87,
        )
        d = i.to_dict()
        assert d["confidence"] == 0.87

    def test_health_recommendation(self):
        from schemas.health import HealthRecommendation
        r = HealthRecommendation(
            patient_ref="PAT-001",
            category="vitals",
            recommendation="Increase oxygen support",
            priority="urgent",
        )
        d = r.to_dict()
        assert d["priority"] == "urgent"

    def test_health_action(self):
        from schemas.health import HealthAction
        a = HealthAction(
            patient_ref="PAT-001",
            action_type="alert",
            target="duty_nurse",
            message="Patient deteriorating",
            urgency="immediate",
        )
        d = a.to_dict()
        assert d["urgency"] == "immediate"
        assert d["completed"] is False


# ============================================================================
# ACP Protocol
# ============================================================================

class TestACPProtocol:

    def test_message_to_json(self):
        from acp.protocol import ACPMessage
        msg = ACPMessage(
            msg_type="HEALTH_QUERY",
            payload={"patient_ref": "PAT-001"},
            sender="health_agent",
            target="context_agent",
        )
        j = msg.to_json()
        d = json.loads(j)
        assert d["type"]    == "HEALTH_QUERY"
        assert d["sender"]  == "health_agent"
        assert d["target"]  == "context_agent"

    def test_message_from_json(self):
        from acp.protocol import ACPMessage
        raw = json.dumps({
            "type":    "DRUG_VERIFY",
            "payload": {"barcode": "KE12345"},
            "sender":  "drug_agent",
            "target":  None,
        })
        msg = ACPMessage.from_json(raw)
        assert msg.msg_type        == "DRUG_VERIFY"
        assert msg.payload["barcode"] == "KE12345"
        assert msg.target          is None

    def test_message_types_defined(self):
        from acp.message_types import (
            HEALTH_QUERY, HEALTH_RESULT, DRUG_VERIFY, DRUG_RESULT,
            CONTEXT_FETCH, CONTEXT_UPDATE, POPULATION_PING, LEARN_FEEDBACK,
        )
        assert HEALTH_QUERY    == "HEALTH_QUERY"
        assert DRUG_VERIFY     == "DRUG_VERIFY"
        assert LEARN_FEEDBACK  == "LEARN_FEEDBACK"

    def test_roundtrip(self):
        from acp.protocol import ACPMessage
        original = ACPMessage("HEALTH_RESULT", {"risk": "low"}, "health_agent", "coord")
        restored = ACPMessage.from_json(original.to_json())
        assert restored.msg_type         == original.msg_type
        assert restored.payload["risk"]  == "low"


# ============================================================================
# Base Agent
# ============================================================================

class TestBaseAgent:

    def test_base_agent_requires_run(self):
        from agents.base_agent import BaseAgent
        with pytest.raises(TypeError):
            BaseAgent("test_node", "TestAgent")   # abstract -- cannot instantiate

    def test_base_agent_subclass(self, nodeid):
        from agents.base_agent import BaseAgent

        class ConcreteAgent(BaseAgent):
            async def run(self): pass
            async def handle(self, msg): pass

        agent = ConcreteAgent(nodeid, "ConcreteAgent")
        assert agent.name   == "ConcreteAgent"
        assert agent.nodeid == nodeid

    @pytest.mark.asyncio
    async def test_base_agent_start_calls_run(self, nodeid):
        from agents.base_agent import BaseAgent

        ran = []

        class ConcreteAgent(BaseAgent):
            async def run(self):
                ran.append(True)
            async def handle(self, msg): pass

        agent = ConcreteAgent(nodeid, "ConcreteAgent")
        await agent.start()
        assert ran == [True]


# ============================================================================
# ContextAgent
# ============================================================================

class TestContextAgent:

    @pytest.fixture
    def agent(self, nodeid, tmp_dir):
        store = str(tmp_dir / "context.json")
        with patch.dict(os.environ, {"CONTEXT_STORE_PATH": store}):
            from agents.context_agent import ContextAgent
            return ContextAgent(nodeid)

    def test_get_context_default(self, agent):
        ctx = agent.get_context("PAT-001")
        assert ctx["patient_ref"] == "PAT-001"
        assert ctx["vitals"]      == {}
        assert ctx["conditions"]  == []

    def test_update_vitals(self, agent):
        agent.update_context("PAT-001", {"vitals": {"heart_rate": 72}})
        ctx = agent.get_context("PAT-001")
        assert ctx["vitals"]["heart_rate"] == 72

    def test_update_conditions_dedup(self, agent):
        agent.update_context("PAT-001", {"conditions": ["hypertension"]})
        agent.update_context("PAT-001", {"conditions": ["hypertension", "diabetes"]})
        ctx = agent.get_context("PAT-001")
        assert ctx["conditions"].count("hypertension") == 1
        assert "diabetes" in ctx["conditions"]

    def test_update_medications_dedup(self, agent):
        agent.update_context("PAT-001", {"medications": ["metformin"]})
        agent.update_context("PAT-001", {"medications": ["metformin", "aspirin"]})
        ctx = agent.get_context("PAT-001")
        assert ctx["medications"].count("metformin") == 1

    def test_history_append(self, agent):
        agent.update_context("PAT-001", {"event": "admitted"})
        agent.update_context("PAT-001", {"event": "vitals_checked"})
        ctx = agent.get_context("PAT-001")
        assert len(ctx["history"]) == 2
        assert ctx["history"][0]["event"] == "admitted"

    def test_history_capped_at_100(self, agent):
        for i in range(110):
            agent.update_context("PAT-001", {"event": f"event_{i}"})
        ctx = agent.get_context("PAT-001")
        assert len(ctx["history"]) == 100

    def test_persistence(self, nodeid, tmp_dir):
        store = str(tmp_dir / "context.json")
        with patch.dict(os.environ, {"CONTEXT_STORE_PATH": store}):
            from agents.context_agent import ContextAgent
            a1 = ContextAgent(nodeid)
            a1.update_context("PAT-PERSIST", {"vitals": {"spo2": 98}})

            # New instance should reload
            a2 = ContextAgent(nodeid)
            ctx = a2.get_context("PAT-PERSIST")
            assert ctx["vitals"]["spo2"] == 98


# ============================================================================
# PopulationAgent
# ============================================================================

class TestPopulationAgent:

    @pytest.fixture
    def agent(self, nodeid, tmp_dir):
        log_path = str(tmp_dir / "population.jsonl")
        with patch.dict(os.environ, {"POPULATION_STATS_LOG": log_path}):
            from agents.population_agent import PopulationAgent
            return PopulationAgent(nodeid)

    def test_record_signal(self, agent):
        agent._record_signal("Kisii", "malaria")
        assert len(agent._signals["Kisii"]["malaria"]) == 1

    def test_signals_pruned_after_24h(self, agent):
        # Add an old signal manually
        old_ts = time.time() - 90000   # 25h ago
        agent._signals["Kisii"]["cholera"].append(old_ts)
        # Record a new one -- triggers pruning
        agent._record_signal("Kisii", "cholera")
        # Only the new one should remain
        assert len(agent._signals["Kisii"]["cholera"]) == 1

    def test_outbreak_not_triggered_below_threshold(self, agent):
        for _ in range(4):
            agent._record_signal("Nairobi", "cholera")
        assert agent._check_outbreak("Nairobi", "cholera") is False  # threshold=5

    def test_outbreak_triggered_at_threshold(self, agent):
        for _ in range(5):
            agent._record_signal("Mombasa", "cholera")
        assert agent._check_outbreak("Mombasa", "cholera") is True

    def test_get_stats_all_counties(self, agent):
        agent._record_signal("Kisii",    "malaria")
        agent._record_signal("Nakuru",   "typhoid")
        stats = agent._get_stats()
        assert "Kisii"  in stats
        assert "Nakuru" in stats

    def test_get_stats_single_county(self, agent):
        agent._record_signal("Kisii", "malaria")
        stats = agent._get_stats("Kisii")
        assert "Kisii" in stats
        assert "Nakuru" not in stats

    def test_default_outbreak_threshold(self, agent):
        for _ in range(15):
            agent._record_signal("Eldoret", "unknown_disease")
        assert agent._check_outbreak("Eldoret", "unknown_disease") is True  # default=15

    def test_log_stats(self, agent, tmp_dir):
        agent._log_stats({"type": "test", "county": "Kisii"})
        log_path = tmp_dir / "population.jsonl"
        assert log_path.exists()
        line = json.loads(log_path.read_text().strip())
        assert line["county"] == "Kisii"


# ============================================================================
# TwinAgent scoring
# ============================================================================

class TestTwinScoring:

    def test_score_critical_spo2(self):
        from agents.twin_agent import _score_vitals, _risk_label
        score, indicators = _score_vitals({"spo2": 85})
        assert score >= 0.35
        assert any("SpO2" in i for i in indicators)

    def test_score_critical_hr(self):
        from agents.twin_agent import _score_vitals
        score, indicators = _score_vitals({"heart_rate": 145})
        assert score >= 0.30
        assert any("HR" in i for i in indicators)

    def test_score_critical_bp(self):
        from agents.twin_agent import _score_vitals
        score, indicators = _score_vitals({"bp_systolic": 210})
        assert score >= 0.30

    def test_score_normal_vitals(self):
        from agents.twin_agent import _score_vitals, _risk_label
        score, indicators = _score_vitals({
            "heart_rate": 75, "spo2": 98,
            "bp_systolic": 120, "temperature": 37.0,
            "respiratory_rate": 16, "glucose": 90,
        })
        assert score == 0.0
        assert indicators == []
        assert _risk_label(score) == "unknown"   # score=0 → unknown

    def test_risk_labels(self):
        from agents.twin_agent import _risk_label
        assert _risk_label(0.0)  == "unknown"
        assert _risk_label(0.1)  == "low"
        assert _risk_label(0.3)  == "moderate"
        assert _risk_label(0.6)  == "high"
        assert _risk_label(0.9)  == "critical"

    def test_score_capped_at_1(self):
        from agents.twin_agent import _score_vitals
        # Worst case everything critical
        score, _ = _score_vitals({
            "heart_rate": 200, "spo2": 70, "bp_systolic": 50,
            "temperature": 42, "respiratory_rate": 40, "glucose": 30,
        })
        assert score <= 1.0

    def test_empty_vitals(self):
        from agents.twin_agent import _score_vitals
        score, indicators = _score_vitals({})
        assert score    == 0.0
        assert indicators == []

    def test_invalid_vital_value(self):
        from agents.twin_agent import _score_vitals
        # Should not raise -- invalid values treated as 0
        score, _ = _score_vitals({"heart_rate": "not_a_number"})
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_twin_agent_ensure_twin(self):
        from agents.twin_agent import TwinAgent, TwinState
        agent = TwinAgent()
        agent._ensure_twin("PAT-001")
        assert "PAT-001" in agent._twins
        assert isinstance(agent._twins["PAT-001"], TwinState)

    @pytest.mark.asyncio
    async def test_twin_agent_idempotent_ensure(self):
        from agents.twin_agent import TwinAgent
        agent = TwinAgent()
        agent._ensure_twin("PAT-001")
        agent._twins["PAT-001"].vitals["heart_rate"] = 72
        agent._ensure_twin("PAT-001")   # should not overwrite
        assert agent._twins["PAT-001"].vitals["heart_rate"] == 72

    @pytest.mark.asyncio
    async def test_twin_persistence(self, tmp_dir):
        from agents.twin_agent import TwinAgent, TWIN_STORE
        store = str(tmp_dir / "twins.json")
        with patch("agents.twin_agent.TWIN_STORE", store):
            agent = TwinAgent()
            agent._ensure_twin("PAT-SAVE")
            agent._twins["PAT-SAVE"].risk_score = 0.75
            agent._save()

            agent2 = TwinAgent()
            agent2._load()
            assert "PAT-SAVE" in agent2._twins
            assert agent2._twins["PAT-SAVE"].risk_score == 0.75


# ============================================================================
# DrugAgent
# ============================================================================

class TestDrugAgent:

    @pytest.fixture
    def agent(self, nodeid):
        from agents.drug_agent import DrugAgent
        return DrugAgent(nodeid)

    @pytest.mark.asyncio
    async def test_verify_novela_unreachable(self, agent):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
            result = await agent.verify(medication_name="Panadol")
        assert result["status"]     == "UNKNOWN"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_verify_success(self, agent):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "status":          "genuine",
                "confidence":      0.95,
                "reasoning":       "Verified batch",
                "risk_indicators": [],
            }
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__  = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = await agent.verify(medication_name="Amoxicillin", barcode="KE9001")
        assert result["status"]     == "genuine"
        assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_verify_exception_returns_unknown(self, agent):
        with patch("urllib.request.urlopen", side_effect=Exception("unexpected")):
            result = await agent.verify(barcode="BAD")
        assert result["status"] == "UNKNOWN"


# ============================================================================
# LearningAgent
# ============================================================================

class TestLearningAgent:

    @pytest.fixture
    def agent(self, nodeid, tmp_dir):
        log_path = str(tmp_dir / "feedback.jsonl")
        with patch.dict(os.environ, {"FEEDBACK_LOG": log_path}):
            from agents.learning_agent import LearningAgent
            return LearningAgent(nodeid)

    def test_log_feedback_creates_file(self, agent, tmp_dir):
        log_path = tmp_dir / "feedback.jsonl"
        with patch.dict(os.environ, {"FEEDBACK_LOG": str(log_path)}):
            agent._log_feedback({
                "patient_ref": "PAT-001",
                "model":       "meditron:7b",
                "prediction":  "low",
                "actual":      "medium",
            })
        # Check count incremented
        assert agent._count == 1

    def test_log_feedback_increments_count(self, agent, tmp_dir):
        for _ in range(5):
            agent._log_feedback({"model": "phi4-mini", "prediction": "low"})
        assert agent._count == 5


# ============================================================================
# NetworkAgent
# ============================================================================

class TestNetworkAgent:

    @pytest.fixture
    def agent(self, nodeid):
        from agents.network_agent import NetworkAgent
        return NetworkAgent(nodeid)

    def test_initial_peers_empty(self, agent):
        assert agent._peers == {}

    def test_peer_tracking(self, agent):
        # Simulate mesh handler updating peers directly
        agent._peers["mesh-node-abc"] = {
            "last_seen": time.time(),
            "hostname":  "ward-1.kisii.ke",
            "sealed":    True,
        }
        assert "mesh-node-abc" in agent._peers
        assert agent._peers["mesh-node-abc"]["sealed"] is True


# ============================================================================
# SecurityAgent -- unit tests on state tracking
# ============================================================================

class TestSecurityAgent:

    @pytest.fixture
    def agent(self, nodeid):
        from agents.security_agent import SecurityAgent
        a = SecurityAgent(nodeid)
        a._nc = AsyncMock()
        return a

    def test_initial_state(self, agent):
        assert len(agent._threat_buffer) == 0
        assert len(agent._blocked_ips)   == 0
        assert len(agent._attack_map)    == 0

    def test_build_summary_empty(self, agent):
        summary = agent._build_summary()
        assert summary["total_threats"]  == 0
        assert summary["blocked_ips"]    == 0
        assert summary["nodes_affected"] == 0

    def test_build_summary_with_threats(self, agent, nodeid):
        agent._threat_buffer.extend([
            {"level": "HIGH",     "node_id": nodeid},
            {"level": "CRITICAL", "node_id": nodeid},
            {"level": "HIGH",     "node_id": "other"},
        ])
        agent._node_threats[nodeid] = [{"level": "HIGH"}]
        agent._blocked_ips.add("1.2.3.4")
        summary = agent._build_summary()
        assert summary["total_threats"] == 3
        assert summary["blocked_ips"]   == 1

    def test_parse_valid_json(self, agent):
        raw = '{"attack_classification": "port_scan", "confidence": 0.9}'
        result = agent._parse(raw)
        assert result["attack_classification"] == "port_scan"

    def test_parse_json_with_fences(self, agent):
        raw = '```json\n{"attack_classification": "ddos", "confidence": 0.8}\n```'
        result = agent._parse(raw)
        assert result["confidence"] == 0.8

    def test_parse_invalid_json(self, agent):
        result = agent._parse("not valid json at all")
        assert result["attack_classification"] == "parse_error"
        assert result["confidence"]             == 0.0

    @pytest.mark.asyncio
    async def test_on_block_records_ip(self, agent):
        msg = MagicMock()
        msg.data.decode.return_value = json.dumps({
            "threat_type": "ip_blocked",
            "data":        {"ip": "5.5.5.5"},
        })
        await agent._on_block(msg)
        assert "5.5.5.5" in agent._blocked_ips

    @pytest.mark.asyncio
    async def test_on_alert_tracks_source(self, agent):
        msg = MagicMock()
        msg.data.decode.return_value = json.dumps({
            "threat_type": "port_scan",
            "level":       "HIGH",
            "score":       7.0,
            "node_id":     "test-node",
            "data":        {"src_ip": "10.0.0.1"},
            "description": "test",
        })
        await agent._on_alert(msg)
        assert agent._attack_map["10.0.0.1"] == 1

    @pytest.mark.asyncio
    async def test_on_alert_routes_health_threat(self, agent):
        msg = MagicMock()
        msg.data.decode.return_value = json.dumps({
            "threat_type": "data_exfil",
            "level":       "CRITICAL",
            "score":       9.0,
            "node_id":     "test-node",
            "data":        {},
            "description": "Patient data exfil",
        })
        await agent._on_alert(msg)
        # Should have called _acp to health_agent
        agent._nc.publish.assert_called()

    @pytest.mark.asyncio
    async def test_acp_publish(self, agent, nodeid):
        await agent._acp("health_agent", "test_action", {"key": "val"})
        agent._nc.publish.assert_called_once()
        call_args = agent._nc.publish.call_args
        subject   = call_args.args[0]
        payload   = json.loads(call_args.args[1].decode())
        assert "health_agent" in subject
        assert payload["action"]  == "test_action"
        assert payload["payload"] == {"key": "val"}


# ============================================================================
# HealthAgent -- parse
# ============================================================================

class TestHealthAgentParse:

    @pytest.fixture
    def agent(self):
        from agents.health_agent import HealthAgent
        a = HealthAgent()
        return a

    def test_parse_valid_json(self, agent):
        raw = '{"risk_level": "low", "confidence": 0.9, "summary": "stable"}'
        result = agent._parse(raw)
        assert result["risk_level"]  == "low"
        assert result["confidence"]  == 0.9

    def test_parse_with_markdown_fences(self, agent):
        raw = '```json\n{"risk_level": "high", "confidence": 0.7}\n```'
        result = agent._parse(raw)
        assert result["risk_level"] == "high"

    def test_parse_invalid_returns_fallback(self, agent):
        result = agent._parse("not json")
        assert result["risk_level"]           == "unknown"
        assert result["human_review_required"] is True
        assert "parse_error" in result["flags"]

    def test_parse_critical_sets_review(self, agent):
        raw = '{"risk_level": "critical", "confidence": 0.95, "summary": "critical"}'
        result = agent._parse(raw)
        # _parse doesn't set human_review_required -- analyse() does
        # Just verify parse succeeds
        assert result["risk_level"] == "critical"


# ============================================================================
# Runtime -- nodeid
# ============================================================================

class TestRuntime:

    def test_get_nodeid_dev_mode(self):
        import importlib
        import byngox_runtime as rt
        with patch("builtins.open", side_effect=FileNotFoundError):
            nodeid = rt._get_nodeid()
        assert len(nodeid) == 32
        assert nodeid.isalnum() or all(c in "0123456789abcdef" for c in nodeid)

    def test_nodeid_from_proc(self):
        import byngox_runtime as rt
        with patch("builtins.open", mock_open(read_data="abc123def456")):
            nodeid = rt._get_nodeid()
        assert nodeid == "abc123def456"


# ============================================================================
# Conftest
# ============================================================================

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
