FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad
USER appuser
