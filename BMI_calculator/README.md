Graphical BMI Calculator (Tkinter + SQLite)

Overview

This project is a Graphical BMI Calculator built using Python’s Tkinter library. It calculates BMI, stores data in SQLite, shows history, and displays BMI trends using matplotlib.

Features

BMI calculation with category classification.
SQLite storage with timestamps.
User history viewing.
BMI trend graph.
CSV export.
Ability to delete user data.
Clear input fields.
Requirements

tkinter (built‑in)
sqlite3 (built‑in)
matplotlib
Install matplotlib:

pip install matplotlib
How to Run

python bmi_calculator.py
Database

The app creates bmi_data.db automatically.

Fields: - id - name - date - weight - height - bmi

Output Files

bmi_data.db
Exported CSV files (optional)
