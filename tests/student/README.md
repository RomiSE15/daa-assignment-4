
`cases.json` holds the extra cases. `mixed.jsonl` is four requests for one process. `check_cases.py` checks both. `search_bench.py` prints the naive/KMP/RK timings used in ANALYSIS.md.

From the repository root:

```sh
python tests/student/check_cases.py
python tests/student/search_bench.py
```
