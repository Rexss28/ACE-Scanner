import PySide6
import PySide6.QtCore
import sqlite3
import serial
import hid

print(f"PySide6 version: {PySide6.__version__}")
print(f"Qt version: {PySide6.QtCore.__version__}")
print(f"SQLite version: {sqlite3.sqlite_version}")
print(f"pyserial version: {serial.__version__}")
print(f"hidapi loaded: {hid.__name__}")