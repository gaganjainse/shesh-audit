"""Real hot-path benchmarks for shesh-audit (stdlib only, CI-safe).

Measures the actual hot paths: policy-gate checks (allow + deny) and
hash-chained audit log appends. Median of N runs with loose bounds.
Run:  python benchmarks/bench_hotpaths.py
"""

from __future__ import annotations

import statistics
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shesh_audit.gate import Guard  # noqa: E402
from shesh_audit.log import AuditLog  # noqa: E402


def bench(label: str, fn, n: int = 200) -> float:
    times: list[float] = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    med = statistics.median(times)
    print(f"  {label:44s} median {med * 1e6:9.2f} µs  (n={n})")
    return med


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="shesh-audit-bench-")

    audit = AuditLog(root=Path(tmp) / "audit")
    guard = Guard(audit=audit)

    # Allowed call path (fast path): read-only tool.
    bench("guard check allow (read tool)", lambda: guard.check("read_file", {"path": "/tmp/x"}), n=1000)
    # Denied call path: protected path.
    bench("guard check deny (protected path)", lambda: guard.check("write_file", {"path": "/home/u/.ssh/id_rsa"}), n=1000)

    # Hash-chained append throughput.
    def append_one() -> None:
        audit.record("agent", "tool", "allow", args={"tool": "read"})

    bench("audit append (hash-chained)", append_one, n=500)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
