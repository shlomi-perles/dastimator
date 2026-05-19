---
name: cli
description: Command-line interface, rendering options, and quality flags
metadata:
  tags: cli, render, quality, preview, command, terminal
---

# Manim CLI

The `manim` command-line interface for rendering scenes.

## Basic Usage

```bash
# Render a scene
python -m manim file.py SceneName

# With preview (opens video after rendering)
python -m manim -p file.py SceneName

# Preview with low quality (fast)
python -m manim -pql file.py SceneName
```

## Quality Flags

Quality presets for different use cases:

```bash
# Low Quality: 854x480, 15fps (fast for testing)
python -m manim -ql file.py SceneName

# Medium Quality: 1280x720, 30fps
python -m manim -qm file.py SceneName

# High Quality: 1920x1080, 60fps
python -m manim -qh file.py SceneName

# 2K Quality: 2560x1440, 60fps
python -m manim -qp file.py SceneName

# 4K Quality: 3840x2160, 60fps
python -m manim -qk file.py SceneName
```

### Common Combinations

```bash
# Preview + Low Quality (development workflow)
python -m manim -pql file.py SceneName

# Preview + High Quality (final check)
python -m manim -pqh file.py SceneName
```

## Preview Flag

```bash
# -p: Open video after rendering
python -m manim -p file.py SceneName

# Without -p: Render only (no auto-open)
python -m manim file.py SceneName
```

## Rendering Multiple Scenes

```bash
# Render all scenes in file
python -m manim -a file.py

# Render specific scenes
python -m manim file.py Scene1 Scene2 Scene3
```

## Output Options

### Save Last Frame Only

```bash
# -s: Save only the last frame as PNG
python -m manim -s file.py SceneName

# With quality
python -m manim -sql file.py SceneName
```

### Output Format

```bash
# GIF output
python -m manim --format gif file.py SceneName

# PNG sequence
python -m manim --format png file.py SceneName

# WebM (default is MP4)
python -m manim --format webm file.py SceneName
```

### Custom Output Directory

```bash
python -m manim -o custom_name file.py SceneName
python -m manim --media_dir /path/to/output file.py SceneName
```

## Frame Control

```bash
# Start from specific animation number
python -m manim -n 5 file.py SceneName

# Render frames from animation 3 to 7
python -m manim -n 3,7 file.py SceneName
```

## Resolution and FPS

```bash
# Custom resolution
python -m manim -r 1920,1080 file.py SceneName

# Custom frame rate
python -m manim --fps 24 file.py SceneName

# Both
python -m manim -r 1280,720 --fps 30 file.py SceneName
```

## Transparency

```bash
# Render with transparent background
python -m manim -t file.py SceneName
```

## Renderer Selection

```bash
# Cairo renderer (default, 2D)
python -m manim --renderer cairo file.py SceneName

# OpenGL renderer (3D, faster preview)
python -m manim --renderer opengl file.py SceneName
```

## Other Useful Flags

```bash
# Verbose output
python -m manim -v DEBUG file.py SceneName

# Quiet mode
python -m manim -v WARNING file.py SceneName

# Show progress bar
python -m manim --progress_bar display file.py SceneName

# Disable caching
python -m manim --disable_caching file.py SceneName

# Write to movie even if no animations
python -m manim --write_to_movie file.py SceneName

# Execute scene without writing image/video files
python -m manim --dry_run file.py SceneName

# Reproducible random scene
python -m manim --seed 42 file.py SceneName
```

## Help

```bash
# Show all options
python -m manim --help

# Show render command options
python -m manim render --help
```

## Other Commands

```bash
# Check installation and dependencies
python -m manim checkhealth

# Initialize new project
python -m manim init

# Show config values
python -m manim cfg show

# Write current config to file
python -m manim cfg write

# List installed plugins
python -m manim plugins -l
```

## Jupyter Notebook Support

Use the `%%manim` cell magic in Jupyter notebooks:

```python
%%manim -qm -v WARNING MyScene
class MyScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
```

Flags work the same as CLI (`-qm`, `-ql`, etc.).

## Typical Development Workflow

```bash
# 1. Develop with fast preview
python -m manim -pql scene.py MyScene

# 2. Check at medium quality
python -m manim -pqm scene.py MyScene

# 3. Final render at high quality
python -m manim -qh scene.py MyScene

# 4. Create GIF for sharing
python -m manim --format gif -qm scene.py MyScene
```

## Best Practices

1. **Use -pql for development** - Fast iteration cycle
2. **Use -qh for final output** - Good quality, reasonable render time
3. **Use -s for thumbnails** - Quick last-frame capture
4. **Use -a sparingly** - Renders everything, can be slow
5. **Use --dry_run for fast validation** - Catches construct-time errors without media output
6. **Use --seed for reproducibility** - Helpful for random layouts, colors, and simulations
7. **Use --format gif for demos** - Easy to share and embed
