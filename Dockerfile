FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad
USER appuser
