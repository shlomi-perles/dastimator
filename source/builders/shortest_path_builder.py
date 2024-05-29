from shortest_weighted_path.dijkstra import *
from shortest_weighted_path.bellman_ford import *
from tools.movie_maker import render_scenes

PRESENTATION_MODE = True
DISABLE_CACHING = True

scenes_lst = [Intro, ShortestPath, DijkstraIntro, Relax, DijkstraExample, DijkstraComplexity, BellmanFordIntro,
              BellmanFordExample, BellmanFordComplexity]

render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=True,
              movie_name="Dijkstra&BF", description_title="Dijkstra and Bellman-Ford", description="",
              scenes_to_gif_frames={DijkstraExample: [18 + i for i in range(5)]})
