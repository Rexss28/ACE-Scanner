"""SQLite database access layer.

This is the ONLY file in the app that talks to SQLite.
All other layers must go through the DataAccess class.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from core.models import Employee, ScanResult, RaffleWinner


class DataAccess:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            base = Path(__file__).resolve().parent.parent
            db_path = str(base / "attendance.db")
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS Employees (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode    TEXT NOT NULL UNIQUE,
                    full_name  TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ScanLogs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode   TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    time_in   TEXT NOT NULL,
                    full_date TEXT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_scan_unique
                ON ScanLogs (barcode, full_date);

                CREATE TABLE IF NOT EXISTS RaffleWinners (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode   TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    prize     TEXT NOT NULL,
                    drawn_at  TEXT NOT NULL
                );
            """)

    # ------------------------------------------------------------------
    # Barcode generation
    # ------------------------------------------------------------------
    def generate_barcode(self, prefix: str = "EMP") -> str:
        """Generate the next sequential barcode (EMP0001, EMP0002, ...)."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT barcode FROM Employees "
                "WHERE barcode LIKE ? "
                "ORDER BY id DESC LIMIT 1;",
                (f"{prefix}%",),
            ).fetchone()

        if row is None:
            return f"{prefix}0001"

        last_num = int(row["barcode"].replace(prefix, ""))
        return f"{prefix}{last_num + 1:04d}"

    # ------------------------------------------------------------------
    # Employees
    # ------------------------------------------------------------------
    def add_employee(self, barcode: str, full_name: str) -> Employee:
        """Insert a new employee. Raises if barcode already exists."""
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO Employees (barcode, full_name, created_at) "
                "VALUES (?, ?, ?);",
                (barcode, full_name, now),
            )
        return Employee(barcode=barcode, full_name=full_name)

    def get_employee_by_barcode(self, barcode: str) -> Employee | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT barcode, full_name FROM Employees WHERE barcode = ? LIMIT 1;",
                (barcode,),
            ).fetchone()
        if row is None:
            return None
        return Employee(barcode=row["barcode"], full_name=row["full_name"])

    def list_employees(self) -> list[Employee]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT barcode, full_name FROM Employees ORDER BY id;"
            ).fetchall()
        return [Employee(barcode=r["barcode"], full_name=r["full_name"]) for r in rows]

    def count_employees(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM Employees;").fetchone()[0]


        # ------------------------------------------------------------------
    # Employee scan status
    # ------------------------------------------------------------------
    def has_scanned(self, barcode: str, date: str | None = None) -> bool:
        """Check if an employee has scanned.

        Args:
            barcode: The employee's barcode.
            date: If provided (YYYY-MM-DD), checks that specific date.
                  If None, checks if they've scanned on any date.

        Returns:
            True if a matching ScanLogs row exists, False otherwise.
        """
        if date is None:
            query = "SELECT 1 FROM ScanLogs WHERE barcode = ? LIMIT 1;"
            params = (barcode,)
        else:
            query = (
                "SELECT 1 FROM ScanLogs WHERE barcode = ? AND full_date = ? LIMIT 1;"
            )
            params = (barcode, date)

        with self._connect() as conn:
            return conn.execute(query, params).fetchone() is not None

    def get_all_employees_with_status(self, date: str | None = None) -> list[dict]:
        """Return every employee + whether they've scanned.

        Args:
            date: If provided (YYYY-MM-DD), only considers scans on that date.
                  If None, considers any scan ever.

        Returns:
            List of dicts: [{"barcode": ..., "full_name": ..., "has_scanned": bool}, ...]
        """
        with self._connect() as conn:
            if date is None:
                rows = conn.execute("""
                    SELECT e.barcode, e.full_name,
                           CASE WHEN s.id IS NULL THEN 0 ELSE 1 END AS has_scanned
                    FROM Employees e
                    LEFT JOIN ScanLogs s ON e.barcode = s.barcode
                    GROUP BY e.barcode, e.full_name
                    ORDER BY e.full_name;
                """).fetchall()
            else:
                rows = conn.execute("""
                    SELECT e.barcode, e.full_name,
                           CASE WHEN s.id IS NULL THEN 0 ELSE 1 END AS has_scanned
                    FROM Employees e
                    LEFT JOIN ScanLogs s ON e.barcode = s.barcode AND s.full_date = ?
                    GROUP BY e.barcode, e.full_name
                    ORDER BY e.full_name;
                """, (date,)).fetchall()

        return [
            {
                "barcode": r["barcode"],
                "full_name": r["full_name"],
                "has_scanned": bool(r["has_scanned"]),
            }
            for r in rows
        ]



    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------
    def log_scan(self, barcode: str) -> ScanResult:
        """Record a scan. Deduplicated per barcode per day."""
        now = datetime.now()
        time_in = now.strftime("%H:%M:%S")
        full_date = now.strftime("%Y-%m-%d")

        employee = self.get_employee_by_barcode(barcode)

        if employee is None:
            full_name = "UNKNOWN"
            known = False
        else:
            full_name = employee.full_name
            known = True

        already_scanned = self._already_scanned_today(barcode, full_date)

        if not already_scanned:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO ScanLogs (barcode, full_name, time_in, full_date) "
                    "VALUES (?, ?, ?, ?);",
                    (barcode, full_name, time_in, full_date),
                )

        return ScanResult(
            barcode=barcode,
            full_name=full_name,
            time_in=time_in,
            full_date=full_date,
            known=known,
            already_scanned=already_scanned,
        )

    def _already_scanned_today(self, barcode: str, full_date: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM ScanLogs WHERE barcode = ? AND full_date = ? LIMIT 1;",
                (barcode, full_date),
            ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def get_recent_scans(self, limit: int = 20) -> list[ScanResult]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT barcode, full_name, time_in, full_date "
                "FROM ScanLogs ORDER BY id DESC LIMIT ?;",
                (limit,),
            ).fetchall()
        return [
            ScanResult(
                barcode=r["barcode"],
                full_name=r["full_name"],
                time_in=r["time_in"],
                full_date=r["full_date"],
                known=True,
                already_scanned=False,
            )
            for r in rows
        ]

    def get_unique_attendees(self) -> list[Employee]:
        """Everyone who has at least one scan — used for the raffle."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT barcode, full_name FROM ScanLogs "
                "WHERE full_name != 'UNKNOWN' ORDER BY full_name;"
            ).fetchall()
        return [Employee(barcode=r["barcode"], full_name=r["full_name"]) for r in rows]

    def count_attendees(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                "SELECT COUNT(DISTINCT barcode) FROM ScanLogs WHERE full_name != 'UNKNOWN';"
            ).fetchone()[0]

    # ------------------------------------------------------------------
    # Raffle
    # ------------------------------------------------------------------
    def log_winner(self, barcode: str, full_name: str, prize: str) -> RaffleWinner:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO RaffleWinners (barcode, full_name, prize, drawn_at) "
                "VALUES (?, ?, ?, ?);",
                (barcode, full_name, prize, now),
            )
        return RaffleWinner(barcode=barcode, full_name=full_name, prize=prize, drawn_at=now)

    def get_winners(self) -> list[RaffleWinner]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT barcode, full_name, prize, drawn_at FROM RaffleWinners "
                "ORDER BY id;"
            ).fetchall()
        return [
            RaffleWinner(
                barcode=r["barcode"],
                full_name=r["full_name"],
                prize=r["prize"],
                drawn_at=r["drawn_at"],
            )
            for r in rows
        ]