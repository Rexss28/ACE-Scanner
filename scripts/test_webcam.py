"""Webcam QR/barcode scanner.

Usage:
    python -m scripts.test_webcam

Controls:
    Q or ESC — quit
"""

import sys
from pathlib import Path

import cv2
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_access import DataAccess


# Only decode the formats we actually use.
ALLOWED_SYMBOLS = [ZBarSymbol.QRCODE, ZBarSymbol.CODE128, ZBarSymbol.CODE39]


def main():
    db = DataAccess()
    print(f"Employees in DB: {db.count_employees()}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("=" * 60)
    print("  WEBCAM SCANNER")
    print("=" * 60)
    print("  Q or ESC — quit")
    print("=" * 60)
    print()

    last_scanned = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Decode directly on grayscale — QR codes handle this well
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray, symbols=ALLOWED_SYMBOLS)

        for b in barcodes:
            try:
                value = b.data.decode("utf-8")
            except UnicodeDecodeError:
                value = b.data.decode("latin-1", errors="replace")

            if value == last_scanned:
                continue
            last_scanned = value

            print(f"\n🔍 Scanned: {value} ({b.type})")

            result = db.log_scan(value)

            if not result.known:
                print(f"   ❌ UNKNOWN barcode")
                color = (0, 0, 255)      # red
            elif result.already_scanned:
                print(f"   ⚠  {result.full_name} — already scanned today")
                color = (0, 165, 255)    # orange
            else:
                print(f"   ✅ {result.full_name} — checked in at {result.time_in}")
                color = (0, 255, 0)      # green

            # Draw box + label
            x, y, w, h = b.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame,
                value,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
            )

        cv2.imshow("Scanner", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nTotal attendees: {db.count_attendees()}")


if __name__ == "__main__":
    main()