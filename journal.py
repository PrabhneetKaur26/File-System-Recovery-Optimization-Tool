"""
journal.py - Journaling system for crash recovery
"""

import time
import json


class JournalEntry:
    STATES = ["pending", "committed", "checkpointed", "aborted"]

    def __init__(self, op_type, details):
        self.timestamp = time.time()
        self.op_type = op_type   # "create", "write", "delete", "mkdir"
        self.details = details   # dict with all info needed to replay/undo
        self.state = "pending"

    def commit(self):
        self.state = "committed"

    def checkpoint(self):
        self.state = "checkpointed"

    def abort(self):
        self.state = "aborted"

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "op_type": self.op_type,
            "details": self.details,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, d):
        e = cls.__new__(cls)
        e.timestamp = d["timestamp"]
        e.op_type = d["op_type"]
        e.details = d["details"]
        e.state = d["state"]
        return e


class Journal:
    def __init__(self):
        self.entries = []
        self.log = []  # human-readable log lines

    def begin(self, op_type, details):
        entry = JournalEntry(op_type, details)
        self.entries.append(entry)
        self.log.append(f"[BEGIN]  {op_type.upper()} — {details}")
        return entry

    def commit(self, entry):
        entry.commit()
        self.log.append(f"[COMMIT] {entry.op_type.upper()} committed ✅")

    def checkpoint(self, entry):
        entry.checkpoint()
        self.log.append(f"[CKPT]   {entry.op_type.upper()} checkpointed 💾")

    def abort(self, entry):
        entry.abort()
        self.log.append(f"[ABORT]  {entry.op_type.upper()} aborted ❌")

    def crash_event(self):
        self.log.append("💥 CRASH DETECTED — Journal recovery required!")
        # Mark all pending entries as needing replay
        for e in self.entries:
            if e.state == "pending":
                e.state = "aborted"

    def get_recoverable(self):
        """Return committed-but-not-checkpointed entries for replay."""
        return [e for e in self.entries if e.state == "committed"]

    def replay(self, filesystem):
        """Replay committed journal entries to restore consistency."""
        recovered = []
        for entry in self.get_recoverable():
            try:
                if entry.op_type == "create":
                    d = entry.details
                    filesystem._replay_create(d["name"], d["content"], d.get("path", "/"))
                    entry.checkpoint()
                    recovered.append(f"Recovered file: {d['name']}")
                elif entry.op_type == "delete":
                    d = entry.details
                    filesystem._replay_delete(d["name"], d.get("path", "/"))
                    entry.checkpoint()
                    recovered.append(f"Replayed delete: {d['name']}")
                elif entry.op_type == "write":
                    d = entry.details
                    filesystem._replay_write(d["name"], d["content"], d.get("path", "/"))
                    entry.checkpoint()
                    recovered.append(f"Recovered write: {d['name']}")
            except Exception as ex:
                recovered.append(f"Replay failed for {entry.op_type}: {ex}")
        self.log.append(f"🔄 Recovery complete — {len(recovered)} operations replayed")
        return recovered

    def get_log(self):
        return list(self.log)

    def serialize(self):
        return json.dumps([e.to_dict() for e in self.entries])

    @classmethod
    def deserialize(cls, data):
        j = cls.__new__(cls)
        j.entries = [JournalEntry.from_dict(d) for d in json.loads(data)]
        j.log = []
        return j