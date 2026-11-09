"""Dedicated OpenTelemetry log export for Weather Station sensor operations."""

import atexit
import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

posthog_log_logger = logging.getLogger("weather_station.posthog")
posthog_log_logger.setLevel(logging.INFO)
posthog_log_logger.propagate = False


def _is_production() -> bool:
    """Return whether this process is running in production."""
    environment = os.getenv("POSTHOG_ENVIRONMENT", os.getenv("ENVIRONMENT", ""))
    return environment.lower() == "production"


def _warn_missing_configuration(variable_name: str) -> None:
    """Warn in non-production when log export cannot be initialized."""
    if not _is_production():
        logging.getLogger(__name__).warning(
            "%s variable required by PostHog is missing or un-configured, "
            "this causes events to be silently missed. This error stops "
            "appearing once %s is configured",
            variable_name,
            variable_name,
        )


def _initialize_log_exporter() -> Optional[object]:
    """Configure an OTLP exporter only for this module's dedicated logger."""
    project_token = os.getenv("POSTHOG_PROJECT_TOKEN")
    host = os.getenv("POSTHOG_HOST")

    if not project_token:
        _warn_missing_configuration("POSTHOG_PROJECT_TOKEN")
        return None
    if not host:
        _warn_missing_configuration("POSTHOG_HOST")
        return None

    try:
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    except ImportError:
        if not _is_production():
            logging.getLogger(__name__).warning(
                "PostHog log capture dependencies are not installed; "
                "sensor operation logs will not be exported"
            )
        return None

    try:
        logger_provider = LoggerProvider()
        exporter = OTLPLogExporter(
            endpoint=f"{host.rstrip('/')}/i/v1/logs",
            headers={"Authorization": f"Bearer {project_token}"},
        )
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        posthog_log_logger.addHandler(LoggingHandler(logger_provider=logger_provider))
        return logger_provider
    except Exception:
        if not _is_production():
            logging.getLogger(__name__).warning(
                "PostHog log export could not be initialized; log capture is disabled"
            )
        return None


_posthog_log_provider = _initialize_log_exporter()

if _posthog_log_provider:
    atexit.register(_posthog_log_provider.shutdown)


def log_sensor_reading_completed(interface: str, i2c_address: int) -> None:
    """Export a best-effort structured log after a successful sensor read."""
    try:
        posthog_log_logger.info(
            "sensor_reading_completed",
            extra={
                "sensor_model": "bme280",
                "i2c_address": i2c_address,
                "interface": interface,
            },
        )
    except Exception:
        pass
