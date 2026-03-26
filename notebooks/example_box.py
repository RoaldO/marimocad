import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import marimo_cad as cad
    from build123d import Box, Cylinder, fillet, Axis

    return Axis, Box, cad, fillet, mo


@app.cell
def _(mo):
    width  = mo.ui.slider(5, 100, value=40, step=1, label="Width")
    depth  = mo.ui.slider(5, 100, value=30, step=1, label="Depth")
    height = mo.ui.slider(5, 100, value=20, step=1, label="Height")
    radius = mo.ui.slider(0, 10,  value=3,  step=1, label="Fillet radius")
    mo.vstack([width, depth, height, radius])
    return depth, height, radius, width


@app.cell
def _(Axis, Box, cad, depth, fillet, height, radius, width):
    box = Box(width.value, depth.value, height.value)
    if radius.value > 0:
        box = fillet(box.edges().filter_by(Axis.Z), radius.value)
    viewer = cad.Viewer()
    viewer.render(box)
    viewer
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
