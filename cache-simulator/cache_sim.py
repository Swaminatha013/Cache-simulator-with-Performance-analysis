"""
cache_sim.py - A simple CPU cache simulator.

Supports: direct-mapped, N-way set-associative, fully associative
Replacement policies: LRU, FIFO, Random
Write policy: write-back + write-allocate
"""
import math
import random
from collections import OrderedDict


class Cache:
    def __init__(self, cache_size, block_size, associativity, policy="LRU",
                 hit_time=1, miss_penalty=100):
        # cache_size, block_size in bytes. associativity = ways per set.
        # associativity=1 -> direct-mapped; associativity=num_blocks -> fully associative
        assert cache_size % (block_size * associativity) == 0, "Bad cache geometry"
        self.cache_size = cache_size
        self.block_size = block_size
        self.assoc = associativity
        self.policy = policy.upper()
        self.hit_time = hit_time
        self.miss_penalty = miss_penalty

        self.num_sets = cache_size // (block_size * associativity)
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(self.num_sets))

        # Each set maps tag -> dirty_bit. OrderedDict keeps insertion/use order.
        self.sets = [OrderedDict() for _ in range(self.num_sets)]
        self.seen_blocks = set()  # to detect compulsory (first-ever) misses

        self.hits = self.misses = self.compulsory = 0
        self.reads = self.writes = self.writebacks = 0

    def _split(self, address):
        offset_mask = (1 << self.offset_bits) - 1
        index = (address >> self.offset_bits) & (self.num_sets - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        return tag, index, address & offset_mask

    def access(self, address, is_write=False):
        """Simulate one memory access. Returns True on hit, False on miss."""
        tag, index, _ = self._split(address)
        cache_set = self.sets[index]
        if is_write:
            self.writes += 1
        else:
            self.reads += 1

        if tag in cache_set:                       # ---- HIT ----
            self.hits += 1
            if self.policy == "LRU":
                cache_set.move_to_end(tag)         # mark most recently used
            if is_write:
                cache_set[tag] = True              # dirty
            return True

        # ---- MISS ----
        self.misses += 1
        block_id = address >> self.offset_bits
        if block_id not in self.seen_blocks:
            self.compulsory += 1
            self.seen_blocks.add(block_id)

        if len(cache_set) >= self.assoc:           # set full -> evict
            if self.policy == "RANDOM":
                victim = random.choice(list(cache_set.keys()))
            else:                                  # LRU and FIFO: oldest is first
                victim = next(iter(cache_set))
            if cache_set.pop(victim):              # dirty -> write back to memory
                self.writebacks += 1
        cache_set[tag] = is_write                  # write-allocate
        return False

    # ---------- statistics ----------
    @property
    def accesses(self):
        return self.hits + self.misses

    @property
    def hit_rate(self):
        return self.hits / self.accesses if self.accesses else 0.0

    @property
    def miss_rate(self):
        return 1 - self.hit_rate if self.accesses else 0.0

    @property
    def amat(self):
        """Average Memory Access Time = hit_time + miss_rate * miss_penalty"""
        return self.hit_time + self.miss_rate * self.miss_penalty

    def report(self, title="Cache"):
        kind = ("Direct-mapped" if self.assoc == 1 else
                "Fully associative" if self.num_sets == 1 else f"{self.assoc}-way set-associative")
        print(f"\n===== {title} =====")
        print(f"Config        : {self.cache_size} B, {self.block_size} B blocks, {kind}, {self.policy}")
        print(f"Sets / Index  : {self.num_sets} sets, {self.index_bits} index bits, {self.offset_bits} offset bits")
        print(f"Accesses      : {self.accesses}  (reads {self.reads}, writes {self.writes})")
        print(f"Hits / Misses : {self.hits} / {self.misses}  (compulsory misses: {self.compulsory})")
        print(f"Hit rate      : {self.hit_rate*100:.2f}%")
        print(f"Miss rate     : {self.miss_rate*100:.2f}%")
        print(f"Write-backs   : {self.writebacks}")
        print(f"AMAT          : {self.amat:.2f} cycles")


# ---------------- trace generators ----------------
def sequential_trace(n, stride=4):
    return [(i * stride, False) for i in range(n)]

def loop_trace(array_bytes, repeats, stride=4):
    return [(a, False) for _ in range(repeats) for a in range(0, array_bytes, stride)]

def random_trace(n, addr_space=1 << 16, write_ratio=0.3, seed=1):
    rnd = random.Random(seed)
    return [(rnd.randrange(0, addr_space, 4), rnd.random() < write_ratio) for _ in range(n)]

def matrix_trace(n, row_major=True, elem=4):
    """Walk an n x n matrix of 4-byte ints either row-by-row or column-by-column."""
    out = []
    for i in range(n):
        for j in range(n):
            r, c = (i, j) if row_major else (j, i)
            out.append(((r * n + c) * elem, False))
    return out

def run_trace(cache, trace):
    for addr, is_write in trace:
        cache.access(addr, is_write)
    return cache


if __name__ == "__main__":
    # Quick demo: 4 KB, 64 B blocks, 2-way, LRU on a mixed random trace
    c = Cache(cache_size=4096, block_size=64, associativity=2, policy="LRU")
    run_trace(c, random_trace(10000))
    c.report("Demo: random trace")

    # Row-major vs column-major (spatial locality!)
    for rm in (True, False):
        c = Cache(4096, 64, 4, "LRU")
        run_trace(c, matrix_trace(64, row_major=rm))
        c.report("Matrix " + ("ROW-major" if rm else "COLUMN-major"))
