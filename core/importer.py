#Reads the HR-provided employee list (CSV or Excel) and inserts them into the Employees table
"""CSV/Excel importer for employee lists.

NOTE: Only bare codes, will update soon.

"""

from core.data_access import DataAccess
from core.models import ImportResult


class EmployeeImporter:
    def __init__(self, db: DataAccess):
        self.db = db

    def import_from_csv(self, path: str) -> ImportResult:
        raise NotImplementedError("Coming in Week 2")

    def import_from_excel(self, path: str) -> ImportResult:
        raise NotImplementedError("Coming in Week 2")