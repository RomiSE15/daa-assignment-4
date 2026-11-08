import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Python" / "source"))
import algorithms

SEED = 20261108
SIZES = [(500, 30), (1500, 80), (3000, 200)]

def make_random(n, m, rng):
    alphabet = [chr(code) for code in range(32, 127)]
    text = "".join(rng.choice(alphabet) for _ in range(n))
    pattern = "".join(rng.choice(alphabet) for _ in range(m))
    return text, pattern

def make_repetitive(n, m, rng):
    return "a" * n, "a" * m

def milliseconds(fn, request):
    start = time.perf_counter()
    fn(request)
    return (time.perf_counter() - start) * 1000

def main():
    print("python", sys.version.split()[0])
    algorithms_to_time = [
        ("naive", algorithms.naive),
        ("kmp", algorithms.kmp),
        ("rk", algorithms.rk),
    ]
    makers = [("random", make_random), ("repetitive", make_repetitive)]
    for kind, maker in makers:
        for n, m in SIZES:
            rng = random.Random(SEED)
            text, pattern = maker(n, m, rng)
            request = {"text": text, "pattern": pattern}
            outputs = [fn(request)["positions"] for _, fn in algorithms_to_time]
            if not outputs[0] == outputs[1] == outputs[2]:
                print("MISMATCH", kind, n, m)
                return 1
            print(f"CHECK {kind} n={n} m={m} count={len(outputs[0])}")
            for name, fn in algorithms_to_time:
                fn(request)
                runs = [milliseconds(fn, request) for _ in range(3)]
                median = statistics.median(runs)
                print(
                    f"{kind}\t{n}\t{m}\t{SEED}\t{name}\t"
                    f"{runs[0]:.3f}\t{runs[1]:.3f}\t{runs[2]:.3f}\t{median:.3f}"
                )
    return 0

if __name__ == "__main__":
    sys.exit(main())
