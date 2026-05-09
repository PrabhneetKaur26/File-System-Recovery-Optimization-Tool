"""
bitmap.py - Bitmap-based free space management
"""


class Bitmap:
    def __init__(self, total_blocks):
        self.total_blocks = total_blocks
        # True = free, False = used
        self.bits = [True] * total_blocks
        # Reserve block 0 for superblock, 1 for bitmap, 2-3 for inode table
        for i in range(4):
            self.bits[i] = False

    def allocate_block(self):
        """Allocate next free block. Returns block number or -1."""
        for i in range(self.total_blocks):
            if self.bits[i]:
                self.bits[i] = False
                return i
        return -1  # no free block

    def allocate_contiguous(self, count):
        """Allocate `count` contiguous blocks. Returns list or []."""
        start = -1
        run = 0
        for i in range(self.total_blocks):
            if self.bits[i]:
                if run == 0:
                    start = i
                run += 1
                if run == count:
                    for j in range(start, start + count):
                        self.bits[j] = False
                    return list(range(start, start + count))
            else:
                run = 0
                start = -1
        return []

    def free_block(self, block_num):
    # Prevent freeing reserved system blocks
        if 0 <= block_num < 4:
            return

        if 0 <= block_num < self.total_blocks:
            self.bits[block_num] = True
        if block_num < 4:
            return

    def free_blocks(self, block_list):
        for b in block_list:
            self.free_block(b)

    def free_count(self):
        return sum(self.bits)

    def used_count(self):
        return self.total_blocks - self.free_count()

    def is_free(self, block_num):
        return self.bits[block_num]

    def get_bitmap(self):
        return list(self.bits)

    def serialize(self):
        return "".join("1" if b else "0" for b in self.bits)

    @classmethod
    def deserialize(cls, total_blocks, data):
        bm = cls.__new__(cls)
        bm.total_blocks = total_blocks
        bm.bits = [c == "1" for c in data]
        return bm