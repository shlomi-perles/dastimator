---
name: Manim Slides CLI
description: Render, present, convert, and configure manim-slides from the command line
tags: [manim, manim-slides, cli, render, convert, present]
---

# Manim Slides CLI

Manim Slides provides a CLI with `render`, `present`, and `convert`. If no
command is specified, it defaults to `present`.

## Typical workflow

```bash
# 1) Render the scene with Manim
manim example.py BasicExample

# 2) Present locally
manim-slides present BasicExample

# 3) Or convert to HTML
manim-slides convert BasicExample basic_example.html -ccontrols=true
```

## Core commands

### `manim-slides render`
Runs Manim under the hood. Pick a renderer:

```bash
manim-slides render --CE example.py BasicExample
manim-slides render --GL example.py BasicExample
```

### `manim-slides present`
Presents rendered slides from the `slides/` folder.

Useful options:
- `--folder <DIRECTORY>` to point at a custom slides folder.
- `--start-at`, `--start-at-scene-number`, `--start-at-slide-number` for resume.
- `--playback-rate <RATE>` to speed up or slow down playback.
- `--next-terminates-loop` to break out of looping slides.

### `manim-slides convert`
Converts slides into HTML, PDF, PPTX, or ZIP.

```bash
manim-slides convert BasicExample slides.html
manim-slides convert BasicExample slides.pdf
```

Key options:
- `--to <FORMAT>`: `auto`, `html`, `pdf`, `pptx`, `zip`.
- `--folder <DIRECTORY>`: input slides folder (default `slides`).
- `-c<option>=<value>`: pass converter or RevealJS options.
- `--use-template <FILE>`: use a custom HTML template.
- `--show-template`: print the default template.
- `--show-config`: list supported options for the target format.
- `--one-file`: embed local assets into the output.
- `--offline`: embed remote assets into the output.

## Config files

You can create a `.manim-slides.toml`:

```bash
manim-slides init
manim-slides wizard
```

## Slides folder layout

When sharing rendered slides, expect a structure like:

```
slides/
  BasicExample.json
  files/
    BasicExample/
      <video assets>
```

Treat the JSON schema as an implementation detail. Inspect actual files before
assuming fields.

## Environment variables

- `MANIM_SLIDES_VERBOSITY` controls CLI verbosity.
- `MANIM_RENDERER` and `MANIMGL_RENDERER` control default renderer selection.
