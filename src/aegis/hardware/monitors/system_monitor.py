import cpuinfo
import psutil
from typing import List
from aegis.hardware.models import SystemStatus
from aegis.utils.logger import setup_logger


class SystemMonitor:
    """Monitors core system resources like CPU and RAM using psutil and py-cpuinfo."""

    def __init__(self):
        self.logger = setup_logger('SystemMonitor')
        self.info = cpuinfo.get_cpu_info()
        self.logger.info("SystemMonitor initialized.")

    def get_status(self) -> SystemStatus:
        """
        Retrieves the current status of the CPU and RAM.

        Returns:
            SystemStatus: A Pydantic model instance with the system's state.
        """
        self.logger.debug("Fetching CPU and RAM status.")

        cpu_util_per_core = psutil.cpu_percent(interval=0.5, percpu=True)
        mem_info = psutil.virtual_memory()

        bytes_to_gb = 1024 ** 3
        ram_total_gb = mem_info.total / bytes_to_gb
        ram_available_gb = mem_info.available / bytes_to_gb

        cpu_cores_physical = psutil.cpu_count(logical=False) or 0
        cpu_cores_logical = psutil.cpu_count(logical=True) or 0
        cpu_utilization: List[float] = [float(p) for p in cpu_util_per_core]

        status = SystemStatus(
            cpu_brand=self.info.get('brand_raw', 'N/A'),
            cpu_arch=self.info.get('arch_string_raw', 'N/A'),
            cpu_cores_physical=cpu_cores_physical,
            cpu_cores_logical=cpu_cores_logical,
            cpu_utilization_per_core=cpu_utilization,
            ram_total_gb=round(ram_total_gb, 2),
            ram_available_gb=round(ram_available_gb, 2)
        )
        self.logger.debug("Successfully fetched CPU and RAM status.")
        return status
