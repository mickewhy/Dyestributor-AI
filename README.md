<a name="top"></a>
![language](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
[![Steam Badge](https://img.shields.io/badge/Steam-000?logo=steam&logoColor=fff&style=for-the-badge)](https://store.steampowered.com/app/2106590/Dyestributor/)

# Dyestributor-AI
An AI solution finder for Dyestributor, built with Python

## 🗂️ Table of Contents
- [About](#-about)
- [How to Use](#-how-to-use)
- [Tips](#%EF%B8%8F-tips)

## 🎨 About

This project is an AI solution finder for [Dyestributor](https://store.steampowered.com/app/2106590/Dyestributor/), it utilizes Breadth-First Search or optionally Depth-First Search to iteratively try out all the possible moves until a solution is found. BFS is highly recommended for this usage but you can opt to use DFS if you wish, as shown in [Tips](#%EF%B8%8F-tips). This program was built on freely available [source code](https://cs50.harvard.edu/ai/2024/weeks/0/) provided by Harvard's CS50 course.

"Dyestributor is an indie puzzler with both simple and complicated mechanics that combine to make fun levels! You can perfect your gameplay to earn trophies or make and play custom levels in this relaxing (but admittedly difficult) puzzle game!"

This program should only be used to test out new levels for development and custom levels made by the playerbase.

## 📝 How to Use

To use this program, follow these steps:

```shell
# Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)

# Assuming git is installed, clone the repository
# You can also do this through Github Desktop
git clone https://github.com/mickewhy/dyestributor.git

# Navigate to the project directory
cd dyestributor

# Install the requirements
pip install -r requirements.txt

# Run the program and follow the steps printed in the terminal
python dyestributor.py

```

## 🖌️ Tips
- If you wish to try out DFS instead of BFS, you can switch out the class names in `solve()`.
```python
class Puzzle:
  def solve(self):
    """Finds a solution to puzzle, if one exists."""
    
    # Keep track of number of states explored
    self.num_explored = 0
    
    # Initialize frontier to just the starting position
    start = Node(state=self.start, parent=None, action=None)
    frontier = QueueFrontier()
    #          ^^^^^^^^^^^^^^^ Switch this out with StackFrontier()
```
- You can use the provided [lookup chart](./lookupchart.txt) to find what different emojis represent.
- Feel free to switch out the display method in `printGrid()` to fit your terminal. Some emojis and spaces might appear out of place for you, as this was fitted to work with the VS Code terminal.

[Back to top](#top)
