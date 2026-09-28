Commands

Scanner Test
 - python -m scripts.test_scanner (barcode)
- python -m scripts.test_webcam (webcam)

Clear DB (Keep Schema)
- python -c "import sqlite3; c=sqlite3.connect('attendance.db'); c.execute('DELETE FROM ScanLogs'); c.execute('DELETE FROM Employees'); c.execute('DELETE FROM RaffleWinners'); c.execute('DELETE FROM sqlite_sequence'); c.commit(); c.close(); print('All tables cleared')"

Barcode/QR Generator
- python -m scripts.generate_barcodes

Get Employees from Excel
- python -m scripts.import_test

Test Functions if working
- pytest tests/test_data_access.py -v
