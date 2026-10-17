"""Tiny runner so every test file also works without pytest:  py -3 tests\\test_x.py

Calls each module-level test_* function; a function that takes a `tmp` argument
gets its own empty temporary folder.
"""
from __future__ import annotations

import inspect
import tempfile
import traceback
from pathlib import Path


def run(namespace: dict) -> int:
    tests = [(n, f) for n, f in namespace.items() if n.startswith("test_") and callable(f)]
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        for i, (name, fn) in enumerate(tests):
            args = []
            if "tmp" in inspect.signature(fn).parameters:
                sub = Path(td) / f"t{i}"
                sub.mkdir()
                args.append(sub)
            try:
                fn(*args)
                print(f"PASS  {name}")
            except Exception:
                failures += 1
                print(f"FAIL  {name}")
                traceback.print_exc()
    print("OK" if failures == 0 else f"{failures} test(s) failed")
    return 1 if failures else 0
