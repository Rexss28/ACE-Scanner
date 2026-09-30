"""Tests for the database merge workflow."""

import os
import tempfile
from pathlib import Path

from core.data_access import DataAccess
from scripts.merge_databases import merge


def make_temp_db() -> str:
    """Create a fresh temp DB path. Caller is responsible for cleanup."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.unlink(path)  # DataAccess will create it
    return path


def cleanup(*paths):
    """Delete DB files and their WAL/SHM sidecars with retry."""
    import gc
    import time

    gc.collect()
    time.sleep(0.05)

    for p in paths:
        for suffix in ["", "-wal", "-shm"]:
            f = Path(str(p) + suffix)
            if f.exists():
                for attempt in range(5):
                    try:
                        f.unlink()
                        break
                    except PermissionError:
                        time.sleep(0.05)


# ----------------------------------------------------------------------
# Basic merge tests
# ----------------------------------------------------------------------
def test_merge_two_databases():
    """Two laptops, each scans different people, merge into one."""
    db_a = make_temp_db()
    db_b = make_temp_db()
    master = make_temp_db()

    try:
        # Both laptops have the SAME roster (3 employees)
        for path in [db_a, db_b, master]:
            db = DataAccess(path)
            db.add_employee("EMP0001", "Juan Dela Cruz")
            db.add_employee("EMP0002", "Maria Santos")
            db.add_employee("EMP0003", "Jose Reyes")

        # Laptop A scans EMP0001 and EMP0002
        a = DataAccess(db_a)
        a.log_scan("EMP0001")
        a.log_scan("EMP0002")

        # Laptop B scans EMP0003
        b = DataAccess(db_b)
        b.log_scan("EMP0003")

        # Merge
        result = merge(master, [db_a, db_b])

        assert result["employees"] == 3
        assert result["attendees"] == 3
        assert result["scans_added"] == 3
        assert result["scans_skipped"] == 0

        # Verify master has all three attendees
        m = DataAccess(master)
        attendees = {e.barcode for e in m.get_unique_attendees()}
        assert attendees == {"EMP0001", "EMP0002", "EMP0003"}

    finally:
        cleanup(db_a, db_b, master)


def test_merge_handles_duplicate_scans():
    """Same person scanned on both laptops — merge should dedup."""
    db_a = make_temp_db()
    db_b = make_temp_db()
    master = make_temp_db()

    try:
        for path in [db_a, db_b, master]:
            db = DataAccess(path)
            db.add_employee("EMP0001", "Juan Dela Cruz")

        # Both laptops scan Juan
        DataAccess(db_a).log_scan("EMP0001")
        DataAccess(db_b).log_scan("EMP0001")

        result = merge(master, [db_a, db_b])

        # Only one scan should survive
        assert result["attendees"] == 1
        assert result["scans_added"] == 1
        assert result["scans_skipped"] == 1

        # Verify master has exactly one scan
        m = DataAccess(master)
        assert m.count_attendees() == 1

    finally:
        cleanup(db_a, db_b, master)


def test_merge_accepts_source_employees():
    """Merge copies employees from source into a fresh master."""
    db_a = make_temp_db()
    master = make_temp_db()

    try:
        # Laptop A has Juan
        a = DataAccess(db_a)
        a.add_employee("EMP0001", "Juan Dela Cruz")
        a.log_scan("EMP0001")

        # Merge into master (master is empty — merge will recreate it)
        result = merge(master, [db_a])

        # Juan's employee + scan are merged into the master
        assert result["employees"] == 1     # only EMP0001
        assert result["attendees"] == 1     # only Juan scanned
        assert result["scans_added"] == 1

        # Verify the employee is actually in the master
        m = DataAccess(master)
        emp = m.get_employee_by_barcode("EMP0001")
        assert emp is not None
        assert emp.full_name == "Juan Dela Cruz"

    finally:
        cleanup(db_a, master)


def test_merge_empty_source():
    """Merging an empty source DB is a no-op."""
    db_a = make_temp_db()
    master = make_temp_db()

    try:
        for path in [db_a, master]:
            DataAccess(path).add_employee("EMP0001", "Juan Dela Cruz")

        result = merge(master, [db_a])

        assert result["scans_added"] == 0
        assert result["attendees"] == 0

    finally:
        cleanup(db_a, master)


def test_merge_missing_source():
    """Nonexistent source DB is skipped gracefully."""
    master = make_temp_db()

    try:
        DataAccess(master).add_employee("EMP0001", "Juan Dela Cruz")

        result = merge(master, ["does_not_exist.db"])

        assert result["scans_added"] == 0
        assert result["attendees"] == 0

    finally:
        cleanup(master)


def test_merge_preserves_original_timestamp():
    """Merged scans keep their original time_in."""
    db_a = make_temp_db()
    master = make_temp_db()

    try:
        # Source laptop
        a = DataAccess(db_a)
        a.add_employee("EMP0001", "Juan Dela Cruz")
        a.log_scan("EMP0001")

        # Master must have the same roster
        m = DataAccess(master)
        m.add_employee("EMP0001", "Juan Dela Cruz")

        original = a.get_recent_scans(1)[0]
        original_time = original.time_in
        original_date = original.full_date

        merge(master, [db_a])

        m = DataAccess(master)
        merged = m.get_recent_scans(1)[0]

        assert merged.time_in == original_time
        assert merged.full_date == original_date

    finally:
        cleanup(db_a, master)