"""
app.py — Application Entry Point
==================================
This is the file you run to start the Game Library.

How to run:
    python src/app.py

What happens:
    1. The app window opens with a connection screen
    2. You enter your MySQL credentials and click Connect
    3. The app loads your games from the database
    4. You can add, edit, delete, and search games — no SQL needed!

Architecture:
    app.py  →  starts the GUI
    gui.py  →  handles everything the user sees
    database.py  →  handles all MySQL communication
"""

from gui import GameLibraryApp


def main():
    """Launch the Game Library application."""
    app = GameLibraryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
