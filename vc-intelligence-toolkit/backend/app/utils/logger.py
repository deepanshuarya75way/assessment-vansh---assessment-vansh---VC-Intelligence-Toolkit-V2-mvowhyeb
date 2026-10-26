import logging

from rich.logging import RichHandler

from app.core.config import settings


def _configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
        force=True,
    )


_configure_logging()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
