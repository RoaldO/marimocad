# MarimoCAD Starter Notebook — Design

## Goal

When a user creates a new notebook in MarimoCAD, it is pre-filled with build123d imports and an interactive box example — instead of marimo's default empty notebook.

## How Marimo Creates New Notebooks

When the user clicks "New Notebook" in marimo's file browser, the server calls `create_file_or_directory` in `/usr/local/lib/python3.13/site-packages/marimo/_server/files/os_file_system.py`. The relevant branch:

```python
elif file_type == "notebook" and not contents:
    ir = AppFileManager(None).app.to_ir()  # ← creates empty app
    converter = MarimoConvert.from_ir(ir)
    notebook_code = converter.to_py()
    full_path.write_text(notebook_code, encoding="utf-8")
```

`AppFileManager(None)` produces an empty marimo app. We replace this with code that reads from a template file baked into the image.

## Architecture

Two changes to the Docker image:

1. **Template file** — `notebooks/example_box.py` is copied into the image at `/usr/local/share/marimocad/template.py`. This file contains the build123d imports and interactive box with sliders.

2. **Patch to os_file_system.py** — A `RUN` step in the Dockerfile replaces the `AppFileManager(None)` block with code that reads from the template file. Falls back to the original empty-notebook behavior if the template is missing.

## Patched Branch

The patched `elif` block in `os_file_system.py`:

```python
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
    contents = notebook_code.encode("utf-8")
```

## Template Content

`notebooks/example_box.py` (already exists in the repo):
- Imports: `marimo`, `marimo_cad`, `build123d` (`Box`, `Cylinder`, `fillet`, `Axis`)
- UI: four sliders — width, depth, height, fillet radius
- Viewer: renders the filleted box with `cad.Viewer()`
- Layout: two-column (`width="columns"`) — controls left, viewer right

## Dockerfile Changes

```dockerfile
FROM ghcr.io/marimo-team/marimo:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /usr/local/etc/jupyter && uv pip install --no-cache-dir marimo-cad

# Starter notebook template
COPY notebooks/example_box.py /usr/local/share/marimocad/template.py

# Patch os_file_system.py to use template for new notebooks
RUN python3 /usr/local/share/marimocad/patch_marimo.py

USER appuser
```

A separate `patch_marimo.py` script (also copied into the image) performs the string replacement on `os_file_system.py`. Using a script rather than inline `sed` avoids quoting issues and is easier to read and maintain.

## Upgrade Safety

If marimo is upgraded and `os_file_system.py` changes significantly, the patch script will fail loudly (the target string won't be found), which is the correct behavior — it forces a conscious review rather than silently producing a broken image.

## Verification

1. Build and push the image
2. Restart the MarimoCAD pod (`kubectl rollout restart deployment/marimocad`)
3. Open MarimoCAD, click "New Notebook", name it
4. Confirm the new file opens with build123d imports and the box render
