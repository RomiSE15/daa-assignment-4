import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Python" / "source"))
import algorithms

def main():
    cases = json.loads((ROOT / "tests" / "student" / "cases.json").read_text(encoding="utf-8"))
    failed = 0
    for case in cases:
        task = case["input"]["task"]
        got = getattr(algorithms, task)(case["input"])
        if got != case["expected"]:
            failed += 1
            print("FAIL", case["name"])
            print(" expected", case["expected"])
            print(" actual  ", got)
        else:
            print("PASS", case["name"])
    mixed = (ROOT / "tests" / "student" / "mixed.jsonl").read_text(encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "Python" / "source" / "main.py")],
        input=mixed,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=20,
    )
    lines = proc.stdout.splitlines()
    ok = proc.returncode == 0 and len(lines) == 4
    parsed = [json.loads(line) for line in lines] if ok else []
    ok = ok and parsed[0]["length"] == 4 and parsed[1]["cost"] == 14
    ok = ok and parsed[2]["positions"] == [0, 1, 2] and parsed[3] == {"length": 0, "sequence": ""}
    if ok:
        print("PASS mixed-process")
    else:
        failed += 1
        print("FAIL mixed-process")
        print(proc.stdout)
        print(proc.stderr)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
