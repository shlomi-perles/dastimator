# ManimCE API Index

Use this as a class-discovery map when planning a scene. Check local signatures in `.venv/Lib/site-packages/manim` or official docs before relying on rarely used constructor parameters.

## Scene Types

- `Scene`: default 2D scene.
- `MovingCameraScene`: 2D zoom/pan with `self.camera.frame`.
- `ThreeDScene`: 3D camera, surfaces, fixed-frame overlays.
- `ZoomedScene`: inset zoom workflows.
- `VoiceoverScene`: available through the voiceover plugin, not core ManimCE.

## Core Mobjects

- Geometry: `Circle`, `Square`, `Rectangle`, `RoundedRectangle`, `Triangle`, `Polygon`, `Polygram`, `RegularPolygon`, `RegularPolygram`, `Star`.
- Arcs and angles: `Arc`, `ArcBetweenPoints`, `TangentialArc`, `Angle`, `RightAngle`, `Annulus`, `AnnularSector`, `Sector`.
- Lines and connectors: `Line`, `DashedLine`, `Arrow`, `DoubleArrow`, `CurvedArrow`, `Vector`, `Brace`, `BraceBetweenPoints`, `ArcBrace`, `LabeledLine`, `LabeledArrow`.
- Shape matchers: `SurroundingRectangle`, `BackgroundRectangle`, `Underline`, `Cross`.
- Labeled geometry: `Label`, `LabeledPolygram`, `BraceLabel`, `BraceText`, `ConvexHull`.
- Groups: `VGroup` for vector mobjects, `Group` for mixed mobjects, `VDict` for keyed groups.

## Text and Data Mobjects

- Text: `Text`, `MarkupText`, `Paragraph`.
- LaTeX: `MathTex`, `Tex`, `SingleStringMathTex`, `Title`, `BulletedList`.
- Numbers: `DecimalNumber`, `Integer`, `Variable`, `ValueTracker`, `ComplexValueTracker`.
- Code and tables: `Code`, `Table`, `MathTable`, `DecimalTable`, `IntegerTable`, `MobjectTable`.
- Matrices: `Matrix`, `DecimalMatrix`, `IntegerMatrix`, `MobjectMatrix`.

## Coordinates and Graphing

- Axes: `Axes`, `NumberPlane`, `ComplexPlane`, `PolarPlane`, `ThreeDAxes`, `NumberLine`, `UnitInterval`.
- Graphs: `Graph`, `DiGraph`, `GenericGraph`.
- Functions: `FunctionGraph`, `ParametricFunction`, `ImplicitFunction`, `TangentLine`.
- Fields: `VectorField`, `ArrowVectorField`, `StreamLines`.
- Data visuals: `BarChart`, `SampleSpace`.

## Images and Assets

- Raster images: `ImageMobject`.
- Vector assets: `SVGMobject`, `VMobjectFromSVGPath`.
- Camera-derived images: `ImageMobjectFromCamera`.
- Use `ImageMobject` for PNG/JPEG/NumPy arrays and `SVGMobject` when paths need to scale or animate cleanly.

## 3D Mobjects

- Solids: `Sphere`, `Cube`, `Prism`, `Cylinder`, `Cone`, `Torus`.
- Polyhedra: `Tetrahedron`, `Dodecahedron`, `Icosahedron`, `Octahedron`, `Polyhedron`, `ConvexHull3D`.
- 3D lines: `Line3D`, `Arrow3D`, `Dot3D`.
- Surfaces: `Surface`, `ThreeDVMobject`.
- Fixed overlays: use `add_fixed_in_frame_mobjects` on `ThreeDScene`.

## OpenGL-Specific Classes

Read `rules/opengl.md` before using these.

- Renderer classes: `OpenGLMobject`, `OpenGLVMobject`, `OpenGLGroup`, `OpenGLVGroup`.
- Surfaces: `OpenGLSurface`, `OpenGLSurfaceMesh`, `OpenGLTexturedSurface`, `OpenGLSurfaceGroup`.
- Raster: `OpenGLImageMobject`.
- Point clouds: `DotCloud`, `OpenGLPMobject`, `OpenGLPGroup`, `OpenGLPoint`.

## Animation Families

- Creation/removal: `Create`, `Uncreate`, `Write`, `Unwrite`, `DrawBorderThenFill`, `SpiralIn`, `Add`.
- Fading: `FadeIn`, `FadeOut`, `FadeTransform`, `FadeTransformPieces`, `FadeToColor`.
- Growth: `GrowFromCenter`, `GrowFromPoint`, `GrowFromEdge`, `GrowArrow`, `SpinInFromNothing`.
- Transforms: `Transform`, `ReplacementTransform`, `TransformFromCopy`, `TransformMatchingTex`, `TransformMatchingShapes`, `MoveToTarget`, `ApplyMethod`, `ApplyFunction`, `ApplyMatrix`.
- Groups/timing: `AnimationGroup`, `LaggedStart`, `LaggedStartMap`, `Succession`, `Wait`, `ChangeSpeed`.
- Indication: `Indicate`, `Circumscribe`, `Flash`, `FocusOn`, `ApplyWave`, `Wiggle`, `ShowPassingFlash`.
- Movement/traces: `MoveAlongPath`, `TracedPath`, `MaintainPositionRelativeTo`, `UpdateFromFunc`, `UpdateFromAlphaFunc`.
- Text-specific: `AddTextLetterByLetter`, `RemoveTextLetterByLetter`, `TypeWithCursor`, `UntypeWithCursor`.
- Defaults/updaters: `Animation.set_default(...)` for animation-class defaults; `mobject.always.method(...)` for simple "keep following" updaters.

## Constants and Config

- Directions: `UP`, `DOWN`, `LEFT`, `RIGHT`, `IN`, `OUT`, `ORIGIN`, `UL`, `UR`, `DL`, `DR`.
- Angles: `PI`, `TAU`, `DEGREES`.
- Buffs: `SMALL_BUFF`, `MED_SMALL_BUFF`, `MED_LARGE_BUFF`, `LARGE_BUFF`.
- Colors: `BLUE_A` through `BLUE_E`, similarly for common palettes; `PURE_CYAN`, `PURE_MAGENTA`, `PURE_YELLOW`, `HSV`, `DVIPSNAMES`, `SVGNAMES`, and `ManimColor.lighter/darker/contrasting` are available in v0.20.x.
- Renderer: `config.renderer = "cairo"` or `"opengl"`; CLI equivalent is `--renderer cairo|opengl`.
- Reproducibility: `config.seed = 42` or `--seed 42`.
