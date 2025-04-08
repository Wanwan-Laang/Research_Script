
# visualize_cascade_core.ovito.py
# Use OVITO Python API to visualize cascade core from a LAMMPS dump
# 用 OVITO API 標出 cascade core 區域並渲染圖片
from ovito.io import import_file
from ovito.modifiers import DisplacementVectorModifier, ColorCodingModifier
from ovito.vis import Viewport

# Load LAMMPS dump file
pipeline = import_file("dump.PKA.final")

# Add displacement vector modifier (from initial frame)
pipeline.modifiers.append(DisplacementVectorModifier())

# Add color coding by displacement magnitude
pipeline.modifiers.append(ColorCodingModifier(
    property = "Displacement Magnitude",
    start_value = 0.0,
    end_value = 10.0,
    logarithmic = False,
    color_scheme = ColorCodingModifier.ColorScheme.Jet))

# Render interactive view
vp = Viewport()
vp.type = Viewport.Type.Perspective
vp.camera_pos = (200, 200, 200)
vp.fov = 60.0
vp.render_image(filename="cascade_core.png", size=(800,600), background=(1,1,1), frame=0)

