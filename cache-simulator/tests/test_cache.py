"""Basic correctness tests. Run:  python -m pytest tests   (or)   python tests/test_cache.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cache_sim import Cache, run_trace, sequential_trace, matrix_trace


def test_geometry():
    c = Cache(4096, 64, 2)
    assert c.num_sets == 32 and c.offset_bits == 6 and c.index_bits == 5


def test_address_split():
    c = Cache(4096, 64, 2)
    tag, index, offset = c._split(6720)
    assert (tag, index, offset) == (3, 9, 0)


def test_first_access_is_compulsory_miss_then_hit():
    c = Cache(1024, 32, 1)
    assert c.access(0) is False
    assert c.access(4) is True          # same block -> hit
    assert c.compulsory == 1


def test_direct_mapped_conflict():
    c = Cache(1024, 32, 1)              # 32 sets
    a, b = 0, 1024                      # same index, different tag
    c.access(a); c.access(b)
    assert c.access(a) is False         # a was evicted by b


def test_lru_vs_fifo():
    # 2-way, single set (fully assoc, 2 blocks). Pattern A B A C A:
    lru, fifo = Cache(64, 32, 2, "LRU"), Cache(64, 32, 2, "FIFO")
    for blk in [0, 1, 0, 2, 0]:
        lru.access(blk * 32); fifo.access(blk * 32)
    assert lru.hits == 2 and fifo.hits == 1   # LRU keeps A, FIFO evicts it


def test_writeback_counts_dirty_evictions():
    c = Cache(32, 32, 1)                # one block only
    c.access(0, is_write=True)
    c.access(32)                        # evicts dirty block
    assert c.writebacks == 1


def test_sequential_hit_rate():
    c = run_trace(Cache(4096, 64, 2), sequential_trace(1024, 4))
    assert abs(c.hit_rate - 15 / 16) < 1e-9     # 1 miss per 16 ints


def test_row_vs_column_major():
    row = run_trace(Cache(4096, 64, 4), matrix_trace(64, True))
    col = run_trace(Cache(4096, 64, 4), matrix_trace(64, False))
    assert row.miss_rate < col.miss_rate


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("PASS", name)
