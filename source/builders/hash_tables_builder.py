from hash_tables.hash_tables_scenes import *
from tools.movie_maker import render_scenes

PRESENTATION_MODE = True
DISABLE_CACHING = True

scenes_lst = [Intro, HashTableRecipe, UniversalHashFamilies, UniversalHashExamples, UniversalHashBaseExample,
              CheckTriplets, KUniversalHashFamilies, TwoUniversalsAreUniversal]

render_scenes(scenes_lst, OUT_DIR, PRESENTATION_MODE, DISABLE_CACHING, overwrite_scenes=False, movie_name="Hash Tables",
              description_title="Hash Tables", description="Welcome to the World of Hash Tables! "
                                                           "These marvelous data structures perform the magical trick of "
                                                           "transforming keys into array indices for lightning-fast data access. "
                                                           "Beware! A naive approach can attract malicious agents who overload the hash "
                                                           "table and wreak havoc on its efficiency. To thwart the bad guys, we introduce Universal Hash"
                                                           "Families—a clever way to keep your hash tables safe and speedy 🗝️🔑.",
              scenes_to_gif_frames={UniversalHashFamilies: [2]})
