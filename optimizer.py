"""
optimizer.py - Caching and performance optimization
"""

import time
from collections import OrderedDict


class LRUCache:
    """LRU cache for disk block reads."""

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

    def invalidate(self, key):
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()

    def hit_rate(self):
        total = self.hits + self.misses
        return round((self.hits / total) * 100, 1) if total > 0 else 0.0

    def stats(self):
        return {
            "capacity": self.capacity,
            "used": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_%": self.hit_rate(),
        }


class FragmentationAnalyzer:
    """Analyzes file fragmentation on disk."""

    def __init__(self, disk, inode_table):
        self.disk = disk
        self.inode_table = inode_table

    def analyze(self):
        results = []
        for inode in self.inode_table.all_inodes():
            if inode.file_type != "file" or not inode.blocks:
                continue
            blocks = sorted(inode.blocks)
            fragments = 1
            for i in range(1, len(blocks)):
                if blocks[i] != blocks[i - 1] + 1:
                    fragments += 1
            results.append({
                "file": inode.name,
                "blocks": inode.blocks,
                "fragments": fragments,
                "fragmented": fragments > 1,
            })
        return results

    def fragmentation_score(self):
        results = self.analyze()
        if not results:
            return 0.0
        fragmented = sum(1 for r in results if r["fragmented"])
        return round((fragmented / len(results)) * 100, 1)


class PerformanceMonitor:
    """Tracks read/write latency over time."""

    def __init__(self):
        self.read_times = []
        self.write_times = []

    def record_read(self, elapsed_ms):
        self.read_times.append(round(elapsed_ms, 3))
        if len(self.read_times) > 50:
            self.read_times.pop(0)

    def record_write(self, elapsed_ms):
        self.write_times.append(round(elapsed_ms, 3))
        if len(self.write_times) > 50:
            self.write_times.pop(0)

    def avg_read(self):
        return round(sum(self.read_times) / len(self.read_times), 3) if self.read_times else 0.0

    def avg_write(self):
        return round(sum(self.write_times) / len(self.write_times), 3) if self.write_times else 0.0

    def summary(self):
        return {
            "avg_read_ms": self.avg_read(),
            "avg_write_ms": self.avg_write(),
            "total_reads": len(self.read_times),
            "total_writes": len(self.write_times),
        }