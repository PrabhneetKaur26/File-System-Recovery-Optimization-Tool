"""
inode.py - Inode-based file system metadata
"""

import time


class Inode:
    def __init__(self, inode_id, name, file_type="file", size=0, blocks=None):
        self.inode_id = inode_id
        self.name = name
        self.file_type = file_type  # "file" or "dir"
        self.size = size
        self.blocks = blocks or []  # list of block numbers
        self.created_at = time.time()
        self.modified_at = time.time()
        self.permissions = "rw-r--r--"
        self.link_count = 1

    def update_modified(self):
        self.modified_at = time.time()

    def add_block(self, block_num):
        self.blocks.append(block_num)
        self.update_modified()

    def remove_blocks(self):
        blocks = list(self.blocks)
        self.blocks = []
        self.size = 0
        self.update_modified()
        return blocks

    def to_dict(self):
        return {
            "inode_id": self.inode_id,
            "name": self.name,
            "file_type": self.file_type,
            "size": self.size,
            "blocks": self.blocks,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "permissions": self.permissions,
            "link_count": self.link_count,
        }

    @classmethod
    def from_dict(cls, d):
        node = cls(d["inode_id"], d["name"], d["file_type"], d["size"], d["blocks"])
        node.created_at = d["created_at"]
        node.modified_at = d["modified_at"]
        node.permissions = d["permissions"]
        node.link_count = d["link_count"]
        return node


class InodeTable:
    def __init__(self, max_inodes=32):
        self.max_inodes = max_inodes
        self.inodes = {}
        self._next_id = 1

    def create(self, name, file_type="file"):
        if len(self.inodes) >= self.max_inodes:
            raise OverflowError("Inode table full")
        inode_id = self._next_id
        self._next_id += 1
        node = Inode(inode_id, name, file_type)
        self.inodes[inode_id] = node
        return node

    def get(self, inode_id):
        return self.inodes.get(inode_id)

    def delete(self, inode_id):
        return self.inodes.pop(inode_id, None)

    def all_inodes(self):
        return list(self.inodes.values())

    def serialize(self):
        import json
        return json.dumps({str(k): v.to_dict() for k, v in self.inodes.items()})

    @classmethod
    def deserialize(cls, data):
        import json
        table = cls.__new__(cls)
        table.max_inodes = 32
        raw = json.loads(data)
        table.inodes = {int(k): Inode.from_dict(v) for k, v in raw.items()}
        table._next_id = max(table.inodes.keys(), default=0) + 1
        return table