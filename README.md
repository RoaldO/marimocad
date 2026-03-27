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

## Getting started

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### Build and start

```bash
git clone https://github.com/RoaldO/marimocad.git
cd marimocad
docker compose up --build
```

On subsequent starts the image is already built, so `--build` can be omitted:

```bash
docker compose up
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

## Managing design projects

The `notebooks/` folder is mounted into the container as the working directory. It is intentionally excluded from this repository (except for the example file) so that your personal designs don't end up in the marimocad repo.

The recommended workflow is to give each design project its own git repository and clone it into `notebooks/`:

```bash
cd notebooks/
git clone https://github.com/you/my-project.git
```

The result looks like this:

```
marimocad/
  notebooks/
    example_box.py        ← tracked by marimocad
    my-project/           ← ignored by marimocad, has its own git repo
      bracket.py
      enclosure.py
```

Each project folder is a self-contained git repository. You commit, branch, and push from within that folder, completely independent of marimocad. marimocad itself only provides the environment.

To start a new design project from scratch:

```bash
cd notebooks/
mkdir my-project && cd my-project
git init
```
