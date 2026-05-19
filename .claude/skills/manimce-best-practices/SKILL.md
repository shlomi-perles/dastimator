---
name: manimce-best-practices
description: |
  Trigger when: (1) User mentions "manim" or "Manim Community" or "ManimCE", (2) Code contains `from manim import *`, (3) User runs `manim` CLI commands, (4) Working with Scene, MathTex, Create(), OpenGLSurface, or ManimCE-specific classes.

  Best practices for Manim Community Edition v0.20.1 - the community-maintained Python animation engine. Covers Scene structure, animations, LaTeX/MathTex, 3D with ThreeDScene, OpenGL rendering, camera control, styling, updaters, configuration, and CLI usage.

  For OpenGL-only 3D scenes, use this as the main ManimCE guide and optionally load `manimgl-best-practices` as the OpenGL 3D companion.
---

## How to use

Target Manim Community Edition v0.20.1 with Python 3.11+. Verify the active executable with `python -m manim --version` when version confusion is possible.

Read individual rule files for detailed explanations and code examples. Prefer `python -m manim ...` in examples unless the bare `manim` executable is known to be on PATH.

### Core Concepts
- [rules/first-scene-tutorial.md](rules/first-scene-tutorial.md) - First scene walkthrough, render commands, and common beginner mistakes
- [rules/scenes.md](rules/scenes.md) - Scene structure, construct method, and scene types
- [rules/mobjects.md](rules/mobjects.md) - Mobject types, VMobject, Groups, and positioning
- [rules/animations.md](rules/animations.md) - Animation classes, playing animations, and timing

### Creation & Transformation
- [rules/creation-animations.md](rules/creation-animations.md) - Create, Write, FadeIn, DrawBorderThenFill
- [rules/transform-animations.md](rules/transform-animations.md) - Transform, ReplacementTransform, morphing
- [rules/animation-groups.md](rules/animation-groups.md) - AnimationGroup, LaggedStart, Succession

### Text & Math
- [rules/equations.md](rules/equations.md) - MathTex splitting, equation transforms, and precise term control
- [rules/equation-derivations.md](rules/equation-derivations.md) - Step-by-step derivation patterns and dim/reveal workflows
- [rules/text.md](rules/text.md) - Text mobjects, fonts, and styling
- [rules/latex.md](rules/latex.md) - MathTex, Tex, LaTeX rendering, and coloring formulas
- [rules/text-animations.md](rules/text-animations.md) - Write, AddTextLetterByLetter, TypeWithCursor

### Styling & Appearance
- [rules/colors.md](rules/colors.md) - Color constants, gradients, and color manipulation
- [rules/decorations.md](rules/decorations.md) - Braces, labels, arrows, highlights, and annotation patterns
- [rules/styling.md](rules/styling.md) - Fill, stroke, opacity, and visual properties

### Positioning & Layout
- [rules/positioning.md](rules/positioning.md) - move_to, next_to, align_to, shift methods
- [rules/grouping.md](rules/grouping.md) - VGroup, Group, arrange, and layout patterns

### Coordinate Systems & Graphing
- [rules/axes.md](rules/axes.md) - Axes, NumberPlane, coordinate systems
- [rules/graphing.md](rules/graphing.md) - Plotting functions, parametric curves
- [rules/matrices-linalg.md](rules/matrices-linalg.md) - Matrix display and linear transformation scenes
- [rules/3d.md](rules/3d.md) - ThreeDScene, 3D axes, surfaces, camera orientation
- [rules/opengl.md](rules/opengl.md) - OpenGL renderer, OpenGLSurface, textured surfaces, surface meshes

### Animation Control
- [rules/timing.md](rules/timing.md) - Rate functions, easing, run_time, lag_ratio
- [rules/updaters.md](rules/updaters.md) - Updaters, ValueTracker, dynamic animations
- [rules/camera.md](rules/camera.md) - MovingCameraScene, zoom, pan, frame manipulation
- [rules/moving-camera.md](rules/moving-camera.md) - MovingCameraScene workflows and camera-frame choreography

### Configuration & CLI
- [rules/cli.md](rules/cli.md) - Command-line interface, rendering options, quality flags
- [rules/config.md](rules/config.md) - Configuration system, manim.cfg, settings
- [rules/troubleshooting.md](rules/troubleshooting.md) - Common errors, silent bugs, and removed API replacements

### Slides and Presentations
- [rules/manim-slides-overview.md](rules/manim-slides-overview.md) - Optional manim-slides classes and slide lifecycle
- [rules/manim-slides-cli.md](rules/manim-slides-cli.md) - manim-slides render/present/convert commands
- [rules/manim-slides-web.md](rules/manim-slides-web.md) - RevealJS/web export guidance

### Shapes & Geometry
- [rules/shapes.md](rules/shapes.md) - Circle, Square, Rectangle, Polygon, and geometric primitives
- [rules/lines.md](rules/lines.md) - Line, Arrow, Vector, DashedLine, and connectors

## References

- [references/api-index.md](references/api-index.md) - Class discovery map for mobjects, animations, OpenGL classes, and constants

## Working Examples

Complete example files demonstrating common patterns:

- [examples/basic_animations.py](examples/basic_animations.py) - Shape creation, text, lagged animations, path movement
- [examples/math_visualization.py](examples/math_visualization.py) - LaTeX equations, color-coded math, derivations
- [examples/updater_patterns.py](examples/updater_patterns.py) - ValueTracker, dynamic animations, physics simulations
- [examples/graph_plotting.py](examples/graph_plotting.py) - Axes, functions, areas, Riemann sums, polar plots
- [examples/3d_visualization.py](examples/3d_visualization.py) - ThreeDScene, surfaces, 3D camera, parametric curves

## Scene Templates

Copy and modify these templates to start new projects:

- [templates/basic_scene.py](templates/basic_scene.py) - Standard 2D scene template
- [templates/camera_scene.py](templates/camera_scene.py) - MovingCameraScene with zoom/pan
- [templates/threed_scene.py](templates/threed_scene.py) - 3D scene with surfaces and camera rotation
- [templates/style.py](templates/style.py) - Shared semantic palette, sizes, and helper mobjects
- [templates/equation_explainer.py](templates/equation_explainer.py) - Dim-and-reveal equation scaffold
- [templates/paper_explainer.py](templates/paper_explainer.py) - Paper explainer scene scaffold

## Quick Reference

### Basic Scene Structure
```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # Create mobjects
        circle = Circle()

        # Add to scene (static)
        self.add(circle)

        # Or animate
        self.play(Create(circle))

        # Wait
        self.wait(1)
```

### Render Command
```bash
# Basic render with preview
python -m manim -pql scene.py MyScene

# Quality flags: -ql (low), -qm (medium), -qh (high), -qk (4k)
python -m manim -pqh scene.py MyScene

# Reproducible random scenes
python -m manim --seed 42 -pql scene.py MyScene
```

### OpenGL 3D Companion

ManimCE includes an OpenGL renderer. For dense 3D scenes, textured surfaces, or explicit OpenGL classes, keep the normal ManimCE API and add:

```python
from manim import *
from manim.opengl import *

config.renderer = "opengl"
config.write_to_movie = True
```

Render with:

```bash
python -m manim -pql --renderer=opengl --write_to_movie scene.py MyScene
```

Use `ThreeDScene.set_camera_orientation`, `move_camera`, `begin_ambient_camera_rotation`, and `add_fixed_in_frame_mobjects`; avoid direct camera-frame choreography from older snippets.

### Jupyter Notebook Support

Use the `%%manim` cell magic:

```python
%%manim -qm MyScene
class MyScene(Scene):
    def construct(self):
        self.play(Create(Circle()))
```

### Common Pitfalls to Avoid

1. **Version confusion** - Ensure you're using Manim Community v0.20.1 through the project venv when available.
2. **Check imports** - Use `from manim import *`; add `from manim.opengl import *` only for explicit OpenGL classes.
3. **Outdated tutorials** - Video tutorials may be outdated; prefer official documentation and local 0.20.1 source.
4. **Old CONFIG dictionaries** - Modern ManimCE uses constructor kwargs, class attributes, and `config`, not legacy `CONFIG = {...}` patterns
5. **PATH issues (Windows)** - If `manim` command not found or points to another install, use `python -m manim`

### Current 0.20.x Notes

- `Mobject.always` is available for simple "keep this next to that" updater patterns; use `add_updater` or `always_redraw` when arguments depend on a `ValueTracker`.
- `MathTex` splitting is more robust in 0.20.x, and 0.20.1 fixes a double-brace edge case, but precise animation control still benefits from separate strings or `substrings_to_isolate`.
- `Code` now uses `code_file=` or `code_string=` plus `language=` and `formatter_style=`; use `Code.get_styles_list()` for available styles.
- `SurroundingRectangle` accepts one or more mobjects; pass `color=...` and `buff=...` as keywords.
- `Mobject.always`, `Animation.set_default`, `Add`, `TypeWithCursor`, `axes @ (x, y)`, `colorscale`, `BraceLabel`, `LabeledLine`, `ConvexHull`, and `ManimColor.lighter/darker/contrasting` are available in the current API and should replace homegrown equivalents.
- Use `--seed` or `config.seed` for reproducible scenes that use randomness.
- Prefer constants over magic numbers for intentional non-default values. Omit explicit arguments when they match Manim defaults, such as `to_edge(UP)` instead of `to_edge(UP, buff=MED_LARGE_BUFF)`.

### Installation

```bash
# Recommended for a new project
uv add manim

# Also valid in an existing Python environment
python -m pip install manim

# Check installation
python -m manim checkhealth
```

### Useful Commands

```bash
python -m manim -pql scene.py Scene      # Preview low quality
python -m manim -pqh scene.py Scene      # Preview high quality
python -m manim --dry_run scene.py Scene # Execute without writing media
python -m manim --format gif scene.py    # Output as GIF
python -m manim checkhealth              # Verify installation
python -m manim plugins -l               # List plugins
```
