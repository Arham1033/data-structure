"""All 7 algorithms (2 searches, 5 sorts). Each one counts comparisons and swaps and records animation steps."""

import time

MAX_STEPS = 30000


def log(steps, op, data=None, msg=""):
    if steps is not None and len(steps) < MAX_STEPS:
        steps.append({"op": op, "i": data, "msg": msg})


def fmt(value):
    return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)


def linear_search(values, target, steps=None):
    comparisons = 0
    for i, value in enumerate(values):
        comparisons += 1
        log(steps, "cmp", [i], f"Look at index {i}. The value there is {fmt(value)}. Is it equal to {fmt(target)}? If yes we stop here, if not we move on to the next item.")
        if value == target:
            log(steps, "found", [i], f"Yes, it matches! Found {fmt(target)} at index {i} after {comparisons} comparison(s). Linear search stops at the first match.")
            return i, comparisons
    log(steps, "notfound", None, f"We checked every item and reached the end, so {fmt(target)} is not in the list ({comparisons} comparisons).")
    return -1, comparisons


def binary_search(values, target, steps=None):
    low, high = 0, len(values) - 1
    comparisons = 0
    while low <= high:
        log(steps, "range", [low, high], f"The target can only be between index {low} and index {high}. Everything outside this range is ignored.")
        mid = (low + high) // 2
        comparisons += 1
        log(steps, "cmp", [mid], f"The middle of this range is index {mid}, value {fmt(values[mid])}. Compare it with {fmt(target)}: equal means found, otherwise one half can be thrown away.")
        if values[mid] == target:
            log(steps, "found", [mid], f"The middle value equals {fmt(target)}, so it is found at index {mid} after {comparisons} comparison(s).")
            return mid, comparisons
        if values[mid] > target:
            log(steps, "range", [low, mid - 1], f"{fmt(values[mid])} is bigger than {fmt(target)}. The list is sorted, so the target can only be on the left. Throw away the middle and the right half.")
            high = mid - 1
        else:
            log(steps, "range", [mid + 1, high], f"{fmt(values[mid])} is smaller than {fmt(target)}. The list is sorted, so the target can only be on the right. Throw away the middle and the left half.")
            low = mid + 1
    log(steps, "range", None, "")
    log(steps, "notfound", None, f"The range is empty, so there is nothing left to check. {fmt(target)} is not in the list ({comparisons} comparisons).")
    return -1, comparisons


def bubble_sort(values, steps=None):
    arr = list(values)
    n = len(arr)
    comparisons = swaps = 0
    for i in range(n - 1):
        did_swap = False
        for j in range(n - i - 1):
            comparisons += 1
            log(steps, "cmp", [j, j + 1], f"Compare the neighbours {fmt(arr[j])} (index {j}) and {fmt(arr[j + 1])} (index {j + 1}). If the left one is bigger they are in the wrong order.")
            if arr[j] > arr[j + 1]:
                log(steps, "swap", [j, j + 1], f"{fmt(arr[j])} is bigger than {fmt(arr[j + 1])}, so swap them. The bigger value moves one place to the right.")
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                did_swap = True
            else:
                log(steps, "note", [j, j + 1], f"{fmt(arr[j])} is not bigger than {fmt(arr[j + 1])}, so they are already in order. No swap.")
        log(steps, "mark", [n - i - 1], f"End of pass {i + 1}: the biggest value left, {fmt(arr[n - i - 1])}, has bubbled to the end and is in its final place.")
        if not did_swap:
            log(steps, "mark", list(range(n - i - 1)), "No swap in this pass, so the list is already sorted. Stop early.")
            break
    log(steps, "mark", list(range(n)), "The list is sorted.")
    return arr, comparisons, swaps


def selection_sort(values, steps=None):
    arr = list(values)
    n = len(arr)
    comparisons = swaps = 0
    for i in range(n - 1):
        smallest = i
        log(steps, "pivot", [i], f"Pass {i + 1}: start with {fmt(arr[i])} (index {i}) as the smallest so far, then look through the rest of the list for anything smaller.")
        for j in range(i + 1, n):
            comparisons += 1
            log(steps, "cmp", [j, smallest], f"Is {fmt(arr[j])} (index {j}) smaller than the smallest so far, {fmt(arr[smallest])}?")
            if arr[j] < arr[smallest]:
                smallest = j
                log(steps, "pivot", [j], f"Yes, so {fmt(arr[j])} (index {j}) becomes the new smallest.")
        if smallest != i:
            log(steps, "swap", [i, smallest],
                f"The smallest of this pass is {fmt(arr[smallest])}. Swap it with the first unsorted item {fmt(arr[i])} so it goes to the front.")
            arr[i], arr[smallest] = arr[smallest], arr[i]
            swaps += 1
        else:
            log(steps, "note", [i], f"{fmt(arr[i])} is already the smallest of the unsorted part, so no swap is needed.")
        log(steps, "pivot", None, "")
        log(steps, "mark", [i], f"{fmt(arr[i])} is now in its final place. The sorted part grows by one.")
    log(steps, "mark", list(range(n)), "The list is sorted.")
    return arr, comparisons, swaps


def insertion_sort(values, steps=None):
    arr = list(values)
    n = len(arr)
    comparisons = swaps = 0
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        shown = i
        log(steps, "zone", [0, i - 1], "")
        log(steps, "key", [shown], f"Take {fmt(key)} (index {i}) as the key. We will slide it left into the correct place inside the sorted part on its left.")
        while j >= 0:
            comparisons += 1
            log(steps, "cmp", [j, shown], f"Is {fmt(arr[j])} bigger than the key {fmt(key)}? If yes it must move right to make room, if not the key has found its place.")
            if arr[j] <= key:
                log(steps, "note", [j, shown], f"{fmt(arr[j])} is not bigger than the key, so the key stays right after it. Stop sliding.")
                break
            log(steps, "swap", [j, shown], f"Yes, so shift {fmt(arr[j])} one place to the right and keep going left.")
            arr[j + 1] = arr[j]
            swaps += 1
            shown = j
            j -= 1
        arr[j + 1] = key
        log(steps, "key", None, f"Drop the key {fmt(key)} into its place at index {j + 1}. The sorted part on the left is now one item longer.")
    log(steps, "zone", None, "")
    log(steps, "mark", list(range(n)), "The list is sorted.")
    return arr, comparisons, swaps


def merge_sort(values, steps=None):
    arr = list(values)
    counts = {"comparisons": 0, "swaps": 0}

    def merge(lo, mid, hi):
        left, right = arr[lo:mid + 1], arr[mid + 1:hi + 1]
        merged = []
        i = j = 0
        log(steps, "range", [lo, hi], f"Merge the two sorted halves {lo}..{mid} and {mid + 1}..{hi} into one sorted piece by always taking the smaller front item.")
        while i < len(left) and j < len(right):
            counts["comparisons"] += 1
            log(steps, "cmp", [lo + i, mid + 1 + j], f"Compare the front item of the left half, {fmt(left[i])}, with the front item of the right half, {fmt(right[j])}. The smaller one goes next.")
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged += left[i:] + right[j:]
        for k, value in enumerate(merged):
            arr[lo + k] = value
            counts["swaps"] += 1
            log(steps, "set", [lo + k, value], f"Write {fmt(value)} back into the list at index {lo + k}.")

    def sort(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        log(steps, "range", [lo, hi], f"Split indices {lo}..{hi} into two halves: {lo}..{mid} and {mid + 1}..{hi}. Each half is sorted on its own first.")
        sort(lo, mid)
        sort(mid + 1, hi)
        merge(lo, mid, hi)

    sort(0, len(arr) - 1)
    log(steps, "range", None, "")
    log(steps, "mark", list(range(len(arr))), "The list is sorted.")
    return arr, counts["comparisons"], counts["swaps"]


def quick_sort(values, steps=None):
    arr = list(values)
    comparisons = swaps = 0
    stack = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo > hi:
            continue
        if lo == hi:
            log(steps, "mark", [lo], f"{fmt(arr[lo])} is alone, so it is in its final place.")
            continue
        pivot = arr[hi]
        i = lo
        log(steps, "range", [lo, hi], f"Now sort indices {lo}..{hi}.")
        log(steps, "pivot", [hi], f"Choose the last item, {fmt(pivot)}, as the pivot. Smaller items will go to its left, the others to its right.")
        for j in range(lo, hi):
            comparisons += 1
            log(steps, "cmp", [j, hi], f"Is {fmt(arr[j])} (index {j}) smaller than the pivot {fmt(pivot)}?")
            if arr[j] < pivot:
                if i != j:
                    log(steps, "swap", [i, j], f"Yes, so move {fmt(arr[j])} into the left part (the part of smaller items).")
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps += 1
                i += 1
            else:
                log(steps, "note", [j, hi], f"{fmt(arr[j])} is not smaller than the pivot, so it stays in the right part.")
        if i != hi:
            log(steps, "swap", [i, hi], f"All items are checked. Put the pivot {fmt(pivot)} between the smaller part and the bigger part.")
            arr[i], arr[hi] = arr[hi], arr[i]
            swaps += 1
        log(steps, "pivot", None, "")
        log(steps, "mark", [i], f"The pivot {fmt(pivot)} is now in its final place (index {i}). The left and right parts are sorted next.")
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))
    log(steps, "range", None, "")
    log(steps, "mark", list(range(len(arr))), "The list is sorted.")
    return arr, comparisons, swaps


SEARCHES = {"linear": linear_search, "binary": binary_search}
SORTS = {"bubble": bubble_sort, "selection": selection_sort, "insertion": insertion_sort,
         "merge": merge_sort, "quick": quick_sort}


def time_ms(func, *args):
    start = time.perf_counter()
    func(*args)
    first = time.perf_counter() - start
    repeats = min(50, max(1, int(0.02 / max(first, 1e-7))))
    if repeats == 1:
        return first * 1000
    best = first
    for _ in range(3):
        start = time.perf_counter()
        for _ in range(repeats):
            func(*args)
        best = min(best, (time.perf_counter() - start) / repeats)
    return best * 1000


def run_sort(name, values):
    steps = []
    arr, comparisons, swaps = SORTS[name](values, steps)
    return {"algorithm": name, "array": arr, "comparisons": comparisons, "swaps": swaps,
            "time_ms": time_ms(SORTS[name], values), "steps": steps, "truncated": len(steps) >= MAX_STEPS}


def run_search(name, values, target):
    steps = []
    index, comparisons = SEARCHES[name](values, target, steps)
    return {"algorithm": name, "target": target, "found": index != -1, "index": index,
            "indices": [i for i, v in enumerate(values) if v == target],
            "comparisons": comparisons, "swaps": 0,
            "input_sorted": all(values[i] <= values[i + 1] for i in range(len(values) - 1)),
            "time_ms": time_ms(SEARCHES[name], values, target),
            "steps": steps, "truncated": len(steps) >= MAX_STEPS}
