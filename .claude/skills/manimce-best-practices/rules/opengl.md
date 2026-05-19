---
name: opengl
description: ManimCE OpenGL renderer, OpenGL surfaces, textured surfaces, meshes, and renderer-specific workflow
metadata:
  tags: opengl, renderer, surface, texture, mesh, 3d
---

# OpenGL Renderer

ManimCE's OpenGL renderer is part of `manim`. Keep using `from manim import *`; add `from manim.opengl import *` only when you need explicit OpenGL-only classes such as `OpenGLSurface`, `OpenGLSurfaceMesh`, or `OpenGLTexturedSurface`.

## Enable OpenGL

Prefer the CLI for one-off renders:

```bash
python -m manim -pql --renderer=opengl --write_to_movie scene.py SceneName
```

Or configure it in the scene file before constructing mobjects:

```python
from manim import *
from manim.opengl import *

config.renderer = "opengl"
config.write_to_movie = True
```

When using the OpenGL renderer from the CLI, Manim does not write a movie unless `--write_to_movie` is passed or `config.write_to_movie = True` is set.

## When to Use OpenGL

Use OpenGL for dense 3D scenes, textured surfaces, interactive preview, point clouds, and scenes where Cairo rendering becomes too slow. Use Cairo for ordinary 2D math animations unless OpenGL-specific features are needed.

## Surface Basics

Use `OpenGLSurface` when you want renderer-specific control over 3D surfaces.

```python
class GradientSurface(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(theta=30 * DEGREES, phi=70 * DEGREES)

        axes = ThreeDAxes(
            x_range=(-3, 3, 1),
            y_range=(-3, 3, 1),
            z_range=(0, 5, 1),
            x_length=6,
            y_length=6,
            z_length=4,
        )

        def height(x, y):
            return 0.3 * x**2 + 0.4 * y**2

        surface = OpenGLSurface(
            lambda u, v: axes.c2p(u, v, height(u, v)),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(80, 80),
            opacity=0.7,
            gloss=0.3,
            shadow=0.4,
        )
        surface.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)

        mesh = OpenGLSurfaceMesh(surface, resolution=(18, 18), stroke_width=1)
        self.play(FadeIn(axes), FadeIn(surface), Create(mesh))
```

For value-based surface colors, pass `axes=axes`, `colorscale=[...]`, and `colorscale_axis=2` to `OpenGLSurface`.

## Textured Surfaces

Use `OpenGLTexturedSurface` to wrap a generated image or texture file over an `OpenGLSurface`.

```python
from pathlib import Path

texture = Path("images/laplace_transform_texture.png")
base_surface = OpenGLSurface(
    lambda u, v: axes.c2p(u, v, np.abs(transform(u + 1j * v))),
    u_range=[-5, 5],
    v_range=[-5, 5],
    resolution=(120, 120),
    opacity=0.7,
    color=GRAY,
    shadow=0.8,
)
textured_surface = OpenGLTexturedSurface(base_surface, image_file=texture)
```

`OpenGLTexturedSurface` already creates the internal `LightTexture` and `DarkTexture` entries. Pass `dark_image_file=...` when the dark-mode texture differs; do not mutate `texture_paths` unless replacing textures dynamically.

Texture coordinates reverse the image's vertical direction internally. For generated NumPy/PIL textures, render a quick low-quality preview and flip the source image only if the orientation is visibly wrong.

## Fixed Frame Overlays

Use fixed-frame mobjects for titles, formulas, and labels that should remain screen-aligned while the 3D camera moves.

```python
title = Text("Loss Landscape", font_size=48).to_corner(UL)
self.add_fixed_in_frame_mobjects(title)
self.play(FadeIn(title))
```

## Camera Workflow

OpenGL scenes still use `ThreeDScene` camera methods:

```python
self.set_camera_orientation(theta=30 * DEGREES, phi=70 * DEGREES)
self.move_camera(theta=-30 * DEGREES, run_time=3)
self.begin_ambient_camera_rotation(rate=0.35)
self.wait(10)
self.stop_ambient_camera_rotation()
```

Avoid direct camera-frame calls from older snippets. Replace `frame.reorient(...)` with `self.set_camera_orientation(...)`, animated frame reorientation with `self.move_camera(...)`, and `mob.fix_in_frame()` with `self.add_fixed_in_frame_mobjects(mob)`.

## Explicit OpenGL Classes

Only swap explicit base classes:

| Ordinary class | OpenGL class |
| --- | --- |
| `Mobject` | `OpenGLMobject` |
| `VMobject` | `OpenGLVMobject` |
| `PMobject` | `OpenGLPMobject` |
| `Mobject1D` | `OpenGLPMobject` |
| `Mobject2D` | `OpenGLPMobject` |
| `Surface` | `OpenGLSurface` |
| `SurfaceMesh` | `OpenGLSurfaceMesh` |

High-level mobjects that work with the renderer, such as `Sphere`, `Cube`, `Torus`, `ThreeDAxes`, `Text`, and `MathTex`, normally keep their standard names.

## Performance Notes

- Keep `OpenGLSurface.resolution` no higher than needed; `(80, 80)` is already dense.
- Use a lower `OpenGLSurfaceMesh` resolution than the surface resolution.
- Precompute expensive texture arrays before animations start.
- Guard complex-valued formulas with `np.nan_to_num` and small denominators before converting to color or height.
- Use `--dry_run` for construct-time validation before enabling in-file `config.write_to_movie = True`; for file-configured OpenGL scenes, prefer a fast `-ql` render in a temp media dir.

## Common Pitfalls

1. **Using old OpenGL snippets unchanged** - ManimCE OpenGL uses `manim`, `MathTex`, `Write`/`Create`, and `ThreeDScene`.
2. **Forgetting `--write_to_movie`** - OpenGL CLI renders do not write video files unless movie writing is requested.
3. **Changing renderer too late** - Set `config.renderer = "opengl"` before constructing mobjects.
4. **Manual texture path mutation** - Prefer constructor arguments (`image_file`, `dark_image_file`) over editing `texture_paths`.
5. **Unbounded complex functions** - Clamp singularities and NaNs before creating textures or surface heights.
