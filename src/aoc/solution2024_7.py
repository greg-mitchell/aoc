from input import open_input
import re
from dataclasses import dataclass
from enum import Enum
import functools

input = ""
with open_input(filename="input.txt") as f:
    input = f.read().strip()

@dataclass
class Equation():
    value: int
    operands: list[int]


class Op(Enum):
    ADD = 1
    MUL = 2
    CON = 3

def parse_input(input: str) -> list[Equation]:
    eqs: list[Equation] = []
    for i, l in enumerate(input.splitlines()):
        match = re.match(r'(?P<value>\d+):( (?P<operand>\d+))+', l)
        if match is None:
            raise ValueError(f"Line {i + 1} was in an unexpected format: {l}")
        
        value, op_str = l.split(':')
        operands = op_str.split(' ')

        assert len(operands) > 1, "There should be at least two operands"
        
        eqs.append(Equation(
            int(value), 
            # operands has a trailing space, which we need to ignore
            [int(op) for op in operands[1:]]))

    return eqs


def satisfies(eq: Equation, available_ops: list[Op] = [Op.ADD, Op.MUL]) -> bool:
    def foldr(ops: list[Op]) -> int:
        assert len(ops) == len(eq.operands) - 1
        acc = eq.operands[0]
        for operand_i in range(1, len(eq.operands)):
            op = ops[operand_i - 1]
            operand = eq.operands[operand_i]
            match op:
                case Op.ADD:
                    acc += operand
                case Op.MUL:
                    acc *= operand
                case Op.CON:
                    acc = int(f"{acc}{operand}")
        return acc     

    def satisfies_recur(ops: list[Op]) -> bool:
        if len(ops) == len(eq.operands) - 1:
            return foldr(ops) == eq.value
        
        for op in available_ops:
            if satisfies_recur([*ops, op]):
                return True
            continue

        return False
    
    return satisfies_recur([])


def sum_eq_values(eqs: list[Equation]) -> int:
    acc = 0
    for eq in eqs:
        acc += eq.value
    return acc


eqs = parse_input(input)
satisfying_eqs = [eq for eq in eqs if satisfies(eq, [Op.ADD, Op.MUL, Op.CON])]

# print(f"eqs: {parse_input(input)}")
# print(f"Satisfying equations: {satisfying_eqs}")
print(f"Sum of satisfying: {sum_eq_values(satisfying_eqs)}")