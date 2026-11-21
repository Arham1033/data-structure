# Algorithm Visualizer (Data Structures project)

Searching and sorting algorithms with step-by-step animation.
**Backend:** Python (Flask). **Frontend:** HTML, CSS, JavaScript. JavaScript talks to Python with `fetch()`.

## Run
```
pip install -r requirements.txt
python main.py
```
Open http://127.0.0.1:5000

## Files
```
main.py            Flask server: receives the list, calls the algorithms, sends JSON back
algorithms.py      the 7 algorithms (linear, binary, bubble, selection, insertion, merge, quick) + timing
analysis.py        complexity table, best/average/worst sample lists, "which case is my list?"
test_project.py    tests  (python -m unittest test_project)
frontend/
  index.html       the page
  style.css        colours and layout
  script.js        page logic (list, buttons, results, tables)
  animation.js     plays the recorded steps as bars
  charts.js        bar charts (no libraries)
```

## The page follows the project instructions, top to bottom
1. **Enter your list**: any numbers (positive, negative, zero, decimals, repeats).
2. **Choose an algorithm** and watch it step by step (Play, Pause, Step, Back, Speed). Binary search asks you to sort first.
3. **Result, execution time, comparisons, swaps**, and which case (best / average / worst) your list was.
4. **Time and space complexity** of all 7 algorithms.
5. **Best, average and worst case**: measured comparison counts and charts.
6. **Compare** all algorithms on your list with charts and a table.

## Notes
- Linear search stops at the first match. Binary search needs a sorted list.
- "Swaps" = swaps (bubble, selection, quick), shifts (insertion), element moves (merge).
- Lists of more than 80 numbers are calculated but not animated. Maximum list size: 1000.
