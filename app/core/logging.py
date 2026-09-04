import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level.upper(),
        stream=sys.stdout,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )

    # Reduce noisy logs in local development
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
