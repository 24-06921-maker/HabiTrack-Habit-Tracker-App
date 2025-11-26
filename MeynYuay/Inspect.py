import sqlite3
from pathlib import Path

# Use absolute path relative to this script's location (works from any directory)
SCRIPT_DIR = Path(__file__).resolve().parent
DATABASE_DIR = SCRIPT_DIR / "Database"
DATABASE_DIR.mkdir(exist_ok=True)  # auto-create folder if missing

DB_PATH = DATABASE_DIR / "habits_pandas.db"

print(f"Database path: {DB_PATH}")
print(f"Database exists: {DB_PATH.exists()}\n")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get all tables
print("=" * 50)
print("AVAILABLE TABLES IN DATABASE")
print("=" * 50)
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cur.fetchall()

if not tables:
    print("No tables found in database.")
else:
    for i, (table_name,) in enumerate(tables, 1):
        print(f"{i}. {table_name}")
        
        # Get row count for each table
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cur.fetchone()[0]
        print(f"   Rows: {row_count}")

print("\n" + "=" * 50)
print("To view data from a specific table, use:")
print("print_table('table_name')")
print("=" * 50 + "\n")

def print_table(table_name):
    """Print all data from a specific table."""
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cur.fetchall()]
        print(f"\nTable: {table_name}")
        print(f"Columns: {', '.join(columns)}")
        print("-" * 50)
        
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        if not rows:
            print("(No data)")
        else:
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error reading table '{table_name}': {e}")

def print_table_filtered(table_name, starts_with=None):
    """Print data from a specific table, optionally filtered by first column starting with a letter."""
    try:
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cur.fetchall()]
        print(f"\nTable: {table_name}")
        if starts_with:
            print(f"Filter: First column starts with '{starts_with}'")
        print(f"Columns: {', '.join(columns)}")
        print("-" * 50)
        
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        if not rows:
            print("(No data)")
        else:
            filtered_count = 0
            for row in rows:
                # Check if first column starts with the specified letter (case-insensitive)
                if starts_with is None or (isinstance(row[0], str) and row[0].upper().startswith(starts_with.upper())):
                    print(row)
                    filtered_count += 1
            if starts_with and filtered_count == 0:
                print(f"(No rows found starting with '{starts_with}')")
    except Exception as e:
        print(f"Error reading table '{table_name}': {e}")

print_table("habit_logs")
# Print all data from habit_logs table filtered by names starting with 'N'
print_table_filtered("habit_logs", starts_with="J")

conn.close()
