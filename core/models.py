"""Data models shared across all layers of the app.

These define the agreed-upon "shape" of data as it moves between
the UI, scanner, and database layers. Freeze this file early —
changes here break everyone.
"""

from dataclasses import dataclass


@dataclass
class Employee:
    """An employee registered for the event."""
    barcode: str
    full_name: str


@dataclass
class ScanResult:
    """Result of a single barcode scan."""
    barcode: str
    full_name: str
    time_in: str          # HH:MM:SS
    full_date: str        # YYYY-MM-DD
    known: bool           # Was the barcode found in Employees?
    already_scanned: bool # Did this barcode already scan today?


@dataclass
class ImportResult:
    """Result of importing employees from a file."""
    total: int
    imported: int
    skipped: int
    errors: list[str]


@dataclass
class RaffleWinner:
    """A single raffle winner record."""
    barcode: str
    full_name: str
    prize: str
    drawn_at: str