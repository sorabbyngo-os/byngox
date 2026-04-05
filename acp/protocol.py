# ACP Protocol Handler
# Routes messages between Byngox agents over NATS

import json
import logging
log = logging.getLogger(__name__)

class ACPMessage:
    def __init__(self, msg_type: str, payload: dict, sender: str, target: str = None):
        self.msg_type = msg_type
        self.payload = payload
        self.sender = sender
        self.target = target

    def to_json(self) -> str:
        return json.dumps({
            "type": self.msg_type,
            "payload": self.payload,
            "sender": self.sender,
            "target": self.target,
        })

    @classmethod
    def from_json(cls, data: str) -> "ACPMessage":
        d = json.loads(data)
        return cls(d["type"], d["payload"], d["sender"], d.get("target"))
