"""Time / space complexity table and best / average / worst case helpers."""

import random
from functools import lru_cache

from algorithms import SORTS, SEARCHES

SEARCH_ORDER = ["linear", "binary"]
SORT_ORDER = ["bubble", "selection", "insertion", "merge", "quick"]

# ---------------------------------------------------------------- theory table
COMPLEXITY = {
    "linear": {
        "name": "Linear search", "type": "search",
        "best": "O(1)", "average": "O(n)", "worst": "O(n)", "space": "O(1)",
        "summary": "Checks the items one by one. Works on sorted and unsorted lists.",
        "best_note": "The target is the first item: 1 comparison.",
        "average_note": "About n / 2 comparisons when the target is somewhere in the list.",
        "worst_note": "The target is the last item or is missing: n comparisons.",
        "space_note": "Only a loop index and a few variables.",
    },
    "binary": {
        "name": "Binary search", "type": "search",
        "best": "O(1)", "average": "O(log n)", "worst": "O(log n)", "space": "O(1)",
        "summary": "Compares with the middle item and keeps one half. The list must be sorted.",
        "best_note": "The target is the middle item: 1 comparison.",
        "average_note": "Each comparison throws away half of the remaining items.",
        "worst_note": "The target is missing or found at the very end: about log2(n) comparisons.",
        "space_note": "The loop version keeps only low, high and mid.",
    },
    "bubble": {
        "name": "Bubble sort", "type": "sort",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "summary": "Swaps neighbours that are out of order; the largest value bubbles to the end.",
        "best_note": "Already sorted: one pass with no swap, then stop (needs the did_swap flag).",
        "average_note": "About n(n-1)/2 comparisons and roughly half as many swaps.",
        "worst_note": "Reverse order: n(n-1)/2 comparisons and n(n-1)/2 swaps.",
        "space_note": "Sorts in place with one temporary variable for swapping.",
    },
    "selection": {
        "name": "Selection sort", "type": "sort",
        "best": "O(n²)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "summary": "Finds the smallest item of the unsorted part and swaps it to the front.",
        "best_note": "Always n(n-1)/2 comparisons, even if the list is already sorted.",
        "average_note": "n(n-1)/2 comparisons and at most n - 1 swaps.",
        "worst_note": "n(n-1)/2 comparisons and at most n - 1 swaps.",
        "space_note": "Sorts in place with a few variables.",
    },
    "insertion": {
        "name": "Insertion sort", "type": "sort",
        "best": "O(n)", "average": "O(n²)", "worst": "O(n²)", "space": "O(1)",
        "summary": "Takes the next item (key) and slides it left into its place, like sorting cards.",
        "best_note": "Already sorted: each key is compared once and never moves (n - 1 comparisons).",
        "average_note": "About half of the worst case.",
        "worst_note": "Reverse order: every key moves to the front, n(n-1)/2 comparisons.",
        "space_note": "Sorts in place; only the key is held aside.",
    },
    "merge": {
        "name": "Merge sort", "type": "sort",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n log n)", "space": "O(n)",
        "summary": "Splits the list in halves, sorts each half and merges the sorted halves.",
        "best_note": "Always splits in halves (log n levels) and merges n items per level.",
        "average_note": "Same as the best case: n log n.",
        "worst_note": "Same as the best case: n log n. It needs a temporary list of size n.",
        "space_note": "Merging needs temporary lists of total size n.",
    },
    "quick": {
        "name": "Quick sort", "type": "sort",
        "best": "O(n log n)", "average": "O(n log n)", "worst": "O(n²)", "space": "O(log n)",
        "summary": "Picks a pivot, puts smaller items on its left and the others on its right, then repeats.",
        "best_note": "The pivot splits the list into two parts of similar size.",
        "average_note": "Usually a fairly balanced split: n log n.",
        "worst_note": "The pivot is always the smallest or largest item (for example a sorted list "
                      "with the last item as pivot): n(n-1)/2 comparisons.",
        "space_note": "In place; the stack depth is about log n when the smaller part is done first.",
    },
}


# ---------------------------------------------------------------- best / average / worst order of YOUR numbers
def _balanced_for_quick(values):
    """Order sorted values so quick sort (last item = pivot) always splits in the middle."""
    if len(values) <= 2:
        return list(values)
    mid = len(values) // 2
    left = _balanced_for_quick(values[:mid])
    right = _balanced_for_quick(values[mid + 1:])
    if right:                                   # the partition step moves one item, so rotate by one
        right = [right[-1]] + right[:-1]
    return left + right + [values[mid]]


def _worst_for_merge(values):
    """Interleave the halves so every merge needs the most comparisons."""
    if len(values) <= 1:
        return list(values)
    return _worst_for_merge(values[0::2]) + _worst_for_merge(values[1::2])


def _order(algorithm, case, n, seed=7):
    """An order of the ranks 1..n that gives the best / average / worst case of a sort."""
    base = list(range(1, n + 1))
    if case == "best":
        return _balanced_for_quick(base) if algorithm == "quick" else base
    if case == "worst":
        return {"quick": base, "merge": _worst_for_merge(base)}.get(algorithm, base[::-1])
    random.Random(seed).shuffle(base)
    return base


def arrange(algorithm, case, values, seed=7):
    """Re-order YOUR numbers (same numbers, new order) for the best / average / worst case.

    Returns {"array": [...], "target": number or None}. Searches also get a number to find.
    """
    vals = sorted(values)
    n = len(vals)
    if algorithm in SEARCHES:
        missing = vals[-1] + 1
        if algorithm == "linear":      # linear search works on any order: keep the list as it is
            arr = list(values)
            target = {"best": arr[0], "average": arr[n // 2], "worst": missing}[case]
        else:                          # binary search needs a sorted list
            arr = vals
            target = {"best": vals[(n - 1) // 2], "average": vals[n // 4], "worst": missing}[case]
        return {"array": arr, "target": target}
    if n < 2:
        return {"array": vals, "target": None}
    if case == "average":              # a random order of the same numbers
        arr = list(values)
        random.Random(seed).shuffle(arr)
    else:
        arr = [vals[rank - 1] for rank in _order(algorithm, case, n)]
    return {"array": arr, "target": None}


# ---------------------------------------------------------------- measured cases
def _whole(x):
    """Round to a whole number, halves go up (5.5 -> 6, 2.5 -> 3)."""
    return int(x + 0.5)


@lru_cache(maxsize=64)
def measured_cases(values):
    """Real comparison counts for the best / average / worst arrangement of the given numbers."""
    vals = sorted(values)
    n = len(vals)
    out = {}
    for name in SEARCH_ORDER:                      # every number in the list is tried as the target
        counts = [SEARCHES[name](vals, t)[1] for t in vals]
        out[name] = {"best": min(counts), "average": _whole(sum(counts) / n),
                     "worst": max(max(counts), SEARCHES[name](vals, vals[-1] + 1)[1])}
    for name in SORT_ORDER:
        average = [SORTS[name](arrange(name, "average", values, seed=s)["array"])[1] for s in range(5)]
        out[name] = {"best": SORTS[name](arrange(name, "best", values)["array"])[1],
                     "average": _whole(sum(average) / 5),
                     "worst": SORTS[name](arrange(name, "worst", values)["array"])[1]}
    return {"n": n, "cases": out}


# ---------------------------------------------------------------- which case is MY list?
@lru_cache(maxsize=256)
def _bounds(algorithm, n):
    """(fewest, most) comparisons of merge / quick sort on n numbers."""
    ranks = tuple(range(1, n + 1))
    return (SORTS[algorithm](arrange(algorithm, "best", ranks)["array"])[1],
            SORTS[algorithm](arrange(algorithm, "worst", ranks)["array"])[1])


REASONS = {
    "linear": {
        "best": "The number is at the very first index, so one comparison is enough.",
        "average": "The number is somewhere in the middle, so about half of the list was checked.",
        "worst": "The number is at the last index or is missing, so every item was checked.",
    },
    "binary": {
        "best": "The number is exactly in the middle, so the first comparison finds it.",
        "average": "The number was found after a few halvings.",
        "worst": "The number is missing or found on the last possible halving, so the most comparisons were needed.",
    },
    "bubble": {
        "best": "Your list is already sorted: no swap happens, so bubble sort stops after one pass.",
        "average": "Your list is partly in order, so only some pairs need swapping.",
        "worst": "Your list is in reverse order: every pair needs a swap.",
    },
    "insertion": {
        "best": "Your list is already sorted: every key stays where it is.",
        "average": "Your list is partly in order, so each key slides only part of the way.",
        "worst": "Your list is in reverse order: every key slides all the way to the front.",
    },
    "merge": {
        "best": "The halves rarely mix (a sorted list is the best), so merging needs the fewest comparisons.",
        "average": "The halves mix in some places. Merge sort stays O(n log n) for every list.",
        "worst": "The halves mix in every merge, so every merge needs the most comparisons.",
    },
    "quick": {
        "best": "The last item splits the list into two similar halves every time.",
        "average": "The last item splits the list fairly evenly most of the time.",
        "worst": "The last item is always the smallest or biggest (a sorted or reverse sorted list), "
                 "so each split leaves one side empty.",
    },
}


def classify(algorithm, values, result):
    """Say whether the list the user ran is a best, average or worst case for the algorithm."""
    n = len(values)
    info = COMPLEXITY[algorithm]
    if n < 2:
        return {"case": "same", "label": "Same in every case", "big_o": info["best"],
                "reason": "With a single number every case is the same."}
    if algorithm == "selection":
        return {"case": "same", "label": "Same in every case", "big_o": info["average"],
                "reason": "Selection sort makes n(n-1)/2 comparisons for any list, "
                          "so best, average and worst case are the same."}

    comparisons, swaps = result["comparisons"], result["swaps"]
    if algorithm == "linear":
        if result["found"] and result["index"] == 0:
            case = "best"
        elif not result["found"] or result["index"] == n - 1:
            case = "worst"
        else:
            case = "average"
    elif algorithm == "binary":
        if comparisons == 1:
            case = "best"
        elif not result["found"] or comparisons == n.bit_length():
            case = "worst"
        else:
            case = "average"
    elif algorithm in ("bubble", "insertion"):
        # swaps = number of out-of-order pairs: 0 means sorted, n(n-1)/2 means reversed
        if swaps == 0:
            case = "best"
        elif swaps == n * (n - 1) // 2:
            case = "worst"
        else:
            case = "average"
    else:  # merge and quick sort: compare with the fewest / most possible comparisons
        low, high = _bounds(algorithm, n)
        case = "best" if comparisons <= low else "worst" if comparisons >= high else "average"

    return {"case": case, "label": case.capitalize() + " case", "big_o": info[case],
            "reason": REASONS[algorithm][case]}
