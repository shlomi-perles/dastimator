from dijkstra import *
from bellman_ford import *

PRESENTATION_MODE = True
DISABLE_CACHING = False

scenes_lst = [Intro, ShortestPath, DijkstraIntro, Relax, DijkstraExample, DijkstraComplexity, BellmanFordIntro,
              BellmanFordExample, BellmanFordComplexity]

run_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=False, movie_name="Dijkstra&BF",
           gif_scenes={DijkstraExample: 18 + i for i in range(5)})
