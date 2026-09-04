# MarimoCAD Starter Notebook — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Patch the MarimoCAD Docker image so that creating a new notebook pre-fills it with build123d imports and an interactive box example instead of a blank file.

**Architecture:** A Python patch script (`notebooks/patch_marimo.py`) is copied into the image and run at build time via `RUN python3 ...` in the Dockerfile. It replaces the new-notebook branch in marimo's `os_file_system.py` to read from a template file (`/usr/local/share/marimocad/template.py`) instead of generating an empty app. The template file is `notebooks/example_box.py` copied into the image. The patch fails loudly if the target string is not found, so marimo upgrades that change the file are caught at build time.

**Tech Stack:** Docker, Python 3, marimo internals (`_server/files/os_file_system.py`), GitHub Actions (build/push)

---

### Task 1: Write the patch script

**Files:**
- Create: `notebooks/patch_marimo.py`

- [ ] **Step 1: Verify the exact target string in the running container**

```bash
kubectl exec -n default $(kubectl get pod -l app=marimocad -o name) -- \
  sed -n '155,172p' /usr/local/lib/python3.13/site-packages/marimo/_server/files/os_file_system.py
```

Expected output (confirm it matches exactly before writing the patch):
```
        elif file_type == "notebook" and not contents:
            from marimo._convert.converters import MarimoConvert

            full_path.parent.mkdir(parents=True, exist_ok=True)
            # Create a new AppFileManager to get the default notebook code
            # We pass None as filename to get the empty notebook template
            ir = AppFileManager(None).app.to_ir()
            converter = MarimoConvert.from_ir(ir)
            if full_path.suffix in (".md", ".qmd"):
                notebook_code = converter.to_markdown(full_path.name)
            else:
                notebook_code = converter.to_py()
            full_path.write_text(notebook_code, encoding="utf-8")
            contents = notebook_code.encode("utf-8")
```

- [ ] **Step 2: Create `notebooks/patch_marimo.py`**

```python
import sys
from pathlib import Path

TARGET = Path(
    "/usr/local/lib/python3.13/site-packages/marimo/_server/files/os_file_system.py"
)

OLD = '''\
        elif file_type == "notebook" and not contents:
            from marimo._convert.converters import MarimoConvert

            full_path.parent.mkdir(parents=True, exist_ok=True)
            # Create a new AppFileManager to get the default notebook code
            # We pass None as filename to get the empty notebook template
            ir = AppFileManager(None).app.to_ir()
            converter = MarimoConvert.from_ir(ir)
            if full_path.suffix in (".md", ".qmd"):
                notebook_code = converter.to_markdown(full_path.name)
            else:
                notebook_code = converter.to_py()
            full_path.write_text(notebook_code, encoding="utf-8")
            contents = notebook_code.encode("utf-8")'''

NEW = '''\
        elif file_type == "notebook" and not contents:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            _template = Path("/usr/local/share/marimocad/template.py")
            if _template.exists() and full_path.suffix not in (".md", ".qmd"):
                notebook_code = _template.read_text(encoding="utf-8")
            else:
                from marimo._convert.converters import MarimoConvert
                ir = AppFileManager(None).app.to_ir()
                converter = MarimoConvert.from_ir(ir)
                if full_path.suffix in (".md", ".qmd"):
                    notebook_code = converter.to_markdown(full_path.name)
                else:
                    notebook_code = converter.to_py()
            full_path.write_text(notebook_code, encoding="utf-8")
            contents = notebook_code.encode("utf-8")'''


def main() -> None:
    source = TARGET.read_text(encoding="utf-8")
    if OLD not in source:
        print(
            "ERROR: patch target not found in os_file_system.py — "
            "marimo may have been upgraded and the file changed. "
            "Review the new version and update patch_marimo.py.",
            file=sys.stderr,
        )
        sys.exit(1)
    patched = source.replace(OLD, NEW, 1)
    TARGET.write_text(patched, encoding="utf-8")
    print("Patched os_file_system.py successfully.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add notebooks/patch_marimo.py
git commit -m "feat: add marimo patch script for starter notebook template"
```

---

### Task 2: Update the Dockerfile

**Files:**
- Modify: `Dockerfile`

Current `Dockerfile`:
```dockerfile
FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad
USER appuser
```

- [ ] **Step 1: Update `Dockerfile`**

```dockerfile
FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad

RUN mkdir -p /usr/local/share/marimocad
COPY notebooks/example_box.py /usr/local/share/marimocad/template.py
COPY notebooks/patch_marimo.py /usr/local/share/marimocad/patch_marimo.py
RUN python3 /usr/local/share/marimocad/patch_marimo.py

USER appuser
```

- [ ] **Step 2: Verify the Dockerfile looks correct**

```bash
cat Dockerfile
```

Expected: all 4 `USER root` block lines present, `patch_marimo.py` run before `USER appuser`.

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat: bake starter notebook template into image, patch marimo on build"
```

---

### Task 3: Push to trigger image build

**Files:** none (GitHub Actions handles the build)

- [ ] **Step 1: Push to main**

```bash
git push origin main
```

- [ ] **Step 2: Watch the Actions run**

Open `https://github.com/RoaldO/marimocad/actions` and confirm the workflow completes successfully.

Expected: green checkmark, image pushed to `ghcr.io/roaldo/marimocad:latest`.

If the run fails with "patch target not found", the marimo version in the base image changed. Go back to Task 1 Step 1, re-verify the exact string in the new version, update `patch_marimo.py`, and push again.

---

### Task 4: Deploy and verify

- [ ] **Step 1: Restart the MarimoCAD pod to pull the new image**

```bash
kubectl rollout restart deployment/marimocad
kubectl rollout status deployment/marimocad
```

Expected: `deployment "marimocad" successfully rolled out`

- [ ] **Step 2: Open MarimoCAD**

Go to `http://192.168.100.120:30881`

- [ ] **Step 3: Create a new notebook**

In the file browser, click **New File** → choose notebook type → give it any name (e.g. `test.py`).

- [ ] **Step 4: Verify the template loaded**

Expected: the new notebook opens with:
- Four sliders (Width, Depth, Height, Fillet radius)
- A 3D box rendered in the viewer on the right column

If it opens blank, the patch did not take effect — check the pod logs:
```bash
kubectl logs -n default $(kubectl get pod -l app=marimocad -o name)
```

- [ ] **Step 5: Update the install guide**

In `/home/roald/Projects/kubernetes-proxmox-install.md`, mark the starter notebook task as done:

```
- [x] marimocad starter notebook — example_box.py baked into image as template;
  patch_marimo.py patches os_file_system.py at build time so new notebooks
  start with build123d imports and interactive box instead of blank file
```
