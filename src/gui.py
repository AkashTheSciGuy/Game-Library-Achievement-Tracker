"""
gui.py — The Graphical User Interface
=======================================
This file builds everything the user sees and clicks.
It uses CustomTkinter for a modern, professional look
with dark/light mode support.

Architecture:
    GameLibraryApp (main window)
    ├── Connection Screen → Asks for MySQL credentials
    ├── Library Screen    → Shows games table + action buttons
    └── GameForm (popup)  → Add/Edit game form

The GUI never writes SQL directly. It calls functions
from database.py, which handles all the SQL.
"""

# ─────────────────────────────────────────────
# CustomTkinter gives us modern-looking widgets
# (buttons, entries, switches) instead of the
# old-school Tkinter look from the 1990s.
# ─────────────────────────────────────────────
import customtkinter as ctk

# ─────────────────────────────────────────────
# ttk.Treeview is used for the game table.
# CustomTkinter doesn't have its own table widget,
# so we use tkinter's built-in one and style it
# to match the dark/light theme.
# ─────────────────────────────────────────────
from tkinter import ttk, messagebox
import tkinter as tk

# ─────────────────────────────────────────────
# datetime helps us validate date inputs
# (e.g., making sure "2007-11-05" is a real date)
# ─────────────────────────────────────────────
from datetime import datetime

# ─────────────────────────────────────────────
# Our own database module — the one we just built
# ─────────────────────────────────────────────
from database import Database


# ═══════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ═══════════════════════════════════════════════

class GameLibraryApp(ctk.CTk):
    """
    The main application window.

    Flow:
        1. App opens → Shows connection screen (small window)
        2. User connects → Window expands to show game library
        3. User can add/edit/delete/search games
        4. User can toggle dark/light mode
        5. User can disconnect → Returns to connection screen
    """

    def __init__(self):
        super().__init__()

        # ── Window settings ──
        self.title("Game Library & Achievement Tracker")
        self.geometry("500x420")
        self.minsize(500, 420)
        self._center_window(500, 420)

        # ── Database (not connected yet) ──
        self.db = None

        # ── Theme: Start in dark mode ──
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Sort tracking for table columns ──
        self._sort_column = None
        self._sort_reverse = False

        # ── Show the connection screen first ──
        self._show_connection_screen()

    # ───────────────────────────────────────
    #  UTILITY: Center window on screen
    # ───────────────────────────────────────

    def _center_window(self, width, height):
        """Place the window in the center of the screen."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ───────────────────────────────────────
    #  SCREEN 1: Connection
    # ───────────────────────────────────────

    def _show_connection_screen(self):
        """
        Display the database connection form.
        The user enters their MySQL credentials here.
        """
        # Clear any existing widgets from the window
        for widget in self.winfo_children():
            widget.destroy()

        # ── Outer frame (fills the entire window) ──
        frame = ctk.CTkFrame(self, corner_radius=0)
        frame.pack(fill="both", expand=True)

        # ── Inner card (centered, with rounded corners) ──
        card = ctk.CTkFrame(frame, corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # ── App icon and title ──
        ctk.CTkLabel(
            card, text="🎮", font=("Segoe UI", 48)
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            card, text="Game Library",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            card, text="Connect to your MySQL database",
            font=("Segoe UI", 13),
            text_color="gray"
        ).pack(pady=(0, 25))

        # ── Form fields container ──
        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(padx=40, pady=(0, 10))

        # Host field (where MySQL is running)
        ctk.CTkLabel(fields, text="Host", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(5, 2))
        self._host_entry = ctk.CTkEntry(
            fields, width=280, placeholder_text="localhost"
        )
        self._host_entry.insert(0, "localhost")
        self._host_entry.pack(pady=(0, 5))

        # Username field
        ctk.CTkLabel(fields, text="Username", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(5, 2))
        self._user_entry = ctk.CTkEntry(
            fields, width=280, placeholder_text="root"
        )
        self._user_entry.insert(0, "root")
        self._user_entry.pack(pady=(0, 5))

        # Password field (show="•" hides the characters)
        ctk.CTkLabel(fields, text="Password", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(5, 2))
        self._pass_entry = ctk.CTkEntry(
            fields, width=280, show="•",
            placeholder_text="Enter your MySQL password"
        )
        self._pass_entry.pack(pady=(0, 5))
        # Pressing Enter in the password field triggers connect
        self._pass_entry.bind("<Return>", lambda e: self._attempt_connection())

        # Database name field
        ctk.CTkLabel(fields, text="Database", anchor="w",
                     font=("Segoe UI", 12)).pack(fill="x", pady=(5, 2))
        self._db_entry = ctk.CTkEntry(
            fields, width=280, placeholder_text="game_library"
        )
        self._db_entry.insert(0, "game_library")
        self._db_entry.pack(pady=(0, 15))

        # Connect button
        self._connect_btn = ctk.CTkButton(
            card, text="Connect", width=280, height=42,
            font=("Segoe UI", 14, "bold"),
            command=self._attempt_connection
        )
        self._connect_btn.pack(pady=(0, 10))

        # Status message (shows success/error)
        self._conn_status = ctk.CTkLabel(
            card, text="", font=("Segoe UI", 11),
            text_color="gray"
        )
        self._conn_status.pack(pady=(0, 30))

        # Auto-focus on password field (host/user/db already filled)
        self._pass_entry.focus()

    def _attempt_connection(self):
        """
        Try to connect to MySQL with the entered credentials.
        If successful, transition to the library screen.
        """
        host = self._host_entry.get().strip()
        user = self._user_entry.get().strip()
        password = self._pass_entry.get()
        database = self._db_entry.get().strip()

        # Show "connecting" status
        self._conn_status.configure(text="Connecting...", text_color="gray")
        self._connect_btn.configure(state="disabled")
        self.update()

        # Create database object and try to connect
        self.db = Database()
        success, message = self.db.connect(host, user, password, database)

        if success:
            self._conn_status.configure(
                text="✅ Connected!", text_color="#22c55e"
            )
            self.update()
            # Wait 500ms so the user sees the success message,
            # then switch to the library screen
            self.after(500, self._show_library_screen)
        else:
            self._conn_status.configure(
                text=f"❌ {message}", text_color="#ef4444"
            )
            self._connect_btn.configure(state="normal")
            self.db = None

    # ───────────────────────────────────────
    #  SCREEN 2: Game Library
    # ───────────────────────────────────────

    def _show_library_screen(self):
        """
        Display the main game library interface.
        This is where users manage their games.
        """
        # Clear the connection screen
        for widget in self.winfo_children():
            widget.destroy()

        # Resize window to be larger for the library view
        self.geometry("1200x720")
        self.minsize(950, 600)
        self._center_window(1200, 720)

        # Configure the main grid layout
        # Row 0 = header, Row 1 = toolbar, Row 2 = table, Row 3 = status bar
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Table row expands

        # Build each section
        self._create_header()
        self._create_toolbar()
        self._create_table()
        self._create_status_bar()

        # Load games from database into the table
        self._refresh_table()

    # ── HEADER ──

    def _create_header(self):
        """Build the top bar with app title, theme toggle, and disconnect."""
        header = ctk.CTkFrame(self, corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # App title (left side)
        ctk.CTkLabel(
            header, text="🎮  Game Library",
            font=("Segoe UI", 22, "bold")
        ).grid(row=0, column=0, padx=20, pady=12, sticky="w")

        # Right side controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.grid(row=0, column=2, padx=10, pady=12)

        # Theme toggle: Sun ☀️ [switch] Moon 🌙
        ctk.CTkLabel(
            controls, text="☀️", font=("Segoe UI", 14)
        ).pack(side="left", padx=(0, 5))

        self._theme_switch = ctk.CTkSwitch(
            controls, text="", width=48,
            command=self._toggle_theme,
            onvalue="dark", offvalue="light"
        )
        self._theme_switch.select()  # Start in dark mode (on)
        self._theme_switch.pack(side="left")

        ctk.CTkLabel(
            controls, text="🌙", font=("Segoe UI", 14)
        ).pack(side="left", padx=(5, 15))

        # Disconnect button
        ctk.CTkButton(
            controls, text="⏻  Disconnect", width=120, height=32,
            font=("Segoe UI", 12),
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            hover_color=("gray85", "gray25"),
            command=self._disconnect
        ).pack(side="left")

    # ── TOOLBAR (Search + Action Buttons) ──

    def _create_toolbar(self):
        """Build the toolbar with search bar and CRUD buttons."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=15, pady=(8, 5))
        toolbar.grid_columnconfigure(0, weight=1)

        # ── Left side: Search ──
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="w")

        self._search_entry = ctk.CTkEntry(
            search_frame, width=350, height=38,
            placeholder_text="🔍  Search by title, developer, publisher, platform...",
            font=("Segoe UI", 13)
        )
        self._search_entry.pack(side="left", padx=(0, 8))
        # Pressing Enter triggers search
        self._search_entry.bind("<Return>", lambda e: self._search_games())
        # Clear search reloads all games when the search box is emptied
        self._search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        ctk.CTkButton(
            search_frame, text="Search", width=80, height=38,
            font=("Segoe UI", 13),
            command=self._search_games
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            search_frame, text="Clear", width=70, height=38,
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            hover_color=("gray85", "gray25"),
            command=self._clear_search
        ).pack(side="left")

        # ── Right side: Action buttons ──
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        # Add Game (green)
        ctk.CTkButton(
            btn_frame, text="➕  Add Game", width=135, height=38,
            font=("Segoe UI", 13, "bold"),
            fg_color="#22c55e", hover_color="#16a34a",
            text_color="white",
            command=self._open_add_form
        ).pack(side="left", padx=(0, 8))

        # Edit (amber)
        ctk.CTkButton(
            btn_frame, text="✏️  Edit", width=100, height=38,
            font=("Segoe UI", 13),
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="white",
            command=self._open_edit_form
        ).pack(side="left", padx=(0, 8))

        # Delete (red)
        ctk.CTkButton(
            btn_frame, text="🗑️  Delete", width=100, height=38,
            font=("Segoe UI", 13),
            fg_color="#ef4444", hover_color="#dc2626",
            text_color="white",
            command=self._delete_selected
        ).pack(side="left")

    # ── GAME TABLE ──

    def _create_table(self):
        """
        Build the games table using ttk.Treeview.

        A Treeview is like a spreadsheet/grid widget.
        Each row shows one game, each column shows one attribute.

        We hide the 'description' column (too long for a table)
        and the 'game_id' column (users don't need to see IDs).
        Both are still accessible when editing.
        """
        # Container frame for the table and scrollbar
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Define which columns to show
        columns = (
            "game_id", "title", "platform", "developer",
            "publisher", "price", "steam_rating", "age_rating",
            "release_date"
        )

        # Create the Treeview widget
        self._tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",       # Hide the default tree column
            selectmode="browse"    # Only one row can be selected at a time
        )

        # Configure each column's heading text and width
        col_config = {
            "game_id":      ("ID",           50),
            "title":        ("Title",        250),
            "platform":     ("Platform",     110),
            "developer":    ("Developer",    140),
            "publisher":    ("Publisher",     140),
            "price":        ("Price ($)",    90),
            "steam_rating": ("Rating ⭐",   80),
            "age_rating":   ("Age",          60),
            "release_date": ("Released",     110),
        }

        for col, (heading, width) in col_config.items():
            # Clicking a heading sorts by that column
            self._tree.heading(
                col, text=heading,
                command=lambda c=col: self._sort_table(c)
            )
            self._tree.column(col, width=width, minwidth=50)

        # Hide the game_id column (still accessible in code)
        self._tree.column("game_id", width=0, stretch=False)

        # Scrollbar for when there are many games
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        # Place table and scrollbar
        self._tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Double-clicking a row opens the edit form
        self._tree.bind("<Double-1>", lambda e: self._open_edit_form())

        # Apply dark/light styling to the table
        self._style_treeview()

    def _style_treeview(self):
        """
        Apply custom colors to the Treeview to match
        the current theme (dark or light).

        This is necessary because ttk.Treeview doesn't
        automatically follow CustomTkinter's theme.
        """
        style = ttk.Style()
        mode = ctk.get_appearance_mode()

        if mode == "Dark":
            bg = "#2b2b2b"
            fg = "#e0e0e0"
            heading_bg = "#333333"
            heading_fg = "#ffffff"
            selected_bg = "#4a6cf7"
            odd_bg = "#313131"
        else:
            bg = "#ffffff"
            fg = "#1a1a1a"
            heading_bg = "#f0f0f0"
            heading_fg = "#1a1a1a"
            selected_bg = "#4a6cf7"
            odd_bg = "#f7f7f7"

        style.theme_use("clam")

        # Table body style
        style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            rowheight=36,
            font=("Segoe UI", 11),
            borderwidth=0,
        )

        # Column header style
        style.configure(
            "Treeview.Heading",
            background=heading_bg,
            foreground=heading_fg,
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
        )

        # Selected row style
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "#ffffff")],
        )

        style.map(
            "Treeview.Heading",
            background=[("active", heading_bg)],
        )

        # Alternating row colors (zebra striping)
        # Makes the table easier to read
        self._tree.tag_configure("oddrow", background=odd_bg)
        self._tree.tag_configure("evenrow", background=bg)

    # ── STATUS BAR ──

    def _create_status_bar(self):
        """Build the bottom bar showing status and game count."""
        status_bar = ctk.CTkFrame(self, height=35, corner_radius=0)
        status_bar.grid(row=3, column=0, sticky="ew")

        self._status_label = ctk.CTkLabel(
            status_bar, text="Ready",
            font=("Segoe UI", 11), text_color="gray"
        )
        self._status_label.pack(side="left", padx=15, pady=5)

        self._count_label = ctk.CTkLabel(
            status_bar, text="Total: 0 games",
            font=("Segoe UI", 11), text_color="gray"
        )
        self._count_label.pack(side="right", padx=15, pady=5)

    # ───────────────────────────────────────
    #  TABLE OPERATIONS
    # ───────────────────────────────────────

    def _refresh_table(self):
        """
        Reload all games from MySQL into the table.

        This is called after every add/edit/delete to
        keep the display in sync with the database.
        """
        # Clear the current table contents
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Fetch all games from the database
        # (This runs: SELECT * FROM games ORDER BY title)
        rows, columns = self.db.get_all_games()

        # Insert each game as a row in the table
        for i, row in enumerate(rows):
            # Row data from MySQL (column order matches CREATE TABLE):
            #   row[0] = game_id
            #   row[1] = title
            #   row[2] = description  (not shown in table)
            #   row[3] = release_date
            #   row[4] = price
            #   row[5] = age_rating
            #   row[6] = platform
            #   row[7] = developer
            #   row[8] = publisher
            #   row[9] = steam_rating

            # Alternating row colors
            tag = "oddrow" if i % 2 else "evenrow"

            # Format values for display (handle None/NULL values)
            game_id = row[0]
            title = row[1] or ""
            release_date = str(row[3]) if row[3] else ""
            price = f"{row[4]:.2f}" if row[4] is not None else ""
            age_rating = row[5] or ""
            platform = row[6] or ""
            developer = row[7] or ""
            publisher = row[8] or ""
            steam_rating = str(row[9]) if row[9] is not None else ""

            # Insert the row into the table
            # The order here must match the columns defined in _create_table
            self._tree.insert("", "end", values=(
                game_id, title, platform, developer, publisher,
                price, steam_rating, age_rating, release_date
            ), tags=(tag,))

        # Update the game count in the status bar
        count = len(rows)
        self._count_label.configure(
            text=f"Total: {count} game{'s' if count != 1 else ''}"
        )
        self._status_label.configure(text="✅ Data loaded")

    def _sort_table(self, column):
        """
        Sort the table when a column header is clicked.

        Click once  → Sort A-Z (or low to high)
        Click again → Sort Z-A (or high to low)
        """
        # Get all items and their values for this column
        items = [
            (self._tree.set(item, column), item)
            for item in self._tree.get_children()
        ]

        # Try numeric sort first (for price, rating)
        # If that fails, sort alphabetically
        try:
            items.sort(key=lambda t: float(t[0]) if t[0] else 0)
        except ValueError:
            items.sort(key=lambda t: t[0].lower() if t[0] else "")

        # Toggle sort direction if clicking the same column again
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_reverse = False
            self._sort_column = column

        if self._sort_reverse:
            items.reverse()

        # Reorder items in the table
        for i, (_, item) in enumerate(items):
            self._tree.move(item, "", i)
            # Re-apply alternating row colors
            tag = "oddrow" if i % 2 else "evenrow"
            self._tree.item(item, tags=(tag,))

    # ───────────────────────────────────────
    #  CRUD ACTIONS
    # ───────────────────────────────────────

    def _open_add_form(self):
        """Open an empty form to add a new game."""
        GameForm(self, "Add New Game", self.db, callback=self._refresh_table)

    def _open_edit_form(self):
        """Open the form pre-filled with the selected game's data."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a game from the table first."
            )
            return

        # Get the game_id from the selected row
        values = self._tree.item(selected[0])["values"]
        game_id = values[0]

        # Fetch the full game data from the database
        # (We need all fields, including description which isn't in the table)
        rows, _ = self.db.get_all_games()
        game_data = None
        for row in rows:
            if row[0] == game_id:
                game_data = row
                break

        if game_data:
            GameForm(
                self, "Edit Game", self.db,
                game_data=game_data, callback=self._refresh_table
            )

    def _delete_selected(self):
        """Delete the selected game after confirmation."""
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a game from the table first."
            )
            return

        values = self._tree.item(selected[0])["values"]
        game_id = values[0]
        game_title = values[1]

        # Ask for confirmation before deleting
        # (Remember: DELETE is permanent! No undo!)
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\n"
            f"\"{game_title}\"?\n\n"
            f"This cannot be undone."
        )

        if confirm:
            success, message = self.db.delete_game(game_id)
            if success:
                self._status_label.configure(
                    text=f"🗑️ Deleted: {game_title}"
                )
                self._refresh_table()
            else:
                messagebox.showerror("Error", message)

    # ───────────────────────────────────────
    #  SEARCH
    # ───────────────────────────────────────

    def _search_games(self):
        """
        Search for games matching the keyword.
        Uses the LIKE query from database.py.
        """
        keyword = self._search_entry.get().strip()

        if not keyword:
            self._refresh_table()
            return

        # Clear current table
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Search the database
        rows, _ = self.db.search_games(keyword)

        # Display results
        for i, row in enumerate(rows):
            tag = "oddrow" if i % 2 else "evenrow"

            game_id = row[0]
            title = row[1] or ""
            release_date = str(row[3]) if row[3] else ""
            price = f"{row[4]:.2f}" if row[4] is not None else ""
            age_rating = row[5] or ""
            platform = row[6] or ""
            developer = row[7] or ""
            publisher = row[8] or ""
            steam_rating = str(row[9]) if row[9] is not None else ""

            self._tree.insert("", "end", values=(
                game_id, title, platform, developer, publisher,
                price, steam_rating, age_rating, release_date
            ), tags=(tag,))

        count = len(rows)
        self._count_label.configure(
            text=f"Found: {count} game{'s' if count != 1 else ''}"
        )
        self._status_label.configure(text=f"🔍 Search: \"{keyword}\"")

    def _on_search_change(self):
        """When the search box is cleared, show all games again."""
        if not self._search_entry.get().strip():
            self._refresh_table()

    def _clear_search(self):
        """Clear the search field and show all games."""
        self._search_entry.delete(0, "end")
        self._refresh_table()

    # ───────────────────────────────────────
    #  THEME TOGGLE
    # ───────────────────────────────────────

    def _toggle_theme(self):
        """Switch between dark and light mode."""
        mode = self._theme_switch.get()
        ctk.set_appearance_mode(mode)
        # Re-style the treeview after a short delay
        # (gives CustomTkinter time to update its widgets)
        self.after(100, self._style_treeview)
        self.after(200, self._refresh_table)

    # ───────────────────────────────────────
    #  DISCONNECT
    # ───────────────────────────────────────

    def _disconnect(self):
        """
        Disconnect from MySQL and return to the connection screen.
        Like logging out of the application.
        """
        if self.db:
            self.db.disconnect()
            self.db = None
        self.geometry("500x420")
        self.minsize(500, 420)
        self._center_window(500, 420)
        self._show_connection_screen()


# ═══════════════════════════════════════════════
#  ADD / EDIT GAME FORM (Popup Window)
# ═══════════════════════════════════════════════

class GameForm(ctk.CTkToplevel):
    """
    A popup window with a form to add or edit a game.

    When adding: All fields are empty.
    When editing: Fields are pre-filled with the game's current data.

    The form validates all inputs before saving:
    - Title is required
    - Price must be a valid number
    - Rating must be 0-10
    - Date must be in YYYY-MM-DD format
    """

    # Age rating options for the dropdown
    AGE_RATINGS = [
        "E - Everyone",
        "E10+ - Everyone 10+",
        "T - Teen",
        "M - Mature 17+",
        "AO - Adults Only",
        "RP - Rating Pending",
    ]

    # Mapping from short code → full label (for populating edit form)
    AGE_RATING_MAP = {
        "E": "E - Everyone",
        "E10+": "E10+ - Everyone 10+",
        "T": "T - Teen",
        "M": "M - Mature 17+",
        "AO": "AO - Adults Only",
        "RP": "RP - Rating Pending",
    }

    # Platform options for the dropdown
    PLATFORMS = [
        "Windows",
        "PC",
        "PlayStation 4",
        "PlayStation 5",
        "Xbox One",
        "Xbox Series X/S",
        "Nintendo Switch",
        "Mobile",
        "Multi-platform",
    ]

    def __init__(self, parent, title, db, game_data=None, callback=None):
        super().__init__(parent)

        self.db = db
        self.game_data = game_data
        self.callback = callback
        self.is_edit = game_data is not None

        # ── Window settings ──
        self.title(title)
        self.geometry("520x680")
        self.resizable(False, False)

        # transient → This window belongs to the parent
        # grab_set  → User must interact with this window first
        #             (can't click the main window while this is open)
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self._center_on_parent(parent)

        # Build the form
        self._create_form()

        # If editing, fill in the existing data
        if self.is_edit:
            self._populate_fields()

    def _center_on_parent(self, parent):
        """Position this popup in the center of the parent window."""
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w, h = 520, 680
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _create_form(self):
        """Build all the form fields."""
        # Scrollable container (in case the form is taller than the window)
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Form title ──
        icon = "✏️" if self.is_edit else "➕"
        heading = "Edit Game Details" if self.is_edit else "Add a New Game"

        ctk.CTkLabel(
            scroll, text=f"{icon}  {heading}",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 15), anchor="w")

        # ── Title (required) ──
        self._title_entry = self._create_text_field(
            scroll, "Title *", "e.g. Call of Duty: Modern Warfare"
        )

        # ── Description (multi-line text box) ──
        ctk.CTkLabel(
            scroll, text="Description",
            font=("Segoe UI", 13), anchor="w"
        ).pack(fill="x", pady=(12, 3))
        self._desc_entry = ctk.CTkTextbox(
            scroll, height=80, font=("Segoe UI", 12),
            border_width=1, border_color=("gray70", "gray30")
        )
        self._desc_entry.pack(fill="x", pady=(0, 5))

        # ── Platform (dropdown) ──
        ctk.CTkLabel(
            scroll, text="Platform",
            font=("Segoe UI", 13), anchor="w"
        ).pack(fill="x", pady=(12, 3))
        self._platform_entry = ctk.CTkComboBox(
            scroll, values=self.PLATFORMS,
            font=("Segoe UI", 12), state="normal"
        )
        self._platform_entry.set("")
        self._platform_entry.pack(fill="x", pady=(0, 5))

        # ── Developer ──
        self._dev_entry = self._create_text_field(
            scroll, "Developer", "e.g. Infinity Ward"
        )

        # ── Publisher ──
        self._pub_entry = self._create_text_field(
            scroll, "Publisher", "e.g. Activision"
        )

        # ── Release Date ──
        self._date_entry = self._create_text_field(
            scroll, "Release Date", "YYYY-MM-DD  (e.g. 2007-11-05)"
        )

        # ── Price ──
        self._price_entry = self._create_text_field(
            scroll, "Price ($)", "e.g. 59.99"
        )

        # ── Age Rating (dropdown) ──
        ctk.CTkLabel(
            scroll, text="Age Rating",
            font=("Segoe UI", 13), anchor="w"
        ).pack(fill="x", pady=(12, 3))
        self._age_entry = ctk.CTkComboBox(
            scroll, values=self.AGE_RATINGS,
            font=("Segoe UI", 12), state="normal"
        )
        self._age_entry.set("")
        self._age_entry.pack(fill="x", pady=(0, 5))

        # ── Steam Rating ──
        self._rating_entry = self._create_text_field(
            scroll, "Steam Rating (0 - 10)", "e.g. 8.5"
        )

        # ── Buttons ──
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(25, 10))

        save_text = "💾  Save Changes" if self.is_edit else "💾  Add Game"
        ctk.CTkButton(
            btn_frame, text=save_text, height=42,
            font=("Segoe UI", 14, "bold"),
            fg_color="#22c55e", hover_color="#16a34a",
            text_color="white",
            command=self._save
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text="Cancel", height=42,
            font=("Segoe UI", 14),
            fg_color="transparent", border_width=1,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            hover_color=("gray85", "gray25"),
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _create_text_field(self, parent, label, placeholder):
        """
        Helper: Create a label + text entry pair.
        Reduces repeated code for each form field.
        """
        ctk.CTkLabel(
            parent, text=label,
            font=("Segoe UI", 13), anchor="w"
        ).pack(fill="x", pady=(12, 3))

        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=("Segoe UI", 12)
        )
        entry.pack(fill="x", pady=(0, 5))
        return entry

    def _populate_fields(self):
        """
        Fill the form with existing game data when editing.

        game_data tuple order (from MySQL):
            [0] game_id      (not editable)
            [1] title
            [2] description
            [3] release_date
            [4] price
            [5] age_rating
            [6] platform
            [7] developer
            [8] publisher
            [9] steam_rating
        """
        data = self.game_data

        if data[1]:
            self._title_entry.insert(0, data[1])

        if data[2]:
            self._desc_entry.insert("1.0", data[2])

        if data[3]:
            self._date_entry.insert(0, str(data[3]))

        if data[4] is not None:
            self._price_entry.insert(0, str(data[4]))

        if data[5]:
            # Convert short code "M" → full label "M - Mature 17+"
            full_label = self.AGE_RATING_MAP.get(data[5], data[5])
            self._age_entry.set(full_label)

        if data[6]:
            self._platform_entry.set(data[6])

        if data[7]:
            self._dev_entry.insert(0, data[7])

        if data[8]:
            self._pub_entry.insert(0, data[8])

        if data[9] is not None:
            self._rating_entry.insert(0, str(data[9]))

    def _save(self):
        """
        Validate all inputs and save to database.

        Validation checks:
            1. Title is required (NOT NULL in the table)
            2. Price must be a valid number
            3. Steam rating must be between 0 and 10
            4. Release date must be YYYY-MM-DD format
        """
        # ── Collect all values ──
        title = self._title_entry.get().strip()
        description = self._desc_entry.get("1.0", "end-1c").strip()
        platform = self._platform_entry.get().strip()
        developer = self._dev_entry.get().strip()
        publisher = self._pub_entry.get().strip()
        release_date = self._date_entry.get().strip()
        price_str = self._price_entry.get().strip()
        age_rating = self._age_entry.get().strip()
        rating_str = self._rating_entry.get().strip()

        # ── Validate: Title is required ──
        if not title:
            messagebox.showwarning(
                "Missing Field",
                "Title is required!",
                parent=self
            )
            self._title_entry.focus()
            return

        # ── Validate: Price ──
        price = None
        if price_str:
            try:
                price = float(price_str)
                if price < 0:
                    messagebox.showwarning(
                        "Invalid Price",
                        "Price cannot be negative.",
                        parent=self
                    )
                    return
            except ValueError:
                messagebox.showwarning(
                    "Invalid Price",
                    "Price must be a number (e.g. 59.99)",
                    parent=self
                )
                self._price_entry.focus()
                return

        # ── Validate: Steam Rating ──
        steam_rating = None
        if rating_str:
            try:
                steam_rating = float(rating_str)
                if steam_rating < 0 or steam_rating > 10:
                    messagebox.showwarning(
                        "Invalid Rating",
                        "Rating must be between 0 and 10.",
                        parent=self
                    )
                    return
            except ValueError:
                messagebox.showwarning(
                    "Invalid Rating",
                    "Rating must be a number (e.g. 8.5)",
                    parent=self
                )
                self._rating_entry.focus()
                return

        # ── Validate: Release Date ──
        if release_date:
            try:
                datetime.strptime(release_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Date must be in YYYY-MM-DD format\n"
                    "(e.g. 2007-11-05)",
                    parent=self
                )
                self._date_entry.focus()
                return

        # ── Convert empty strings to None ──
        # MySQL stores empty values as NULL, not ""
        description = description or None
        platform = platform or None
        developer = developer or None
        publisher = publisher or None
        release_date = release_date or None

        # Extract short age rating code
        # "M - Mature 17+" → "M"
        if age_rating and " - " in age_rating:
            age_rating = age_rating.split(" - ")[0]
        age_rating = age_rating or None

        # ── Build the data tuple ──
        # This order must match the INSERT/UPDATE SQL in database.py
        game_data = (
            title, description, release_date, price,
            age_rating, platform, developer, publisher, steam_rating
        )

        # ── Save to database ──
        if self.is_edit:
            game_id = self.game_data[0]
            success, message = self.db.update_game(game_id, game_data)
        else:
            success, message = self.db.add_game(game_data)

        if success:
            # Refresh the main table to show the changes
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Database Error", message, parent=self)
