---
name: Manim Slides Web Integration
description: HTML template customization, RevealJS options, and web generator integration notes
tags: [manim, manim-slides, web, html, revealjs, template]
---

# Manim Slides Web Integration

This guide focuses on converting manim-slides output into a custom web
experience while preserving RevealJS behavior.

## HTML conversion pipeline

```bash
manim-slides convert MyScene site.html
```

To customize the HTML:

```bash
# Inspect the default template
manim-slides convert --show-template --to=html

# Use your own template
manim-slides convert MyScene site.html --use-template path/to/template.html
```

When customizing, keep the RevealJS slide container and its initialization
intact. Wrap UI around it rather than replacing it.

## RevealJS configuration

Manim Slides exposes RevealJS options via `-c<option>=<value>` and `--show-config`.
Common web options:

- `controls`, `progress`, `slide_number`, `show_slide_number`
- `hash`, `respond_to_hash_changes`, `jump_to_slide`, `history`
- `navigation_mode`, `rtl`, `loop`
- `touch`, `mouse_wheel`
- `transition`, `transition_speed`, `background_transition`
- `auto_animate`, `auto_animate_duration`, `auto_animate_easing`
- `view_distance`, `mobile_view_distance`
- `disable_layout`, `center`
- `background_color`

If you need a full list, run:

```bash
manim-slides convert --show-config --to=html
```

## Notes and slide metadata

- `notes` passed to `next_slide()` are supported in `present`, HTML, and PPTX.
- In HTML, speaker notes are shown in the speaker view (press `S`).
- Set `show_notes` to display notes to all viewers.

## Vertical slides

Use `direction="vertical"` to place slides under a horizontal parent. In HTML,
left/right navigates horizontal, up/down navigates vertical stacks.

## External media slides

Use `src` on `next_slide()` to inject images, gifs, or videos. The asset is
copied into the output folder so the HTML can reference it locally.

## Thumbnails and previews

Some converters support `frame_index` and `resolution` to choose which video
frame represents a slide and at what resolution. Verify support with
`convert --show-config` and use these settings when you need predictable
thumbnail generation. If not supported for your format, extract a frame from
the rendered video assets.

## Web generator integration checklist

- Read slides from the `slides/` folder and assets from `slides/files/`.
- Use `--folder` when the generator points at a non-default slides directory.
- Preserve RevealJS container markup in the HTML template.
- Avoid page-level scrolling that can steal touch navigation on mobile.
- Keep `touch=true` unless you are replacing navigation entirely.
- Do not place looping slides at the first or last position when using RevealJS.
