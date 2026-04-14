"""
Byngox — Health Agent
Sorabbyngo AI-OS | sorabbyngo-Labs/byngox

Primary clinical intelligence agent. Handles risk scoring,
clinical decision support, and health signal analysis.

Tier routing:
  Tier 1 → meditron:7b  (always-on, 4GB RAM)
  Tier 2 → meditron:70b (GPU, clinical depth)
  Tier 2 → deepseek-r1:70b (when explanation required)
  Tier 2 → mixtral:8x22b (specialist multi-domain)

⚠️  This agent provides clinical DECISION SUPPORT only.
⚠️  Never outputs diagnosis. Always flags high-risk for human review.
"""

import asyncio
import json
import logging
import os
from typing import Any

import httpx
import nats

log = logging.getLogger(__name__)

OLLAMA_URL       = os.environ.get("OLLAMA_URL",          "http://localhost:11434")
NATS_URL         = os.environ.get("NATS_URL",            "nats://localhost:4222")
AGENT_SUBJECT    = os.environ.get("HEALTH_AGENT_SUBJECT","byngox.health.analyse")
REPLY_TIMEOUT    = float(os.environ.get("HEALTH_AGENT_TIMEOUT", "120"))

# ── Model roster ────────────────────────────────────────────────────────────
TIER1_MEDICAL    = os.environ.get("TIER1_MEDICAL_MODEL",     "meditron:7b")
TIER2_MEDICAL    = os.environ.get("TIER2_MEDICAL_MODEL",     "meditron:70b")
TIER2_REASONING  = os.environ.get("TIER2_REASONING_MODEL",  "deepseek-r1:70b")
TIER2_SPECIALIST = os.environ.get("TIER2_SPECIALIST_MODEL", "mixtral:8x22b")
TIER1_FAST       = os.environ.get("TIER1_FAST_MODEL",       "phi4-mini")

CLINICAL_SYSTEM = """You are a clinical decision support engine operating within Sorabbyngo OS.

Rules:
- You support healthcare professionals — NOT patients directly
- Never provide a diagnosis — provide risk assessment and evidence-based recommendations
- Always include a confidence score (0.0–1.0)
- Flag HIGH_RISK cases explicitly for immediate human review
- Cite reasoning steps clearly
- If uncertain, say so — uncertainty is safer than false confidence

Output format (JSON):
{
  "risk_level": "low|medium|high|critical",
  "confidence": 0.0-1.0,
  "summary": "brief clinical summary",
  "reasoning": ["step 1", "step 2", ...],
  "recommendations": ["action 1", "action 2", ...],
  "human_review_required": true|false,
  "flags": []
}"""


# ── Ollama client ────────────────────────────────────────────────────────────

async def _ollama_generate(model: str, prompt: str, require_json: bool = False) -> str:
    system = CLINICAL_SYSTEM if require_json else ""
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    payload = {
        "model":  model,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature":  0.1,   # Low temp for clinical consistency
            "top_p":        0.95,
            "num_predict":  2048,
        },
    }
    async with httpx.AsyncClient(timeout=REPLY_TIMEOUT) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        return r.json().get("response", "").strip()


async def _get_available_models() -> set:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            return {m["name"] for m in r.json().get("models", [])}
    except Exception:
        return set()


# ── Tier selection ────────────────────────────────────────────────────────────

async def _select_model(payload: dict, available: set) -> tuple[str, int]:
    """
    Returns (model_name, tier) based on payload flags and available models.

    Priority:
      1. require_explanation=True → DeepSeek-R1 (chain-of-thought)
      2. risk_level=critical      → Meditron 70B
      3. specialist=True          → Mixtral 8x22B
      4. GPU available            → Meditron 70B
      5. Default                  → Meditron 7B (Tier 1)
    """
    require_explanation = payload.get("require_explanation", False)
    risk_level          = payload.get("risk_level", "unknown")
    specialist          = payload.get("specialist", False)

    # Tier 2 checks
    if require_explanation and TIER2_REASONING in available:
        return TIER2_REASONING, 2
    if risk_level == "critical" and TIER2_MEDICAL in available:
        return TIER2_MEDICAL, 2
    if specialist and TIER2_SPECIALIST in available:
        return TIER2_SPECIALIST, 2
    if TIER2_MEDICAL in available:
        return TIER2_MEDICAL, 2

    # Tier 1 fallback
    if TIER1_MEDICAL in available:
        return TIER1_MEDICAL, 1

    # Last resort — fast model
    return TIER1_FAST, 1


# ── Core analysis ────────────────────────────────────────────────────────────

async def analyse(payload: dict) -> dict:
    """
    Main health analysis entry point.

    Args:
        payload: {
            "patient_context":      dict,   # Vitals, history, medications
            "clinical_question":    str,    # What to assess
            "risk_level":           str,    # Pre-triage hint: low|medium|high|critical
            "require_explanation":  bool,   # Force DeepSeek-R1 chain-of-thought
            "specialist":           bool,   # Route to Mixtral for multi-domain
            "language":             str,    # ISO code
        }

    Returns:
        {
            "tier":                 int,
            "model":                str,
            "risk_level":           str,
            "confidence":           float,
            "summary":              str,
            "reasoning":            list,
            "recommendations":      list,
            "human_review_required":bool,
            "flags":                list,
            "raw":                  str,    # Raw model output for audit
        }
    """
    available = await _get_available_models()
    model, tier = await _select_model(payload, available)

    context  = payload.get("patient_context", {})
    question = payload.get("clinical_question", "Assess patient risk.")

    prompt = (
        f"Patient Context:\n{json.dumps(context, indent=2)}\n\n"
        f"Clinical Question: {question}\n\n"
        f"Respond with valid JSON only. No markdown. No preamble."
    )

    log.info("[HealthAgent] analyse · tier=%d model=%s", tier, model)

    try:
        raw = await _ollama_generate(model, prompt, require_json=True)

        # Strip markdown fences if present
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        result["tier"]  = tier
        result["model"] = model
        result["raw"]   = raw

        # Safety gate — always flag critical for human review
        if result.get("risk_level") == "critical":
            result["human_review_required"] = True

        log.info(
            "[HealthAgent] complete · risk=%s confidence=%.2f human_review=%s",
            result.get("risk_level"),
            result.get("confidence", 0),
            result.get("human_review_required"),
        )
        return result

    except json.JSONDecodeError:
        log.error("[HealthAgent] JSON parse failed, returning raw text")
        return {
            "tier":                 tier,
            "model":                model,
            "risk_level":           "unknown",
            "confidence":           0.0,
            "summary":              raw[:500] if raw else "Model response unparseable",
            "reasoning":            [],
            "recommendations":      ["Manual clinical review required"],
            "human_review_required":True,
            "flags":                ["parse_error"],
            "raw":                  raw,
        }
    except Exception as e:
        log.error("[HealthAgent] analyse failed: %s", e)
        return {
            "tier":                 tier,
            "model":                model,
            "risk_level":           "unknown",
            "confidence":           0.0,
            "summary":              f"Analysis failed: {e}",
            "reasoning":            [],
            "recommendations":      ["Manual clinical review required"],
            "human_review_required":True,
            "flags":                ["inference_error"],
            "raw":                  "",
        }


# ── NATS subscriber ──────────────────────────────────────────────────────────

async def run_agent():
    """Subscribe to NATS and process health analysis requests."""
    log.info("[HealthAgent] Connecting to NATS at %s", NATS_URL)
    nc = await nats.connect(NATS_URL)

    async def handler(msg):
        try:
            payload = json.loads(msg.data.decode())
            result  = await analyse(payload)
            if msg.reply:
                await nc.publish(msg.reply, json.dumps(result).encode())
        except Exception as e:
            log.error("[HealthAgent] NATS handler error: %s", e)
            if msg.reply:
                await nc.publish(msg.reply, json.dumps({
                    "error": str(e),
                    "human_review_required": True
                }).encode())

    await nc.subscribe(AGENT_SUBJECT, cb=handler)
    log.info("[HealthAgent] Subscribed to %s", AGENT_SUBJECT)

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await nc.drain()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_agent())
