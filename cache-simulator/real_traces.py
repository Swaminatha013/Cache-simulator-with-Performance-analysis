"""
real_traces.py - Load REAL memory traces and run the cache simulator on them.

Supported trace formats (auto-detected per line):
  1. Valgrind 'lackey' :   " L 04222c88,8"   " S 1ffefff8,4"   " M 0421e1a0,4"   ("I ..." = instruction fetch)
  2. Dinero / 'din'    :   "0 7fff1234"  (0=data read, 1=data write, 2=instruction fetch)
  3. CS:APP cache-lab  :   "L 10,4" / "S 18,4" / "M 20,4"   (same as lackey)
"""
import sys, gzip
from cache_sim import Cache, run_trace


def load_trace(path, include_instructions=False, max_accesses=None):
    """Return a list of (address, is_write). 'M' (modify) = a read followed by a write."""
    trace = []
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt') as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            try:
                if parts[0] in ("L", "S", "M", "I"):            # lackey / CS:APP
                    kind = parts[0]
                    addr = int(parts[1].split(",")[0], 16)
                    if kind == "I" and not include_instructions:
                        continue
                    if kind == "M":
                        trace.append((addr, False)); trace.append((addr, True))
                    else:
                        trace.append((addr, kind == "S"))
                else:                                           # Dinero 'din'
                    label, addr = int(parts[0]), int(parts[1], 16)
                    if label == 2 and not include_instructions:
                        continue
                    trace.append((addr, label == 1))
            except (ValueError, IndexError):
                continue                                        # skip comments / ==pid== lines
            if max_accesses and len(trace) >= max_accesses:
                break
    return trace


if __name__ == "__main__":
    # Usage: python real_traces.py traces/matmul.trace
    path = sys.argv[1] if len(sys.argv) > 1 else "traces/matmul.trace"
    t = load_trace(path)
    print(f"Loaded {len(t):,} accesses from {path}")
    c = run_trace(Cache(8192, 64, 4, "LRU"), t)
    c.report(f"Real trace: {path}")
