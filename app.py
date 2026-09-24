"""
Maze Solver Robot (DFS) - Streamlit demo
Python port of the C++ project (maze_solver.cpp).
Concepts: Abstract class, Child class, Encapsulation, Stack (push / pop)
Run:  streamlit run app.py
"""
import time
from abc import ABC, abstractmethod

import streamlit as st

# ---------------- colours ----------------
WALL, OPEN, VISITED = "#1F2F30", "#EAF4F2", "#BFDCD7"
PATH, INK, ROBOT = "#F2A541", "#0F3D3E", "#E4572E"

DIRS = {"UP": (-1, 0), "RIGHT": (0, 1), "DOWN": (1, 0), "LEFT": (0, -1)}


# =====================================================
#  MAZE  (Encapsulation: grid and goal are private)
# =====================================================
class Maze:
    def __init__(self, layout):
        self.__grid = [list(row) for row in layout]
        self.__start = self.__goal = (0, 0)
        for r, row in enumerate(self.__grid):
            for c, ch in enumerate(row):
                if ch == "S":
                    self.__start = (r, c)
                if ch == "G":
                    self.__goal = (r, c)

    def is_wall(self, r, c):
        if r < 0 or c < 0 or r >= self.rows() or c >= self.cols():
            return True                       # outside the maze = wall
        return self.__grid[r][c] == "#"

    def is_goal(self, pos):
        return pos == self.__goal             # robot never learns WHERE the goal is

    def get_start(self):
        return self.__start

    def rows(self):
        return len(self.__grid)

    def cols(self):
        return len(self.__grid[0])

    def symbol(self, r, c):                   # used only for drawing the picture
        return self.__grid[r][c]


# =====================================================
#  ROBOT  (Abstract class: cannot be created directly)
# =====================================================
class Robot(ABC):
    def __init__(self, maze):
        self._maze = maze
        self._pos = maze.get_start()
        self._path = [self._pos]              # STACK (list: append = push, pop = pop)
        self._steps = 0
        self.history = []                     # snapshots, used for the replay slider

    @abstractmethod
    def choose_direction(self):               # pure virtual: decide
        ...

    @abstractmethod
    def move(self, direction):                # pure virtual: act, returns action name
        ...

    def _visited_cells(self):
        return set(self._path)

    def _record(self, action):
        self.history.append({
            "action": action,
            "pos": self._pos,
            "stack": list(self._path),
            "visited": set(self._visited_cells()),
        })

    def solve(self, max_steps=5000):
        """Main loop, written once. Works for any child robot (polymorphism)."""
        self._record("start")
        while not self._maze.is_goal(self._pos) and self._steps < max_steps:
            action = self.move(self.choose_direction())
            self._steps += 1
            self._record(action)
            if action == "stuck":
                break
        return self._maze.is_goal(self._pos)

    def get_steps(self):
        return self._steps

    def get_path(self):
        return list(self._path)


# =====================================================
#  DFS ROBOT  (Child class)
# =====================================================
class DFSRobot(Robot):
    def __init__(self, maze):
        super().__init__(maze)
        self.__visited = {self._pos}          # private memory

    def __next(self, pos, direction):
        dr, dc = DIRS[direction]
        return (pos[0] + dr, pos[1] + dc)

    def _visited_cells(self):
        return self.__visited

    def choose_direction(self):
        for d in ("UP", "RIGHT", "DOWN", "LEFT"):
            r, c = self.__next(self._pos, d)
            if not self._maze.is_wall(r, c) and (r, c) not in self.__visited:
                return d                      # found a new cell
        return None                           # dead end

    def move(self, direction):
        if direction is None:                 # BACKTRACK
            if len(self._path) > 1:
                self._path.pop()              # POP
                self._pos = self._path[-1]
                return "pop"
            return "stuck"                    # stack has only the start: no exit
        self._pos = self.__next(self._pos, direction)   # FORWARD
        self.__visited.add(self._pos)
        self._path.append(self._pos)          # PUSH
        return "push"


# =====================================================
#  DRAWING HELPERS
# =====================================================
PRESETS = {
    "Maze 1 - straight route": "#########\n#S..#...#\n#.#.#.#.#\n#.#...#G#\n#########",
    "Maze 2 - dead end + backtracking": "#######\n#S..#G#\n#.###.#\n#.....#\n#######",
    "Maze 3 - no exit": "#######\n#S.#G.#\n#######",
    "Maze 4 - bigger maze": (
        "###############\n#S....#.......#\n#.###.#.#####.#\n#.#...#.#...#.#\n"
        "#.#.###.#.#.#.#\n#.#.....#.#...#\n#.#######.###.#\n#.........#..G#\n###############"
    ),
    "Custom (edit below)": "#########\n#S......#\n#.#####.#\n#......G#\n#########",
}


def parse_layout(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return None, "The maze is empty."
    if len({len(ln) for ln in lines}) != 1:
        return None, "All rows must have the same length."
    joined = "".join(lines)
    if set(joined) - set("#.SG"):
        return None, "Use only  #  .  S  G  characters."
    if joined.count("S") != 1 or joined.count("G") != 1:
        return None, "The maze needs exactly one S and one G."
    return lines, None


def cell_html(bg, txt="", fg="#22323A"):
    return (f"<div style='width:36px;height:36px;background:{bg};color:{fg};display:flex;"
            f"align-items:center;justify-content:center;font-weight:700;"
            f"border-radius:4px;font-size:18px'>{txt}</div>")


def maze_html(maze, snap):
    on_path, visited, pos = set(snap["stack"]), snap["visited"], snap["pos"]
    rows = []
    for r in range(maze.rows()):
        cells = []
        for c in range(maze.cols()):
            sym = maze.symbol(r, c)
            if sym == "#":
                cells.append(cell_html(WALL))
            elif (r, c) == pos:
                cells.append(cell_html(ROBOT, "🤖"))
            elif sym in "SG":
                cells.append(cell_html(INK, sym, "#FFFFFF"))
            elif (r, c) in on_path:
                cells.append(cell_html(PATH))
            elif (r, c) in visited:
                cells.append(cell_html(VISITED))
            else:
                cells.append(cell_html(OPEN))
        rows.append("<div style='display:flex;gap:2px'>" + "".join(cells) + "</div>")
    return "<div style='display:flex;flex-direction:column;gap:2px'>" + "".join(rows) + "</div>"


def stack_html(snap):
    items = []
    for i, cell in enumerate(reversed(snap["stack"])):
        bg = PATH if i == 0 else OPEN
        tag = "  &larr; top" if i == 0 else ""
        items.append(f"<div style='background:{bg};color:#0F3D3E;border:1px solid #5E8C88;"
                     f"border-radius:4px;padding:4px 10px;margin-bottom:3px;font-weight:600;"
                     f"font-family:monospace'>({cell[0]},{cell[1]}){tag}</div>")
    return ("<div style='min-width:150px'><div style='font-weight:700;margin-bottom:6px'>"
            "Stack (top first)</div><div style='max-height:340px;overflow-y:auto'>"
            + "".join(items) + "</div></div>")


def action_text(snap):
    r, c = snap["pos"]
    return {
        "start": f"Robot placed at the start ({r},{c}). Start cell pushed on the stack.",
        "push": f"PUSH: moved forward to ({r},{c}) and pushed it on the stack.",
        "pop": f"POP: dead end. Popped the stack and went back to ({r},{c}).",
        "stuck": "Stuck: every path was explored and there is no exit.",
    }[snap["action"]]


def draw(maze, history, i, placeholder):
    snap = history[i]
    placeholder.markdown(
        f"<div style='margin-bottom:10px'><b>Step {i} of {len(history) - 1}:</b> "
        f"{action_text(snap)}</div>"
        f"<div style='display:flex;gap:40px;align-items:flex-start;flex-wrap:wrap'>"
        f"{maze_html(maze, snap)}{stack_html(snap)}</div>",
        unsafe_allow_html=True,
    )


# =====================================================
#  STREAMLIT PAGE
# =====================================================
st.set_page_config(page_title="Maze Solver Robot (DFS)", page_icon="🤖", layout="wide")
st.title("🤖 Maze Solver Robot using DFS")
st.caption("Depth-First Search with a stack: go deep, push each new cell, pop when stuck.")

with st.sidebar:
    st.header("Settings")
    choice = st.selectbox("Choose a maze", list(PRESETS))
    text = st.text_area("Maze layout (# wall, . open, S start, G goal)",
                        PRESETS[choice], height=220)
    speed = st.slider("Animation speed (seconds per step)", 0.05, 1.0, 0.3, 0.05)
    st.markdown("**Legend**  \n🟧 path (stack)  \n🟩 visited, backtracked  \n🟥🤖 robot now")

layout, error = parse_layout(text)
if error:
    st.error(error)
    st.stop()

maze = Maze(layout)
robot = DFSRobot(maze)
solved = robot.solve()
history = robot.history

m1, m2, m3 = st.columns(3)
m1.metric("Result", "Goal reached ✅" if solved else "No path ❌")
m2.metric("Total steps (with backtracking)", robot.get_steps())
m3.metric("Final path length (cells)", len(robot.get_path()) if solved else 0)

view = st.empty()
step = st.slider("Step (drag to replay the robot)", 0, len(history) - 1, len(history) - 1)
play = st.button("▶ Play animation")

if play:
    for i in range(len(history)):
        draw(maze, history, i, view)
        time.sleep(speed)
else:
    draw(maze, history, step, view)

with st.expander("How does it work?"):
    st.markdown("""
1. **Look**: check up, right, down, left for a cell that is not a wall and not visited.
2. **Move**: found one? Step there and **PUSH** it on the stack.
3. **Backtrack**: dead end? **POP** the stack and go back one step.

When the robot reaches `G`, the stack holds the exact path from `S` to `G`.

**OOP used:** `Robot` is an abstract class, `DFSRobot` is its child class,
`Maze` keeps its grid private (encapsulation), and the path is a stack.
""")
