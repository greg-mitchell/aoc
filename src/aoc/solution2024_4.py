from input import open_input
from collections import defaultdict, OrderedDict
from itertools import product

import regex
import sys

word_search = ""
with open_input() as f:
    word_search = f.read().strip()

def get_width(ws: str) -> int:
    lines = ws.splitlines()
    first_line_len = len(lines[0])
    for line_num, line in enumerate(lines, 1):
        if len(line) != first_line_len:
            raise ValueError(f"Expected all lines to have length {first_line_len}, but line {line_num} had length {len(line)}")
        
    return first_line_len

line_width = get_width(word_search)

def strip_newlines(ws: str) -> str:
    return regex.compile(r'\n|\r').sub('', ws)


type NamedPatterns = dict[str, str|regex.Pattern]


def build_skip_col(offset: int, newlines_are_stripped=True) -> str:
    """Builds a pattern the skips 1 col down, plus an offset (which may be negative)."""
    
    # if newlines are stripped, skipping line_width will skip the char 1 row down 
    newline_adjustment = -1 if newlines_are_stripped else 0
    return r'.{' + f"{line_width - 1 + offset}" + '}' 


def build_patterns() -> NamedPatterns:
    """Line width is the width without carriage returns or newlines."""
    forward_seq = ['X', 'M', 'A', 'S']      # sequence of chars in XMAS forwards
    backward_seq = ['S', 'A', 'M', 'X']     # sequence of chars in XMAS backwards
    
    # upon analysis, this won't work because it allows wrapping
    # it's not obvious how to handle patterns that span multiple lines but can't wrap
    return {
        'forward': ''.join(forward_seq),
        'backward': ''.join(backward_seq),
        'down': build_skip_col(0).join(forward_seq),
        'up': build_skip_col(0).join(backward_seq),
        'down_right': build_skip_col(+1).join(forward_seq),
        'down_left': build_skip_col(-1).join(forward_seq),
        'up_right': build_skip_col(-1).join(backward_seq),
        'up_left': build_skip_col(+1).join(backward_seq),
    }
    

patterns = build_patterns()

print(f"debug: line_width=[{line_width}], patterns=[{patterns}]")

def count_matches(ws: str, patterns: NamedPatterns) -> int:
    count = 0
    for name, pattern in patterns.items():
        matches_for_pattern = 0
        # print(f"matching pattern {name}: [{pattern}]...")
        for m in regex.finditer(pattern, ws, overlapped=True, flags=regex.DOTALL):
            matches_for_pattern += 1
            # print(f"{m.span()}")
        print(f"found {matches_for_pattern} matches for {name}")
        count += matches_for_pattern

    return count


def fuglede_solution_pt1(ws: str):
    """ws is assumed to be the raw input as a string
    Copied from https://github.com/fuglede/adventofcode/blob/master/2024/day04/solutions.py
    for debugging purposes."""
    ls = ws.strip().splitlines()
    
    # holds a map of index to char for each item in the word map
    boardz = defaultdict(str) 
    # real part is the row, imag is the col
    boardz |= {i + 1j * j: x for i, l in enumerate(ls) for j, x in enumerate(l)}
    # set of basis vectors for valid directions. (0,0) will never produce XMAS because XMAS has different letters
    octdir = {i + 1j * j for (i, j) in set(product((-1, 0, 1), (-1, 0, 1))) - {(0, 0)}}

    # original solution. break apart for debugging
    # Part 1
    # print(
    #     sum(
    #         [boardz[z + i * dz] for i in range(4)] == ["X", "M", "A", "S"]
    #         for z in list(boardz.keys())
    #         for dz in octdir
    #     )
    # )
    count_by_basis = defaultdict(int)
    for z in list(boardz.keys()):
        for dz in octdir:
            # offset from position z by 0..3 * the basis vector
            if [boardz[z + i * dz] for i in range(4)] == ["X", "M", "A", "S"]:
                count_by_basis[dz] += 1
    
    human_readable_basis = OrderedDict([
        (0+1j, "forward"),
        (0-1j, "backward"),
        (1+0j, "down"),
        (-1+0j, "up"),
        (1+1j, "down_right"),
        (1-1j, "down_left"),
        (-1+1j, "up_right"),
        (-1-1j, "up_left"),
        ])
    count = 0 
    for dz, human_readable_name in human_readable_basis.items():
        print(f"found {count_by_basis[dz]} matches for {human_readable_name}")
        count += count_by_basis[dz]
    print(f"found {count} xmas")


print(f"pt 1: XMAS found: {count_matches(strip_newlines(word_search), patterns)}")
print("debugging with alternate solution:")
fuglede_solution_pt1(word_search)

def build_patterns_pt2() -> NamedPatterns:
    non_newline_pattern = r'[^\n]'
    # the direction is the arrow from Ms to Ss
    def build_x_mas(corners: tuple[str, str, str, str]) -> str:
        """Builds a pattern matching the x-mas from the four corners starting top-left
        and proceeding clockwise"""
        return corners[0] + non_newline_pattern + corners[1] + build_skip_col(-1, False) + \
        non_newline_pattern + 'A' + build_skip_col(0, False) + \
        corners[3] + non_newline_pattern + corners[2]

    right = build_x_mas(('M', 'S', 'S', 'M'))
    up = build_x_mas(('S', 'S', 'M', 'M'))
    down = build_x_mas(('M', 'M', 'S', 'S'))
    left = build_x_mas(('S', 'M', 'M', 'S'))
    
    return {
        'right': right,
        'up': up,
        'down': down,
        'left': left,
    }


patterns_pt2 = build_patterns_pt2()
print(f"x-mas patterns: {patterns_pt2}")
print(f"pt 2: X-MAS found: {count_matches(word_search, patterns_pt2)}")


