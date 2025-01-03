from input import open_input
from collections import defaultdict
import bisect
import re

def get_sorted_lists():
    """Opens the input for this problem and reads the lists into
    a sorted left and right lists, which are returned"""

    left_list, right_list = [], []
    with open_input() as inFile:
        for line_number, line in enumerate(inFile, 1):
            if not line.strip():
                # Skip empty lines
                continue

            match = re.match(r'(\d+)\s+(\d+)', line)
            if not match:
                raise ValueError(f"Unexpected format for line {line_number}: {line}")
            
            l = int(match.group(1))
            r = int(match.group(2))
            bisect.insort(left_list, l)
            bisect.insort(right_list, r)

        assert len(left_list) == len(right_list)
        assert len(left_list) != 0

    return left_list, right_list
    

left_list, right_list = get_sorted_lists()

def dist_metric(l, r):
    sum_dist = 0
    for i in range(len(left_list)):
        dist = left_list[i] - right_list[i]
        dist = abs(dist)
        sum_dist += dist

    return sum_dist

print(f"pt 1: distance = {dist_metric(left_list, right_list)}")

def similarity_metric(l, r):
    d = defaultdict(lambda: 0)
    for n in r:
        d[n] += 1

    similarity = 0
    for n in l:
        similarity += n * d[n]

    return similarity

print(f"pt 2: similarity = {similarity_metric(left_list, right_list)}")

# output (correct):
# pt 1: distance = 2344935
# pt 2: similarity = 27647262