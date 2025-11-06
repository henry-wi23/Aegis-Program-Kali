from pydantic import BaseModel, Field
from typing import List, Optional


class GPUStatus(BaseModel):
    """Represents the status of a single GPU."""

    name: str = Field(..., description="The official name of the GPU model.")
    vram_total_gb: float = Field(..., description="Total dedicated VRAM in gigabytes.")
    vram_used_gb: float = Field(..., description="Used dedicated VRAM in gigabytes.")
    utilization_percent: float = Field(..., description="Current GPU core utilization percentage.")


class SystemStatus(BaseModel):
    """Represents the status of core system resources (CPU and RAM)."""

    cpu_brand: str = Field(..., description="The brand name of the CPU.")
    cpu_arch: str = Field(..., description="The architecture of the CPU.")
    cpu_cores_physical: int = Field(..., description="Number of physical CPU cores.")
    cpu_cores_logical: int = Field(..., description="Number of logical CPU cores (threads).")
    cpu_utilization_per_core: List[float] = Field(..., description="A list of utilization percentages, one for each logical CPU core.")
    ram_total_gb: float = Field(..., description="Total physical system RAM in gigabytes.")
    ram_available_gb: float = Field(..., description="Available system RAM in gigabytes.")


class IntelComputeStatus(BaseModel):
    """Lists the available Intel compute devices discovered by OpenVINO."""

    available_devices: List[str] = Field(
        ...,
        description="List of device identifiers (e.g., 'CPU', 'GPU', 'NPU').",
    )


class HardwareState(BaseModel):
    """A composite model that provides a complete snapshot of the system's hardware state. This is the primary data contract for the entire Hardware Abstraction Layer."""

    gpu: Optional[GPUStatus] = Field(None, description="Status of the primary dedicated GPU.")
    system: SystemStatus = Field(..., description="Status of the core system CPU and RAM.")
    intel_devices: Optional[IntelComputeStatus] = Field(
        None,
        description="Status of available Intel compute devices (iGPU, NPU).",
    )
