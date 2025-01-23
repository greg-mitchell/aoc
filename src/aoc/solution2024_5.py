from input import open_input
from collections import defaultdict, deque, namedtuple
from typing import Sequence, DefaultDict, Set, Iterable, Mapping, Optional

input = ""
with open_input(filename="input.txt") as f:
    input = f.read().strip()

## solution generated from claude

# Custom types
Rule = namedtuple('Rule', ['before', 'after'])
DependencyGraph = DefaultDict[int, Set[int]]
Update = list[int]
Updates = list[Update]
Rules = list[Rule]

def parse_input(lines: Iterable[str]) -> tuple[Rules, Updates]:
    """Parse input into rules and updates.
    
    Args:
        lines: Iterator of input lines containing rules and updates
        
    Returns:
        Tuple of (rules, updates) where rules is list of Rule objects
        and updates is list of number sequences to validate
    """
    rules: Rules = []
    updates: Updates = []
    reading_rules = True
    
    for line in lines:
        line = line.strip()
        if not line:  # Empty line separates rules from updates
            reading_rules = False
            continue
            
        if reading_rules:
            before, after = line.split('|')
            rules.append(Rule(int(before), int(after)))
        else:
            updates.append([int(x) for x in line.split(',')])
            
    return rules, updates


def build_dependency_graph(rules: Iterable[Rule]) -> DependencyGraph:
    """Build a complete dependency graph from all rules.
    
    Args:
        rules: Sequence of Rule objects representing ordering rules
        
    Returns:
        Graph as adjacency list where graph[a] contains all nodes that must come after a
    """
    graph: DependencyGraph = defaultdict(set)
    
    for rule in rules:
        graph[rule.before].add(rule.after)
        # Ensure nodes with no outgoing edges are in the graph
        if rule.after not in graph:
            graph[rule.after] = set()
            
    return graph


def is_valid_order(updates: Iterable[int], graph: Mapping[int, Set[int]]) -> bool:
    """Check if a given order satisfies the dependency rules.
    
    Args:
        updates: Sequence of numbers in the order to validate
        graph: Dependency graph where graph[a] contains numbers that must come after a
        
    Returns:
        True if the order is valid, False otherwise
    """
    # Convert the given order to position mapping for O(1) lookup
    position = {num: i for i, num in enumerate(updates)}
    update_set = set(updates)
    
    # Check each pair of numbers in the update
    for start in updates:
        # Only check rules where both numbers are in this update
        for end in graph[start] & update_set:
            if position[start] > position[end]:
                return False
                
    return True


## claude-generated for pt 2

from dataclasses import dataclass

@dataclass
class Correction:
    original: list[int]
    corrected: list[int]
    swaps: list[tuple[int, int]]  # Positions that need to be swapped

def topological_sort(nodes: Set[int], graph: Mapping[int, Set[int]]) -> Optional[list[int]]:
    """Perform topological sort on the given nodes using Kahn's algorithm.
    
    Returns None if graph has cycles.
    """
    # Build in-degree mapping
    in_degree: DefaultDict[int, int] = defaultdict(int)
    for node in nodes:
        for neighbor in graph[node] & nodes:
            in_degree[neighbor] += 1
    
    # Initialize queue with nodes that have no dependencies
    queue = deque([node for node in nodes if in_degree.get(node, 0) == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Reduce in-degree for all neighbors
        for neighbor in graph[node] & nodes:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If we couldn't process all nodes, there must be a cycle
    if len(result) != len(nodes):
        return None
        
    return result

def get_minimum_swaps(source: list[int], target: list[int]) -> list[tuple[int, int]]:
    """Calculate minimum swaps needed to transform source into target."""
    # Create position mapping for target list
    target_pos = {num: i for i, num in enumerate(target)}
    
    # Copy source array to track swaps
    src_cpy = source.copy()
    swaps = []
    
    for i in range(len(src_cpy)):
        while target_pos[src_cpy[i]] != i:
            swap_idx = target_pos[src_cpy[i]]
            # Record the swap
            swaps.append((i, swap_idx))
            # Perform the swap
            src_cpy[i], src_cpy[swap_idx] = src_cpy[swap_idx], src_cpy[i]
            
    return swaps

def correct_invalid_update(update: list[int], graph: Mapping[int, Set[int]]) -> Optional[Correction]:
    """Generate a corrected version of an invalid update using minimum swaps.
    
    Returns None if no valid ordering exists (due to cycles).
    """
    # Get topologically sorted order
    sorted_order = topological_sort(set(update), graph)
    if sorted_order is None:
        return None
        
    # Calculate minimum swaps needed
    swaps = get_minimum_swaps(update, sorted_order)
    
    return Correction(
        original=update,
        corrected=sorted_order,
        swaps=swaps
    )

# Example usage (continuing from previous code)
def process_updates(input_lines: Sequence[str]) -> tuple[list[int], dict[int, Correction]]:
    """Process all updates, identifying valid ones and correcting invalid ones."""
    rules, updates = parse_input(iter(input_lines))
    graph = build_dependency_graph(rules)
    
    valid_updates = []
    corrections: dict[int, Correction] = {}
    
    for i, update in enumerate(updates, 1):
        if is_valid_order(update, graph):
            valid_updates.append(i)
        else:
            correction = correct_invalid_update(update, graph)
            if correction:
                corrections[i] = correction
    
    return valid_updates, corrections


## driver code

def validate_updates(input_lines: Iterable[str]) -> tuple[Updates, list[Correction]]:
    """Find which updates satisfy all ordering rules.
    
    Args:
        input_lines: Sequence of strings containing rules and updates
        
    Returns:
        List of indices (1-based) of valid updates
    """
    # Parse input
    rules, updates = parse_input(input_lines)
    
    # Build the complete dependency graph once
    graph = build_dependency_graph(rules)
    
    # Check each update against the graph
    valid_updates = []
    corrections: list[Correction] = []

    for _i, update in enumerate(updates, 1):
        if is_valid_order(update, graph):
            valid_updates.append(update)
        else:
            correction = correct_invalid_update(update, graph)
            if correction:
                corrections.append(correction)
    
    return valid_updates, corrections


def sum_middle(updates: Updates) -> int:
    sum = 0
    for u in updates:
        assert len(u) > 0
        sum += u[int(len(u) / 2)]
    return sum


valid, corrections = validate_updates(input.splitlines())
solution_pt1 = sum_middle(valid)
solution_pt2 = sum_middle([c.corrected for c in corrections])
print(f"Valid updates are: {solution_pt1}")
print(f"Sum of corrected updates are: {solution_pt2}")