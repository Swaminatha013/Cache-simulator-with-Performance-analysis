"""
experiments.py - Performance analysis: sweeps cache parameters and plots results.
Run:  python experiments.py
Needs: pip install matplotlib
"""
import matplotlib
matplotlib.use("Agg")           # saves images instead of opening windows
import matplotlib.pyplot as plt
from cache_sim import *

import os
OUT = "results"
os.makedirs(OUT, exist_ok=True)

def table(title, header, rows):
    print(f"\n### {title}")
    print(" | ".join(f"{h:>14}" for h in header))
    print("-" * (17 * len(header)))
    for r in rows:
        print(" | ".join(f"{str(x):>14}" for x in r))

# A realistic-ish workload with locality:
#  - 80% of accesses hit a small "hot" region (temporal locality)
#  - 15% walk sequentially through an array (spatial locality)
#  - 5%  jump to random far-away addresses (cache pollution)
#  - plus two arrays 4KB apart accessed together (causes conflict misses in low-associativity caches)
def make_workload(n=40000, seed=7):
    rnd = random.Random(seed)
    trace, seq = [], 0
    for _ in range(n):
        r = rnd.random()
        if r < 0.80:
            addr = rnd.randrange(0, 3072, 4)
        elif r < 0.95:
            addr = 0x10000 + seq; seq = (seq + 4) % 8192
        else:
            addr = rnd.randrange(0x40000, 0x80000, 4)
        trace.append((addr, rnd.random() < 0.25))
        if rnd.random() < 0.10:                       # conflicting pair of arrays
            a = rnd.randrange(0, 256, 4)
            trace += [(0x20000 + a, False), (0x20000 + 4096 + a, False), (0x20000 + 8192 + a, False)]
    return trace

workload = make_workload()

# ---- Experiment 1: cache size ----
sizes = [512, 1024, 2048, 4096, 8192, 16384]
mr = []
for s in sizes:
    c = run_trace(Cache(s, 32, 2, "LRU"), workload)
    mr.append(c.miss_rate * 100)
table("Exp 1: Cache size vs miss rate (32B blocks, 2-way, LRU)",
      ["Size (B)", "Miss rate %"], [(s, f"{m:.2f}") for s, m in zip(sizes, mr)])
plt.figure(); plt.plot(sizes, mr, "o-"); plt.xscale("log", base=2)
plt.xlabel("Cache size (bytes)"); plt.ylabel("Miss rate (%)")
plt.title("Cache size vs miss rate"); plt.grid(True); plt.savefig(f"{OUT}/exp1_size.png"); plt.close()

# ---- Experiment 2: associativity ----
ways = [1, 2, 4, 8, 16]
mr = []
for w in ways:
    c = run_trace(Cache(4096, 32, w, "LRU"), workload)
    mr.append(c.miss_rate * 100)
table("Exp 2: Associativity vs miss rate (4KB, 32B blocks, LRU)",
      ["Ways", "Miss rate %"], [(w, f"{m:.2f}") for w, m in zip(ways, mr)])
plt.figure(); plt.plot(ways, mr, "s-", color="green"); plt.xscale("log", base=2)
plt.xlabel("Associativity (ways)"); plt.ylabel("Miss rate (%)")
plt.title("Associativity vs miss rate"); plt.grid(True); plt.savefig(f"{OUT}/exp2_assoc.png"); plt.close()

# ---- Experiment 3: block size ----
blocks = [8, 16, 32, 64, 128, 256]
mr = []
for b in blocks:
    c = run_trace(Cache(4096, b, 2, "LRU"), workload)
    mr.append(c.miss_rate * 100)
table("Exp 3: Block size vs miss rate (4KB, 2-way, LRU)",
      ["Block (B)", "Miss rate %"], [(b, f"{m:.2f}") for b, m in zip(blocks, mr)])
plt.figure(); plt.plot(blocks, mr, "^-", color="red"); plt.xscale("log", base=2)
plt.xlabel("Block size (bytes)"); plt.ylabel("Miss rate (%)")
plt.title("Block size vs miss rate"); plt.grid(True); plt.savefig(f"{OUT}/exp3_block.png"); plt.close()

# ---- Experiment 4: replacement policy ----
rows = []
for p in ["LRU", "FIFO", "RANDOM"]:
    random.seed(42)
    c = run_trace(Cache(4096, 32, 4, p), workload)
    rows.append((p, f"{c.miss_rate*100:.2f}", f"{c.amat:.2f}"))
table("Exp 4: Replacement policy (4KB, 32B, 4-way)", ["Policy", "Miss rate %", "AMAT (cycles)"], rows)
plt.figure(); plt.bar([r[0] for r in rows], [float(r[1]) for r in rows], color=["#4c72b0", "#dd8452", "#55a868"])
plt.ylabel("Miss rate (%)"); plt.title("Replacement policy comparison")
plt.savefig(f"{OUT}/exp4_policy.png"); plt.close()

# ---- Experiment 5: spatial locality (matrix traversal) ----
rows = []
for name, rm in [("Row-major", True), ("Column-major", False)]:
    c = run_trace(Cache(4096, 64, 4, "LRU"), matrix_trace(64, rm))
    rows.append((name, f"{c.miss_rate*100:.2f}", f"{c.amat:.2f}"))
table("Exp 5: 64x64 matrix traversal (4KB, 64B, 4-way)", ["Order", "Miss rate %", "AMAT (cycles)"], rows)

print("\nSaved plots in results/: exp1_size.png, exp2_assoc.png, exp3_block.png, exp4_policy.png")
