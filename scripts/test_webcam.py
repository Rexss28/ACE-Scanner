"""Webcam barcode scanner with preprocessing for screen-reading.

Usage:
    python -m scripts.test_webcam

Controls:
    Q or ESC — quit
    S — save the current frame to debug_frame.png (for troubleshooting)
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_access import DataAccess


# Only decode the formats we actually use.
# This prevents ZBar from running its PDF417 decoder, which spams
# warnings when it sees 1D barcodes.
ALLOWED_SYMBOLS = [ZBarSymbol.QRCODE, ZBarSymbol.CODE128, ZBarSymbol.CODE39]

def preprocess(frame):
    """Preprocess a frame to improve barcode detection."""
    # 1. Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Increase contrast with CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3. Apply Gaussian blur to reduce noise (helps with screen pixelation)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # 4. Adaptive threshold to get pure black/white edges
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=25,
        C=10,
    )

    return gray, enhanced, thresh


def main():
    db = DataAccess()
    print(f"Employees in DB: {db.count_employees()}")

    # Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Set a decent resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("=" * 60)
    print("  WEBCAM BARCODE SCANNER")
    print("=" * 60)
    print("  Q or ESC — quit")
    print("  S        — save current frame for debugging")
    print("=" * 60)
    print()

    last_scanned = None  # to avoid spamming the same barcode

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Preprocess
        gray, enhanced, thresh = preprocess(frame)

        # Try decoding on multiple versions — pyzbar sometimes
        # succeeds on one but fails on another
        found = []

        for image, label in [(gray, "gray"), (enhanced, "enhanced"), (thresh, "thresh")]:
            barcodes = pyzbar.decode(image, symbols=ALLOWED_SYMBOLS)
            for b in barcodes:
                try:
                    value = b.data.decode("utf-8")
                except UnicodeDecodeError:
                    value = b.data.decode("latin-1", errors="replace")

                if value not in [f[0] for f in found]:
                    found.append((value, b.type, label, b.rect))

        # Process found barcodes
        for value, btype, source, rect in found:
            if value == last_scanned:
                continue  # skip duplicates in the same session
            last_scanned = value

            print(f"\n🔍 Scanned: {value} ({btype}) [via {source}]")

            result = db.log_scan(value)

            if not result.known:
                print(f"   ❌ UNKNOWN barcode")
            elif result.already_scanned:
                print(f"   ⚠  {result.full_name} — already scanned today")
            else:
                print(f"   ✅ {result.full_name} — checked in at {result.time_in}")

            # Draw rectangle on frame
            x, y, w, h = rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{value}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        # Show all four windows so you can see what's happening
        cv2.imshow("Original", frame)
        cv2.imshow("Grayscale", gray)
        cv2.imshow("Enhanced (CLAHE)", enhanced)
        cv2.imshow("Threshold", thresh)

        # Key handling
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:  # Q or ESC
            break
        elif key == ord("s"):
            cv2.imwrite("debug_frame_original.png", frame)
            cv2.imwrite("debug_frame_gray.png", gray)
            cv2.imwrite("debug_frame_enhanced.png", enhanced)
            cv2.imwrite("debug_frame_thresh.png", thresh)
            print("Saved debug frames.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nTotal attendees: {db.count_attendees()}")


if __name__ == "__main__":
    main()