# ABOUTME: Formatter JSON compartilhado pela app Flask e pelos logs do gunicorn.
# ABOUTME: Campos normalizados (time, level, logger, message) p/ query no Loki.
import json
import logging
from datetime import datetime, timezone

# Campos que o logging ja injeta no record e nao devem virar campos do JSON.
_RESERVED = {
    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
    'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
    'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
    'processName', 'process', 'taskName', 'message', 'asctime',
}


class JsonFormatter(logging.Formatter):
    """Uma linha JSON por log: time (ISO-8601), level (minisculo), logger, message.

    Campos extras passados via `extra=` sao incluidos (ex.: request_id).
    """

    def format(self, record):
        payload = {
            'time': datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec='milliseconds'),
            'level': record.levelname.lower(),
            'logger': record.name,
            'message': record.getMessage(),
        }
        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith('_'):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False, default=str)
