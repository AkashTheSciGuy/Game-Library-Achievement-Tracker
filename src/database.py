"""
database.py — The Database Layer
=================================
This file is the "translator" between Python and MySQL.
Every function here runs an SQL query that you already learned.

Think of it like this:
    When the user clicks "Add Game" in the GUI...
    → gui.py calls database.py's add_game() function
    → add_game() runs: INSERT INTO games (...) VALUES (...)
    → MySQL stores the data

The user never sees or writes SQL. Python does it for them.

SQL Concepts Used:
    SELECT    → get_all_games(), search_games(), get_game_count()
    INSERT    → add_game()
    UPDATE    → update_game()
    DELETE    → delete_game()
    WHERE     → Used in update, delete, and search
    LIKE      → Used in search (partial text matching)
    ORDER BY  → Used to sort results alphabetically
    COUNT(*)  → Used to count total games
"""

# ─────────────────────────────────────────────
# mysql.connector is the library that lets
# Python "talk" to MySQL. Without it, Python
# has no way to send SQL commands.
# ─────────────────────────────────────────────
import mysql.connector
from mysql.connector import Error


class Database:
    """
    Manages the MySQL connection and provides methods
    for all game library operations.

    CRUD = the four basic database operations:
        C = Create  (INSERT INTO)
        R = Read    (SELECT)
        U = Update  (UPDATE ... SET)
        D = Delete  (DELETE FROM)
    """

    def __init__(self):
        # This will hold our MySQL connection object.
        # It starts as None because we haven't connected yet.
        self.connection = None

    # ═══════════════════════════════════════════
    #  CONNECTION
    # ═══════════════════════════════════════════

    def connect(self, host, user, password, database):
        """
        Connect to the MySQL server.

        This is like opening MySQL Workbench and typing
        in your username and password — but Python does it.

        Parameters:
            host     → Usually "localhost" (your own computer)
            user     → Usually "root" (the admin account)
            password → The password you set during MySQL installation
            database → "game_library" (the database we created)

        Returns:
            (True, message)  if connection worked
            (False, message) if something went wrong
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            return True, "Connected successfully!"
        except Error as e:
            return False, str(e)

    def disconnect(self):
        """
        Close the connection to MySQL.

        Always disconnect when you're done — it's like
        logging out of MySQL Workbench.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def is_connected(self):
        """Check if we're still connected to MySQL."""
        return self.connection is not None and self.connection.is_connected()

    # ═══════════════════════════════════════════
    #  READ — SELECT (Retrieve data)
    # ═══════════════════════════════════════════

    def get_all_games(self):
        """
        Get every game from the database, sorted by title.

        SQL: SELECT * FROM games ORDER BY title;

        In English:
            "Show me all games, sorted alphabetically by title."

        ORDER BY is new — it sorts the results.
            ORDER BY title       → A to Z
            ORDER BY title DESC  → Z to A  (DESC = descending)

        Returns:
            rows    → A list of tuples, each tuple is one game
            columns → A list of column names
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM games ORDER BY title")
            rows = cursor.fetchall()
            # cursor.description gives us the column names
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return rows, columns
        except Error as e:
            print(f"Error fetching games: {e}")
            return [], []

    def search_games(self, keyword):
        """
        Search for games that contain a keyword.

        SQL:
            SELECT * FROM games
            WHERE title LIKE '%keyword%'
               OR developer LIKE '%keyword%'
               OR publisher LIKE '%keyword%'
               OR platform LIKE '%keyword%'
            ORDER BY title;

        In English:
            "Show me all games where the title, developer,
             publisher, or platform contains this word."

        LIKE is new — it does partial matching:
            LIKE '%war%' would match:
                ✅ "Call of Duty: World at War"
                ✅ "God of War"
                ✅ "Warcraft"
            The % symbols mean "anything can go here"

        IMPORTANT — Security Note:
            We use %s placeholders instead of putting the keyword
            directly into the SQL string. This prevents a hack
            called "SQL injection" where someone could type SQL
            commands into the search box and damage your database.

        Returns:
            rows    → Matching games
            columns → Column names
        """
        try:
            cursor = self.connection.cursor()
            sql = """
                SELECT * FROM games
                WHERE title LIKE %s
                   OR developer LIKE %s
                   OR publisher LIKE %s
                   OR platform LIKE %s
                ORDER BY title
            """
            # Wrap the keyword with % on both sides for partial matching
            search_term = f"%{keyword}%"
            cursor.execute(sql, (search_term, search_term, search_term, search_term))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return rows, columns
        except Error as e:
            print(f"Error searching games: {e}")
            return [], []

    def get_game_count(self):
        """
        Count the total number of games.

        SQL: SELECT COUNT(*) FROM games;

        In English:
            "How many games are in the table?"

        You already learned this in MySQL Workbench!
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM games")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            return 0

    # ═══════════════════════════════════════════
    #  CREATE — INSERT (Add new data)
    # ═══════════════════════════════════════════

    def add_game(self, game_data):
        """
        Add a new game to the database.

        SQL:
            INSERT INTO games
                (title, description, release_date, price,
                 age_rating, platform, developer, publisher, steam_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);

        In English:
            "Add this new game to the games table with these values."

        Notice we don't include game_id — AUTO_INCREMENT handles that!

        Parameters:
            game_data → A tuple with 9 values in this order:
                (title, description, release_date, price, age_rating,
                 platform, developer, publisher, steam_rating)

        Returns:
            (True, message)  if it worked
            (False, message) if something went wrong
        """
        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO games
                    (title, description, release_date, price, age_rating,
                     platform, developer, publisher, steam_rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, game_data)
            # commit() saves the change permanently.
            # Without it, the INSERT would be temporary and lost.
            self.connection.commit()
            cursor.close()
            return True, "Game added successfully!"
        except Error as e:
            return False, str(e)

    # ═══════════════════════════════════════════
    #  UPDATE — Modify existing data
    # ═══════════════════════════════════════════

    def update_game(self, game_id, game_data):
        """
        Update an existing game's information.

        SQL:
            UPDATE games
            SET title = %s, description = %s, ...
            WHERE game_id = %s;

        In English:
            "Change this game's details, but ONLY for the game
             with this specific game_id."

        The WHERE clause is critical here!
        Without it, UPDATE would change EVERY game in the table.

        Parameters:
            game_id   → Which game to update (e.g., 1)
            game_data → Tuple of new values (same order as add_game)

        Returns:
            (True, message)  if it worked
            (False, message) if something went wrong
        """
        try:
            cursor = self.connection.cursor()
            sql = """
                UPDATE games SET
                    title = %s,
                    description = %s,
                    release_date = %s,
                    price = %s,
                    age_rating = %s,
                    platform = %s,
                    developer = %s,
                    publisher = %s,
                    steam_rating = %s
                WHERE game_id = %s
            """
            # We add game_id to the end of the tuple
            # because it's the last %s in the SQL (the WHERE part)
            cursor.execute(sql, (*game_data, game_id))
            self.connection.commit()
            cursor.close()
            return True, "Game updated successfully!"
        except Error as e:
            return False, str(e)

    # ═══════════════════════════════════════════
    #  DELETE — Remove data
    # ═══════════════════════════════════════════

    def delete_game(self, game_id):
        """
        Delete a game from the database.

        SQL:
            DELETE FROM games WHERE game_id = %s;

        In English:
            "Remove the game with this ID from the table."

        Again, WHERE is critical — without it, DELETE would
        remove ALL games. That's exactly what we discussed
        in our earlier lesson!

        Parameters:
            game_id → Which game to delete

        Returns:
            (True, message)  if it worked
            (False, message) if something went wrong
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM games WHERE game_id = %s", (game_id,))
            self.connection.commit()
            cursor.close()
            return True, "Game deleted successfully!"
        except Error as e:
            return False, str(e)
