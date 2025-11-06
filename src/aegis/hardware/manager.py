from typing import Optional

from aegis.utils.logger import setup_logger
from .models import HardwareState, GPUStatus, IntelComputeStatus, SystemStatus
from .monitors.nvidia_monitor import NvidiaGpuMonitor
from .monitors.system_monitor import SystemMonitor
from .monitors.intel_monitor import IntelComputeMonitor


class HardwareManager:
    """
    A façade class that provides a unified interface to all hardware monitors.
    It orchestrates data collection from individual monitors and composes
    it into a single, comprehensive HardwareState object.
    """

    def __init__(self) -> None:
        self.logger = setup_logger('HardwareManager')
        self.logger.info("Initializing HardwareManager and its monitors...")
        self.gpu_monitor: NvidiaGpuMonitor = NvidiaGpuMonitor()
        self.system_monitor: SystemMonitor = SystemMonitor()
        self.intel_monitor: IntelComputeMonitor = IntelComputeMonitor()
        self.logger.info("HardwareManager initialized.")

    def get_hardware_state(self) -> HardwareState:
        """
        Queries all underlying hardware monitors and returns a composite
        state of the entire system.
        """
        self.logger.debug("Fetching full hardware state...")

        gpu_state: Optional[GPUStatus] = self.gpu_monitor.get_status()
        system_state: SystemStatus = self.system_monitor.get_status()
        intel_state: Optional[IntelComputeStatus] = self.intel_monitor.get_status()

        hardware_state = HardwareState(
            gpu=gpu_state,
            system=system_state,
            intel_devices=intel_state,
        )
        self.logger.debug("Hardware state compiled.")
        return hardware_state
