"""Generate QR code images for every employee in the database.

Usage:
    python -m scripts.generate_barcodes
    python -m scripts.generate_barcodes --overwrite
"""

import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.data_access import DataAccess


def generate_qr_codes(output_dir: str = "wristbands", overwrite: bool = False):
    """
    Generates a QR code PNG for every employee in the database.

    Args:
        output_dir: Where to save the PNG files.
        overwrite:  If False, skip codes whose PNG already exists.
    """
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    db = DataAccess()
    employees = db.list_employees()

    if not employees:
        print("No employees found in the database. Run the seed script first.")
        return

    print(f"Checking {len(employees)} employees...")

    generated = 0
    skipped = 0

    for emp in employees:
        file_path = out_path / f"{emp.barcode}.png"

        if file_path.exists() and not overwrite:
            skipped += 1
            continue

        # Build the QR code
        qr = qrcode.QRCode(
            version=None,                         # auto-size
            error_correction=ERROR_CORRECT_M,     # 15% damage recovery
            box_size=10,                          # pixel size per module
            border=4,                             # quiet zone (spec-required)
        )
        qr.add_data(emp.barcode)                  # e.g. "EMP0001"
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(str(file_path))
        generated += 1

    print(f"Done! Generated: {generated}, Skipped (already existed): {skipped}")
    print(f"Output folder: {out_path.absolute()}")


if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    generate_qr_codes(overwrite=overwrite)