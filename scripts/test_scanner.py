"""Manual test: scan barcodes and verify they log correctly.

Usage:
    python -m scripts.test_scanner

Press Ctrl+C to stop.
"""

import sys
from pathlib import Path

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_access import DataAccess


def seed_if_empty(db: DataAccess):
    """Ensure there are some employees to match against."""
    if db.count_employees() == 0:
        print("No employees found — seeding 5 test employees...")
        for i in range(1, 6):
            barcode = f"EMP{i:04d}"
            db.add_employee(barcode, f"Test Employee {i}")
        print("Seeded EMP0001 through EMP0005\n")


def main():
    db = DataAccess()
    seed_if_empty(db)

    print("=" * 60)
    print("  SCANNER TEST — ready for input")
    print("=" * 60)
    print()
    print("Instructions:")
    print("  1. Click into this terminal window")
    print("  2. Scan a barcode with your LS2208")
    print("  3. Watch the result below")
    print()
    print("Note: The scanner must be in USB HID Keyboard mode")
    print("      and send an Enter key after the barcode.")
    print()
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    print()

    try:
        while True:
            # The scanner 'types' the barcode + Enter, so input() captures it
            barcode = input("Scan > ").strip()

            if not barcode:
                continue

            result = db.log_scan(barcode)

            if not result.known:
                print(f"  ❌ UNKNOWN barcode: {result.barcode}")
                print(f"     (logged anyway at {result.time_in})")
            elif result.already_scanned:
                print(f"  ⚠  {result.full_name} — already scanned today")
            else:
                print(f"  ✅ {result.full_name} — checked in at {result.time_in}")
            print()

    except KeyboardInterrupt:
        print("\n\nStopped.")
        print(f"Total employees: {db.count_employees()}")
        print(f"Total unique attendees: {db.count_attendees()}")


if __name__ == "__main__":
    main()