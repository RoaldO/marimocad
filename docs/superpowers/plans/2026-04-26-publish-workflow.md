# Publish Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a GitHub Actions workflow that builds the marimocad Docker image and pushes it to GHCR on every push to `main`, tagged as both `latest` and a short git SHA.

**Architecture:** Single workflow file using the standard three-action Docker pattern (login → metadata → build-push). `GITHUB_TOKEN` provides GHCR authentication — no secrets configuration required.

**Tech Stack:** GitHub Actions, `docker/login-action@v3`, `docker/metadata-action@v5`, `docker/build-push-action@v6`

---

### Task 1: Install actionlint

**Files:**
- No files created — tooling only

- [ ] **Step 1: Install actionlint**

```bash
bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
sudo mv actionlint /usr/local/bin/
```

- [ ] **Step 2: Verify installation**

Run: `actionlint --version`
Expected output: `actionlint 1.x.x` (any version printed without error)

---

### Task 2: Create the workflow file

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/publish.yml`**

```yaml
name: Publish Docker image

on:
  push:
    branches:
      - main

permissions:
  contents: read
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/marimocad
          tags: |
            type=raw,value=latest
            type=sha,format=short

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

- [ ] **Step 3: Lint the workflow**

Run: `actionlint .github/workflows/publish.yml`
Expected: no output (exit code 0 means no errors)

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/publish.yml
git commit -m "feat: add GHCR publish workflow"
```

---

### Task 3: Push and verify the workflow runs

**Files:**
- No new files

- [ ] **Step 1: Push to main**

```bash
git push origin main
```

- [ ] **Step 2: Watch the workflow run**

Open: `https://github.com/RoaldO/marimocad/actions`

Expected: a workflow run named "Publish Docker image" appears and completes with a green checkmark.

- [ ] **Step 3: Verify the image appears in GHCR**

Open: `https://github.com/RoaldO/marimocad/pkgs/container/marimocad`

Expected: package page shows two tags — `latest` and `sha-<7-char-sha>` (e.g. `sha-d878a7f`).

---

### Task 4: Make the package public (manual)

**Files:**
- No files

- [ ] **Step 1: Open package settings**

Navigate to: `https://github.com/RoaldO/marimocad/pkgs/container/marimocad`

Click **Package settings** (bottom-right of the page).

- [ ] **Step 2: Change visibility to public**

Scroll to **Danger Zone** → **Change visibility** → select **Public** → confirm.

Expected: the package page no longer shows a lock icon; `docker pull ghcr.io/roaldo/marimocad:latest` works without authentication.
