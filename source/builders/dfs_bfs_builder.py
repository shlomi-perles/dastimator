from BFS.bfs import *
from DFS.dfs import *
from tools.movie_maker import render_scenes

PRESENTATION_MODE = True
DISABLE_CACHING = True

scenes_lst = [GraphsIntro, EdgesUpperBound, GraphRepresentation, BFSIntro, BFSBigGraph, DirectedGraphBFS,
              BFSComplexity, RecursiveDFSMainExamp, DFSBigGraph]

render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=True, movie_name="BFS&DFS",
              description_title='BFS and DFS',
              description="", scenes_to_gif_frames={DirectedGraphBFS: [28 + i for i in range(6)]})
