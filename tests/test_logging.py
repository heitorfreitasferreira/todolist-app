# ABOUTME: Testes do formatter JSON: campos base e correlacao com trace OTel.
# ABOUTME: Garante que o trace_id aparece no log so quando ha um span ativo.
import json
import logging

from logging_json import JsonFormatter


def _record(message='ola'):
    return logging.LogRecord(
        name='todolist', level=logging.INFO, pathname=__file__, lineno=1,
        msg=message, args=(), exc_info=None)


def test_formatter_campos_base():
    payload = json.loads(JsonFormatter().format(_record()))
    assert payload['level'] == 'info'
    assert payload['logger'] == 'todolist'
    assert payload['message'] == 'ola'
    assert 'trace_id' not in payload


def test_formatter_inclui_trace_id_com_span_ativo():
    from opentelemetry.sdk.trace import TracerProvider

    tracer = TracerProvider().get_tracer('test')
    with tracer.start_as_current_span('operacao'):
        payload = json.loads(JsonFormatter().format(_record()))

    assert len(payload['trace_id']) == 32
    assert len(payload['span_id']) == 16
