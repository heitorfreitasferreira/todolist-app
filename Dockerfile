FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

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
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
