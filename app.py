// ======================================================================
//  Maze Solver Robot - finds the BEST (shortest) path
//  It checks every possible route through the maze, then keeps
//  only the shortest one it found.
// ======================================================================
#include <iostream>
#include <vector>
#include <string>
using namespace std;

struct Position { int row, col; };

// ---------------- MAZE : holds the map (Encapsulation) ----------------
class Maze {
private:
    vector<string> grid;      // private: map data hidden from outside
    Position goal;

public:
    Maze(vector<string> g) {
        grid = g;
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'G') goal = {r, c};
    }

    bool isWall(int r, int c) {
        if (r < 0 || c < 0 || r >= (int)grid.size() || c >= (int)grid[0].size())
            return true;                    // outside the maze = treat as wall
        return grid[r][c] == '#';
    }

    bool isGoal(Position p) {
        return p.row == goal.row && p.col == goal.col;
    }

    Position getStart() {
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'S') return {r, c};
        return {0, 0};
    }

    int rows() { return grid.size(); }
    int cols() { return grid[0].size(); }

    void display(vector<Position> path) {
        vector<string> copy = grid;
        for (auto p : path)
            if (copy[p.row][p.col] == '.') copy[p.row][p.col] = '*';
        for (auto row : copy) cout << row << "\n";
    }
};

// ---------------- ROBOT : abstract class ----------------
class Robot {
protected:
    Maze* maze;
    Position pos;
    int cellsChecked = 0;     // how much work the robot did

    Position nextCell(Position p, int dir) {
        if (dir == 0) return {p.row - 1, p.col};   // UP
        if (dir == 1) return {p.row, p.col + 1};   // RIGHT
        if (dir == 2) return {p.row + 1, p.col};   // DOWN
        return {p.row, p.col - 1};                 // LEFT
    }

public:
    Robot(Maze* m) { maze = m; pos = m->getStart(); }
    virtual ~Robot() {}

    virtual void solve() = 0;                     // pure virtual: HOW to search
    virtual vector<Position> getBestPath() = 0;   // pure virtual: the answer found

    int getCellsChecked() { return cellsChecked; }
};

// ======================================================================
//  SmartRobot (child class)
//  Explores EVERY possible path from S to G using backtracking,
//  and keeps only the SHORTEST complete path it finds.
// ======================================================================
class SmartRobot : public Robot {
private:
    vector<vector<bool>> visited;
    vector<Position> currentPath;   // the path being built right now (acts as a stack)
    vector<Position> bestPath;      // the shortest complete path found so far

    // Tries every direction from the last cell in currentPath.
    // Calling itself (recursion) behaves like a stack: each call waits
    // for the deeper call to finish before it continues.
    void explore() {
        Position current = currentPath.back();

        if (maze->isGoal(current)) {
            if (bestPath.empty() || currentPath.size() < bestPath.size())
                bestPath = currentPath;        // found a shorter complete route
            return;
        }

        for (int dir = 0; dir < 4; dir++) {
            Position n = nextCell(current, dir);
            cellsChecked++;
            if (!maze->isWall(n.row, n.col) && !visited[n.row][n.col]) {
                visited[n.row][n.col] = true;
                currentPath.push_back(n);        // PUSH: step into this cell
                explore();                        // go deeper, try all of ITS options
                currentPath.pop_back();           // POP: undo the step (backtrack)
                visited[n.row][n.col] = false;    // un-mark, so other paths can reuse it
            }
        }
    }

public:
    SmartRobot(Maze* m) : Robot(m) {
        visited.assign(m->rows(), vector<bool>(m->cols(), false));
    }

    void solve() override {
        currentPath.push_back(pos);
        visited[pos.row][pos.col] = true;
        explore();
    }

    vector<Position> getBestPath() override { return bestPath; }
};

// ---------------- MAIN ----------------
int main() {
    vector<string> layout = {
        "###########",
        "#S........#",
        "#.##.###.##",
        "#....#....#",
        "#.##.#.##.#",
        "#....#....#",
        "##.#####.##",
        "#.........#",
        "#.##.#.##.#",
        "#....#...G#",
        "###########"
    };

    Maze maze(layout);
    SmartRobot robot(&maze);

    robot.solve();
    vector<Position> path = robot.getBestPath();

    if (path.empty()) {
        cout << "No path found.\n";
    } else {
        cout << "Best path found:\n";
        maze.display(path);
        cout << "Path length   : " << path.size() << " cells\n";
        cout << "Cells checked : " << robot.getCellsChecked() << "\n";
    }

    return 0;
}
