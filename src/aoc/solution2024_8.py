
from collections import defaultdict
from dataclasses import dataclass, field
from input import open_input
from itertools import combinations, permutations
from typing import Mapping, Set

# real part is row, imaginary is col
type Pos = complex

# single-char representing unique frequencies
type Antenna = str

ROW_DIM = 0
COL_DIM = 1

@dataclass
class Grid():
    # rows, columns
    dim: tuple[int, int]
    antennae: Mapping[Pos, Antenna] = field(default_factory=dict)
    freqs: Set[Antenna] = field(default_factory=set)

    def to_pos(self, row: int, col: int) -> Pos:
        assert row >= 0, f"Invalid position {row}, {col}: row must be positive"
        assert col >= 0, f"Invalid position {row}, {col}: col must be positive"
        assert row < self.dim[ROW_DIM], f"Invalid position {row}, {col}: row must be within dimensions {self.dim}"
        assert col < self.dim[COL_DIM], f"Invalid position {row}, {col}: col must be within dimensions {self.dim}"

        return row + 1j * col
    
    def in_bounds(self, pos: Pos) -> bool:
        return pos.real >= 0 and pos.real < self.dim[ROW_DIM] \
            and pos.imag >= 0 and pos.imag < self.dim[COL_DIM]


    def place_antennae(self, lines: list[list[str]], override_antenna: str | None = None):
        assert len(lines) == self.dim[ROW_DIM]
        assert len(lines[0]) == self.dim[COL_DIM]

        for pos, antenna in self.antennae.items():
            lines[int(pos.real)][int(pos.imag)] = antenna if override_antenna is None else override_antenna


def parse_input(input: str) -> Grid:
    lines = input.splitlines()

    assert len(lines) > 0, f"There must be at least one line"
    assert len(lines[0]) > 0, f"Lines must have at least one position"
    # todo assert all lines same width

    dim = len(lines), len(lines[0])
    g = Grid(dim)

    for row, line in enumerate(lines):
        for col, ch in enumerate(line):
            match ch:
                case '.':
                    continue
                case _:
                    g.freqs.add(ch)
                    g.antennae[g.to_pos(row, col)] = ch

    # todo freeze g somehow
    return g


def freq_to_pos(g: Grid) -> Mapping[Antenna, list[Pos]]:
    result = defaultdict(list)
    for pos, freq in g.antennae.items():
        result[freq].append(pos)
    return result


def distance(p1: Pos, p2: Pos) -> Pos:
    """Calculates a distance vector (represented as a Pos) between two positions"""
    return p2 - p1


def calculate_antinodes(g: Grid) -> Grid:
    """Find antinodes for the grid, and returns a copy of grid where the
    antennae field is set with antinode positions.
    
    If antinodes of different frequencies overlap, the lexographically greatest
    frequency will be set.
    
    An antinode is a position at +/- l from a pair of antennae, where l is the distance
    vector between the antennae.
    """
    f_to_p = freq_to_pos(g)

    an_grid = Grid(g.dim, freqs=g.freqs)
    for freq in sorted(g.freqs):
        for p1, p2 in combinations(f_to_p[freq], 2):
            d = distance(p1, p2)
            antinodes = [p1 - d, p2 + d]
            for an in antinodes:
                if an_grid.in_bounds(an):
                    an_grid.antennae[an] = freq

    return an_grid


def calculate_antinodes_pt2(g: Grid) -> Grid:
    """Find antinodes for the grid, and returns a copy of grid where the
    antennae field is set with antinode positions.
    
    If antinodes of different frequencies overlap, the lexographically greatest
    frequency will be set.
    
    An antinode is a position at +/- l*n from a pair of antennae, where l is the distance
    vector between the antennae, and n is a positive integer. 
    """
    f_to_p = freq_to_pos(g)

    an_grid = Grid(g.dim, freqs=g.freqs)
    for freq in sorted(g.freqs):
        for p1, p2 in permutations(f_to_p[freq], 2):
            basis = distance(p1, p2)
            n = 0
            while an_grid.in_bounds(an := p2 + basis * n):
                an_grid.antennae[an] = freq   
                n += 1                 

    return an_grid


def render_antinodes(grid: Grid, antinode_grid: Grid) -> str:
    """Returns a string representation of the grid, where antinodes are marked with '#'.
    
    Assumes that the antinode_grid has already deduplicated positions in a resonable way."""

    dim = grid.dim
    result = [['.' for _j in range(dim[COL_DIM])] for _i in range(dim[ROW_DIM])]
    antinode_grid.place_antennae(result, '#')
    grid.place_antennae(result)

    return '\n'.join([''.join(line) for line in result])


def count_antinodes(antinode_grid: Grid) -> int:
    return len(antinode_grid.antennae)


def main():
    input = ""
    with open_input(filename="input.txt") as f:
        input = f.read().strip()

    g = parse_input(input)
    an_grid = calculate_antinodes_pt2(g)

    # print(f"parsed grid:\t{g}")
    # print(f"antinode grid:\t{an_grid}")
    print(f"Antinode count: {count_antinodes(an_grid)}")

if __name__ == '__main__':
    main()