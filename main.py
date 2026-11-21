"""Flask backend. Run:  python main.py   then open http://127.0.0.1:5000

The browser (JavaScript) sends the list to these routes, Python runs the
algorithm and sends the result back as JSON.
"""

import math
import os

from flask import Flask, jsonify, request, send_from_directory

from algorithms import SEARCHES, SORTS, run_search, run_sort, time_ms
import analysis

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")

MAX_LIST = 1000
MAX_CASE_LIST = 300     # step 5 runs every algorithm many times


class ApiError(Exception):
    pass


@app.errorhandler(ApiError)
def api_error(err):
    return jsonify({"error": str(err)}), 400


@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "Not found."}), 404


# ---------------------------------------------------------------- reading the request
def get_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Send JSON data.")
    return data


def get_number(value, what):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ApiError(f"The {what} must be a number.")
    return int(value) if isinstance(value, float) and value.is_integer() else value


def get_array(data):
    arr = data.get("array")
    if not isinstance(arr, list) or not arr:
        raise ApiError("Add at least one number.")
    if len(arr) > MAX_LIST:
        raise ApiError(f"The list can have at most {MAX_LIST} numbers.")
    return [get_number(v, "list items") for v in arr]


def get_name(data, table):
    if data.get("algorithm") not in table:
        raise ApiError("Unknown algorithm.")
    return data["algorithm"]


# ---------------------------------------------------------------- routes
@app.route("/")
def home():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/api/complexity")
def complexity():
    return jsonify({"algorithms": analysis.COMPLEXITY,
                    "search_order": analysis.SEARCH_ORDER, "sort_order": analysis.SORT_ORDER})


@app.route("/api/search", methods=["POST"])
def search():
    data = get_json()
    name, arr = get_name(data, SEARCHES), get_array(data)
    if "target" not in data:
        raise ApiError("Enter the number to find.")
    result = run_search(name, arr, get_number(data["target"], "number to find"))
    result["case"] = analysis.classify(name, arr, result)
    return jsonify(result)


@app.route("/api/sort", methods=["POST"])
def sort():
    data = get_json()
    name, arr = get_name(data, SORTS), get_array(data)
    result = run_sort(name, arr)
    result["case"] = analysis.classify(name, arr, result)
    return jsonify(result)


@app.route("/api/compare", methods=["POST"])
def compare():
    """Run all five sorts on the same list."""
    arr = get_array(get_json())
    sorts = {}
    for name, func in SORTS.items():
        _, comparisons, swaps = func(arr)
        sorts[name] = {"comparisons": comparisons, "swaps": swaps, "time_ms": time_ms(func, arr)}
    return jsonify({"n": len(arr), "sorts": sorts})


@app.route("/api/cases", methods=["POST"])
def cases():
    """Best / average / worst comparison counts for the numbers of the user's list."""
    arr = get_array(get_json())
    if len(arr) > MAX_CASE_LIST:
        raise ApiError(f"Step 5 works for lists of up to {MAX_CASE_LIST} numbers.")
    return jsonify(analysis.measured_cases(tuple(arr)))


@app.route("/api/sample", methods=["POST"])
def sample():
    """The same numbers re-ordered as the best / average / worst case of one algorithm."""
    data = get_json()
    name = data.get("algorithm")
    if name not in SEARCHES and name not in SORTS:
        raise ApiError("Unknown algorithm.")
    if data.get("case") not in ("best", "average", "worst"):
        raise ApiError("case must be best, average or worst.")
    return jsonify(analysis.arrange(name, data["case"], get_array(data)))


if __name__ == "__main__":
    app.run(debug=True)
