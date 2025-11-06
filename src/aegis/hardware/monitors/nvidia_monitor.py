import pynvml
from aegis.hardware.models import GPUStatus
from aegis.utils.logger import setup_logger


class NvidiaGpuMonitor:
    """Monitors an NVIDIA GPU using the pynvml library."""

    def __init__(self, device_index: int = 0):
        self.logger = setup_logger(f'NvidiaGpuMonitor_Device{device_index}')
        self.handle = None
        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
            gpu_name = self._decode_name(pynvml.nvmlDeviceGetName(self.handle))
            self.logger.info(f"Successfully initialized monitor for GPU: {gpu_name}")
        except pynvml.NVMLError as e:
            self.logger.warning(f"Could not initialize NVML or find GPU at index {device_index}. GPU monitoring will be disabled. Error: {e}")

    def get_status(self) -> GPUStatus | None:
        """
        Retrieves the current status of the NVIDIA GPU.

        Returns:
            GPUStatus | None: A Pydantic model with the GPU's state, or None if initialization failed.
        """
        if not self.handle:
            return None

        try:
            self.logger.debug("Fetching NVIDIA GPU status.")
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self.handle)

            bytes_to_gb = 1024 ** 3

            status = GPUStatus(
                name=self._decode_name(pynvml.nvmlDeviceGetName(self.handle)),
                vram_total_gb=round(memory_info.total / bytes_to_gb, 2),
                vram_used_gb=round(memory_info.used / bytes_to_gb, 2),
                utilization_percent=float(utilization.gpu)
            )
            self.logger.debug("Successfully fetched NVIDIA GPU status.")
            return status
        except pynvml.NVMLError as e:
            self.logger.error(f"Failed to get GPU status: {e}")
            return None

    def __del__(self):
        """Ensures nvmlShutdown is called when the object is destroyed."""
        try:
            if self.handle:
                pynvml.nvmlShutdown()
                self.logger.info("NVML shutdown successful.")
                self.handle = None
        except pynvml.NVMLError:
            pass

    @staticmethod
    def _decode_name(raw_name: bytes | str) -> str:
        """Decode raw GPU name bytes into a human-readable string."""
        if isinstance(raw_name, bytes):
            return raw_name.decode('utf-8', errors='replace')
        return raw_name
