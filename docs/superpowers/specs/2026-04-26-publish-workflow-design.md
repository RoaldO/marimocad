# Publish Workflow Design

**Date:** 2026-04-26  
**Status:** Approved

## Goal

Build the `marimocad` Docker image on every push to `main` and publish it to GHCR so it can be pulled by a Kubernetes cluster.

## Trigger

`push` to `main` branch only.

## Permissions

```yaml
permissions:
  contents: read
  packages: write
```

`GITHUB_TOKEN` is used for both checkout and GHCR login — no extra secrets required.

## Image

- Registry: `ghcr.io`
- Image: `ghcr.io/${{ github.repository_owner }}/marimocad` (GHCR normalizes to lowercase)
- Tags on every push:
  - `latest`
  - Short git SHA (7 characters, e.g. `b330458`)

## Job: `build-and-push`

Runs on `ubuntu-latest`. Steps in order:

| Step | Action | Purpose |
|------|--------|---------|
| 1 | `actions/checkout@v4` | Fetch repo contents |
| 2 | `docker/login-action@v3` | Authenticate to `ghcr.io` with `GITHUB_TOKEN` |
| 3 | `docker/metadata-action@v5` | Generate `latest` + short-SHA tags and OCI labels |
| 4 | `docker/build-push-action@v6` | Build from repo-root `Dockerfile`, push with metadata output |

## Build

- Source: `Dockerfile` in repo root
- No layer caching (builds are infrequent)
- Platform: `linux/amd64` (default, no multi-arch)

## Out of scope

- Kubernetes deployment YAML
- Versioned / semver releases
- Multi-arch builds
- Build caching

## Post-deploy manual step

After the first successful push, set package visibility to **public** in GitHub:  
Settings → Packages → marimocad → Package settings → Change visibility → Public
