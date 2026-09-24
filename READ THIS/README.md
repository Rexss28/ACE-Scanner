# Attendance Scanner

Offline attendance tracking and raffle system for company events.

## Overview

This app is used at company events to:
1. Register employees and assign them a barcode
2. Scan barcodes at the entrance to log attendance
3. Pick raffle winners from attendees at the end of the event

It runs **fully offline** — no internet required.

## Tech Stack

- **Python 3.13**
- **PySide6** (Qt-based UI)
- **SQLite** (local offline database)
- **pyserial / hidapi** (barcode scanner input)

## Project Structure

core/ — Data layer: database, models, importer
hardware/ — Barcode scanner input handler
ui/ — PySide6 windows (main, admin, raffle)
scripts/ — One-off utilities (seed data, export reports)
tests/ — Automated tests
main.py — App entry point


## Setup

```powershell
git clone <repo-url>
cd AttendanceScanner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python test_setup.py

If test_setup.py prints version numbers for PySide6, SQLite, pyserial, and hidapi, you're ready

Running the App
python main.py