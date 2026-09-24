"""Seed the database with fake employees for testing.

Usage:
    python -m scripts.seed_employees 1000
"""

import sys
import random
from pathlib import Path

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_access import DataAccess

FIRST_NAMES = ["Juan", "Maria", "Jose", "Ana", "Pedro", "Rosa", "Carlo", "Liza"]
LAST_NAMES = ["Dela Cruz", "Santos", "Reyes", "Garcia", "Bautista", "Mendoza"]


def seed(count: int = 1000):
    db = DataAccess()
    print(f"Seeding {count} employees...")

    for i in range(count):
        barcode = db.generate_barcode()
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        try:
            db.add_employee(barcode, name)
        except Exception as e:
            print(f"Skipped {barcode}: {e}")

    print(f"Done. Total employees: {db.count_employees()}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed(count)