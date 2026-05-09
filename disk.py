"""
disk.py - Simulated disk with block storage
"""

import time
import random

BLOCK_SIZE = 512  # bytes per block
TOTAL_BLOCKS = 64  # total blocks on disk


class Disk:
    def __init__(self, total_blocks=TOTAL_BLOCKS, block_size=BLOCK_SIZE):
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.blocks = [None] * total_blocks  # None = free, bytes = used
        self.read_count = 0
        self.write_count = 0
        self.read_time_total = 0.0
        self.write_time_total = 0.0
        self.corrupted_blocks = set()

    def read_block(self, block_num):
        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(f"Block {block_num} out of range")
        start = time.perf_counter()
        time.sleep(0.001)  # simulate disk latency
        elapsed = time.perf_counter() - start
        self.read_count += 1
        self.read_time_total += elapsed
        if block_num in self.corrupted_blocks:
            return None  # simulate unreadable block
        return self.blocks[block_num]

    def write_block(self, block_num, data):
        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(f"Block {block_num} out of range")
        start = time.perf_counter()
        time.sleep(0.002)  # simulate disk write latency
        elapsed = time.perf_counter() - start
        self.write_count += 1
        self.write_time_total += elapsed
        self.blocks[block_num] = data
        return True

    def free_block(self, block_num):
        if 0 <= block_num < self.total_blocks:
            self.blocks[block_num] = None
            self.corrupted_blocks.discard(block_num)

    def simulate_crash(self, corruption_ratio=0.2):
        """Randomly corrupt some blocks to simulate a disk crash."""
        used = [i for i in range(self.total_blocks) if self.blocks[i] is not None]
        num_corrupt = max(1, int(len(used) * corruption_ratio))
        crashed = random.sample(used, min(num_corrupt, len(used)))
        for b in crashed:
            self.corrupted_blocks.add(b)
        return crashed

    def get_stats(self):
        used = sum(1 for b in self.blocks if b is not None)
        avg_read = (self.read_time_total / self.read_count * 1000) if self.read_count else 0
        avg_write = (self.write_time_total / self.write_count * 1000) if self.write_count else 0
        return {
            "total_blocks": self.total_blocks,
            "used_blocks": used,
            "free_blocks": self.total_blocks - used,
            "corrupted_blocks": len(self.corrupted_blocks),
            "read_count": self.read_count,
            "write_count": self.write_count,
            "avg_read_ms": round(avg_read, 3),
            "avg_write_ms": round(avg_write, 3),
        }

    def get_block_map(self):
        """Returns list of block states: 'free', 'used', 'corrupted'"""
        states = []
        for i in range(self.total_blocks):
            if i in self.corrupted_blocks:
                states.append("corrupted")
            elif self.blocks[i] is not None:
                states.append("used")
            else:
                states.append("free")
        return states