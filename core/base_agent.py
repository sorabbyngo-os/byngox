#!/usr/bin/env python3
"""
core/base_agent.py — Byngox Base Agent
All health agents inherit from this.
"""

import json
import time
import socket
import threading
import logging
from abc import ABC, abstractmethod

NATS_HOST = "127.0.0.1"
NATS_PORT = 4222


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name     = name
        self._sock    = None
        self._lock    = threading.Lock()
        self._buf     = ""
        self._running = False
        self.logger   = logging.getLogger(f"byngox.{name}")

    def start(self):
        self.logger.info(f"{self.name} starting...")
        self._connect()
        self._running = True
        self._subscribe()
        self.logger.info(f"{self.name} active")
        self._listen()

    def _connect(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((NATS_HOST, NATS_PORT))
                s.recv(1024)
                s.sendall(b'CONNECT {"verbose":false}\r\n')
                s.settimeout(None)
                self._sock = s
                self.logger.info(f"{self.name} connected to NATS")
                return
            except Exception as e:
                self.logger.warning(f"NATS unavailable: {e} — retrying in 3s")
                time.sleep(3)

    def publish(self, subject: str, payload: dict):
        payload = dict(payload)           # never mutate caller's dict
        payload["agent"]     = self.name
        payload["timestamp"] = time.time()
        msg  = json.dumps(payload)
        data = f"PUB {subject} {len(msg)}\r\n{msg}\r\n".encode()
        with self._lock:
            try:
                self._sock.sendall(data)
            except Exception:
                self._connect()
                self._sock.sendall(data)

    def subscribe(self, subject: str, sid: int):
        self._sock.sendall(f"SUB {subject} {sid}\r\n".encode())
        self.logger.info(f"Subscribed: {subject}")

    @abstractmethod
    def _subscribe(self):
        pass

    @abstractmethod
    def on_message(self, subject: str, data: dict):
        pass

    def _listen(self):
        while self._running:
            try:
                chunk = self._sock.recv(4096).decode("utf-8", errors="ignore")
                if not chunk:
                    self._connect()
                    self._subscribe()
                    continue
                self._buf += chunk
                self._buf  = self._process(self._buf)
            except Exception:
                try:
                    self._connect()
                    self._subscribe()
                except Exception:
                    pass

    def _process(self, buf: str) -> str:
        while "\r\n" in buf:
            line, buf = buf.split("\r\n", 1)
            if line.startswith("MSG "):
                parts = line.split()
                # NATS MSG format: MSG <subject> <sid> [reply] <#bytes>
                if len(parts) == 4:
                    subject = parts[1]
                    nbytes  = int(parts[3])
                elif len(parts) == 5:
                    subject = parts[1]
                    nbytes  = int(parts[4])
                else:
                    continue
                if len(buf) >= nbytes:
                    payload = buf[:nbytes]
                    buf     = buf[nbytes:].lstrip("\r\n")
                    try:
                        data = json.loads(payload)
                        self.on_message(subject, data)
                    except json.JSONDecodeError:
                        pass
        return buf
