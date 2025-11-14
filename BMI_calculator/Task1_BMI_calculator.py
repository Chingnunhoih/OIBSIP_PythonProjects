"""
Graphical BMI Calculator with Tkinter
-------------------------------------

Features:
- User-friendly GUI with weight/height input.
- BMI calculation and health categorization.
- SQLite storage per user with timestamps.
- Historical BMI viewing + matplotlib trend graph.
- CSV export and data deletion options.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

DB_NAME = "bmi_data.db"

# ---------------------- DATABASE ----------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_record(name, weight, height, bmi):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO bmi_records (name, date, weight, height, bmi) VALUES (?, ?, ?, ?, ?)",
        (name, datetime.now().strftime("%Y-%m-%d %H:%M"), weight, height, bmi),
    )
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT DISTINCT name FROM bmi_records ORDER BY name")
    users = [u[0] for u in c.fetchall()]
    conn.close()
    return users

def get_user_history(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, bmi FROM bmi_records WHERE name=? ORDER BY date", (name,))
    data = c.fetchall()
    conn.close()
    return data

def delete_user_data(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM bmi_records WHERE name=?", (name,))
    conn.commit()
    conn.close()

# ---------------------- BMI FUNCTIONS ----------------------
def calculate_bmi(weight, height):
    return weight / (height * height)

def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# ---------------------- GUI ----------------------
class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")
        self.root.geometry("850x550")
        self.root.resizable(False, False)
        init_db()
        self.setup_ui()

    def setup_ui(self):
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text="Enter Details", padding=10)
        input_frame.place(x=20, y=20, width=380, height=250)

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var, width=25).grid(row=0, column=1)

        ttk.Label(input_frame, text="Weight (kg):").grid(row=1, column=0, sticky="w")
        self.weight_var = tk.DoubleVar()
        ttk.Entry(input_frame, textvariable=self.weight_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(input_frame, text="Height (m):").grid(row=2, column=0, sticky="w")
        self.height_var = tk.DoubleVar()
        ttk.Entry(input_frame, textvariable=self.height_var, width=10).grid(row=2, column=1, sticky="w")

        ttk.Button(input_frame, text="Calculate & Save", command=self.calculate_and_save).grid(row=3, column=0, pady=10)
        ttk.Button(input_frame, text="Clear", command=self.clear_fields).grid(row=3, column=1, pady=10)

        # Result display
        self.result_label = ttk.LabelFrame(self.root, text="Result", padding=10)
        self.result_label.place(x=20, y=290, width=380, height=220)
        self.result_text = tk.Text(self.result_label, width=45, height=8, state="disabled")
        self.result_text.pack()

        # History section
        history_frame = ttk.LabelFrame(self.root, text="User History & BMI Trend", padding=10)
        history_frame.place(x=420, y=20, width=400, height=490)

        ttk.Label(history_frame, text="Select User:").pack(anchor="w")
        self.user_combo = ttk.Combobox(history_frame, values=get_users(), state="readonly")
        self.user_combo.pack(fill="x")
        self.user_combo.bind("<<ComboboxSelected>>", lambda e: self.show_user_history())

        self.history_listbox = tk.Listbox(history_frame, height=8)
        self.history_listbox.pack(fill="x", pady=5)

        # Plot
        self.figure, self.ax = plt.subplots(figsize=(4, 2.2))
        self.canvas = FigureCanvasTkAgg(self.figure, history_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buttons
        ttk.Button(history_frame, text="Refresh", command=self.refresh_users).pack(side="left", padx=5, pady=5)
        ttk.Button(history_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(history_frame, text="Delete User", command=self.delete_user).pack(side="left", padx=5)

    # ---------------------- Event Handlers ----------------------
    def calculate_and_save(self):
        try:
            name = self.name_var.get().strip()
            weight = self.weight_var.get()
            height = self.height_var.get()

            if not name:
                raise ValueError("Please enter a name.")
            if not (2 <= weight <= 500):
                raise ValueError("Weight must be between 2kg and 500kg.")
            if not (0.3 <= height <= 2.5):
                raise ValueError("Height must be between 0.3m and 2.5m.")

            bmi = calculate_bmi(weight, height)
            category = categorize_bmi(bmi)

            insert_record(name, weight, height, round(bmi, 2))
            self.display_result(name, weight, height, bmi, category)
            self.refresh_users()
            messagebox.showinfo("Success", "Record saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_result(self, name, weight, height, bmi, category):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Name: {name}\n")
        self.result_text.insert(tk.END, f"Weight: {weight} kg\nHeight: {height} m\n")
        self.result_text.insert(tk.END, f"BMI: {bmi:.2f} ({category})")
        self.result_text.config(state="disabled")

    def show_user_history(self):
        user = self.user_combo.get()
        data = get_user_history(user)
        self.history_listbox.delete(0, tk.END)
        if not data:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.canvas.draw()
            return
        dates, bmis = zip(*data)
        for d, b in data:
            self.history_listbox.insert(tk.END, f"{d} - BMI: {b:.2f}")
        self.ax.clear()
        self.ax.plot(dates, bmis, marker="o", linestyle="-")
        self.ax.set_title(f"BMI Trend for {user}")
        self.ax.tick_params(axis="x", rotation=45)
        self.ax.set_ylabel("BMI")
        self.canvas.draw()

    def refresh_users(self):
        self.user_combo["values"] = get_users()

    def export_csv(self):
        user = self.user_combo.get()
        if not user:
            messagebox.showinfo("Info", "Select a user first.")
            return
        data = get_user_history(user)
        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "BMI"])
                writer.writerows(data)
            messagebox.showinfo("Export", f"Data exported to {file_path}")

    def delete_user(self):
        user = self.user_combo.get()
        if not user:
            messagebox.showinfo("Info", "Select a user to delete.")
            return
        if messagebox.askyesno("Confirm", f"Delete all data for {user}?"):
            delete_user_data(user)
            self.refresh_users()
            self.history_listbox.delete(0, tk.END)
            self.ax.clear()
            self.canvas.draw()
            messagebox.showinfo("Deleted", f"Data for {user} deleted.")

    def clear_fields(self):
        self.name_var.set("")
        self.weight_var.set(0.0)
        self.height_var.set(0.0)
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()
