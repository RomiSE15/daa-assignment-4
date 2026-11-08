# Assignment 4 - analysis

## Environment and commands

- Language: Python. Measured with CPython 3.12.0. The source uses ordinary Python and is the file run by the Python 3.12 launcher in GitHub Actions
- Machine used for the timings below: Windows 11, AMD Ryzen 5 7430U with Radeon Graphics, 2.30 GHz, 16 GB RAM
- Commands from the repository root:

```sh
python tools/run.py --setup
python tools/run.py --check
python tests/student/check_cases.py
python tests/student/search_bench.py
```

`submission.json` selects `Python`. The final commit URL is submitted in Moodle, not stored here

## Algorithm explanations

### lcs

`dp[i][j]` is the LCS length of the prefixes `a[:i]` and `b[:j]`. The base row and column are 0, so an empty string has length 0 and sequence `""`. If `a[i-1] == b[j-1]`, the transition is `dp[i-1][j-1] + 1`. Otherwise it is `max(dp[i-1][j], dp[i][j-1])`. Cells are filled by increasing `i` and `j`, so both shorter prefixes already exist. A common subsequence cannot be longer than this optimum: a match extends one shorter optimum, and a mismatch keeps one of the two shorter prefixes. Reconstruction starts at `(n, m)`. A matching pair is taken and both indices move back; otherwise the walk follows the neighbor with the larger value (the upper one on a tie). The taken characters are one optimal subsequence. Another walk can be optimal too; any one is accepted. Time and extra memory are `O((|a|+1)(|b|+1))` for the full table, plus the output string. The case `a="abc"`, `b="xyz"` returns length 0. A bug that reports a common character which is not shared fails this case

### merge

`dp[l][r]` is the cheapest way to reduce the adjacent blocks that cover original indices `l..r` into one block. `dp[i][i] = 0`. For `r > l`, try the last split `k` and set

`dp[l][r] = min(dp[l][k] + dp[k+1][r] + sum(sizes[l..r]))`.

The added cost is the combined size of the two blocks being merged. Prefix sums compute that in `O(1)`. Intervals are solved by increasing length, so both sides of the split are ready. Every full parenthesization of adjacent merges is considered, so the minimum is optimal. A plan that merges non-adjacent blocks is not allowed. `split[l][r]` stores the best `k` (the smallest `k` on a tie). The plan is built by emitting the left side, then the right side, then `[l, k, r]`, so child merges exist before the parent merge. For `n <= 1` the cost is 0 and the plan is empty. For `n > 1` there are `n-1` merges. Time is `O(n^3)`. Extra memory is `O(n^2)` for `dp` and `split`, plus `O(n)` for the prefix array and the plan. `[1, 100, 1]` has cost 203. Merging the two 1s first would be cheaper but they are not adjacent, so that plan is rejected

### tree

Root the tree at vertex 0. The root is only a computation order; the edges stay undirected. `take[u]` is the best independent set in `u`'s subtree that includes `u`. `skip[u]` is the best set in that subtree that excludes `u`. Leaves use `take = weight` and `skip = 0`. After the children are known,

`take[u] = weight[u] + sum(skip[child])`,

`skip[u] = sum(max(take[child], skip[child]))`

An iterative DFS stores a parent and a discovery order. The DP walks that order backwards, so children are ready before the parent. Deep chains do not use recursion. The answer at the root is `max(take[0], skip[0])`. It is at least 0 because every `skip` is a sum of maxima that bottom out at 0, so an all-negative tree selects nothing. Reconstruction walks from the root: a vertex is selected only when its parent was not selected and `take[u] > skip[u]`. Equal values skip the vertex and leave the children free, which keeps the same total. Selected ids are unique and not adjacent. Time and extra memory are `O(n)` for the adjacency lists, order, and two DP arrays, plus the output set. Weights `[-2, -3]` must return weight 0. Selecting a negative vertex fails that case.

### naive

Every start `i` from 0 through `n-m` is compared with the pattern, character by character. A full match appends `i`. Starts stay increasing, and overlap is kept because `i` grows by 1. An empty pattern matches the `n+1` boundaries `0..n` before any character test. A pattern longer than the text returns `[]`. No library search is used. Time is `O(n*m + n + 1)` in the worst case. Extra memory besides the output list is `O(1)`. `"aaaa"` with `"aa"` must return `[0, 1, 2]`. Stopping after the first match, or skipping overlaps, fails it.

### kmp

`pi[i]` is the longest proper prefix of `pattern[:i+1]` that is also its suffix. It is built left to right: after a mismatch, `k = pi[k-1]` until the characters fit or `k` is 0. The search uses the same `pi` on the text. After a full match of length `m`, the next state is `pi[m-1]`, not 0, so an overlap can still be a match. Empty pattern and long pattern are handled like `naive`, before `pi` is indexed. On the same strings, `naive`, `kmp` and `rk` return the same starts. Time is `O(n+m+z)`. Extra memory is the `O(m)` prefix array. `"abababa"` / `"aba"` returns `[0, 2, 4]`. Resetting the state to 0 after a match drops the overlaps.

### rk

The fingerprint is a polynomial hash, base 31, modulus 101, with the leftmost character on the highest power: `h = (h * 31 + ord(c)) % 101`. The pattern hash and the first window are built directly. The next window removes the outgoing character times `31^(m-1) mod 101`, then multiplies by 31 and adds the incoming character. Python's `% 101` makes the remainder non-negative. An equal hash is only a candidate. The window is accepted after a real character comparison. Empty and overlong patterns are handled before a window exists, with the same positions as `kmp`. Time is `O(n+m+c*m)`, where `c` is the number of equal-hash windows. That can be quadratic; it is not claimed to be linear. Extra memory is `O(1)` besides the output. In `"abdj"`, `"ab"` and `"dj"` both hash to 75. The result for `"ab"` is `[0]`, not `[0, 2]`. Reporting the hash collision without comparing characters fails this case

### suffix

Prefix doubling and Kasai are separate

**Doubling.** `sa` is a permutation of `0..n-1`. `rank[i]` is the order of the length-`k` block starting at `i`. At `k = 1` the rank is the character code. Each round sorts the pairs `(rank[i], rank[i+k])`, using -1 when `i+k` is past the end, so a shorter suffix comes first when it is a prefix of another. Sorting is two stable counting passes, second key then first key. Ranks are then renumbered from the sorted order. `k` doubles. When every rank is unique, or `k >= n`, the order is the lexicographic order of the whole suffixes. No suffix string is stored. The empty suffix and any sentinel are absent from the output.

**Kasai.** `lcp[0] = 0`. `lcp[i]` is the shared prefix length of the adjacent suffixes `sa[i-1]` and `sa[i]`. If suffix `i` had height `h` with its predecessor, suffix `i+1` has height at least `h-1` with its own predecessor, so the comparisons are `O(n)` together. A repeated substring is a common prefix of two different suffixes. The longest one appears as the maximum adjacent LCP, because the suffix array groups similar suffixes. The output string is `text[sa[i]:sa[i]+lcp[i]]` at a maximum `lcp[i]`, or `""` when that maximum is 0. Empty text returns three empty results. For `n >= 1`, time is `O(n log n)` for the doubling rounds and `O(n)` for Kasai. Extra and output memory are `O(n)`. `"banana"` has `sa = [5, 3, 1, 0, 4, 2]`, `lcp = [0, 1, 3, 0, 0, 2]` and repeated `"ana"`. A wrong adjacent order fails the `sa` check even if some repeated string is still plausible

### aho

One trie is built for the request. Each pattern ends at a node, and duplicate strings share that node but keep their own dictionary indexes. Failure links are built by BFS. The failure of a node is the longest proper suffix of its path that is a trie prefix; the root failure is the root. Each text starts again at the root with a fresh visit array. A missing edge follows failure links. Each visited node is counted once per arrival. Counts are then added along failure links from deeper nodes toward the root, so a pattern that is a suffix of another pattern is counted without walking an output list per match. Pattern `i` reads the visit count of its terminal node. Duplicate terminals therefore get equal counts. An empty dictionary yields an empty row per text. No texts yields `[]`. An empty text yields zeros. Time per text is `O(|text| + states + p)` after the trie is built. Memory is the trie plus one visit array. Patterns `["he", "she", "he"]` on `"sheshe"` return `[2, 2, 2]`, because `he` ends inside `she`. Counting only the longest pattern fails this case.

## Own tests

Checked with `python tests/student/check_cases.py`. Actual results matched the expected column

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|lcs|`tests/student/cases.json` `lcs-empty`|length 0, sequence `""`|same, PASS|empty input|
|lcs|`lcs-none`|length 0, sequence `""`|same, PASS|no common characters|
|lcs|`lcs-subsequence`|length 3, sequence `abc`|same, PASS|subsequence, not substring|
|merge|`merge-empty`, `merge-one`|cost 0, plan `[]`|same, PASS|`n < 2`|
|merge|`merge-adjacency`, sizes `[1,100,1]`|cost 203|same, PASS|non-adjacent merge is illegal|
|tree|`tree-negative`|weight 0, selected `[]`|same, PASS|negative weights|
|tree|`tree-adjacent`, weights `[5,5]`|weight 5, one vertex|same, PASS|adjacent vertices cannot both be taken|
|naive|`naive-overlap`|`[0,1,2]`|same, PASS|overlaps|
|naive|`naive-empty-pattern`|`[0,1,2]`|same, PASS|empty pattern boundaries|
|kmp|`kmp-overlap`|`[0,2,4]`|same, PASS|fallback after a full match|
|rk|`rk-collision`, `rk-second-window`|`[0]` and `[2]` on `abdj`|same, PASS|hash collision versus a real match|
|suffix|`suffix-banana`|sa `[5,3,1,0,4,2]`, lcp `[0,1,3,0,0,2]`, `ana`|same, PASS|order, LCP and repeat|
|suffix|`suffix-empty`|three empty results|same, PASS|empty text|
|aho|`aho-suffix-duplicate`|`[[2,2,2],[0,0,0]]`|same, PASS|suffix patterns, duplicates, empty text|
|aho|`aho-empty-dictionary`|`[[]]`|same, PASS|empty dictionary|
|mixed|`tests/student/mixed.jsonl`|LCS length 4, merge cost 14, then `[0,1,2]`, then empty LCS|PASS `mixed-process`|one process, different tasks, no stale result|

## Search comparison

The same text and pattern were given to `naive`, `kmp` and `rk`. Outputs were compared and were identical before timing. Generator: `random.Random(20261108)` restarted for each size; each character of a random string is an independent printable ASCII code from 32 to 126. The repetitive strings are `n` and `m` copies of `a`. Sizes are inside the common domain `n, m <= 3000`.

Timing scope: one direct function call after the strings already exist. JSON, process startup and compilation are not included. CPython has no JIT. One untimed warm-up call is discarded, then three measured runs are kept. Unit: milliseconds. Command: `python tests/student/search_bench.py`.

|Case|n|m|Seed/generator|Algorithm|Run 1|Run 2|Run 3|Median|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|random|500|30|20261108, ASCII 32–126|naive|0.135|0.142|0.135|0.135|yes, 0 matches, all three equal|
|random|500|30|20261108, ASCII 32–126|kmp|0.072|0.114|0.140|0.114|yes, 0 matches, all three equal|
|random|500|30|20261108, ASCII 32–126|rk|0.396|0.389|0.413|0.396|yes, 0 matches, all three equal|
|random|1500|80|20261108, ASCII 32–126|naive|0.783|0.506|0.442|0.506|yes, 0 matches, all three equal|
|random|1500|80|20261108, ASCII 32–126|kmp|0.225|0.214|0.214|0.214|yes, 0 matches, all three equal|
|random|1500|80|20261108, ASCII 32–126|rk|1.172|1.230|1.255|1.230|yes, 0 matches, all three equal|
|random|3000|200|20261108, ASCII 32–126|naive|1.291|0.955|1.522|1.291|yes, 0 matches, all three equal|
|random|3000|200|20261108, ASCII 32–126|kmp|0.798|0.791|0.917|0.798|yes, 0 matches, all three equal|
|random|3000|200|20261108, ASCII 32–126|rk|2.325|2.409|2.859|2.409|yes, 0 matches, all three equal|
|repetitive|500|30|20261108, character `a`|naive|2.797|2.585|1.382|2.585|yes, 471 matches, all three equal|
|repetitive|500|30|20261108, character `a`|kmp|0.162|0.171|0.169|0.169|yes, 471 matches, all three equal|
|repetitive|500|30|20261108, character `a`|rk|1.576|1.572|1.578|1.576|yes, 471 matches, all three equal|
|repetitive|1500|80|20261108, character `a`|naive|13.448|13.216|12.538|13.216|yes, 1421 matches, all three equal|
|repetitive|1500|80|20261108, character `a`|kmp|0.716|0.922|0.995|0.922|yes, 1421 matches, all three equal|
|repetitive|1500|80|20261108, character `a`|rk|12.371|12.077|15.069|12.371|yes, 1421 matches, all three equal|
|repetitive|3000|200|20261108, character `a`|naive|65.445|59.847|59.603|59.847|yes, 2801 matches, all three equal|
|repetitive|3000|200|20261108, character `a`|kmp|1.060|1.070|1.065|1.065|yes, 2801 matches, all three equal|
|repetitive|3000|200|20261108, character `a`|rk|68.595|69.653|67.531|68.595|yes, 2801 matches, all three equal|

On random strings the first character usually mismatches, so naive does little work and KMP is only a small constant factor faster. RK still updates a hash for every window, so it is the slowest here even though it is correct. On repetitive strings every window is a real match. Naive and RK both compare those characters, and their times grow much faster (about 60 and 69 ms at n = 3000). KMP stays far lower (0.17 to 1.07 ms) and grows slowly. Times of about a millisecond or less are noisy on a laptop (for example naive, random, n = 1500 ran 0.44 to 0.78 ms), so only large differences should be trusted. These medians are measurements, not a proof of the big-O bounds

Modulus 101 is intentionally small so different windows can share a hash. Equal hashes are candidates only. This pair is a correctness check, not a timing case: text `abdj`, pattern `ab` returns `[0]`, while `dj` has the same hash and is not reported. A production hash usually uses a much larger modulus or a stronger fingerprint. These timings, especially the repetitive RK column, must not be read as the cost of every practical Rabin–Karp implementation. Here the repetitive windows are real matches, so the character check is required even with a perfect hash

## Sources and AI assistance

- Course documents: `docs/Assignment_4_EN.md`, `docs/guide/CONTRACTS.md`, `docs/guide/RUBRIC.md`, `docs/LECTURE_CLARIFICATIONS_EN_RU.md`.
- Standard constructions for LCS, interval DP, tree take/skip DP, the KMP prefix function, polynomial rolling hash, prefix doubling, Kasai's algorithm and Aho–Corasick failure links.
- AI: An AI assistant (Claude) was used to understand the assignment and its file structure and to review and edit the wording of this document. I ran all tests and timings myself.
