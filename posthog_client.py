"""Shared PostHog client for Weather Station scripts."""

import atexit
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from posthog import Posthog

logger = logging.getLogger(__name__)

load_dotenv()


def _is_production() -> bool:
    """Return whether this process is running in production."""
    environment = os.getenv("POSTHOG_ENVIRONMENT", os.getenv("ENVIRONMENT", ""))
    return environment.lower() == "production"


def _warn_missing_configuration(variable_name: str) -> None:
    """Warn in non-production when analytics cannot be initialized."""
    if not _is_production():
        logger.warning(
            "%s variable required by PostHog is missing or un-configured, "
            "this causes events to be silently missed. This error stops "
            "appearing once %s is configured",
            variable_name,
            variable_name,
        )


def _initialize_posthog() -> Optional[Posthog]:
    """Create the process-wide client when PostHog is configured."""
    project_token = os.getenv("POSTHOG_PROJECT_TOKEN")
    host = os.getenv("POSTHOG_HOST")

    if not project_token:
        _warn_missing_configuration("POSTHOG_PROJECT_TOKEN")
        return None

    if not host:
        _warn_missing_configuration("POSTHOG_HOST")
        return None

    try:
        return Posthog(
            project_token,
            host=host,
            enable_exception_autocapture=True,
        )
    except Exception:
        if not _is_production():
            logger.warning("PostHog could not be initialized; analytics are disabled")
        return None


posthog_client = _initialize_posthog()

if posthog_client:
    atexit.register(posthog_client.shutdown)
