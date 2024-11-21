# Dastimator 📚🎥

**Dastimator** is a Python library built on the powerful [Manim](https://www.manim.community/) library, designed to
assist in teaching data structures in an engaging and visual way. Initially developed for use in the Data Structures
course at The Hebrew University of Jerusalem (HUJI), dastimator simplifies the creation of programmatic animations
for educational purposes.

---

## Features 🚀

### 🖥️ **[Dastflix](https://shlomi-perles.github.io/dastimator)**

- A dedicated website hosting presentations about data structures, all created using dastimator.
- Explore the presentations and their source code [here](source).

[<img src="https://github.com/user-attachments/assets/beb76038-d91f-4600-852e-2ebefc145f41" width="620">](https://shlomi-perles.github.io/dastimator)


### 🛠️ **Library Tools**

- A suite of tools that extends Manim's core functionality to simplify the creation of visualizations.
- Includes modules for handling and animating data structures like arrays, graphs, etc.

---

## Example Usage ✍️

Here's a sample snippet showcasing how to create and animate an array:

```python
from tools.array import *
from tools.consts import *
from tools.movie_maker import render_scenes
from tools.scenes import *


class ArrayExample(SectionsScene):
    def construct(self):
        self.next_section("arr", pst.NORMAL)
        array = ArrayMob("Array:", "", "8", "1", "3", "9", show_indices=True, indices_pos=DOWN, starting_index=1)
        array.scale_to_fit_width(config.frame_width * 0.6)
        self.play(Write(array))
        self.play(array.animate.at(1, "b"))
        self.play(array.animate.at(1, 3))
        self.play(array.indicate_at(3))
        self.play(array.push(5))
        self.play(array.pop(4))
        self.play(array.swap(1, 3))

        pointer = ArrayPointer(array, 1, "Here", direction=0.4 * DOWN)
        self.play(Write(pointer))
        self.play(pointer.to_entry(5))

        self.wait(2)
```


https://github.com/user-attachments/assets/221cfdd5-6bd7-4416-b72f-5d9ad3ab5e80

---

## Contributions 🤝

Contributions are welcome! Feel free to:

- Submit issues.
- Fork the project.

---

## License 📜

This project is licensed under the MIT License.

---

## Acknowledgments 🌟

- Built using the Manim library.
- Special thanks to the students of HUJI for inspiring the project.

Explore, create, and teach with Dastimator! 🎉
