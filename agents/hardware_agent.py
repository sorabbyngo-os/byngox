"""
Hardware Agent

Responsible for reasoning about hardware capabilities.
"""

from agents.base_agent import BaseAgent


class HardwareAgent(BaseAgent):

    NAME = "hardware_agent"

    async def handle(self, message):
        """
        Evaluate hardware capability and
        return recommendations.
        """
        return {
            "status": "pending",
            "agent": self.NAME
        }
