from collections import deque

def lcs(request):
    a = request["a"]
    b = request["b"]
    n = len(a)
    m = len(b)
    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}
    # dp[i][j] = LCS length of a[:i] and b[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        prev = dp[i - 1]
        row = dp[i]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                up = prev[j]
                left = row[j - 1]
                row[j] = up if up >= left else left
    i = n
    j = m
    chars = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            chars.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    chars.reverse()
    return {"length": dp[n][m], "sequence": "".join(chars)}

def merge(request):
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}
    pref = [0] * (n + 1)
    for i in range(n):
        pref[i + 1] = pref[i] + sizes[i]
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            base = pref[right + 1] - pref[left]
            best = None
            best_k = left
            for k in range(left, right):
                cost = dp[left][k] + dp[k + 1][right] + base
                if best is None or cost < best:
                    best = cost
                    best_k = k
            dp[left][right] = best
            split[left][right] = best_k
    plan = []

    def build(left, right):
        if left == right:
            return
        k = split[left][right]
        build(left, k)
        build(k + 1, right)
        plan.append([left, k, right])

    build(0, n - 1)
    return {"cost": dp[0][n - 1], "plan": plan}

def tree(request):
    n = request["n"]
    weights = request["weights"]
    if n == 0:
        return {"weight": 0, "selected": []}
    adj = [[] for _ in range(n)]
    for u, v in request["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
                stack.append(v)
    take = [0] * n
    skip = [0] * n
    for u in reversed(order):
        taken = weights[u]
        skipped = 0
        p = parent[u]
        for v in adj[u]:
            if v == p:
                continue
            taken += skip[v]
            child = take[v]
            if child > skip[v]:
                skipped += child
            else:
                skipped += skip[v]
        take[u] = taken
        skip[u] = skipped
    selected = []
    stack = [(0, False)]
    while stack:
        u, parent_taken = stack.pop()
        choose = (not parent_taken) and take[u] > skip[u]
        if choose:
            selected.append(u)
        p = parent[u]
        for v in adj[u]:
            if v != p:
                stack.append((v, choose))
    weight = take[0] if take[0] > skip[0] else skip[0]
    return {"weight": weight, "selected": selected}

def naive(request):
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    positions = []
    last = n - m
    for i in range(last + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)
    return {"positions": positions}

def _prefix(pattern):
    m = len(pattern)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    return pi

def kmp(request):
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    pi = _prefix(pattern)
    positions = []
    k = 0
    for i in range(n):
        while k > 0 and text[i] != pattern[k]:
            k = pi[k - 1]
        if text[i] == pattern[k]:
            k += 1
        if k == m:
            positions.append(i - m + 1)
            k = pi[k - 1]
    return {"positions": positions}

def rk(request):
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    base = 31
    mod = 101
    high = pow(base, m - 1, mod)
    pattern_hash = 0
    window = 0
    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        window = (window * base + ord(text[i])) % mod
    positions = []
    i = 0
    while True:
        if window == pattern_hash:
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                positions.append(i)
        if i + m == n:
            break
        window = (window - ord(text[i]) * high) % mod
        window = (window * base + ord(text[i + m])) % mod
        i += 1
    return {"positions": positions}

def _suffix_array(text):
    n = len(text)
    if n == 0:
        return []
    sa = list(range(n))
    rank = [ord(ch) for ch in text]
    k = 1
    while k < n:
        second = [0] * n
        for index in range(n):
            pos = sa[index] + k
            second[index] = rank[pos] + 1 if pos < n else 0
        limit = n + 1
        if limit < 128:
            limit = 128
        sa = _count_sort(sa, second, limit)
        first = [rank[pos] for pos in sa]
        sa = _count_sort(sa, first, limit)
        new_rank = [0] * n
        classes = 0
        for index in range(1, n):
            a = sa[index - 1]
            b = sa[index]
            a2 = rank[a + k] if a + k < n else -1
            b2 = rank[b + k] if b + k < n else -1
            if rank[a] != rank[b] or a2 != b2:
                classes += 1
            new_rank[b] = classes
        rank = new_rank
        if classes == n - 1:
            break
        k *= 2
    return sa

def _count_sort(order, keys, limit):
    count = [0] * limit
    for key in keys:
        count[key] += 1
    total = 0
    for i in range(limit):
        old = count[i]
        count[i] = total
        total += old
    out = [0] * len(order)
    for index in range(len(order)):
        key = keys[index]
        out[count[key]] = order[index]
        count[key] += 1
    return out

def _kasai(text, sa):
    n = len(text)
    rank = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        r = rank[i]
        if r == 0:
            h = 0
            continue
        j = sa[r - 1]
        while i + h < n and j + h < n and text[i + h] == text[j + h]:
            h += 1
        lcp[r] = h
        if h > 0:
            h -= 1
    return lcp

def suffix(request):
    text = request["text"]
    n = len(text)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}
    sa = _suffix_array(text)
    lcp = _kasai(text, sa)
    best_len = 0
    best_i = 0
    for i in range(1, n):
        if lcp[i] > best_len:
            best_len = lcp[i]
            best_i = i
    if best_len == 0:
        repeated = ""
    else:
        start = sa[best_i]
        repeated = text[start:start + best_len]
    return {"sa": sa, "lcp": lcp, "repeated": repeated}

def aho(request):
    patterns = request["patterns"]
    texts = request["texts"]
    if len(texts) == 0:
        return {"counts": []}
    if len(patterns) == 0:
        return {"counts": [[] for _ in texts]}
    nxt = [{}]
    fail = [0]
    end = []
    for pattern in patterns:
        node = 0
        for ch in pattern:
            child = nxt[node].get(ch)
            if child is None:
                child = len(nxt)
                nxt[node][ch] = child
                nxt.append({})
                fail.append(0)
            node = child
        end.append(node)
    order = []
    queue = deque()
    for child in nxt[0].values():
        queue.append(child)
    while queue:
        u = queue.popleft()
        order.append(u)
        for ch, v in nxt[u].items():
            f = fail[u]
            while f and ch not in nxt[f]:
                f = fail[f]
            if ch in nxt[f]:
                fail[v] = nxt[f][ch]
            else:
                fail[v] = 0
            queue.append(v)
    rows = []
    states = len(nxt)
    for text in texts:
        visits = [0] * states
        state = 0
        for ch in text:
            while state and ch not in nxt[state]:
                state = fail[state]
            child = nxt[state].get(ch)
            if child is None:
                state = 0
            else:
                state = child
            visits[state] += 1
        for u in reversed(order):
            visits[fail[u]] += visits[u]
        rows.append([visits[node] for node in end])
    return {"counts": rows}
