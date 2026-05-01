#!/usr/bin/env python3
"""schemas/health.py — Byngox Message Schemas"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import time

@dataclass
class RawHealthEvent:
    source:      str
    patient_ref: str
    data_type:   str
    payload:     Dict[str, Any] = field(default_factory=dict)
    timestamp:   float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class NormalizedEvent:
    patient_ref:  str
    data_type:    str
    unit:         str
    value:        Any
    normal_range: Optional[str] = None
    icd_code:     Optional[str] = None
    source:       str = ""
    timestamp:    float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class TwinState:
    patient_ref:  str
    vitals:       Dict[str, Any] = field(default_factory=dict)
    conditions:   List[str]      = field(default_factory=list)
    medications:  List[str]      = field(default_factory=list)
    risk_score:   float = 0.0
    baseline_set: bool  = False
    last_updated: float = field(default_factory=time.time)
    timestamp:    float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class HealthInsight:
    patient_ref:  str
    insight_type: str
    severity:     str
    description:  str
    confidence:   float = 0.0
    evidence:     List[str] = field(default_factory=list)
    timestamp:    float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class HealthRecommendation:
    patient_ref:    str
    category:       str
    recommendation: str
    priority:       str = "medium"
    rationale:      str = ""
    expires_at:     Optional[float] = None
    timestamp:      float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)

@dataclass
class HealthAction:
    patient_ref:  str
    action_type:  str
    target:       str
    message:      str
    urgency:      str  = "normal"
    completed:    bool = False
    timestamp:    float = field(default_factory=time.time)
    def to_dict(self): return asdict(self)
