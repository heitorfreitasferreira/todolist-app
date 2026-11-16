FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY logging_json.py .
COPY gunicorn.conf.py .
COPY assets/ ./assets/

# Nao rodar como root: gunicorn na 5000 nao precisa de privilegio.
RUN useradd -r -u 10001 app && chown -R app:app /app
USER 10001

EXPOSE 5000
# `opentelemetry-instrument` liga a auto-instrumentacao (Flask + SQLAlchemy) e
# sobe o gunicorn. O export OTLP e configurado por env (OTEL_*).
CMD ["opentelemetry-instrument", "gunicorn", "-c", "gunicorn.conf.py", "app:app"]
