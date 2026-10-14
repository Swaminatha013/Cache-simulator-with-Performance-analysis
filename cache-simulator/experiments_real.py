"""
experiments_real.py - Performance analysis on REAL traces (captured with Valgrind).
Run:  python experiments_real.py        (takes ~1-2 minutes)
"""
import os, random
from multiprocessing import Pool
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cache_sim import Cache, run_trace
from real_traces import load_trace

PROGRAMS = {                       # name -> trace file
    "matmul (naive)": "traces/matmul.trace.gz",
    "matmul (tiled)": "traces/matmul_tiled.trace.gz",
    "quicksort":      "traces/qsort_prog.trace.gz",
    "linked list":    "traces/linkedlist.trace.gz",
}
_cache_of_traces = {}

def job(args):
    prog, size, block, ways, policy = args
    if prog not in _cache_of_traces:
        _cache_of_traces[prog] = load_trace(PROGRAMS[prog])
    random.seed(42)
    c = run_trace(Cache(size, block, ways, policy), _cache_of_traces[prog])
    return args, c.miss_rate * 100, c.amat

def sweep(pool, name, values, make):
    jobs = [make(p, v) for p in PROGRAMS for v in values]
    res = {a: (m, t) for a, m, t in pool.map(job, jobs)}
    return {p: [res[make(p, v)][0] for v in values] for p in PROGRAMS}, res

def show(title, xname, values, data):
    print(f"\n### {title}")
    print(f"{xname:>10} | " + " | ".join(f"{p:>15}" for p in PROGRAMS))
    print("-" * (13 + 18 * len(PROGRAMS)))
    for i, v in enumerate(values):
        print(f"{v:>10} | " + " | ".join(f"{data[p][i]:>14.2f}%" for p in PROGRAMS))

def plot(values, data, xlabel, title, fname):
    plt.figure(figsize=(6, 4))
    for p in PROGRAMS:
        plt.plot(values, data[p], "o-", label=p)
    plt.xscale("log", base=2); plt.yscale("log")
    plt.xlabel(xlabel); plt.ylabel("Miss rate (%) [log scale]")
    plt.title(title); plt.grid(True, which="both", alpha=.3); plt.legend()
    plt.tight_layout(); plt.savefig(fname, dpi=120); plt.close()

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    with Pool() as pool:
        sizes = [1024, 2048, 4096, 8192, 16384, 32768, 65536]
        d, _ = sweep(pool, "size", sizes, lambda p, v: (p, v, 64, 4, "LRU"))
        show("Exp 1: Cache size (64B blocks, 4-way, LRU)", "Size (B)", sizes, d)
        plot(sizes, d, "Cache size (bytes)", "Real traces: cache size", "results/real_exp1_size.png")

        ways = [1, 2, 4, 8, 16]
        d, _ = sweep(pool, "ways", ways, lambda p, v: (p, 4096, 64, v, "LRU"))
        show("Exp 2: Associativity (4KB, 64B blocks, LRU)", "Ways", ways, d)
        plot(ways, d, "Associativity (ways)", "Real traces: associativity", "results/real_exp2_assoc.png")

        blocks = [16, 32, 64, 128, 256]
        d, _ = sweep(pool, "block", blocks, lambda p, v: (p, 8192, v, 4, "LRU"))
        show("Exp 3: Block size (8KB, 4-way, LRU)", "Block (B)", blocks, d)
        plot(blocks, d, "Block size (bytes)", "Real traces: block size", "results/real_exp3_block.png")

        pols = ["LRU", "FIFO", "RANDOM"]
        jobs = [(p, 2048, 64, 4, pol) for p in PROGRAMS for pol in pols]
        res = {a: m for a, m, _ in pool.map(job, jobs)}
        print("\n### Exp 4: Replacement policy (2KB, 64B blocks, 4-way)")
        print(f"{'Policy':>10} | " + " | ".join(f"{p:>15}" for p in PROGRAMS))
        print("-" * (13 + 18 * len(PROGRAMS)))
        for pol in pols:
            print(f"{pol:>10} | " + " | ".join(f"{res[(p,2048,64,4,pol)]:>14.2f}%" for p in PROGRAMS))

        # AMAT headline
        jobs = [(p, 4096, 64, 4, "LRU") for p in PROGRAMS]
        print("\n### AMAT summary (4KB, 64B, 4-way, LRU)")
        for a, m, t in pool.map(job, jobs):
            print(f"{a[0]:>16}: miss rate {m:6.2f}%   AMAT {t:6.2f} cycles")
    print("\nSaved plots in results/: real_exp1_size.png, real_exp2_assoc.png, real_exp3_block.png")
