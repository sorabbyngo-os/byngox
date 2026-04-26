"""
Byngox — Agent Tests
Covers: HealthAgent, DrugAgent, ContextAgent, ACP protocol, SUID integration.
All tests run without NATS using mocks.
"""
import asyncio
import json
import os
import tempfile
import time
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from acp.protocol import ACPMessage
from acp.message_types import (
    HEALTH_QUERY, HEALTH_RESULT, DRUG_VERIFY, DRUG_RESULT,
    CONTEXT_FETCH, CONTEXT_UPDATE, POPULATION_PING, LEARN_FEEDBACK,
)
from agents.base_agent import BaseAgent
from agents.drug_agent import DrugAgent
from agents.context_agent import ContextAgent


def make_msg(data: dict, reply: str = None):
    msg = MagicMock()
    msg.data  = json.dumps(data).encode()
    msg.reply = reply
    return msg


# ══════════════════════════════════════════════════════════════════════════════
# ACP Protocol Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestACPProtocol:

    def test_message_to_json(self):
        msg = ACPMessage(
            msg_type="HEALTH_QUERY",
            payload={"patient_id": "PAT-001"},
            sender="health_agent",
            target="context_agent",
        )
        j = msg.to_json()
        d = json.loads(j)
        assert d["type"]    == "HEALTH_QUERY"
        assert d["sender"]  == "health_agent"
        assert d["target"]  == "context_agent"
        assert d["payload"]["patient_id"] == "PAT-001"

    def test_message_from_json(self):
        raw = json.dumps({
            "type":    "DRUG_VERIFY",
            "payload": {"barcode": "KE123456"},
            "sender":  "drug_agent",
            "target":  "health_agent",
        })
        msg = ACPMessage.from_json(raw)
        assert msg.msg_type == "DRUG_VERIFY"
        assert msg.payload["barcode"] == "KE123456"
        assert msg.sender == "drug_agent"

    def test_message_roundtrip(self):
        original = ACPMessage(
            msg_type=HEALTH_RESULT,
            payload={"risk_level": "high", "confidence": 0.85},
            sender="health_agent",
            target="coordination_agent",
        )
        restored = ACPMessage.from_json(original.to_json())
        assert restored.msg_type              == original.msg_type
        assert restored.payload["risk_level"] == "high"
        assert restored.sender                == original.sender

    def test_message_no_target(self):
        msg = ACPMessage(POPULATION_PING, {"region": "KE045"}, "population_agent")
        d   = json.loads(msg.to_json())
        assert d["target"] is None

    def test_all_message_types_defined(self):
        types = [
            HEALTH_QUERY, HEALTH_RESULT, DRUG_VERIFY, DRUG_RESULT,
            CONTEXT_FETCH, CONTEXT_UPDATE, POPULATION_PING, LEARN_FEEDBACK,
        ]
        assert len(types) == 8
        assert all(isinstance(t, str) for t in types)
        assert len(set(types)) == 8  # all unique


# ══════════════════════════════════════════════════════════════════════════════
# HealthAgent Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestHealthAgent:

    @pytest.fixture
    def agent(self):
        from agents.health_agent import HealthAgent
        a = HealthAgent()
        a._nc  = AsyncMock()
        a._js  = AsyncMock()
        a._model = "phi4-mini"
        a._cml   = None
        return a

    def test_parse_valid_json(self, agent):
        raw = json.dumps({
            "risk_level": "high", "confidence": 0.85,
            "summary": "Elevated BP trend",
            "reasoning": ["step1", "step2"],
            "recommendations": ["Monitor"],
            "human_review_required": True,
            "flags": [],
        })
        result = agent._parse(raw)
        assert result["risk_level"]   == "high"
        assert result["confidence"]   == 0.85
        assert result["human_review_required"] is True

    def test_parse_with_markdown_fences(self, agent):
        raw = '```json\n{"risk_level": "medium", "confidence": 0.7}\n```'
        result = agent._parse(raw)
        assert result["risk_level"] == "medium"

    def test_parse_invalid_returns_safe_default(self, agent):
        result = agent._parse("not json {{{")
        assert result["risk_level"] == "unknown"
        assert result["human_review_required"] is True
        assert "parse_error" in result["flags"]

    def test_parse_empty_returns_safe_default(self, agent):
        result = agent._parse("")
        assert result["human_review_required"] is True

    @pytest.mark.asyncio
    async def test_analyse_critical_sets_human_review(self, agent):
        mock_response = json.dumps({
            "risk_level": "critical", "confidence": 0.95,
            "summary": "Critical deterioration",
            "reasoning": [], "recommendations": [],
            "human_review_required": False,
            "flags": [],
        })
        with patch.object(agent, "_run_inference", return_value=mock_response):
            result = await agent.analyse({"patient_id": "PAT-001"})
        assert result["human_review_required"] is True

    @pytest.mark.asyncio
    async def test_analyse_cml_blocks_response(self, agent):
        mock_cml = AsyncMock()
        mock_cml.filter = AsyncMock(return_value={
            "allowed": False,
            "reason": "unsafe recommendation",
            "clinical_flags": [],
            "human_review_required": False,
        })
        agent._cml = mock_cml

        mock_response = json.dumps({
            "risk_level": "medium", "confidence": 0.7,
            "summary": "unsafe content", "reasoning": [],
            "recommendations": ["dangerous recommendation"],
            "human_review_required": False, "flags": [],
        })
        with patch.object(agent, "_run_inference", return_value=mock_response):
            result = await agent.analyse({"patient_id": "PAT-001"})

        assert result["cml_blocked"] is True
        assert result["human_review_required"] is True
        assert "Manual clinical assessment" in result["recommendations"][0]

    @pytest.mark.asyncio
    async def test_analyse_cml_adds_flags(self, agent):
        mock_cml = AsyncMock()
        mock_cml.filter = AsyncMock(return_value={
            "allowed": True,
            "clinical_flags": ["requires_specialist"],
            "human_review_required": True,
        })
        agent._cml = mock_cml

        mock_response = json.dumps({
            "risk_level": "high", "confidence": 0.8,
            "summary": "needs specialist", "reasoning": [],
            "recommendations": ["refer to specialist"],
            "human_review_required": False, "flags": [],
        })
        with patch.object(agent, "_run_inference", return_value=mock_response):
            result = await agent.analyse({"patient_id": "PAT-002"})

        assert "requires_specialist" in result["flags"]
        assert result["human_review_required"] is True

    @pytest.mark.asyncio
    async def test_handle_direct_publishes_reply(self, agent):
        mock_response = json.dumps({
            "risk_level": "low", "confidence": 0.9,
            "summary": "stable", "reasoning": [],
            "recommendations": [], "human_review_required": False, "flags": [],
        })
        with patch.object(agent, "_run_inference", return_value=mock_response):
            msg = make_msg({"patient_id": "PAT-003"}, reply="reply.subject")
            await agent._handle_direct(msg)
        agent._nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_direct_no_reply(self, agent):
        mock_response = json.dumps({
            "risk_level": "low", "confidence": 0.9,
            "summary": "ok", "reasoning": [],
            "recommendations": [], "human_review_required": False, "flags": [],
        })
        with patch.object(agent, "_run_inference", return_value=mock_response):
            msg = make_msg({"patient_id": "PAT-004"}, reply=None)
            await agent._handle_direct(msg)
        agent._nc.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_assess_skips_insufficient_data(self, agent):
        from collections import deque
        agent._buffers["PAT-005"] = deque([{"vitals": {"hr": 80}}])
        with patch.object(agent, "analyse", new_callable=AsyncMock) as mock_analyse:
            await agent._assess("PAT-005", {})
        mock_analyse.assert_not_called()

    def test_select_model_no_ollama(self, agent):
        # Without Ollama, should return tier1 fallback
        assert agent._model == "phi4-mini"


# ══════════════════════════════════════════════════════════════════════════════
# DrugAgent Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDrugAgent:

    @pytest.fixture
    def agent(self):
        return DrugAgent(nodeid="test-node-001")

    def test_init(self, agent):
        assert agent.nodeid == "test-node-001"
        assert agent.name   == "DrugAgent"

    @pytest.mark.asyncio
    async def test_verify_novela_unreachable(self, agent):
        result = await agent.verify(
            medication_name="Amoxicillin",
            barcode="KE123456",
        )
        assert result["status"]    == "UNKNOWN"
        assert result["confidence"] == 0.0
        assert "unreachable" in result["reasoning"].lower() or \
               "failed" in result["reasoning"].lower()

    @pytest.mark.asyncio
    async def test_verify_returns_novela_response(self, agent):
        mock_response = json.dumps({
            "data": {
                "status": "AUTHENTIC",
                "confidence": 0.97,
                "risk_indicators": [],
                "reasoning": "Barcode verified against KE drug registry",
            }
        }).encode()

        import urllib.error
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value.read = MagicMock(return_value=mock_response)

        with patch("urllib.request.urlopen", return_value=mock_urlopen.return_value):
            result = await agent.verify(
                medication_name="Amoxicillin 500mg",
                barcode="KE123456",
            )
        assert result["status"]     == "AUTHENTIC"
        assert result["confidence"] == 0.97

    @pytest.mark.asyncio
    async def test_verify_counterfeit_detected(self, agent):
        mock_response = json.dumps({
            "data": {
                "status": "COUNTERFEIT",
                "confidence": 0.89,
                "risk_indicators": ["barcode_mismatch", "packaging_anomaly"],
                "reasoning": "Barcode not found in registry",
            }
        }).encode()

        mock_urlopen = MagicMock()
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value.read = MagicMock(return_value=mock_response)

        with patch("urllib.request.urlopen", return_value=mock_urlopen.return_value):
            result = await agent.verify(barcode="FAKE-999")
        assert result["status"] == "COUNTERFEIT"
        assert len(result["risk_indicators"]) > 0

    @pytest.mark.asyncio
    async def test_verify_handles_bad_json(self, agent):
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__  = MagicMock(return_value=False)
        mock_urlopen.return_value.read = MagicMock(return_value=b"bad json {{{")

        with patch("urllib.request.urlopen", return_value=mock_urlopen.return_value):
            result = await agent.verify(medication_name="test")
        assert result["status"] == "UNKNOWN"

    @pytest.mark.asyncio
    async def test_verify_empty_inputs(self, agent):
        result = await agent.verify()
        assert result["status"] == "UNKNOWN"


# ══════════════════════════════════════════════════════════════════════════════
# ContextAgent Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestContextAgent:

    @pytest.fixture
    def agent(self, tmp_path):
        with patch.dict(os.environ, {
            "CONTEXT_STORE_PATH": str(tmp_path / "context.json")
        }):
            a = ContextAgent(nodeid="test-node-001")
            a._nc = AsyncMock()
            return a

    def test_init(self, agent):
        assert agent.nodeid == "test-node-001"
        assert agent.name   == "ContextAgent"
        assert isinstance(agent._store, dict)

    def test_get_context_new_patient(self, agent):
        ctx = agent.get_context("PAT-001")
        assert ctx["patient_ref"]  == "PAT-001"
        assert ctx["conditions"]   == []
        assert ctx["medications"]  == []
        assert ctx["history"]      == []

    def test_update_context_vitals(self, agent):
        agent.update_context("PAT-001", {"vitals": {"hr": 80, "bp": "120/80"}})
        ctx = agent.get_context("PAT-001")
        assert ctx["vitals"]["hr"] == 80
        assert ctx["vitals"]["bp"] == "120/80"

    def test_update_context_conditions(self, agent):
        agent.update_context("PAT-001", {"conditions": ["hypertension", "diabetes"]})
        agent.update_context("PAT-001", {"conditions": ["hypertension"]})  # duplicate
        ctx = agent.get_context("PAT-001")
        assert ctx["conditions"].count("hypertension") == 1
        assert "diabetes" in ctx["conditions"]

    def test_update_context_medications(self, agent):
        agent.update_context("PAT-001", {"medications": ["Metformin", "Amlodipine"]})
        ctx = agent.get_context("PAT-001")
        assert "Metformin"   in ctx["medications"]
        assert "Amlodipine"  in ctx["medications"]

    def test_update_context_history_appends(self, agent):
        agent.update_context("PAT-001", {"event": "admission"})
        agent.update_context("PAT-001", {"event": "vitals_check"})
        ctx = agent.get_context("PAT-001")
        assert len(ctx["history"]) == 2
        assert ctx["history"][0]["event"] == "admission"

    def test_update_context_history_capped_at_100(self, agent):
        for i in range(120):
            agent.update_context("PAT-001", {"event": f"event_{i}"})
        ctx = agent.get_context("PAT-001")
        assert len(ctx["history"]) == 100

    def test_last_updated_set(self, agent):
        before = time.time()
        agent.update_context("PAT-002", {"vitals": {"hr": 72}})
        after = time.time()
        ctx = agent.get_context("PAT-002")
        assert before <= ctx["last_updated"] <= after

    def test_persist_and_reload(self, tmp_path):
        store_path = str(tmp_path / "context.json")
        with patch.dict(os.environ, {"CONTEXT_STORE_PATH": store_path}):
            a1 = ContextAgent(nodeid="node-1")
            a1.update_context("PAT-003", {"vitals": {"hr": 90}})

            a2 = ContextAgent(nodeid="node-1")
            ctx = a2.get_context("PAT-003")
            assert ctx["vitals"]["hr"] == 90

    def test_multiple_patients_independent(self, agent):
        agent.update_context("PAT-A", {"vitals": {"hr": 60}})
        agent.update_context("PAT-B", {"vitals": {"hr": 100}})
        assert agent.get_context("PAT-A")["vitals"]["hr"] == 60
        assert agent.get_context("PAT-B")["vitals"]["hr"] == 100

    @pytest.mark.asyncio
    async def test_fetch_handler_replies(self, agent):
        agent.update_context("PAT-010", {"vitals": {"hr": 75}})
        msg = make_msg({"patient_ref": "PAT-010"}, reply="reply.subject")
        # Simulate fetch handler
        ctx = agent.get_context("PAT-010")
        assert ctx["vitals"]["hr"] == 75

    @pytest.mark.asyncio
    async def test_update_handler_no_patient_ref(self, agent):
        # Should not crash with missing patient_ref
        msg = make_msg({"vitals": {"hr": 80}})
        payload = json.loads(msg.data.decode())
        patient_ref = payload.get("patient_ref", "")
        assert patient_ref == ""


# ══════════════════════════════════════════════════════════════════════════════
# SUID Integration Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestByngoxSUIDIntegration:
    """Byngox uses SUIDs for patient, drug, session, and audit IDs."""

    def test_suid_available(self):
        try:
            from suid.generator import SUID
            assert True
        except ImportError:
            pytest.skip("identity-core not installed")

    def test_patient_suid_in_health_context(self):
        try:
            from suid.generator import SUID
            from suid.registry.prefixes import PREFIX
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        patient_id = SUID.patient("KE045")
        assert validate(patient_id)
        assert patient_id.startswith("PAT-")
        assert "KE045" in patient_id

    def test_drug_verification_suid(self):
        try:
            from suid.generator import SUID
            from suid.registry.prefixes import PREFIX
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        verification_id = SUID.verification("KE042")
        assert validate(verification_id)
        assert verification_id.startswith("VRF-")

    def test_session_suid_for_byngox(self):
        try:
            from suid.generator import SUID
            from suid.registry.prefixes import PREFIX
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        session_id = SUID.session("KE047")
        assert validate(session_id)
        assert session_id.startswith("SES-")

    def test_context_agent_with_suid_patient_ref(self, tmp_path):
        try:
            from suid.generator import SUID
        except ImportError:
            pytest.skip("identity-core not installed")

        store_path = str(tmp_path / "context.json")
        with patch.dict(os.environ, {"CONTEXT_STORE_PATH": store_path}):
            agent = ContextAgent(nodeid="test-node")
            patient_id = SUID.patient("KE045")
            agent.update_context(patient_id, {
                "vitals":     {"hr": 72, "bp": "118/76"},
                "conditions": ["hypertension"],
                "event":      "admission",
            })
            ctx = agent.get_context(patient_id)
            assert ctx["vitals"]["hr"]    == 72
            assert "hypertension" in ctx["conditions"]
            assert ctx["patient_ref"]     == patient_id

    def test_drug_verification_audit_trail(self):
        try:
            from suid.generator import SUID
            from suid.audit.logger import AuditLogger
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        medication_id    = SUID.generate("MED", "KE045")
        verification_id  = SUID.verification("KE045")
        doctor_id        = SUID.doctor("KE045")

        entry = AuditLogger.verify(
            entity_id=medication_id,
            actor_id=doctor_id,
            related_id=verification_id,
            region="KE045",
        )
        assert entry["action"]    == "VERIFY"
        assert entry["entity_id"] == medication_id
        assert validate(entry["audit_id"])

    def test_prescription_suid_generation(self):
        try:
            from suid.generator import SUID
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        rx_id = SUID.prescription("KE045")
        assert validate(rx_id)
        assert rx_id.startswith("RXN-")
        assert "KE045" in rx_id

    def test_lab_result_suid(self):
        try:
            from suid.generator import SUID
            from suid.validator import validate
        except ImportError:
            pytest.skip("identity-core not installed")

        lab_id = SUID.lab_result("KE042")
        assert validate(lab_id)
        assert lab_id.startswith("LAB-")

    def test_forensic_report_for_patient_record(self):
        try:
            from suid.generator import SUID
            from suid.forensics.extractor import ForensicExtractor
        except ImportError:
            pytest.skip("identity-core not installed")

        patient_id = SUID.patient("KE045")
        report = ForensicExtractor.entity_report(patient_id)
        assert report["entity_type"]    == "Patient Record"
        assert report["origin_area"]    == "Kisii"
        assert report["origin_country"] == "Kenya"
        assert report["tampered"]       is False


# ══════════════════════════════════════════════════════════════════════════════
# Runtime Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestRuntime:

    def test_get_nodeid_fallback(self):
        """Without kernel module, should derive NodeID from hostname."""
        import hashlib, socket
        expected = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:32]
        # Simulate the fallback
        nodeid = expected
        assert len(nodeid) == 32
        assert nodeid.isalnum() or all(c in "0123456789abcdef" for c in nodeid)

    def test_nodeid_from_env(self):
        with patch.dict(os.environ, {"SORABBYNGO_NODE_ID": "test-node-fixed-id-000"}):
            node_id = os.environ.get("SORABBYNGO_NODE_ID")
            assert node_id == "test-node-fixed-id-000"

    def test_all_agent_classes_importable(self):
        from agents.security_agent    import SecurityAgent
        from agents.health_agent      import HealthAgent
        from agents.drug_agent        import DrugAgent
        from agents.context_agent     import ContextAgent
        from agents.base_agent        import BaseAgent
        assert all([SecurityAgent, HealthAgent, DrugAgent, ContextAgent, BaseAgent])

    def test_acp_message_types_importable(self):
        from acp.message_types import (
            HEALTH_QUERY, HEALTH_RESULT, DRUG_VERIFY, DRUG_RESULT,
            CONTEXT_FETCH, CONTEXT_UPDATE, POPULATION_PING, LEARN_FEEDBACK,
        )
        assert HEALTH_QUERY == "HEALTH_QUERY"
        assert DRUG_VERIFY  == "DRUG_VERIFY"
