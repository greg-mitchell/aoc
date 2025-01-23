# allows self-referential member annotations
from __future__ import annotations

from input import open_input
from enum import Enum, StrEnum
from numbers import Complex
from dataclasses import dataclass

input = ""
with open_input(filename="input.txt") as f:
    input = f.read().strip()

"""
the paths are chaotic (large differences from small initial condition changes),
which suggests the best way to count the positions is to simulate the path of 
the guard directly

the most natural representation for a discrete grid like this is a 2-d array.
in python there's a neat representation trick where we can use complex numbers.
The benefits to this are: 
- one-operation calculation of neighboring cells

In this representation, we mirror the 2-d approach by having the first scalar (the
real part) correspond to the row, and the imaginary part represent the column

important considerations will be bounds-checking to find when the guard has left
the area
"""

class MapLabel(StrEnum):
    INVALID = '!'
    EMPTY = '.'
    OBSTACLE = '#'
    TRAVERSED = 'X'
    UP_GUARD = '^'
    RIGHT_GUARD = '>'
    DOWN_GUARD = 'v'
    LEFT_GUARD = '<'

    # There are four directions, so the maximum number of times
    # the guard can enter a square WITHOUT there being a loop is 4
    TRAVERSED_ONE = '1'
    TRAVERSED_TWO = '2'
    TRAVERSED_THREE = '3'
    TRAVERSED_FOUR = '4'

    def turn(self):
        match self:
            case MapLabel.UP_GUARD:
                return MapLabel.RIGHT_GUARD
            case MapLabel.RIGHT_GUARD:
                return MapLabel.DOWN_GUARD
            case MapLabel.DOWN_GUARD:
                return MapLabel.LEFT_GUARD
            case MapLabel.LEFT_GUARD:
                return MapLabel.UP_GUARD
            case _:
                return None
            

    def step(self) -> Complex | None:
        match self:
            case MapLabel.UP_GUARD:
                return -1+0j
            case MapLabel.RIGHT_GUARD:
                return 1j
            case MapLabel.DOWN_GUARD:
                return 1+0j
            case MapLabel.LEFT_GUARD:
                return -1j
            case _:
                return None

            
    def is_guard(self)-> bool:
        return self in {
            MapLabel.UP_GUARD, 
            MapLabel.RIGHT_GUARD, 
            MapLabel.DOWN_GUARD,
            MapLabel.LEFT_GUARD
            }


type GridRepr = dict[Complex, MapLabel]


@dataclass
class Grid():
    repr: GridRepr
    guard_pos: Complex
    row_count: int
    col_count: int

    def __str__(self) -> str:
        return '\n'.join([''.join([self.repr[row + 1j * col] for col in range(self.col_count)]) for row in range(self.row_count)])


    def copy(self) -> Grid:
        return Grid(self.repr.copy(), self.guard_pos, self.row_count, self.col_count)


    class NextResult(Enum):
        INVALID = 0
        OOB = 1
        TURN = 2
        STEP = 3
        STEP_PREV_TRAVERSED = 4
        LOOP_FOUND = 5


    def pos_to_str(pos: Complex) -> str:
        return f"row {int(pos.real)}, col {int(pos.imag)}"


    def next(self, count_traversals: bool = False) -> tuple[Grid, NextResult]:
        """Returns self modified by the guard taking the next step and/or turning.
        Callers should check the result is in bounds after this call to determine
        whether subsequent calls to next will modify the grid.
        """
        curr = self.repr[self.guard_pos]
        assert curr.is_guard(), f"Expected a guard character at {Grid.pos_to_str(self.guard_pos)}, was {curr}"

        next_pos = self.guard_pos + curr.step()
        if not self.pos_in_bounds(next_pos):
            # Don't insert new entries outside the bounds of the grid
            self.repr[self.guard_pos] = MapLabel.TRAVERSED
            self.guard_pos = next_pos
            return self, Grid.NextResult.OOB
        
        result = Grid.NextResult.INVALID
        match self.repr[next_pos]:
            case MapLabel.EMPTY:
                # Continue travelling in the same direction
                self.repr[next_pos] = curr
                self.repr[self.guard_pos] = MapLabel.TRAVERSED if not count_traversals else MapLabel.TRAVERSED_ONE
                self.guard_pos = next_pos
                result = Grid.NextResult.STEP
            case MapLabel.TRAVERSED:
                # Continue travelling in the same direction, but don't say it's a new step
                self.repr[next_pos] = curr
                self.repr[self.guard_pos] = MapLabel.TRAVERSED
                self.guard_pos = next_pos
                result = Grid.NextResult.STEP_PREV_TRAVERSED
            case MapLabel.TRAVERSED_ONE:
                # Same as above, but increment
                self.repr[next_pos] = curr
                self.repr[self.guard_pos] = MapLabel.TRAVERSED_TWO
                self.guard_pos = next_pos
                result = Grid.NextResult.STEP_PREV_TRAVERSED
            case MapLabel.TRAVERSED_TWO:
                # Same as above, but increment
                self.repr[next_pos] = curr
                self.repr[self.guard_pos] = MapLabel.TRAVERSED_THREE
                self.guard_pos = next_pos
                result = Grid.NextResult.STEP_PREV_TRAVERSED
            case MapLabel.TRAVERSED_THREE:
                # Same as above, but increment
                self.repr[next_pos] = curr
                self.repr[self.guard_pos] = MapLabel.TRAVERSED_FOUR
                self.guard_pos = next_pos
                result = Grid.NextResult.STEP_PREV_TRAVERSED
            case MapLabel.TRAVERSED_FOUR:
                return self, Grid.NextResult.LOOP_FOUND
            case MapLabel.OBSTACLE:
                # Don't change positions, turn instead
                self.repr[self.guard_pos] = curr.turn()
                result = Grid.NextResult.TURN
            case _:
                raise ValueError(f"Unexpected value {self.repr[next_pos]} at {Grid.pos_to_str(next_pos)}")

        return self, result
    
    
    def in_bounds(self) -> bool:
        return self.pos_in_bounds(self.guard_pos)


    def pos_in_bounds(self, pos: Complex) -> bool:
        return pos.real >= 0 and \
            pos.imag >= 0 and \
            pos.real < self.row_count and \
            pos.imag < self.col_count


def to_grid(input: str) -> Grid:
    g: GridRepr = {row + col * 1j: MapLabel(c)
                   for row, line in enumerate(input.splitlines())
                   for col, c in enumerate(line)}
    
    lines = input.splitlines()
    guard_pos = -1-1j
    row_count = len(lines)
    col_count = len(lines[0])

    for row, line in enumerate(lines):
        for col, c in enumerate(line):
            # todo check all lines have the same length
            if not c in MapLabel:
                raise ValueError(f"Invalid value {c} at row {row}, col {col}")
            
            label = MapLabel(c)
            pos = row + 1j * col
            if label.is_guard() and guard_pos != -1-1j:
                raise ValueError(f"Two guards found, at row {guard_pos.real}, col {guard_pos.imag}, and at row {pos.real}, col {pos.imag}")
            if label.is_guard():
                guard_pos = pos

            g[pos] = label
    
    return Grid(g, guard_pos, row_count, col_count)


def run_grid(g: Grid, count_traversals: bool = False) -> int:
    """Simulates the movement of the guard in the grid until it leaves the bounds.
    This mutates the grid.
    
    - Returns the count of squares traversed.
    - If the guard loops, raises a ValueError."""

    traversed = 0
    while (grid_and_result := g.next(count_traversals)) and \
         grid_and_result[1] not in {Grid.NextResult.OOB, Grid.NextResult.INVALID, Grid.NextResult.LOOP_FOUND}:
        _g, res = grid_and_result
        traversed += 1 if res == Grid.NextResult.STEP else 0

    # include the final step
    return traversed + 1 if grid_and_result[1] == Grid.NextResult.OOB else -1


def place_obstacles(orig_grid: Grid, final_grid: Grid) -> list[Complex]:
    traversed_positions = [pos for pos, label in final_grid.repr.items() if label == MapLabel.TRAVERSED and pos != orig_grid.guard_pos]

    obstacles: list[Complex] = []
    for pos in traversed_positions:
        g = orig_grid.copy()
        g.repr[pos] = MapLabel.OBSTACLE
        if run_grid(g, True) == -1:
            # print(f"Found loop with obstacle at {Grid.pos_to_str(pos)}")
            obstacles.append(pos)
        
    return obstacles


g = to_grid(input)
steps = run_grid(final_grid := g.copy())
print(f"Traversed {steps} steps.")
# print(f"Final Grid:\n{g}")

obstacles = place_obstacles(g, final_grid)
print(f"Found {len(obstacles)} obstacle placements that would result in a loop")
# print(f"Placements: {[Grid.pos_to_str(o) for o in obstacles]}")

# Outputs 1577, that's too high. What's the issue?