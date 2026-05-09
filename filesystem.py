"""
filesystem.py - Core FileSystem class integrating all components
Upgraded: Defragmentation, Allocation Strategies, Forensic Analysis, WAL recovery
"""

import time
import random
from disk import Disk, TOTAL_BLOCKS, BLOCK_SIZE
from bitmap import Bitmap
from inode import InodeTable
from directory import Directory
from journal import Journal
from optimizer import LRUCache, FragmentationAnalyzer, PerformanceMonitor


STRATEGY_FIRST_FIT  = "First Fit"
STRATEGY_BEST_FIT   = "Best Fit"
STRATEGY_CONTIGUOUS = "Contiguous (Extent)"


class FileSystem:
    def __init__(self):
        self.disk = Disk(TOTAL_BLOCKS, BLOCK_SIZE)
        self.bitmap = Bitmap(TOTAL_BLOCKS)
        self.inode_table = InodeTable(max_inodes=32)
        self.root = Directory("root")
        self.journal = Journal()
        self.cache = LRUCache(capacity=8)
        self.perf = PerformanceMonitor()
        self.crashed = False
        self.allocation_strategy = STRATEGY_CONTIGUOUS
        self.terminal_log = []
        self.iops_counter = 0
        self.bytes_transferred = 0
        self.recently_accessed = set()

    def _term(self, level, msg):
        ts = time.strftime("%H:%M:%S")
        self.terminal_log.append(f"[{ts}][{level}] {msg}")
        if len(self.terminal_log) > 200:
            self.terminal_log.pop(0)

    def _allocate_blocks(self, count):
        if self.allocation_strategy == STRATEGY_CONTIGUOUS:
            alloc = self.bitmap.allocate_contiguous(count)
            if alloc:
                self._term("ALLOC", f"Contiguous extent: blocks {alloc[0]}-{alloc[-1]}")
                return alloc
        if self.allocation_strategy == STRATEGY_BEST_FIT:
            alloc = self._best_fit(count)
            self._term("ALLOC", f"Best-fit allocated: {alloc}")
            return alloc
        alloc = [self.bitmap.allocate_block() for _ in range(count)]
        self._term("ALLOC", f"First-fit allocated: {alloc}")
        return alloc

    def _best_fit(self, count):
        bits = self.bitmap.bits
        runs = []
        i = 0
        while i < len(bits):
            if bits[i]:
                start = i
                while i < len(bits) and bits[i]:
                    i += 1
                runs.append((i - start, start))
            else:
                i += 1
        runs.sort()
        for length, start in runs:
            if length >= count:
                selected = list(range(start, start + count))
                for b in selected:
                    self.bitmap.bits[b] = False
                return selected
        return [self.bitmap.allocate_block() for _ in range(count)]

    def create_file(self, name, content="", path="/"):
        directory = self._resolve_path(path)
        if directory is None:
            raise FileNotFoundError(f"Path '{path}' not found")
        self._term("INFO", f"Creating file '{name}' in '{path}'")
        j_entry = self.journal.begin("create", {"name": name, "content": content, "path": path})
        try:
            inode = self.inode_table.create(name, "file")
            data_bytes = content.encode("utf-8")
            blocks_needed = max(1, -(-len(data_bytes) // BLOCK_SIZE))
            self._term("INFO", f"Allocating {blocks_needed} block(s) via {self.allocation_strategy}")
            alloc = self._allocate_blocks(blocks_needed)
            if -1 in alloc:
                for blk in alloc:
                    if blk != -1:
                        self.bitmap.free_block(blk)
                self.inode_table.delete(inode.inode_id)
                raise OSError("Disk full - not enough free blocks")
            for i, blk in enumerate(alloc):
                chunk = data_bytes[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE]
                self.disk.write_block(blk, chunk)
                inode.add_block(blk)
                self.cache.put(blk, chunk)
                self._term("WRITE", f"inode={inode.inode_id} block={blk}")
            inode.size = len(data_bytes)
            directory.add_file(name, inode.inode_id)
            self.journal.commit(j_entry)
            self.iops_counter += blocks_needed
            self.bytes_transferred += inode.size
            self.perf.record_write(self.disk.get_stats()["avg_write_ms"])
            self._term("OK", f"File '{name}' created - inode #{inode.inode_id}, {inode.size}B")
            return inode
        except Exception as e:
            self.journal.abort(j_entry)
            self._term("ERR", str(e))
            raise e

    def read_file(self, name, path="/"):
        directory = self._resolve_path(path)
        entry = directory.get_entry(name) if directory else None
        if entry is None:
            raise FileNotFoundError(f"File '{name}' not found in '{path}'")
        inode = self.inode_table.get(entry.inode_id)
        if inode is None:
            raise FileNotFoundError(f"Inode for '{name}' is missing")
        self._term("INFO", f"Reading '{name}' - {len(inode.blocks)} block(s)")
        start = time.perf_counter()
        data = b""
        for blk in inode.blocks:
            cached = self.cache.get(blk)
            if cached is not None:
                data += cached
                self._term("CACHE HIT", f"block={blk}")
                self.recently_accessed.add(blk)
            else:
                raw = self.disk.read_block(blk)
                if raw is None:
                    raise IOError(f"Block {blk} is corrupted - run recovery")
                data += raw
                self.cache.put(blk, raw)
                self.recently_accessed.add(blk)
                self._term("DISK READ", f"block={blk}")
            if len(self.recently_accessed) > 16:
                self.recently_accessed.discard(next(iter(self.recently_accessed)))
        elapsed = (time.perf_counter() - start) * 1000
        self.perf.record_read(elapsed)
        self.iops_counter += len(inode.blocks)
        self.bytes_transferred += inode.size
        self._term("OK", f"Read '{name}' - {elapsed:.2f}ms, {inode.size}B")
        return data.decode("utf-8", errors="replace")[:inode.size]

    def write_file(self, name, content, path="/"):
        directory = self._resolve_path(path)
        entry = directory.get_entry(name) if directory else None
        if entry is None:
            return self.create_file(name, content, path)
        inode = self.inode_table.get(entry.inode_id)
        j_entry = self.journal.begin("write", {"name": name, "content": content, "path": path})
        self._term("INFO", f"Writing '{name}' ({len(content)}B)")
        try:
            old_blocks = list(inode.blocks)
            data_bytes = content.encode("utf-8")
            blocks_needed = max(1, -(-len(data_bytes) // BLOCK_SIZE))
            alloc = self._allocate_blocks(blocks_needed)
            if -1 in alloc:
                for blk in alloc:
                    if blk != -1:
                        self.bitmap.free_block(blk)
                raise OSError("Disk full - not enough free blocks")
            new_blocks = []
            for i, blk in enumerate(alloc):
                chunk = data_bytes[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE]
                self.disk.write_block(blk, chunk)
                self.cache.put(blk, chunk)
                new_blocks.append(blk)
                self._term("WRITE", f"inode={inode.inode_id} block={blk}")
            inode.blocks = new_blocks
            inode.size = len(data_bytes)
            inode.update_modified()
            for b in old_blocks:
                self.disk.free_block(b)
                self.bitmap.free_block(b)
                self.cache.invalidate(b)
            self.journal.commit(j_entry)
            self.iops_counter += blocks_needed
            self.bytes_transferred += inode.size
            self._term("OK", f"Write '{name}' complete")
            return inode
        except Exception as e:
            self.journal.abort(j_entry)
            self._term("ERR", str(e))
            raise e

    def delete_file(self, name, path="/"):
        directory = self._resolve_path(path)
        entry = directory.get_entry(name) if directory else None
        if entry is None:
            raise FileNotFoundError(f"File '{name}' not found")
        j_entry = self.journal.begin("delete", {"name": name, "path": path})
        inode = self.inode_table.get(entry.inode_id)
        if inode:
            for b in inode.blocks:
                self.disk.free_block(b)
                self.bitmap.free_block(b)
                self.cache.invalidate(b)
            self.inode_table.delete(entry.inode_id)
            self._term("DELETE", f"Removed '{name}', freed {len(inode.blocks)} block(s)")
        directory.remove(name)
        self.journal.commit(j_entry)

    def make_dir(self, name, path="/"):
        directory = self._resolve_path(path)
        if directory is None:
            raise FileNotFoundError(f"Path '{path}' not found")
        inode = self.inode_table.create(name, "dir")
        directory.add_subdir(name, inode.inode_id)
        self._term("MKDIR", f"Created dir '/{name}'")
        return inode

    def simulate_crash(self, crash_type="random"):
        self.crashed = True
        self._term("CRASH", f"CRASH TRIGGERED - type={crash_type}")
        crashed_blocks = self.disk.simulate_crash(corruption_ratio=0.25)
        self.journal.crash_event()
        self._term("CRASH", f"Corrupted blocks: {crashed_blocks}")
        return crashed_blocks

    def recover(self):
        self._term("RECOVERY", "Journal WAL replay started...")
        self.crashed = False
        self.disk.corrupted_blocks.clear()
        self.cache.clear()
        result = self.journal.replay(self)
        for r in result:
            self._term("RECOVERY", r)
        self._term("OK", f"Recovery complete - {len(result)} ops replayed")
        return result

    def defragment(self):
        self._term("DEFRAG", "Starting defragmentation engine...")
        report = []
        next_free = 4
        for inode in self.inode_table.all_inodes():
            if inode.file_type != "file" or not inode.blocks:
                continue
            old_blocks = list(inode.blocks)
            num = len(old_blocks)
            data = b""
            for blk in old_blocks:
                raw = self.disk.blocks[blk]
                data += (raw or b"\x00" * BLOCK_SIZE)
            for blk in old_blocks:
                self.disk.free_block(blk)
                self.bitmap.free_block(blk)
                self.cache.invalidate(blk)
            new_blocks = []
            for i in range(num):
                target = next_free + i
                if target >= self.disk.total_blocks:
                    break
                chunk = data[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE]
                self.disk.blocks[target] = chunk
                self.bitmap.bits[target] = False
                self.cache.put(target, chunk)
                new_blocks.append(target)
            inode.blocks = new_blocks
            inode.update_modified()
            next_free += num
            self._term("DEFRAG", f"'{inode.name}': {old_blocks} -> {new_blocks}")
            report.append({"file": inode.name, "old": old_blocks, "new": new_blocks})
        self._term("OK", f"Defrag complete - {len(report)} files relocated")
        return report

    def forensic_analysis(self):
        issues = []
        for blk in self.disk.corrupted_blocks:
            issues.append({"severity": "CRITICAL", "type": "Corrupted Block",
                           "detail": f"Block {blk} is unreadable", "action": "Run Recovery"})
        referenced_inodes = {iid for _, iid in self.root.flat_files()}
        for inode in self.inode_table.all_inodes():
            if inode.inode_id not in referenced_inodes and inode.file_type == "file":
                issues.append({"severity": "WARNING", "type": "Orphan Inode",
                               "detail": f"Inode #{inode.inode_id} ('{inode.name}') has no directory entry",
                               "action": "Delete or re-link inode"})
        owned_blocks = set()
        for inode in self.inode_table.all_inodes():
            for b in inode.blocks:
                owned_blocks.add(b)
        for blk_num in range(4, self.disk.total_blocks):
            if self.disk.blocks[blk_num] is not None and blk_num not in owned_blocks:
                issues.append({"severity": "WARNING", "type": "Leaked Block",
                               "detail": f"Block {blk_num} used on disk but owned by no inode",
                               "action": "Free block manually"})
        for blk_num in range(4, self.disk.total_blocks):
            bm_free = self.bitmap.is_free(blk_num)
            disk_has_data = self.disk.blocks[blk_num] is not None
            if bm_free and disk_has_data:
                issues.append({"severity": "WARNING", "type": "Bitmap Inconsistency",
                               "detail": f"Block {blk_num}: bitmap=free but disk=occupied",
                               "action": "Update bitmap"})
        block_owners = {}
        for inode in self.inode_table.all_inodes():
            for b in inode.blocks:
                if b in block_owners:
                    issues.append({"severity": "CRITICAL", "type": "Double Allocation",
                                   "detail": f"Block {b} claimed by inode #{block_owners[b]} AND #{inode.inode_id}",
                                   "action": "Immediate recovery needed"})
                else:
                    block_owners[b] = inode.inode_id
        self._term("FORENSIC", f"Scan complete - {len(issues)} issue(s) found")
        return issues

    def benchmark_strategies(self):
        results = {}
        strategies = [STRATEGY_FIRST_FIT, STRATEGY_BEST_FIT, STRATEGY_CONTIGUOUS]
        test_sizes = [1, 2, 1, 3, 1, 2]
        for strat in strategies:
            bm = Bitmap(64)
            frag_count = 0
            t0 = time.perf_counter()
            for sz in test_sizes:
                if strat == STRATEGY_CONTIGUOUS:
                    blocks = bm.allocate_contiguous(sz) or [bm.allocate_block() for _ in range(sz)]
                elif strat == STRATEGY_BEST_FIT:
                    runs = []
                    i = 0
                    bits = bm.bits
                    while i < len(bits):
                        if bits[i]:
                            start = i
                            while i < len(bits) and bits[i]:
                                i += 1
                            runs.append((i - start, start))
                        else:
                            i += 1
                    runs.sort()
                    blocks = []
                    for length, start in runs:
                        if length >= sz:
                            blocks = list(range(start, start + sz))
                            for b in blocks:
                                bm.bits[b] = False
                            break
                    if not blocks:
                        blocks = [bm.allocate_block() for _ in range(sz)]
                else:
                    blocks = [bm.allocate_block() for _ in range(sz)]
                if blocks and len(blocks) > 1:
                    sblocks = sorted(b for b in blocks if b != -1)
                    for j in range(1, len(sblocks)):
                        if sblocks[j] != sblocks[j - 1] + 1:
                            frag_count += 1
            elapsed = (time.perf_counter() - t0) * 1000
            results[strat] = {"strategy": strat, "fragmentation": frag_count,
                              "alloc_time_ms": round(elapsed, 3), "iops_simulated": len(test_sizes)}
        return results

    def _replay_create(self, name, content, path="/"):
        try:
            directory = self._resolve_path(path)

            # Skip recovery if file already exists
            if directory and directory.get_entry(name):
                self._term("RECOVERY", f"Skipped '{name}' (already exists)")
                return

            self.create_file(name, content, path)
            self._term("RECOVERY", f"Recovered file '{name}'")

        except Exception as e:
            self._term("ERR", f"Replay create failed: {str(e)}")

    def _replay_delete(self, name, path="/"):
        try:
            directory = self._resolve_path(path)

            # Skip if file already deleted
            if not directory or not directory.get_entry(name):
                self._term("RECOVERY", f"Skip delete '{name}' (already removed)")
                return

            self.delete_file(name, path)
            self._term("RECOVERY", f"Recovered delete '{name}'")

        except Exception as e:
            self._term("ERR", f"Replay delete failed: {str(e)}")

    def _replay_write(self, name, content, path="/"):
        try:
            directory = self._resolve_path(path)

            # If file missing, recreate it
            if not directory or not directory.get_entry(name):
                self.create_file(name, content, path)
                self._term("RECOVERY", f"Recovered missing file '{name}'")
            else:
                self.write_file(name, content, path)
                self._term("RECOVERY", f"Recovered write '{name}'")

        except Exception as e:
            self._term("ERR", f"Replay write failed: {str(e)}")

    def _resolve_path(self, path):
        if path in ("/", ""):
            return self.root
        parts = [p for p in path.strip("/").split("/") if p]
        node = self.root
        for part in parts:
            sub = node.get_subdir(part)
            if sub is None:
                return None
            node = sub
        return node

    def list_files(self, path="/"):
        directory = self._resolve_path(path)
        return directory.list_entries() if directory else []

    def get_tree(self):
        return self.root.tree()

    def get_all_files(self):
        files = []
        for path, inode_id in self.root.flat_files():
            inode = self.inode_table.get(inode_id)
            if inode:
                files.append({"name": inode.name, "path": path, "size": inode.size,
                               "blocks": inode.blocks, "created": inode.created_at,
                               "modified": inode.modified_at})
        return files

    def get_fragmentation(self):
        analyzer = FragmentationAnalyzer(self.disk, self.inode_table)
        return analyzer.analyze(), analyzer.fragmentation_score()

    def get_summary(self):
        disk_stats = self.disk.get_stats()
        cache_stats = self.cache.stats()
        perf = self.perf.summary()
        _, frag_score = self.get_fragmentation()
        throughput = round(self.bytes_transferred / 1024, 2) if self.bytes_transferred else 0
        return {
            "disk": disk_stats, "cache": cache_stats, "perf": perf,
            "fragmentation_score": frag_score,
            "total_files": len([i for i in self.inode_table.all_inodes() if i.file_type == "file"]),
            "total_dirs":  len([i for i in self.inode_table.all_inodes() if i.file_type == "dir"]),
            "crashed": self.crashed, "iops": self.iops_counter,
            "throughput_kb": throughput,
            "allocation_strategy": self.allocation_strategy,
            "recently_accessed": list(self.recently_accessed),
        }