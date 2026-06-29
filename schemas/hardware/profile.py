from dataclasses import dataclass


@dataclass
class HardwareProfile:

    cpu: str
    gpu: str
    ram_gb: int
    battery_percent: float
    battery_health: float
    thermal_limit: float
    supports_gpu: bool
    supports_npu: bool
