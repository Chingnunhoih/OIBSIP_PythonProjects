"""
Features:
- Tkinter GUI
- Cryptographically secure generation using secrets
- Options: length, include uppercase/lowercase/digits/symbols
- Option to exclude ambiguous characters (O,0,l,1,I)
- Option to require at least one char from each selected class
- Generate N passwords at once
- Entropy (bits) calculation and quality rating
- Copy single password or all to clipboard
- Save passwords to CSV/Text
- Input validation & user-friendly messages
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import secrets
import string
import math
import csv
from datetime import datetime

# ---------- Constants ----------
AMBIGUOUS_CHARS = "O0Il1"
SYMBOLS = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~"

# ---------- Utility functions ----------
def build_charset(use_lower, use_upper, use_digits, use_symbols, avoid_ambiguous):
    charset = ""
    if use_lower:
        charset += string.ascii_lowercase
    if use_upper:
        charset += string.ascii_uppercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += SYMBOLS
    if avoid_ambiguous:
        charset = "".join(ch for ch in charset if ch not in AMBIGUOUS_CHARS)
    # Ensure uniqueness
    charset = "".join(sorted(set(charset), key=lambda c: (c.isalnum()==False, c)))
    return charset

def calculate_entropy_bits(charset_len, length):
    if charset_len <= 0 or length <= 0:
        return 0.0
    # entropy = log2(charset_size^length) = length * log2(charset_size)
    return length * math.log2(charset_len)

def strength_label(bits):
    # Rough thresholds (bits)
    if bits < 28:
        return "Very Weak"
    if bits < 36:
        return "Weak"
    if bits < 60:
        return "Reasonable"
    if bits < 80:
        return "Strong"
    return "Very Strong"

def human_readable_bits(bits):
    return f"{bits:.1f} bits"

def secure_choice(seq):
    return secrets.choice(seq)

def generate_single_password(length, charset, require_each=False, classes=None):
    """
    Generate a single password of given length using charset.
    If require_each is True, classes must be a list of (name, chars) for required inclusion.
    """
    if not charset:
        raise ValueError("Character set is empty.")
    if length < 1:
        raise ValueError("Length must be at least 1.")
    # If require_each, ensure length >= number of required classes
    if require_each and classes:
        required_classes = [cls for cls in classes if cls[1]]  # only classes with chars
        if length < len(required_classes):
            raise ValueError("Length is too short to include at least one from each required class.")
        # Start with one char from each required class
        pw_chars = [secure_choice(chars) for _, chars in required_classes]
        remaining = length - len(pw_chars)
        for _ in range(remaining):
            pw_chars.append(secure_choice(charset))
        # shuffle securely
        secrets.SystemRandom().shuffle(pw_chars)
        return "".join(pw_chars)
    else:
        return "".join(secure_choice(charset) for _ in range(length))

# ---------- GUI App ----------
class AdvancedPasswordGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        parent.title("Advanced Password Generator")
        self.grid(padx=12, pady=12, sticky="nsew")
        self.create_variables()
        self.create_widgets()
        self.configure_grid()

    def create_variables(self):
        self.length_var = tk.IntVar(value=16)
        self.count_var = tk.IntVar(value=5)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.require_each = tk.BooleanVar(value=True)
        self.avoid_ambiguous = tk.BooleanVar(value=True)
        self.last_charset = ""  # cache for entropy display

    def create_widgets(self):
        # Left frame: options
        opts = ttk.LabelFrame(self, text="Options", padding=10)
        opts.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        ttk.Label(opts, text="Length:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(opts, from_=4, to=256, textvariable=self.length_var, width=6).grid(row=0, column=1, sticky="w")

        ttk.Label(opts, text="Count:").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(opts, from_=1, to=100, textvariable=self.count_var, width=6).grid(row=1, column=1, sticky="w")

        # Character type checkboxes
        ttk.Label(opts, text="Character classes:").grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,0))
        ttk.Checkbutton(opts, text="Lowercase (a-z)", variable=self.use_lower, command=self.update_entropy).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Uppercase (A-Z)", variable=self.use_upper, command=self.update_entropy).grid(row=4, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Digits (0-9)", variable=self.use_digits, command=self.update_entropy).grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Symbols (!@#$...)", variable=self.use_symbols, command=self.update_entropy).grid(row=6, column=0, columnspan=2, sticky="w")

        # Additional options
        ttk.Separator(opts, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Checkbutton(opts, text="Require at least one char from each selected class", variable=self.require_each).grid(row=8, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Avoid ambiguous characters (O,0,I,l,1)", variable=self.avoid_ambiguous, command=self.update_entropy).grid(row=9, column=0, columnspan=2, sticky="w")

        # Entropy display
        self.entropy_label = ttk.Label(opts, text="Entropy: —")
        self.entropy_label.grid(row=10, column=0, columnspan=2, sticky="w", pady=(8,0))

        # Buttons
        btn_frame = ttk.Frame(opts)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btn_frame, text="Generate", command=self.on_generate).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.on_clear).grid(row=0, column=1, padx=4)

        # Right frame: results
        res = ttk.LabelFrame(self, text="Generated Passwords", padding=10)
        res.grid(row=0, column=1, sticky="nsew")

        # Listbox with scrollbar
        self.pw_listbox = tk.Listbox(res, height=12, width=48, font=("Consolas", 10))
        self.pw_listbox.grid(row=0, column=0, columnspan=3, pady=(0,6), sticky="nsew")
        sb = ttk.Scrollbar(res, orient="vertical", command=self.pw_listbox.yview)
        sb.grid(row=0, column=3, sticky="ns", pady=(0,6))
        self.pw_listbox.config(yscrollcommand=sb.set)

        # Buttons for copy/export
        ttk.Button(res, text="Copy Selected", command=self.copy_selected).grid(row=1, column=0, sticky="w", padx=(0,4))
        ttk.Button(res, text="Copy All", command=self.copy_all).grid(row=1, column=1)
        ttk.Button(res, text="Save to File", command=self.save_to_file).grid(row=1, column=2, sticky="e", padx=(4,0))

        # Info label
        self.info_label = ttk.Label(self, text="Tip: Use 'Require at least one...' to ensure policy compliance for passwords.")
        self.info_label.grid(row=2, column=0, columnspan=2, pady=(10,0), sticky="w")

        # initial entropy update
        self.update_entropy()

    def configure_grid(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    # ---------- Actions ----------
    def update_entropy(self):
        charset = build_charset(
            self.use_lower.get(), self.use_upper.get(),
            self.use_digits.get(), self.use_symbols.get(),
            self.avoid_ambiguous.get()
        )
        length = max(0, int(self.length_var.get()))
        bits = calculate_entropy_bits(len(charset), length)
        label = f"Entropy: {human_readable_bits(bits)} — {strength_label(bits)} (Charset size: {len(charset)})"
        self.entropy_label.config(text=label)
        self.last_charset = charset

    def on_generate(self):
        try:
            length = int(self.length_var.get())
            count = int(self.count_var.get())
            if length < 4 or length > 256:
                raise ValueError("Length must be between 4 and 256.")
            if count < 1 or count > 1000:
                raise ValueError("Count must be between 1 and 1000.")

            # Build charset and classes (for require_each)
            charset = build_charset(
                self.use_lower.get(), self.use_upper.get(),
                self.use_digits.get(), self.use_symbols.get(),
                self.avoid_ambiguous.get()
            )

            if not charset:
                raise ValueError("No characters selected for password generation. Enable at least one class.")

            classes = []
            if self.use_lower.get():
                chars = string.ascii_lowercase
                if self.avoid_ambiguous.get():
                    chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
                classes.append(("lower", chars))
            if self.use_upper.get():
                chars = string.ascii_uppercase
                if self.avoid_ambiguous.get():
                    chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
                classes.append(("upper", chars))
            if self.use_digits.get():
                chars = string.digits
                if self.avoid_ambiguous.get():
                    chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
                classes.append(("digits", chars))
            if self.use_symbols.get():
                chars = SYMBOLS
                if self.avoid_ambiguous.get():
                    chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
                classes.append(("symbols", chars))

            require_each = self.require_each.get()

            # Generate
            generated = []
            for _ in range(count):
                pw = generate_single_password(length, charset, require_each=require_each, classes=classes)
                generated.append(pw)

            # Display
            self.pw_listbox.delete(0, tk.END)
            for i, pw in enumerate(generated, start=1):
                self.pw_listbox.insert(tk.END, f"{i:02d}. {pw}")

            # Update entropy label in case length/charset changed
            self.update_entropy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy_selected(self):
        sel = self.pw_listbox.curselection()
        if not sel:
            messagebox.showinfo("Copy", "No password selected. Select one from the list.")
            return
        item = self.pw_listbox.get(sel[0])
        # strip index like "01. "
        pw = item.split(". ", 1)[1] if ". " in item else item
        self.parent.clipboard_clear()
        self.parent.clipboard_append(pw)
        messagebox.showinfo("Copied", "Selected password copied to clipboard.")

    def copy_all(self):
        items = self.pw_listbox.get(0, tk.END)
        if not items:
            messagebox.showinfo("Copy All", "No passwords to copy.")
            return
        all_pw = "\n".join(item.split(". ", 1)[1] if ". " in item else item for item in items)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(all_pw)
        messagebox.showinfo("Copied", f"{len(items)} passwords copied to clipboard.")

    def save_to_file(self):
        items = self.pw_listbox.get(0, tk.END)
        if not items:
            messagebox.showinfo("Save", "No passwords to save.")
            return
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        ftypes = [("Text file", "*.txt"), ("CSV file", "*.csv"), ("All files", "*.*")]
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=ftypes, initialfile=f"passwords_{now}.txt")
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["index", "password"])
                    for row in items:
                        idx, pw = row.split(". ", 1) if ". " in row else ("", row)
                        writer.writerow([idx.strip("."), pw])
            else:
                with open(path, "w", encoding="utf-8") as f:
                    for row in items:
                        f.write(row + "\n")
            messagebox.showinfo("Saved", f"Passwords saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def on_clear(self):
        self.pw_listbox.delete(0, tk.END)

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    # Slightly nicer theme
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    AdvancedPasswordGenerator(root)
    root.mainloop()
