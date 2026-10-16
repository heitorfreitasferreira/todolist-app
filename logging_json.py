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
    Quando existe um span OTel ativo, inclui trace_id/span_id para o Grafana
    ligar o log ao trace no Tempo (ver datasource do Loki).
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
        trace_id, span_id = _current_trace_ids()
        if trace_id:
            payload['trace_id'] = trace_id
            payload['span_id'] = span_id
        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith('_'):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False, default=str)


def _current_trace_ids():
    """trace_id/span_id (hex) do span OTel ativo, ou (None, None).

    Sem a lib instalada (dev) ou fora de um span, devolve None. Assim o
    formatter continua funcionando sem OTel e o log so ganha os campos quando
    ha um trace para correlacionar.
    """
    try:
        from opentelemetry import trace
    except ImportError:
        return None, None
    span_context = trace.get_current_span().get_span_context()
    if span_context is None or not span_context.is_valid:
        return None, None
    return format(span_context.trace_id, '032x'), format(span_context.span_id, '016x')
