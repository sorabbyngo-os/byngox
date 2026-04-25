"""
Byngox — Security Agent Tests
All tests run without NATS using mocks.
"""
import asyncio
import json
from collections import defaultdict, deque
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.security_agent import (
    SecurityAgent,
    HEALTH_THREATS, POPULATION_THREATS,
    AI_SCORE_THRESHOLD, COORDINATION_THRESHOLD,
)


@pytest.fixture
def agent():
    a = SecurityAgent(nodeid="test-node-abc123")
    a._nc = AsyncMock()
    a._js = AsyncMock()
    return a


def make_msg(data: dict):
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    msg.reply = None
    return msg


# ═════════════════════════════════════════════════════════════════════════════
# Init
# ═════════════════════════════════════════════════════════════════════════════

def test_agent_init():
    a = SecurityAgent("node-001")
    assert a.nodeid == "node-001"
    assert len(a._threat_buffer) == 0
    assert len(a._blocked_ips) == 0
    assert len(a._attack_map) == 0


# ═════════════════════════════════════════════════════════════════════════════
# _on_alert
# ═════════════════════════════════════════════════════════════════════════════

async def test_on_alert_records_threat(agent):
    msg = make_msg({
        "threat_type": "port_scan",
        "level": "HIGH",
        "score": 7.5,
        "node_id": "node-abc",
        "data": {"src_ip": "1.2.3.4"},
    })
    await agent._on_alert(msg)
    assert len(agent._threat_buffer) == 1
    assert agent._attack_map["1.2.3.4"] == 1


async def test_on_alert_routes_health_threat(agent):
    msg = make_msg({
        "threat_type": "ransomware",
        "level": "CRITICAL",
        "score": 9.5,
        "node_id": "node-abc",
        "data": {"src_ip": "5.6.7.8"},
    })
    with patch.object(agent, "_acp", new_callable=AsyncMock) as mock_acp:
        await agent._on_alert(msg)
    targets = [call.args[0] for call in mock_acp.call_args_list]
    assert "health_agent" in targets


async def test_on_alert_routes_network_threat(agent):
    msg = make_msg({
        "threat_type": "port_scan",
        "level": "MEDIUM",
        "score": 5.0,
        "node_id": "node-abc",
        "data": {"src_ip": "9.8.7.6"},
    })
    with patch.object(agent, "_acp", new_callable=AsyncMock) as mock_acp:
        await agent._on_alert(msg)
    targets = [call.args[0] for call in mock_acp.call_args_list]
    assert "population_agent" in targets


async def test_on_alert_triggers_ai_on_high_score(agent):
    msg = make_msg({
        "threat_type": "ransomware",
        "level": "CRITICAL",
        "score": AI_SCORE_THRESHOLD + 1,
        "node_id": "node-abc",
        "data": {},
    })
    with patch.object(agent, "_analyse", new_callable=AsyncMock) as mock_ai:
        await agent._on_alert(msg)
        # Give task time to schedule
        await asyncio.sleep(0.05)
    mock_ai.assert_called_once()


async def test_on_alert_no_ai_below_threshold(agent):
    msg = make_msg({
        "threat_type": "port_scan",
        "level": "LOW",
        "score": 3.0,
        "node_id": "node-abc",
        "data": {},
    })
    with patch.object(agent, "_analyse", new_callable=AsyncMock) as mock_ai:
        await agent._on_alert(msg)
        await asyncio.sleep(0.05)
    mock_ai.assert_not_called()


async def test_on_alert_handles_malformed_json(agent):
    msg = MagicMock()
    msg.data = b"not json {"
    await agent._on_alert(msg)  # should not raise
    assert len(agent._threat_buffer) == 0


async def test_on_alert_no_src_ip(agent):
    msg = make_msg({
        "threat_type": "file_tamper",
        "level": "HIGH",
        "score": 7.0,
        "node_id": "node-abc",
        "data": {},
    })
    await agent._on_alert(msg)
    assert len(agent._attack_map) == 0  # no IP to track


# ═════════════════════════════════════════════════════════════════════════════
# _on_block
# ═════════════════════════════════════════════════════════════════════════════

async def test_on_block_adds_to_blocked(agent):
    msg = make_msg({"data": {"ip": "10.0.0.1"}})
    await agent._on_block(msg)
    assert "10.0.0.1" in agent._blocked_ips


async def test_on_block_empty_ip(agent):
    msg = make_msg({"data": {}})
    await agent._on_block(msg)
    assert len(agent._blocked_ips) == 0


async def test_on_block_malformed(agent):
    msg = MagicMock()
    msg.data = b"bad"
    await agent._on_block(msg)  # should not raise


# ═════════════════════════════════════════════════════════════════════════════
# _on_escalation
# ═════════════════════════════════════════════════════════════════════════════

async def test_on_escalation_routes_to_coordination(agent):
    msg = make_msg({
        "reason": "CRITICAL: coordinated attack",
        "node_id": "node-xyz",
    })
    with patch.object(agent, "_acp", new_callable=AsyncMock) as mock_acp:
        await agent._on_escalation(msg)
    assert mock_acp.call_args.args[0] == "coordination_agent"
    assert mock_acp.call_args.args[1] == "security_escalation"


# ═════════════════════════════════════════════════════════════════════════════
# _on_health
# ═════════════════════════════════════════════════════════════════════════════

async def test_on_health_alerts_when_cyberwall_down(agent):
    msg = make_msg({"dead": ["cyberwall"], "node_id": "node-001"})
    with patch.object(agent, "_acp", new_callable=AsyncMock) as mock_acp:
        await agent._on_health(msg)
    mock_acp.assert_called_once()
    assert mock_acp.call_args.args[1] == "security_service_down"


async def test_on_health_no_alert_when_services_healthy(agent):
    msg = make_msg({"dead": [], "node_id": "node-001"})
    with patch.object(agent, "_acp", new_callable=AsyncMock) as mock_acp:
        await agent._on_health(msg)
    mock_acp.assert_not_called()


# ═════════════════════════════════════════════════════════════════════════════
# _on_acp
# ═════════════════════════════════════════════════════════════════════════════

async def test_acp_query_threat_summary(agent):
    agent._threat_buffer.append({"level": "HIGH", "threat_type": "port_scan"})
    msg = make_msg({"action": "query_threat_summary"})
    msg.reply = "reply.subject"
    await agent._on_acp(msg)
    agent._nc.publish.assert_called_once()
    published = json.loads(agent._nc.publish.call_args.args[1])
    assert "total_threats" in published
    assert published["total_threats"] == 1


async def test_acp_is_blocked_true(agent):
    agent._blocked_ips.add("1.1.1.1")
    msg = make_msg({"action": "is_blocked", "payload": {"ip": "1.1.1.1"}})
    msg.reply = "reply.subject"
    await agent._on_acp(msg)
    published = json.loads(agent._nc.publish.call_args.args[1])
    assert published["blocked"] is True


async def test_acp_is_blocked_false(agent):
    msg = make_msg({"action": "is_blocked", "payload": {"ip": "9.9.9.9"}})
    msg.reply = "reply.subject"
    await agent._on_acp(msg)
    published = json.loads(agent._nc.publish.call_args.args[1])
    assert published["blocked"] is False


async def test_acp_no_reply_subject(agent):
    msg = make_msg({"action": "query_threat_summary"})
    msg.reply = None
    await agent._on_acp(msg)  # should not raise, just skip publish


async def test_acp_query_top_attackers(agent):
    agent._attack_map["1.2.3.4"] = 10
    agent._attack_map["5.6.7.8"] = 5
    msg = make_msg({"action": "query_top_attackers"})
    msg.reply = "reply.subject"
    await agent._on_acp(msg)
    published = json.loads(agent._nc.publish.call_args.args[1])
    assert "top_attackers" in published
    assert published["top_attackers"][0][0] == "1.2.3.4"


# ═════════════════════════════════════════════════════════════════════════════
# _parse
# ═════════════════════════════════════════════════════════════════════════════

def test_parse_valid_json(agent):
    raw = '{"attack_classification": "port_scan", "confidence": 0.9}'
    result = agent._parse(raw)
    assert result["attack_classification"] == "port_scan"
    assert result["confidence"] == 0.9


def test_parse_with_markdown_fences(agent):
    raw = '```json\n{"attack_classification": "ddos", "confidence": 0.8}\n```'
    result = agent._parse(raw)
    assert result["attack_classification"] == "ddos"


def test_parse_invalid_returns_fallback(agent):
    result = agent._parse("not json at all {{{")
    assert result["attack_classification"] == "parse_error"
    assert result["confidence"] == 0.0
    assert result["patient_data_risk"] is False


# ═════════════════════════════════════════════════════════════════════════════
# _build_summary
# ═════════════════════════════════════════════════════════════════════════════

def test_build_summary_empty(agent):
    summary = agent._build_summary()
    assert summary["total_threats"] == 0
    assert summary["blocked_ips"] == 0
    assert summary["agent"] == "security_agent"
    assert summary["node_id"] == "test-node-abc123"


def test_build_summary_with_threats(agent):
    agent._threat_buffer.extend([
        {"level": "HIGH", "threat_type": "port_scan"},
        {"level": "CRITICAL", "threat_type": "ransomware"},
        {"level": "HIGH", "threat_type": "file_tamper"},
    ])
    agent._blocked_ips = {"1.2.3.4", "5.6.7.8"}
    summary = agent._build_summary()
    assert summary["total_threats"] == 3
    assert summary["blocked_ips"] == 2
    assert summary["by_level"]["HIGH"] == 2
    assert summary["by_level"]["CRITICAL"] == 1


def test_build_summary_top_attackers(agent):
    agent._attack_map["10.0.0.1"] = 50
    agent._attack_map["10.0.0.2"] = 30
    summary = agent._build_summary()
    assert summary["top_attackers"][0][0] == "10.0.0.1"


# ═════════════════════════════════════════════════════════════════════════════
# _acp helper
# ═════════════════════════════════════════════════════════════════════════════

async def test_acp_publishes_to_correct_subject(agent):
    await agent._acp("health_agent", "test_action", {"key": "value"})
    agent._nc.publish.assert_called_once()
    subject = agent._nc.publish.call_args.args[0]
    assert "health_agent" in subject
    payload = json.loads(agent._nc.publish.call_args.args[1])
    assert payload["action"] == "test_action"
    assert payload["from"] == "security_agent"


async def test_acp_handles_publish_error(agent):
    agent._nc.publish = AsyncMock(side_effect=Exception("NATS down"))
    await agent._acp("some_agent", "action", {})  # should not raise


# ═════════════════════════════════════════════════════════════════════════════
# Threat classification constants
# ═════════════════════════════════════════════════════════════════════════════

def test_health_threats_defined():
    assert "ransomware" in HEALTH_THREATS
    assert "file_tamper" in HEALTH_THREATS
    assert "backdoor" in HEALTH_THREATS


def test_population_threats_defined():
    assert "port_scan" in POPULATION_THREATS
    assert "syn_flood" in POPULATION_THREATS
    assert "ddos" in POPULATION_THREATS


def test_no_overlap_between_threat_sets():
    overlap = HEALTH_THREATS & POPULATION_THREATS
    assert len(overlap) == 0


# ═════════════════════════════════════════════════════════════════════════════
# BaseAgent
# ═════════════════════════════════════════════════════════════════════════════

def test_base_agent_init():
    from agents.base_agent import BaseAgent
    a = BaseAgent("node-001", "TestAgent")
    assert a.nodeid == "node-001"
    assert a.name == "TestAgent"


async def test_base_agent_run_raises():
    from agents.base_agent import BaseAgent
    a = BaseAgent("node-001", "TestAgent")
    with pytest.raises(NotImplementedError):
        await a.run()


async def test_base_agent_handle_raises():
    from agents.base_agent import BaseAgent
    a = BaseAgent("node-001", "TestAgent")
    with pytest.raises(NotImplementedError):
        await a.handle({})
