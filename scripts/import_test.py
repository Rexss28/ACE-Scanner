"""Manual test for the importer.

Usage:
    python -m scripts.import_test
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import importer
from core.data_access import DataAccess
from core.importer import EmployeeImporter


def main():
    db = DataAccess()
    importer = EmployeeImporter(db)

    print(f"Employees before: {db.count_employees()}")

    # Import from CSV (we'll create this file next)
    result = importer.import_from_excel("sample_employees.xlsx")
    print(f"\nImport result:")
    print(f"  Total rows:    {result.total}")
    print(f"  Imported:      {result.imported}")
    print(f"  Skipped:       {result.skipped}")
    print(f"  Errors:        {len(result.errors)}")
    for err in result.errors:
        print(f"    - {err}")

    print(f"\nEmployees after: {db.count_employees()}")


if __name__ == "__main__":
    main()