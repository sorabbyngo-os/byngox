"""
Byngox — CML Client
Every agent calls this before publishing any AI output.
Connects to the CML NATS service on sorabbyngo.cml.filter.request.
Falls back gracefully if CML is offline — never blocks agent operation.
"""
import asyncio
import json
import logging
import os
import time
import uuid

log = logging.getLogger("byngox.cml_client")

NATS_URL    = os.environ.get("NATS_URL",    "nats://localhost:4223")
CML_SUBJECT = "sorabbyngo.cml.filter.request"
CML_TIMEOUT = float(os.environ.get("CML_TIMEOUT", "5.0"))

# Singleton
_client = None


class CMLClient:
    """
    Async CML filter client.
    Usage:
        cml = get_client()
        result = await cml.filter(text="...", component="byngox.health_agent")
        if not result["allowed"]:
            # handle blocked response
    """

    def __init__(self):
        self._nc      = None
        self._ready   = False
        self._lock    = asyncio.Lock()
        self._stats   = {"filtered": 0, "blocked": 0, "errors": 0, "fallbacks": 0}

    async def connect(self):
        try:
            import nats
            self._nc    = await nats.connect(NATS_URL, max_reconnect_attempts=3)
            self._ready = True
            log.info("[CMLClient] connected to NATS %s", NATS_URL)
        except Exception as e:
            log.warning("[CMLClient] NATS unavailable — running in passthrough mode: %s", e)
            self._ready = False

    async def filter(
        self,
        text:      str,
        component: str  = "byngox",
        action:    str  = "ai_output",
        context:   str  = "",
        entity_id: str  = "",
    ) -> dict:
        """
        Submit text to CML safety filter.

        Returns:
            {
                "allowed":               bool,
                "text":                  str,   # scrubbed text
                "scrubbed":              bool,
                "scrub_count":           int,
                "warnings":              list,
                "clinical_flags":        list,
                "human_review_required": bool,
                "reason":                str,
                "cml_online":            bool,
            }
        """
        if not text or not text.strip():
            return self._passthrough(text)

        if not self._ready or self._nc is None:
            self._stats["fallbacks"] += 1
            return self._passthrough(text)

        request_id = str(uuid.uuid4())
        reply_subj = f"sorabbyngo.cml.filter.response.{request_id}"

        payload = json.dumps({
            "request_id": request_id,
            "text":       text,
            "component":  component,
            "action":     action,
            "context":    context,
            "entity_id":  entity_id,
        }).encode()

        try:
            async with self._lock:
                response = await self._nc.request(
                    CML_SUBJECT,
                    payload,
                    timeout=CML_TIMEOUT,
                )

            result = json.loads(response.data.decode())
            self._stats["filtered"] += 1

            if not result.get("allowed", True):
                self._stats["blocked"] += 1
                log.warning(
                    "[CMLClient] BLOCKED by CML: component=%s reason=%s",
                    component, result.get("reason", "policy")
                )

            return {
                "allowed":               result.get("allowed", True),
                "text":                  result.get("text", text),
                "scrubbed":              result.get("scrubbed", False),
                "scrub_count":           result.get("scrub_count", 0),
                "warnings":              result.get("warnings", []),
                "clinical_flags":        result.get("clinical_flags", []),
                "human_review_required": result.get("human_review_required", False),
                "reason":                result.get("reason", ""),
                "cml_online":            True,
            }

        except asyncio.TimeoutError:
            log.warning("[CMLClient] CML timeout after %.1fs — passthrough", CML_TIMEOUT)
            self._stats["errors"] += 1
            return self._passthrough(text, reason="cml_timeout")

        except Exception as e:
            log.error("[CMLClient] filter error: %s", e)
            self._stats["errors"] += 1
            return self._passthrough(text, reason=str(e))

    def _passthrough(self, text: str, reason: str = "cml_offline") -> dict:
        """
        Safe passthrough when CML is unavailable.
        Marks response so agents know CML was not applied.
        """
        return {
            "allowed":               True,
            "text":                  text,
            "scrubbed":              False,
            "scrub_count":           0,
            "warnings":              [f"CML not applied: {reason}"],
            "clinical_flags":        [],
            "human_review_required": False,
            "reason":                reason,
            "cml_online":            False,
        }

    def stats(self) -> dict:
        return dict(self._stats)

    def is_online(self) -> bool:
        return self._ready


# ── Singleton factory ─────────────────────────────────────────────────────────

def get_client() -> "CMLClient":
    """
    Get or create the singleton CML client.
    Call connect() before first use.
    """
    global _client
    if _client is None:
        _client = CMLClient()
    return _client


async def init_cml() -> "CMLClient":
    """
    Initialize and connect the CML client.
    Call once at agent startup.
    """
    client = get_client()
    await client.connect()
    return client
