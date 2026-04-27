"""
Build-time patch: replaces marimo's new-notebook stubs in two files to load
from /usr/local/share/marimocad/template.py instead of a blank app.
Run once by the Dockerfile: RUN python3 /usr/local/share/marimocad/patch_marimo.py
"""
import sys
import sysconfig
from pathlib import Path

_SITE = Path(sysconfig.get_path("purelib"))

# ── Patch 1: file-browser "Add notebook" ──────────────────────────────────────

TARGET_FS = _SITE / "marimo/_server/files/os_file_system.py"

OLD_FS = '''\
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

NEW_FS = '''\
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

# ── Patch 2: landing-page "Create a new notebook" ─────────────────────────────

TARGET_FM = _SITE / "marimo/_session/notebook/file_manager.py"

OLD_FM = '''\
        if app is None:
            # Create new empty app with defaults
            kwargs: dict[str, Any] = default.asdict()

            # Add custom defaults if provided
            if self._defaults.width is not None:
                kwargs["width"] = self._defaults.width
            if self._defaults.auto_download is not None:
                kwargs["auto_download"] = self._defaults.auto_download
            if self._defaults.sql_output is not None:
                kwargs["sql_output"] = self._defaults.sql_output

            empty_app = InternalApp(App(**kwargs))
            empty_app.cell_manager.register_cell(
                cell_id=None,
                code="",
                config=CellConfig(),
            )
            return empty_app'''

NEW_FM = '''\
        if app is None:
            _template = Path("/usr/local/share/marimocad/template.py")
            if path is None and _template.exists():
                app = load.load_app(str(_template))
            if app is None:
                # Create new empty app with defaults
                kwargs: dict[str, Any] = default.asdict()

                # Add custom defaults if provided
                if self._defaults.width is not None:
                    kwargs["width"] = self._defaults.width
                if self._defaults.auto_download is not None:
                    kwargs["auto_download"] = self._defaults.auto_download
                if self._defaults.sql_output is not None:
                    kwargs["sql_output"] = self._defaults.sql_output

                empty_app = InternalApp(App(**kwargs))
                empty_app.cell_manager.register_cell(
                    cell_id=None,
                    code="",
                    config=CellConfig(),
                )
                return empty_app'''


# ── Generic patcher ────────────────────────────────────────────────────────────

def _patch(target: Path, old: str, new: str, label: str) -> None:
    source = target.read_text(encoding="utf-8")
    if new in source:
        print(f"{label}: already patched; nothing to do.")
        return
    if old not in source:
        print(
            f"ERROR: patch target not found in {target.name} — "
            "marimo may have been upgraded and the file changed. "
            f"Review the new version and update patch_marimo.py ({label}).",
            file=sys.stderr,
        )
        sys.exit(1)
    target.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"{label}: patched successfully.")


def main() -> None:
    _patch(TARGET_FS, OLD_FS, NEW_FS, "os_file_system.py")
    _patch(TARGET_FM, OLD_FM, NEW_FM, "file_manager.py")


if __name__ == "__main__":
    main()
