from agents.hardware_agent import HardwareAgent


def test_creation():

    agent = HardwareAgent()

    assert agent.NAME == "hardware_agent"
