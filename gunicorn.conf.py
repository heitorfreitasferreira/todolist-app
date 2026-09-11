# ABOUTME: Config do gunicorn: access log e error log em JSON no stdout.
# ABOUTME: Formato identico ao da app (logging_json.JsonFormatter) p/ Loki.
import logging
import sys

from gunicorn.glogging import Logger

from logging_json import JsonFormatter

bind = "0.0.0.0:5000"
workers = 2
threads = 4

accesslog = "-"
errorlog = "-"
loglevel = "info"

# JSON sempre valido: todo atom entre aspas (podem vir '-' quando ausentes).
access_log_format = (
    '{"time":"%(t)s","level":"info","logger":"gunicorn.access",'
    '"remote":"%(h)s","method":"%(m)s","path":"%(U)s","query":"%(q)s",'
    '"status":"%(s)s","bytes":"%(b)s","duration_us":"%(D)s"}'
)


class JsonGunicornLogger(Logger):
    """Reaplica o formatter JSON no handler de erro do gunicorn."""

    def setup(self, cfg):
        super().setup(cfg)
        self._set_handler(self.error_log, cfg.errorlog, JsonFormatter())


logger_class = JsonGunicornLogger
