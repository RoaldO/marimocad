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
