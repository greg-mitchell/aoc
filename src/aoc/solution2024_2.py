from input import open_input
from collections.abc import Callable

type Report = list[int]

def get_reports() -> list[Report]:
    """Open the input file and extract as a list of reports."""

    reports = []
    with open_input() as in_file:
        for l in in_file:
            reports.append([int(level) for level in l.split()])

    return reports


reports = get_reports()

def classify_level_diff(diff: int, first_gradient: int) -> bool:
    if diff == 0:
        # Levels must be increasing or decreasing 
        return False
    if diff < 0 and first_gradient > 0:
        # Expected this report to have monotonically increasing levels
        return False
    if diff > 0 and first_gradient < 0:
        # Expected this report to have monotonically decreasing levels
        return False
    
    if abs(diff) > 3:
        # Levels must differ by at least 1 and at most 3
        return False
    
    return True


def classify_pt1(report: Report) -> bool:
    """Returns true if the report is safe"""

    if len(report) < 2:
        raise ValueError(f"Expected reports to have at least 2 levels, was: {report}")
    
    first_gradient = report[1] - report[0]
    for i in range(1, len(report)):
        diff = report[i] - report[i - 1]
        
        if not classify_level_diff(diff, first_gradient):
            return False
        
    return True


def count_safe(rs: list[Report], classifier: Callable[[Report], bool]) -> int:
    cnt = 0
    for r in rs:
        if classifier(r):
            cnt += 1

    return cnt


print(f"pt 1: safe reports = {count_safe(reports, classify_pt1)}")

def classify_pt2(report: Report) -> bool:

    first_gradient = report[1] - report[0]
    safe = True
    for i in range(1, len(report)):
        diff = report[i] - report[i - 1]
        
        if not classify_level_diff(diff, first_gradient):
            safe = False
            break

    if safe:
        return True
    
    # Attempt to classify again by removing one level in turn, this time without removals
    for i in range(len(report)):
        dampened_report = report[:i] + report[i+1:]
        if classify_pt1(dampened_report):
            # We found a level which if removed will make the report safe
            return True
        
    return False

print(f"pt 2: safe reports = {count_safe(reports, classify_pt2)}")

# output (correct):
# pt 1: safe reports = 585
# pt 2: safe reports = 626