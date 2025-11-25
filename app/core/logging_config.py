
import logging
import sys
import json
from datetime import datetime, timezone
import structlog
from structlog.types import Processor

# Timezone configuration
IST = timezone(datetime.now(timezone.utc).astimezone().utcoffset())

def get_ist_time(_, __, event_dict: dict) -> dict:
    """Add IST timestamp to the event dictionary."""
    event_dict["timestamp_ist"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S.%f")
    return event_dict

def get_utc_time(_, __, event_dict: dict) -> dict:
    """Add UTC timestamp to the event dictionary."""
    event_dict["timestamp_utc"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%fZ")
    return event_dict

def get_source_location(_, __, event_dict: dict) -> dict:
    """Add source location to the event dictionary."""
    frame = getattr(logging.currentframe(), "f_back", None)
    if frame:
        f_back = frame.f_back
        if f_back:
            event_dict["source_location"] = f"{f_back.f_code.co_filename}:{f_back.f_lineno}"
    return event_dict

def uppercase_log_level(_, __, event_dict: dict) -> dict:
    """
    Format the log level to uppercase.
    """
    if "level" in event_dict:
        event_dict["level"] = event_dict["level"].upper()
    return event_dict

def pretty_print_event_dict(_, __, event_dict: dict) -> dict:
    """
    Pretty-print the event dictionary if it's a dict.
    """
    if isinstance(event_dict.get("event"), dict):
        event_dict["event"] = json.dumps(event_dict["event"])
    return event_dict

def combine_callsite_info(_, __, event_dict: dict) -> dict:
    """
    Combine filename and lineno into a single source_location field.
    """
    if "filename" in event_dict and "lineno" in event_dict:
        event_dict["source_location"] = f"{event_dict['filename']}:{event_dict['lineno']}"
        del event_dict["filename"]
        del event_dict["lineno"]
    return event_dict

def configure_logging():
    """
    Configure structured logging for the application.
    """
    # Mute other loggers
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []

    handler = logging.StreamHandler(sys.stdout)
    # Use a stdlib formatter for simple, useful console output.
    # structlog processors (including wrap_for_formatter) will ensure
    # structured events are converted into the record's message so the
    # stdlib formatter can render timestamps and level in the requested format.
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            uppercase_log_level,
            structlog.stdlib.add_log_level_number,
            get_utc_time,
            # get_ist_time,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            combine_callsite_info,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # This processor needs to be last
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

