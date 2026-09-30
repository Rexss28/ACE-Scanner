"""Merge scan logs from one or more source databases into a master database.

Usage:
    python -m scripts.merge_databases master.db source1.db [source2.db ...]

Assumes:
    - All databases have IDENTICAL Employees tables (same roster).
    - Scans are deduplicated by (barcode, full_date).
    - The master's Employee data is authoritative.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_access import DataAccess


def merge(target_path: str, source_paths: list[str]) -> dict:
    """Merge employees and scans from source DBs into a target DB."""
    import gc
    import time

    target_file = Path(target_path)

    # Force-close lingering connections and delete target
    gc.collect()
    time.sleep(0.05)

    for suffix in ["", "-wal", "-shm"]:
        p = Path(str(target_file) + suffix)
        if p.exists():
            for attempt in range(5):
                try:
                    p.unlink()
                    break
                except PermissionError:
                    time.sleep(0.05)

    master = DataAccess(target_path)
    print(f"Created master DB: {target_path}")

    total_employees_added = 0
    total_employees_skipped = 0
    total_scans_added = 0
    total_scans_skipped = 0

    for src_path in source_paths:
        if not Path(src_path).exists():
            print(f"⚠ Skipping (not found): {src_path}")
            continue

        print(f"\nMerging: {src_path}")
        source = DataAccess(src_path)

        # --- Copy employees ---
        employees = source.list_employees()
        for emp in employees:
            try:
                master.add_employee(emp.barcode, emp.full_name)
                total_employees_added += 1
            except Exception:
                # Duplicate barcode — skip
                total_employees_skipped += 1

        # --- Copy scans ---
        scans = source.get_recent_scans(limit=999_999)
        added = 0
        skipped = 0

        for scan in scans:
            # Skip if barcode not in master's roster
            if master.get_employee_by_barcode(scan.barcode) is None:
                skipped += 1
                continue

            # Skip if already scanned on that day in the master
            if master.has_scanned(scan.barcode, date=scan.full_date):
                skipped += 1
                continue

            master._log_scan_with_timestamp(
                barcode=scan.barcode,
                full_name=scan.full_name,
                time_in=scan.time_in,
                full_date=scan.full_date,
            )
            added += 1

        print(f"  Employees added:    {len(employees)}")
        print(f"  Scans added:        {added}")
        print(f"  Scans skipped:      {skipped}")

        total_scans_added += added
        total_scans_skipped += skipped

    print("\n" + "=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)
    print(f"  Total employees:      {master.count_employees()}")
    print(f"  Total attendees:      {master.count_attendees()}")
    print(f"  Employees added:      {total_employees_added}")
    print(f"  Employees skipped:    {total_employees_skipped}")
    print(f"  Scans added:          {total_scans_added}")
    print(f"  Scans skipped:        {total_scans_skipped}")
    print("=" * 60)

    return {
        "employees": master.count_employees(),
        "attendees": master.count_attendees(),
        "scans_added": total_scans_added,
        "scans_skipped": total_scans_skipped,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python -m scripts.merge_databases "
            "<master.db> <source1.db> [source2.db ...]"
        )
        sys.exit(1)

    merge(sys.argv[1], sys.argv[2:])