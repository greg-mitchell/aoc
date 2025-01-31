from collections import namedtuple
from input import open_input
import itertools as it

# step 1: parse input
# - we're going to need to look at block indices and multiply with file number,
#   which implies we'll probably need to allocate an array with the total size
# - assumes that files and free space are at most 9 blocks
# - linear time. space is at most 9 * 9 / 2 * | n |, or linear
# - can we optimize?
# step 2: compact
# - go through representation backwards, each index considered at most once
# - updating file placement is constant with array representation, so 
#   compaction is linear time, no additional mem

# pt 2
# naive approach: for each file, scan right from start until we find a large enough free block
# - O(n^2) for size of disk if the disk is full
# better approach: preprocess the disk with a freelist
# - how to represent? if just a list of freespaces and index, a disk of size 2 files with 1 free block
#   results in O(n^2) time since you have to scan the freelist each time, which is a constant multiple of n
# - sorting by size doesn't work since we have to move rightmost file to leftmost free block
# start with naive
# - build a mapping of the file and free intervals, where intervals are tuples (start_i, end_i, id)
# - Building that is O(n)
# - Then we process by scanning intervals until we find a free interval that is big enough,
#   move the file to it, and update the free interval.
# naive has unacceptable performance. It seems like it's still n^2, but probably with high constant factors
# let's try preprocessing into a list of intervals that are scanned and updated on move

EMPTY = -1
type Disk = list[int]


def parse_input(input: str) -> Disk:
    assert len(input) > 0, f"Input must have at least one file"

    size = 0
    for c in input:
        size += int(c)
    
    disk: Disk = [EMPTY for _i in range(size)]
    file_id = 0
    curr_i = 0
    for sizes in it.batched(input, n=2):
        file_size = int(sizes[0])
        # fill from curr_i with file_id
        for file_i in range(file_size):
            disk[curr_i + file_i] = file_id
        # update curr_i with file size
        curr_i += file_size
        # skip empty blocks
        curr_i += int(sizes[1]) if len(sizes) > 1 else 0
        # update next ID
        file_id += 1

    return disk


def render_disk(disk: Disk) -> str:
    return ''.join([str(disk[i]) if disk[i] != EMPTY else '.' for i in range(len(disk))])


def leftmost_free_index(disk: Disk, start_i = 0, size = 1) -> int | None:
    free_i = start_i
    free_size = 0
    while free_i < len(disk):
        if disk[free_i] == EMPTY:
            # continue scanning until discovered free_size == size
            free_size += 1
            if free_size == size:
                return free_i - free_size + 1
        else:
            free_size = 0
        free_i += 1
    return None


def file_extent(disk: Disk, last_i: int) -> int:
    """Returns the size of the file in blocks by scanning backwards from last_i"""
    start_i = last_i - 1
    while start_i >= 0 and disk[start_i] == disk[last_i]:
        start_i -= 1
    return last_i - start_i
    

def compact(disk: Disk) -> Disk:
    """Returns a compacted copy of disk"""
    compacted = disk[:]

    free_i = leftmost_free_index(disk)

    file_i = len(compacted) - 1
    while file_i > free_i:
        if compacted[file_i] != EMPTY:
            compacted[free_i] = compacted[file_i]
            compacted[file_i] = EMPTY

            # find the next free index
            free_i += 1
            while compacted[free_i] != EMPTY and free_i < file_i:
                free_i += 1

        file_i -= 1

    return compacted


def find_all_file_extents(disk: Disk) -> dict[int, int]:
    result = {}
    i = len(disk) - 1
    while i >= 0:
        if disk[i] == EMPTY:
            i -= 1
            continue
        extent = file_extent(disk, i)
        result[disk[i]] = extent
        i -= extent

    return result


def compact_pt2(disk: Disk) -> Disk:
    """Returns a compacted copy of disk without fragmenting files."""
    compacted = disk[:]

    free_i = 0
    file_i = len(disk) - 1
    while file_i >= 0 and free_i < file_i:
        file_id = compacted[file_i]
        # scan until we find a file
        if file_id == EMPTY:
            file_i -= 1
            continue
        # find the size of the file
        extent = file_extent(compacted, file_i)
        # get the next place we can put it
        next_free_i = leftmost_free_index(compacted, free_i, extent)
        if next_free_i is None or next_free_i > file_i:
            # no space for the file, leave it here
            file_i -= extent
            continue
        # move the file
        for move_i in range(next_free_i, next_free_i + extent):
            compacted[move_i] = file_id
        # clear the previous location
        for move_i in range(file_i - extent + 1, file_i + 1):
            compacted[move_i] = EMPTY
        # update our file index
        file_i -= extent

    # todo
    return compacted


# Interval is a tuple of indices representing an interval. Both endpoints are inclusive.
Interval = namedtuple('Interval', ['start_i', 'end_i', 'file'])
def interval_length(i: Interval) -> int:
    return i.end_i - i.start_i + 1


def compact_pt2_try2(disk: Disk) -> Disk:
    """Returns a compacted copy of disk without fragmenting files."""
    # Build intervals
    files: list[Interval] = []
    empty_blocks: list[Interval] = []

    curr_file: int | None = None
    start_i = -1

    def add_interval(next_i):
        interval = Interval(start_i, next_i - 1, curr_file)
        if curr_file == EMPTY:
            empty_blocks.append(interval)
        elif curr_file is not None:
            files.append(interval)

    for i in range(len(disk)):
        if (file := disk[i]) == curr_file:
            continue

        add_interval(i)
        start_i = i
        curr_file = file
    # add final file
    add_interval(len(disk))

    # print(f"Files: {files}")
    # print(f"Empty Blocks: {empty_blocks}")
        
    # place files from back to front in empty blocks from front to back
    # todo: should we reverse empty_blocks to make updating more efficient?
    # we don't want to update files in-place because we only want to process each file once
    updated_file_intervals: list[Interval] = []
    while len(files) > 0:
        file = files.pop()
        for empty_i in range(len(empty_blocks)):
            empty_interval = empty_blocks[empty_i]
            if empty_interval.start_i > file.start_i:
                # print(f"Bailing out. Next empty block {empty_interval} was after file {file}")
                break

            if (empty_size := interval_length(empty_interval)) < (file_size := interval_length(file)):
                # print(f"Skipped too-small empty block {empty_interval} for file {file}")
                continue

            # create a new empty interval where the file was. We don't need to worry about maintaining
            # sorted order because we never reexamine space rightward of the file.
            vacated_interval = Interval(file.start_i, file.end_i, EMPTY)
            empty_blocks.append(vacated_interval)

            # update the file interval and the empty interval that it now occupies.
            file = Interval(empty_interval.start_i, empty_interval.start_i + file_size - 1, file.file)
            if empty_size == file_size:
                # print(f"Filled empty block {empty_interval} with file {file}")
                # we've filled this empty block, remove it
                empty_blocks.pop(empty_i)
            else:
                # there's still empty blocks, update the entry
                # print(f"Partially filled empty block {empty_interval} with file {file}")
                empty_blocks[empty_i] = Interval(file.end_i + 1, empty_interval.end_i, EMPTY)

            # we only need to move once
            break
        # if we didn't find a large enough empty block, we still want to append the original file interval
        # print(f"Updated file {file}")
        updated_file_intervals.append(file)

    disk_intervals = sorted([*updated_file_intervals, *empty_blocks])
    # print(disk_intervals)
    # populate the compacted disk from intervals
    return [interval.file for interval in disk_intervals for _ in range(interval_length(interval))]


def checksum(disk: Disk) -> int:
    cs = 0
    for i in range(len(disk)):
        cs += disk[i] * i if disk[i] != EMPTY else 0
    return cs

EXAMPLE_INPUT = "2333133121414131402"

def benchmark_setup():
    global g_input, g_disk 
    g_input = ""
    with open_input(filename="input.txt") as f:
        g_input = f.read().strip()

    g_disk = parse_input(g_input)

def main():
    input = ""
    with open_input(filename="input.txt") as f:
        input = f.read().strip()

    input = EXAMPLE_INPUT
    disk = parse_input(input)

    compacted = compact(disk)
    compacted_pt2 = compact_pt2_try2(disk)
    print(f"Disk:\t\t{render_disk(disk)}")
    print(f"Expected:\t00...111...2...333.44.5555.6666.777.888899")
    print(f"Compacted:\t{render_disk(compacted)}")
    print(f"Expected:\t0099811188827773336446555566..............")
    print(f"Extents:\t{find_all_file_extents(disk)}")
    print(f"Checksum:\t{checksum(compacted)}")
    print(f"Compacted pt2:\t{render_disk(compacted_pt2)}")
    print(f"Expected:\t00992111777.44.333....5555.6666.....8888..")
    print(f"Checksum pt 2:\t{checksum(compacted_pt2)}")

if __name__ == "__main__":

    # main()
    
    import timeit
    num = 10
    result_pt1 = timeit.timeit("compact(g_disk)", globals=locals(), setup="benchmark_setup()", number=num)
    print(f"pt 1 avg time to compact: {result_pt1 / num * 1000:.2f} ms")
    # result_pt2 = timeit.timeit("compact_pt2(g_disk)", globals=locals(), setup="benchmark_setup()", number=num)
    # print(f"pt 2 avg time to compact: {result_pt2 / num * 1000:.2f} ms")
    result_pt2_try2 = timeit.timeit("compact_pt2_try2(g_disk)", globals=locals(), setup="benchmark_setup()", number=num)
    print(f"pt 2 try 2 avg time to compact: {result_pt2_try2 / num * 1000:.2f} ms")

    # pt 1 avg time to compact: 10.481464999975287 ms
    # pt 2 avg time to compact: 52741.53534489997 ms
    # pt 2 try 2 avg time to compact: 485.50 ms
