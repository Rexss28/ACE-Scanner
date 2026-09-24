"""Basic tests for the DataAccess layer."""

import os
import tempfile
from core.data_access import DataAccess


def make_db() -> DataAccess:
    """Create a fresh temp DB for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return DataAccess(db_path=path)


def test_add_and_lookup_employee():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    emp = db.get_employee_by_barcode("EMP0001")
    assert emp is not None
    assert emp.full_name == "Juan Dela Cruz"


def test_lookup_unknown_barcode():
    db = make_db()
    assert db.get_employee_by_barcode("NOPE") is None


def test_generate_barcode_sequential():
    db = make_db()
    assert db.generate_barcode() == "EMP0001"
    db.add_employee("EMP0001", "A")
    assert db.generate_barcode() == "EMP0002"


def test_log_scan_known_employee():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    result = db.log_scan("EMP0001")
    assert result.known is True
    assert result.full_name == "Juan Dela Cruz"
    assert result.already_scanned is False


def test_log_scan_unknown_barcode():
    db = make_db()
    result = db.log_scan("UNKNOWN999")
    assert result.known is False
    assert result.full_name == "UNKNOWN"


def test_duplicate_scan_same_day():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    db.log_scan("EMP0001")
    second = db.log_scan("EMP0001")
    assert second.already_scanned is True


def test_unique_attendees_excludes_unknown():
    db = make_db()
    db.add_employee("EMP0001", "Juan")
    db.log_scan("EMP0001")
    db.log_scan("UNKNOWN999")
    attendees = db.get_unique_attendees()
    assert len(attendees) == 1
    assert attendees[0].full_name == "Juan"

def test_has_scanned_false_for_new_employee():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    assert db.has_scanned("EMP0001") is False


def test_has_scanned_true_after_scan():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    db.log_scan("EMP0001")
    assert db.has_scanned("EMP0001") is True


def test_has_scanned_date_filter():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    db.log_scan("EMP0001")
    # Has scanned today
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    assert db.has_scanned("EMP0001", date=today) is True
    # Has not scanned on a fake date
    assert db.has_scanned("EMP0001", date="2099-01-01") is False


def test_get_all_employees_with_status():
    db = make_db()
    db.add_employee("EMP0001", "Ana Garcia")
    db.add_employee("EMP0002", "Juan Dela Cruz")
    db.log_scan("EMP0002")  # only Juan scans

    statuses = db.get_all_employees_with_status()
    assert len(statuses) == 2

    by_barcode = {s["barcode"]: s for s in statuses}
    assert by_barcode["EMP0001"]["has_scanned"] is False
    assert by_barcode["EMP0002"]["has_scanned"] is True


def test_get_all_employees_with_status_date_filter():
    db = make_db()
    db.add_employee("EMP0001", "Juan Dela Cruz")
    db.log_scan("EMP0001")

    today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    today_status = db.get_all_employees_with_status(date=today)
    assert today_status[0]["has_scanned"] is True

    future_status = db.get_all_employees_with_status(date="2099-01-01")
    assert future_status[0]["has_scanned"] is False