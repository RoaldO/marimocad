# Deploying marimocad

Runs on the homelab Kubernetes cluster. Image `ghcr.io/roaldo/marimocad:latest`
(built + pushed by `.github/workflows/publish.yml`).

## Apply

    kubectl apply -f k8s/marimocad.yml

Creates:

- `marimocad` Deployment + NodePort Service on **30881**
- 1Gi Longhorn PVC `marimocad-notebooks` mounted at `/home/user/notebooks` — notebooks
  survive pod restarts and image upgrades (`workingDir` is set to the same path so
  marimo serves notebooks from there)

## Cluster context

This manifest is listed as an *external manifest* in `~/Projects/homelab/k8s/README.md`
(the single view of everything deployed on the cluster). Deployment-design history and
a future PVC→Seafile notebook-sync idea live under `~/Projects/homelab/docs/`.
