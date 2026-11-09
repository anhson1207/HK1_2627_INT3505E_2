# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r app && useradd -r -g app -d /app app
COPY --from=builder /install /usr/local
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app wsgi.py gunicorn.conf.py entrypoint.sh ./
ENV PYTHONUNBUFFERED=1
USER app
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
 CMD python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:5000/healthz", timeout=3)' || exit 1
ENTRYPOINT ["/app/entrypoint.sh"]
