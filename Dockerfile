FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad

RUN mkdir -p /usr/local/share/marimocad
COPY notebooks/example_box.py /usr/local/share/marimocad/template.py
COPY notebooks/patch_marimo.py /usr/local/share/marimocad/patch_marimo.py
RUN python3 /usr/local/share/marimocad/patch_marimo.py

USER appuser
