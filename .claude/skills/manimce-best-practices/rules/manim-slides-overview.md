---
name: Manim Slides Overview
description: Core classes, slide lifecycle, and API features for manim-slides
tags: [manim, manim-slides, slides, presentation, revealjs]
---

# Manim Slides Overview

Manim Slides adds slide semantics to Manim scenes. You subclass `Slide` or
`ThreeDSlide`, then use `next_slide()` to declare slide boundaries and per-slide
options.

## Minimal pattern

```python
from manim import *
from manim_slides import Slide

class Example(Slide):
    def construct(self):
        title = Text("Hello")
        self.play(FadeIn(title))
        self.next_slide()
        self.play(FadeOut(title))
```

## Core classes

- `Slide` extends Manim `Scene`.
- `ThreeDSlide` extends `Slide` and Manim `ThreeDScene`.
- `next_section()` is an alias for `next_slide()` when using Manim CE.

## `next_slide()` options (most used)

```python
self.next_slide(
    loop=False,
    auto_next=False,
    playback_rate=1.0,
    reversed_playback_rate=1.0,
    notes="",
    dedent_notes=True,
    skip_animations=False,
    src=None,
    type=SlideType.Video,
    direction="horizontal",
)
```

Important constraints from manim-slides:
- `auto_next` is supported by `present` and `convert --to=html`.
- `playback_rate` and `reversed_playback_rate` are supported by `present`.
- `notes` are supported by `present`, HTML, and PPTX conversion.
- `direction="vertical"` is supported by HTML conversion (RevealJS stacks).
- Loops cannot be the first or last slide when rendered with RevealJS.

## Canvas for persistent elements

The canvas is a name-to-mobject mapping for elements that persist across slides.
Typical use: titles, slide numbers, or section headers.

```python
self.add_to_canvas(title=Text("Section").to_corner(UL))
self.play(FadeIn(self.canvas["title"]))
self.next_slide()
self.remove_from_canvas("title")
```

Related helpers:
- `canvas` and `canvas_mobjects`
- `mobjects_without_canvas` (all scene mobjects except canvas entries)

## Transition helpers

Manim Slides ships `wipe()` and `zoom()` helpers, plus animation classes `Wipe`
and `Zoom` for composition.

```python
self.wipe(current_group, future_group)
self.zoom(current_group, future_group)

anim = self.wipe(current_group, future_group, return_animation=True)
self.play(anim)
```

## Slide timing

`wait_time_between_slides` inserts a small wait at the end of each slide. This
is useful when a slide ends immediately after a draw animation.

```python
self.wait_time_between_slides = 0.1
```

## External media slides

Use `src` to include external media (image, gif, video). The file is copied into
the output folder during render/convert.

```python
self.next_slide(src=Path("static/logo.png"))
```

## 3D slides

Use `ThreeDSlide` for camera control. ManimCE OpenGL scenes should still use
`ThreeDScene` camera methods such as `set_camera_orientation`, `move_camera`,
and `begin_ambient_camera_rotation`.

## Vertical slides (RevealJS)

Use `direction="vertical"` to group slides under a horizontal parent. In HTML,
left/right navigates horizontal, and up/down navigates vertical stacks.

## Mobile and input notes

If you customize the HTML, keep touch navigation enabled in RevealJS and avoid
page-level scrolling that can steal swipe/tap gestures. Always test on a phone
before shipping.
