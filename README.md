# 🎮 Game Library & Achievement Tracker

A modern desktop application built to catalog video games and track personal gameplay achievements. This project is built using **Python (CustomTkinter)** for the user interface and **MySQL** for robust database management. 

It was designed and developed to learn and implement advanced database concepts, clean application architecture (MVC-style separation of GUI and database layers), and CRUD operations in a real-world software system.

---

## 🚀 Features

- **🛡️ Secure Database Connection:** Dynamic login screen to securely connect to your local MySQL instance without hardcoding credentials.
- **📊 Real-time Game Table:** Sortable, paginated-style grid showing titles, platforms, developers, publishers, prices, ratings, and release dates.
- **🎨 Dynamic Theme Engine:** Seamless real-time switching between **Dark Mode** and **Light Mode** using modern UI styles.
- **➕ CRUD Operations:** Add new games, edit existing titles (with form auto-population), and safely delete records (with confirmation prompts).
- **🔍 Advanced Search:** Instant search functionality to filter games dynamically by Title, Developer, Publisher, or Platform using SQL `LIKE` wildcard filters.
- **⚠️ Client-Side Validation:** Validates form inputs before sending to the database (e.g., verifying date formats, numeric price scales, and rating boundaries).

---

## 🛠️ Tech Stack & Architecture

- **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (for a modern, rounded, dark-mode first design)
- **Database:** MySQL Server 8.x
- **Connector:** `mysql-connector-python`
- **Language:** Python 3.12+

### 📁 Project Structure

```text
Game-Library-Achievement-Tracker/
│
├── sql/
│   ├── 001_create_database.sql       # Database creation script
│   ├── 002_create_users_table.sql    # Users schema (Phase 2 ready)
│   └── 003_create_games_table.sql    # Games V1 schema script
│
├── src/
│   ├── app.py                        # Application entry point
│   ├── database.py                   # SQL query layer (CRUD and logic)
│   └── gui.py                        # CustomTkinter interface code
│
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have the following installed on your machine:
* **Python 3.12+**
* **MySQL Server** and **MySQL Workbench**

### 2. Database Setup
Run the SQL scripts located in the `/sql` directory in your MySQL Workbench:
1. Run `001_create_database.sql` to create `game_library`.
2. Run `002_create_users_table.sql`.
3. Run `003_create_games_table.sql`.

### 3. Install Dependencies
Open your terminal in the root of the project directory and run:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the desktop interface by executing:
```bash
python src/app.py
```

---

## 🧠 Database Insights (What I Learned)

During Phase 1, I mastered the fundamental concepts of database schemas and data manipulation:

* **`AUTO_INCREMENT` & `PRIMARY KEY`:** Learned how databases uniquely identify rows and auto-generate IDs.
* **Optimal Datatypes:** Used `DECIMAL(10,2)` for financial values to prevent rounding issues, and `TEXT` for dynamic descriptions where character limits aren't known.
* **SQL Queries:**
  * **CREATE:** Schemas and structures.
  * **INSERT INTO:** Adding records.
  * **SELECT & filters (`WHERE`, `LIKE`, `ORDER BY`):** Extracting and sorting relevant data.
  * **UPDATE / DELETE:** Correcting records safely using specific keys.
