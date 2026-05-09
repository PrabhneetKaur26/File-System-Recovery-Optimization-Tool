"""
directory.py - Directory structure (tree)
"""


class DirectoryEntry:
    def __init__(self, name, inode_id, entry_type="file"):
        self.name = name
        self.inode_id = inode_id
        self.entry_type = entry_type  # "file" or "dir"

    def to_dict(self):
        return {"name": self.name, "inode_id": self.inode_id, "entry_type": self.entry_type}


class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent  # parent Directory or None
        self.entries = {}  # name -> DirectoryEntry
        self.subdirs = {}  # name -> Directory

    def add_file(self, name, inode_id):
        if name in self.entries:
            raise FileExistsError(f"'{name}' already exists in '{self.name}'")
        self.entries[name] = DirectoryEntry(name, inode_id, "file")

    def add_subdir(self, name, inode_id):
        if name in self.subdirs:
            raise FileExistsError(f"Directory '{name}' already exists in '{self.name}'")
        self.subdirs[name] = Directory(name, parent=self)
        self.entries[name] = DirectoryEntry(name, inode_id, "dir")
        return self.subdirs[name]

    def remove(self, name):
        self.entries.pop(name, None)
        self.subdirs.pop(name, None)

    def list_entries(self):
        return list(self.entries.values())

    def get_subdir(self, name):
        return self.subdirs.get(name)

    def get_entry(self, name):
        return self.entries.get(name)

    def path(self):
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts[:-1])) if len(parts) > 1 else "/"

    def tree(self, indent=0):
        lines = [" " * indent + f"📁 {self.name}/"]
        for name, entry in self.entries.items():
            if entry.entry_type == "dir":
                sub = self.subdirs.get(name)
                if sub:
                    lines.extend(sub.tree(indent + 2))
            else:
                lines.append(" " * (indent + 2) + f"📄 {name}")
        return lines

    def flat_files(self):
        """Return all (path, inode_id) pairs recursively."""
        results = []
        prefix = self.path()
        for name, entry in self.entries.items():
            full_path = prefix.rstrip("/") + "/" + name
            if entry.entry_type == "file":
                results.append((full_path, entry.inode_id))
            elif entry.entry_type == "dir":
                sub = self.subdirs.get(name)
                if sub:
                    results.extend(sub.flat_files())
        return results