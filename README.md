# marimocad

A build123d CAD environment powered by [marimo](https://marimo.io).

## Goal

marimocad combines the parametric 3D modeling capabilities of [build123d](https://github.com/gumyr/build123d) with the reactive notebook experience of marimo. The result is an interactive CAD environment where changing a parameter instantly updates the 3D model, all within a reproducible, version-controlled notebook.

## Why marimo?

Unlike Jupyter, marimo notebooks are pure Python files that run as reactive scripts — every cell re-executes automatically when its dependencies change. This makes it a natural fit for parametric CAD: tweak a dimension, see the model update live.

## Features (planned)

- Reactive build123d model editing in a marimo notebook
- Live 3D preview via marimo's UI components
- Export to STEP, STL, and other CAD formats
- Clean, git-friendly `.py` notebook files
