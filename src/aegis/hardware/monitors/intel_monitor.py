from __future__ import annotations

from typing import Any, Iterable, Optional

from aegis.hardware.models import IntelComputeStatus
from aegis.utils.logger import setup_logger


class IntelComputeMonitor:
    """Discovers available Intel compute devices using the OpenVINO runtime."""

    def __init__(self) -> None:
        self.logger = setup_logger('IntelComputeMonitor', module_code='HW', script_code='INTL')
        self.core: Optional[Any] = None

        try:
            from openvino.runtime import Core  # type: ignore[import-not-found]

            self.core = Core()
            self.logger.info("OpenVINO runtime initialized successfully.")
        except ImportError:
            self.logger.warning(
                "OpenVINO library not found. Intel device monitoring will be disabled."
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.error(
                "Error initializing OpenVINO Core: %s",
                exc,
                extra={'error_code': 'OV-INIT-FAIL'}
            )

    def get_status(self) -> IntelComputeStatus | None:
        """Retrieve the list of available Intel compute devices."""
        if not self.core:
            return None

        self.logger.debug("Querying for available Intel devices...")
        devices_raw: Iterable[Any] = getattr(self.core, "available_devices", [])
        devices = [str(device) for device in devices_raw]
        self.logger.info("Discovered Intel devices: %s", devices)
        return IntelComputeStatus(available_devices=devices)
