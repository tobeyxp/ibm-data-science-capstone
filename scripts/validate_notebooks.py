"""Validate committed notebook structure without re-running external data calls."""

from pathlib import Path

import nbformat


def main() -> None:
    notebooks = sorted(Path("notebooks").glob("*.ipynb"))
    if len(notebooks) != 7:
        raise SystemExit(f"Expected 7 notebooks, found {len(notebooks)}")

    failures: list[str] = []
    for path in notebooks:
        try:
            notebook = nbformat.read(path, as_version=4)
            # Skills Network exports include harmless extra fields such as an
            # empty `outputs` array on Markdown cells. Validate the canonical
            # notebook structure while allowing those forward-compatible extras.
            nbformat.validate(notebook, relax_add_props=True)
        except Exception as error:  # validation errors carry the useful detail
            failures.append(f"{path}: invalid notebook: {error}")
            continue

        for index, cell in enumerate(notebook.cells, start=1):
            if cell.cell_type != "code":
                continue
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    failures.append(
                        f"{path}: cell {index} contains committed error output "
                        f"{output.get('ename', 'unknown')}"
                    )

    if failures:
        raise SystemExit("\n".join(failures))

    print(f"Validated {len(notebooks)} notebooks; no error outputs found.")


if __name__ == "__main__":
    main()
