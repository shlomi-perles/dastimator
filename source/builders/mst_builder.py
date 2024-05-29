from MST.kruskal import *
from MST.prim import *
from tools.movie_maker import render_scenes

PRESENTATION_MODE = True
DISABLE_CACHING = True

scenes_lst = [Intro, WeightedGraphDefinition, MSTDefinition, TheCutLemma, KruskalUnionExample, KruskalComplexity,
              PrimExample, PrimComplexity]

render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=True, movie_name="Kruskal&Prim",
              description_title="Kruskal and Prim", description="",
              scenes_to_gif_frames={KruskalUnionExample: [28 + i for i in range(6)]})