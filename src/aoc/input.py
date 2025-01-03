from pathlib import Path
import os
import re
import sys

def _get_solution_year_and_number(f):
    """Extract year and problem numbers from an AoC solution filename.
    Expected format: solution2024_1.py or similar
    Returns: (year, problem) tuple of integers
    """
    # Get the entry point script path
    script_path = os.path.basename(sys.argv[0])
    
    # Extract numbers using regex
    # Matches 'solution2024_1.py' -> groups(2024, 1)
    pattern = r'solution(\d{4})_(\d+)\.py'
    match = re.match(pattern, script_path)
    
    if not match:
        raise ValueError(f"Script filename '{script_path}' doesn't match expected format 'solutionYYYY_D.py'")
    
    year = int(match.group(1))
    problem = int(match.group(2))
    
    return year, problem

def open_input(f=sys.argv[0]):
    """Extract year and day numbers from an AoC solution filename and opens the file.
    Expected format: solution2024_1.py or similar
    Returns: open input file
    """
    year, problem = _get_solution_year_and_number(f)
    
    # Find project root (parent of src directory)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(f)))
    
    # Construct input file path
    input_path = os.path.join(project_root, 'resources', str(year), str(problem), 'input.txt')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(input_path), exist_ok=True)
    return open(input_path, 'r')

