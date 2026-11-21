"""Tests. Run:  python -m unittest test_project -v"""

import random
import unittest

import algorithms as alg
import analysis
from main import app


def replay(start, steps):
    """Apply the recorded steps to a copy of the list (the same rules as the browser)."""
    arr, cmps, moves = list(start), 0, 0
    for s in steps:
        d = s["i"]
        if s["op"] == "cmp":
            cmps += 1
        elif s["op"] == "swap":
            arr[d[0]], arr[d[1]] = arr[d[1]], arr[d[0]]
            moves += 1
        elif s["op"] == "set":
            arr[d[0]] = d[1]
            moves += 1
    return arr, cmps, moves


class SortTests(unittest.TestCase):
    def test_every_sort_on_random_lists(self):
        rng = random.Random(1)
        for name, func in alg.SORTS.items():
            for _ in range(150):
                data = [rng.randint(-9, 9) for _ in range(rng.randint(1, 30))]
                self.assertEqual(func(data)[0], sorted(data), (name, data))

    def test_steps_replay_to_same_result_and_counters(self):
        rng = random.Random(2)
        for name, func in alg.SORTS.items():
            for _ in range(60):
                data = [rng.randint(-9, 9) for _ in range(rng.randint(1, 25))]
                steps = []
                result, comparisons, swaps = func(data, steps)
                self.assertEqual(replay(data, steps), (result, comparisons, swaps), (name, data))

    def test_input_is_not_changed(self):
        for func in alg.SORTS.values():
            data = [3, 1, 2]
            func(data)
            self.assertEqual(data, [3, 1, 2])

    def test_known_counts(self):
        self.assertEqual(alg.bubble_sort(list(range(1, 21)))[1:], (19, 0))        # best case O(n)
        self.assertEqual(alg.selection_sort([56, 78, 33, 81, 12])[2], 4)
        self.assertEqual(alg.insertion_sort(list(range(10, 0, -1)))[1], 45)       # n(n-1)/2
        self.assertEqual(alg.quick_sort(list(range(1, 11)))[1], 45)               # sorted = worst case

    def test_long_sorted_list_does_not_crash(self):
        big = list(range(1500))
        self.assertEqual(alg.quick_sort(big)[0], big)


class SearchTests(unittest.TestCase):
    def test_linear(self):
        self.assertEqual(alg.linear_search([5, 3, 9, 3, 1], 3), (1, 2))           # first match
        self.assertEqual(alg.linear_search([5, 3, 9], 7), (-1, 3))
        self.assertEqual(alg.linear_search([0, 1], 0), (0, 1))

    def test_binary(self):
        self.assertEqual(alg.binary_search([3, 9, 14, 22, 31, 45, 58, 67], 45), (5, 2))
        rng = random.Random(3)
        for _ in range(100):
            data = sorted(rng.randint(-20, 20) for _ in range(rng.randint(1, 30)))
            for t in set(data):
                self.assertEqual(data[alg.binary_search(data, t)[0]], t)
            self.assertEqual(alg.binary_search(data, 99)[0], -1)

    def test_binary_on_unsorted_list_can_miss(self):
        self.assertEqual(alg.binary_search([5, 1, 9, 3], 3)[0], -1)


class CaseTests(unittest.TestCase):
    def test_best_average_worst_order(self):
        values = tuple(random.Random(5).sample(range(-50, 200), 60))
        cases = analysis.measured_cases(values)["cases"]
        for name, c in cases.items():
            self.assertLessEqual(c["best"], c["average"], name)
            self.assertLessEqual(c["average"], c["worst"], name)
        self.assertEqual(cases["quick"]["worst"], 60 * 59 // 2)
        self.assertEqual(cases["linear"]["worst"], 60)

    def case_of(self, name, data, target=None):
        if name in alg.SORTS:
            result = alg.run_sort(name, data)
        else:
            result = alg.run_search(name, data, target)
        return analysis.classify(name, data, result)["case"]

    def test_your_list_is_classified(self):
        for name in ("bubble", "insertion"):
            self.assertEqual(self.case_of(name, [1, 2, 3, 4, 5]), "best")
            self.assertEqual(self.case_of(name, [5, 4, 3, 2, 1]), "worst")
            self.assertEqual(self.case_of(name, [3, 1, 4, 2, 5]), "average")
        self.assertEqual(self.case_of("selection", [3, 1, 2]), "same")
        self.assertEqual(self.case_of("linear", [1, 3, 5, 7, 9], 9), "worst")
        self.assertEqual(self.case_of("binary", [1, 3, 5, 7, 9], 5), "best")

    def test_every_sample_list_is_detected(self):
        for name in ("bubble", "insertion", "merge", "quick"):
            for case in ("best", "worst"):
                data = analysis.arrange(name, case, list(range(16, 0, -1)))["array"]
                self.assertEqual(self.case_of(name, data), case, (name, case))

    def test_arrange_keeps_the_same_numbers(self):
        mine = [7, -2, 0, 7, 12, 3]
        for name in alg.SORTS:
            for case in ("best", "average", "worst"):
                self.assertEqual(sorted(analysis.arrange(name, case, mine)["array"]), sorted(mine))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_sort_and_search(self):
        for name in alg.SORTS:
            body = self.client.post("/api/sort", json={"algorithm": name, "array": [5, -1, 0, 5]}).get_json()
            self.assertEqual(body["array"], [-1, 0, 5, 5])
            self.assertIn("case", body)
        body = self.client.post("/api/search", json={"algorithm": "linear", "array": [4, 2, 4], "target": 4}).get_json()
        self.assertEqual((body["found"], body["index"]), (True, 0))

    def test_bad_input_gives_400(self):
        bad = [("/api/sort", {"algorithm": "bubble", "array": []}),
               ("/api/sort", {"algorithm": "bubble", "array": [1, "a"]}),
               ("/api/sort", {"algorithm": "nope", "array": [1]}),
               ("/api/search", {"algorithm": "linear", "array": [1]})]
        for url, body in bad:
            self.assertEqual(self.client.post(url, json=body).status_code, 400, body)

    def test_compare_cases_and_sample(self):
        body = self.client.post("/api/compare", json={"array": [9, 4, 7, 1]}).get_json()
        self.assertEqual(len(body["sorts"]), 5)
        body = self.client.post("/api/cases", json={"array": [5, 3, 9, 1]}).get_json()
        self.assertEqual(body["n"], 4)
        self.assertEqual(body["cases"]["bubble"], {"best": 3, "average": body["cases"]["bubble"]["average"], "worst": 6})
        res = self.client.post("/api/sample", json={"algorithm": "bubble", "case": "worst", "array": [3, 1, 2]})
        self.assertEqual(res.get_json()["array"], [3, 2, 1])
        res = self.client.post("/api/sample", json={"algorithm": "bubble", "case": "best", "array": [3, 1, 2]})
        self.assertEqual(res.get_json()["array"], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
