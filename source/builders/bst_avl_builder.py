from AVL.avl import *
from BST.bst import *
from tools.movie_maker import render_scenes

PRESENTATION_MODE = True
DISABLE_CACHING = True

scenes_lst = [BSTLecture, ComplexitySummaryBST, AVLLectureIntro, AVLLectureIntroInsert, AVLLectureRotations,
              AVLLectureBalance, AVLLectureInsert, ComplexitySummary]

render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=False, movie_name="BST&AVL",
              description_title="BST and AVL Trees", description="Welcome to the wild and wacky world of binary search "
                                                                 "trees (BSTs) and AVL trees! These are data structures "
                                                                 "that store data in a hierarchical way, allowing fast search,"
                                                                 " insertion, and deletion operations. But not all BSTs are"
                                                                 " created equal. Some of them can become unbalanced and lose"
                                                                 " their efficiency. That’s why we need AVL trees, which are"
                                                                 " BSTs that maintain a balance invariant by performing rotations"
                                                                 " when needed. Today, we will learn about operations on a BST,"
                                                                 " the AVL Invariant, the different types of rotations, and how"
                                                                 " to keep your AVLs balanced and stay alive. Let’s get started! 🌳",
              scenes_to_gif_frames={AVLLectureRotations: [1 + i for i in range(9)]})
