from __future__ import annotations

from collections import defaultdict, deque, namedtuple
from dataclasses import dataclass, field
import heapq
from input import open_input
from typing import Mapping

Dim = namedtuple('Dim', ['row', 'col'])
TrailScores = dict[Dim, int]
TRAILHEAD_LEVEL = 0
PEAK_LEVEL = 9

@dataclass
class Map():
    dim: Dim
    repr: list[list[int]] = field(default_factory=list)

    def from_str(input: str) -> Map:
        # todo check input matches regex \d+
        lines = input.splitlines()
        assert len(lines) > 0, f"Expected input to have at least 1 line, was {len(lines)}"
        # todo check all rows are the same length

        return Map(
            dim=Dim(len(lines), len(lines[0])),
            repr=[[int(c) for c in line] for line in lines])
    

    def get(self, pos: Dim) -> int | None:
        if pos.row < 0 or pos.row >= self.dim.row \
            or pos.col < 0 or pos.col >= self.dim.col:
            return None
        return self.repr[pos.row][pos.col]

    def level_positions(self, level) -> list[Dim]:
        """Returns a list of (row, col) indices where the value at that position
        is the topographic level
        """
        return [Dim(row, col) 
                for row in range(self.dim.row) 
                for col in range(self.dim.col) 
                if self.repr[row][col] == level]


    def _get_neighbors(self, curr: Dim) -> list[Dim]:
        curr_val = self.get(curr)
        if curr_val is None:
            return []

        neighbors = [
            # only the non-diagonal neighbors are considered
            Dim(curr.row - 1, curr.col),
            Dim(curr.row + 1, curr.col),
            Dim(curr.row, curr.col - 1),
            Dim(curr.row, curr.col + 1),
        ]
        return [n for n in neighbors
                if (n_val := self.get(n)) is not None and n_val == curr_val + 1]
    

    def find_trails(self, count_all_paths = False) -> TrailScores:
        """Finds all trailheads and scores them by the number of reachable peaks"""
        trailheads = self.level_positions(TRAILHEAD_LEVEL)
        peaks = set(self.level_positions(PEAK_LEVEL))

        result: dict[Dim, int] = dict()
        q: deque[Dim] = deque()
        found_peaks: set[Dim] = set()
        for th in trailheads:
            # reset iteration vars
            trails = 0
            q.clear()
            found_peaks.clear()

            # initialize
            q.append(th)

            # dfs
            while len(q) > 0:
                # consider next position
                curr = q.pop()
                if curr in peaks:  
                    if curr in found_peaks and not count_all_paths:
                        continue
                    # we found a peak, add the trail count
                    trails += 1
                    found_peaks.add(curr)
                    continue
                
                # add all neighbors that follow the trail rule
                for n in self._get_neighbors(curr):
                    q.append(n)
            
            # process result
            result[th] = trails
        return result

    
    def find_trails_dijkstra(self) -> TrailScores:
        """Finds all trailheads and scores them by the number of reachable peaks."""

        trailheads = self.level_positions(TRAILHEAD_LEVEL)
        peaks = set(self.level_positions(PEAK_LEVEL))

        Node = namedtuple('Node', ['dist', 'pos'])

        # many-to-many Dijkstra is reducible to running Dijkstra from each source.
        def dijkstra_from_source(source: Dim) -> set[Dim]:
            """Run Dijkstra's algorithm from a single source.
            Returns set of all reachable positions."""
            distances = defaultdict(lambda: float('inf'))
            distances[source] = 0
            visited: set[Pos] = set()
            # since python tuples use composite value semantics, the natural ordering of
            # distance than position is used for the heap constraint.
            pq = [Node(0, source)]
            
            while pq:
                current_dist, current_pos = heapq.heappop(pq)
                
                if current_pos in visited:
                    continue
                    
                visited.add(current_pos)
                
                for neighbor in self._get_neighbors(current_pos):
                    if neighbor not in visited:
                        new_dist = current_dist + 1
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            heapq.heappush(pq, Node(new_dist, neighbor))
            
            return visited
        
        return {th: len([p
                         for p in dijkstra_from_source(th)
                         if self.get(p) == PEAK_LEVEL])
                for th in trailheads
                }
        


    def sum_trails(self, trails: TrailScores) -> int:
        result = 0
        for _pos, val in trails.items():
            result += val
        return result
        

def setup():
    global g_map
    input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
""".strip()
    with open_input() as f:
        input = f.read().strip()
    g_map = Map.from_str(input)


def dfs_find_trails():
    trails = g_map.find_trails()


def dijkstra_find_trails():
    trails = g_map.find_trails_dijkstra()


if __name__ == '__main__':
    input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
""".strip()
    with open_input() as f:
        input = f.read().strip()
    m: Map = Map.from_str(input)
    # setup()
    # find_trails()

    dfs_trails = m.find_trails(count_all_paths=True)
    # dijkstra_trails = m.find_trails_dijkstra()
    # assert dfs_trails == dijkstra_trails, f"Expected DFS to match Dijkstra. DFS=[{dfs_trails}], Dijkstra=[{dijkstra_trails}]"
    print(f"Sum of trailheads: {m.sum_trails(dfs_trails)}")

    import timeit
    NUMBER = 10
    dfs_result = timeit.timeit("m.find_trails()",
                                globals=locals(), 
                                number=NUMBER)
    dijkstra_result = timeit.timeit("m.find_trails_dijkstra()",
                                globals=locals(), 
                                number=NUMBER)
    
    print(f"DFS time per iteration:\t{dfs_result / NUMBER * 1000:.2f} ms")
    print(f"Dijkstra time per iteration:\t{dijkstra_result / NUMBER * 1000:.2f} ms")