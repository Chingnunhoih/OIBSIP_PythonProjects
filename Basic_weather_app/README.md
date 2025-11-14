Advanced Password Generator (Tkinter + Secrets)

Overview

This project is an Advanced Password Generator built using Python’s
Tkinter GUI toolkit and the secrets module for secure random generation.
It allows users to generate one or many secure passwords with full
customization of character sets, entropy calculation, clipboard
features, and file export options.

Features

-   Tkinter-based graphical user interface
-   Cryptographically secure password generation using secrets
-   Customizable options:
    -   Length selection
    -   Include lowercase, uppercase, digits, symbols
    -   Avoid ambiguous characters (O,0,l,1,I)
    -   Require at least one character from each selected class
-   Generate multiple passwords at once
-   Entropy (bits) calculation for strength estimation
-   Password quality rating (Very Weak → Very Strong)
-   Copy selected or all passwords to clipboard
-   Save generated passwords to TXT or CSV files
-   Input validation and clear error messages

Requirements

Built-in:

    tkinter
    secrets
    string
    math
    csv
    datetime

No external installations required.

How to Run

Save the script (e.g., password_generator.py) and run:

    python password_generator.py

Entropy Explanation

Entropy is computed using:

    entropy = length * log2(charset_size)

Higher entropy = stronger password.

Output Options

-   Copy single password
-   Copy all passwords
-   Save as:
    -   .txt (one password per line)
    -   .csv (indexed format)

Notes

Ensure at least one character type is enabled before generating
passwords. When “Require at least one of each selected class” is
checked, length must be >= number of selected classes.
