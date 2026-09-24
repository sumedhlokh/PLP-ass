# Maze Solver Robot using DFS

A robot finds the exit of a maze using **Depth-First Search** and a **stack**.
It goes deep into one path, pushes every new cell on the stack, and pops the stack to backtrack from dead ends.

Built in **C++** (main project) with a **Streamlit** web demo (Python port of the same logic).

## Concepts covered

| Concept | Where |
|---|---|
| Abstract class | `Robot` (`choose_direction`, `move` are pure virtual) |
| Child class | `DFSRobot` |
| Encapsulation | `Maze` keeps the grid and goal private |
| Polymorphism | `solve()` in `Robot` calls the child's functions |
| Stack | `path`: push on forward move, pop on backtrack |

## Project structure

```
maze-solver-dfs/
├── maze_solver.cpp      C++ project
├── app.py               Streamlit demo
├── requirements.txt
├── presentation/        2-slide PowerPoint
└── README.md
```

## Run the C++ version

```
g++ -std=c++11 maze_solver.cpp -o maze_solver
./maze_solver
```

## Run the Streamlit demo

```
pip install -r requirements.txt
streamlit run app.py
```

Features: pick or edit a maze, watch the robot move step by step, see the stack change (push / pop), and drag a slider to replay any step.

## Live demo

Add your Streamlit Cloud link here after deploying.

## How DFS works here

1. Look at up, right, down, left for a cell that is not a wall and not visited.
2. Found one? Move there and **push** it.
3. Dead end? **Pop** and go back one step.
4. Stop at the goal. The stack holds the path.
