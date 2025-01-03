from input import open_input
import re
import sys

mem_raw = ""
with open_input() as f:
    mem_raw = f.read()

valid_mul_pattern = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')

# MulInput is a tuple of the index of the start of the mul command then the two operands.
type MulInput = tuple[int, int, int]
# Positions is a list of indices corresponding to the start of a match
type Positions = list[int]

def get_mul_inputs(s: str) -> list[MulInput]:
    """Gets all valid multiply instructions from the raw memory input, s.
    A valid mul instruction looks like mul(123,5)"""
    match_iter = re.finditer(valid_mul_pattern, s)
    mul_inputs = [(m.start(), int(m.group(1)), int(m.group(2))) for m in match_iter]

    if not mul_inputs:
        raise ValueError("no valid mul commands in input")
    
    return mul_inputs


def compute_valid(mul_inputs: list[MulInput]) -> int:
    sum = 0
    for m in mul_inputs:
        sum += m[1] * m[2]

    return sum


mul_inputs = get_mul_inputs(mem_raw)
print(f"pt 1: sum of valid muls: {compute_valid(mul_inputs)}")


def get_dos(s: str) -> Positions:
    """Gets the indices of the start of all `do()` commands in the raw memory input"""
    return [m.start() for m in re.finditer(r'do\(\)',s)]


def get_donts(s: str) -> Positions:
    """Gets the indices of the start of all `dont()` commands in the raw memory input"""
    return [m.start() for m in re.finditer(r"don't\(\)",s)]


def compute_valid_pt2(mul_inputs: list[MulInput], dos: Positions, donts: Positions) -> int:
    sum = 0
    enabled = True
    i_mul = 0
    i_do = 0
    i_dont = 0

    while i_mul < len(mul_inputs):
        next_matches = [(mul_inputs[i_mul], 'm'), 
                        ((dos[i_do] if i_do < len(dos) else sys.maxsize,), 'd'),
                        ((donts[i_dont] if i_dont < len(donts) else sys.maxsize,), 'n')]
        next_matches.sort(key=lambda m: m[0][0])
        match next_matches[0]:
            case ((_pos, op1, op2), 'm'):
                if enabled:
                    sum += op1 * op2
                i_mul += 1
            case ((pos,), 'd'):
                enabled = True
                i_do += 1
            case ((pos,), 'n'):
                enabled = False
                i_dont += 1
    
    return sum


print(f"pt 2: sum of muls: {compute_valid_pt2(mul_inputs, get_dos(mem_raw), get_donts(mem_raw))}")

# output (correct):
# pt 1: sum of valid muls: 171183089
# pt 2: sum of muls: 63866497