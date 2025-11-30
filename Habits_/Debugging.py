import sqlite3
from datetime import datetime
from pathlib import Path

# Path to the database
DB_PATH = Path(__file__).resolve().parent.parent / "MeynYuay" / "Database" / "habits_pandas.db"


def print_daily_habits(date_str=None):
    """
    Print all habit records for a specific day.
    
    Args:
        date_str (str): Date in format "YYYY-MM-DD". 
                       If None, uses today's date.
    
    Example:
        print_daily_habits("2025-11-28")
        print_daily_habits()  # Uses today's date
    """
    # Use today's date if not provided
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Query all records for the specified day
        cur.execute("""
            SELECT id, name, done, logged_at 
            FROM habit_logs 
            WHERE DATE(logged_at) = ?
            ORDER BY logged_at ASC
        """, (date_str,))
        
        records = cur.fetchall()
        conn.close()
        
        # Display results
        print(f"\n{'='*70}")
        print(f"Habit Records for: {date_str}")
        print(f"{'='*70}")
        
        if not records:
            print(f"No habits logged on {date_str}")
        else:
            print(f"{'ID':<5} {'Status':<8} {'Habit Name':<35} {'Logged At':<20}")
            print("-" * 70)
            
            for record_id, name, done, logged_at in records:
                status = "✓ Done" if done else "✗ Not Done"
                print(f"{record_id:<5} {status:<8} {name:<35} {logged_at:<20}")
            
            print(f"{'='*70}")
            print(f"Total habits logged: {len(records)}")
            completed = sum(1 for _, _, done, _ in records if done)
            print(f"Completed: {completed}/{len(records)}")
            print(f"{'='*70}\n")
        
        return records
        
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return []


def print_daily_habits_summary(date_str=None):
    """
    Print a summary of completed vs incomplete habits for a day.
    
    Args:
        date_str (str): Date in format "YYYY-MM-DD".
                       If None, uses today's date.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get summary statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) as incomplete
            FROM habit_logs 
            WHERE DATE(logged_at) = ?
        """, (date_str,))
        
        result = cur.fetchone()
        total, completed, incomplete = result
        
        # Get completed habits list
        cur.execute("""
            SELECT name FROM habit_logs 
            WHERE DATE(logged_at) = ? AND done = 1
            ORDER BY logged_at ASC
        """, (date_str,))
        completed_habits = [row[0] for row in cur.fetchall()]
        
        # Get incomplete habits list
        cur.execute("""
            SELECT name FROM habit_logs 
            WHERE DATE(logged_at) = ? AND done = 0
            ORDER BY logged_at ASC
        """, (date_str,))
        incomplete_habits = [row[0] for row in cur.fetchall()]
        
        conn.close()
        
        # Display summary
        print(f"\n{'='*70}")
        print(f"Daily Summary for: {date_str}")
        print(f"{'='*70}")
        print(f"Total Habits: {total}")
        print(f"Completed: {completed}")
        print(f"Incomplete: {incomplete}")
        
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"Completion Rate: {completion_rate:.1f}%")
        
        if completed_habits:
            print(f"\n✓ Completed Habits:")
            for i, habit in enumerate(completed_habits, 1):
                print(f"  {i}. {habit}")
        
        if incomplete_habits:
            print(f"\n✗ Incomplete Habits:")
            for i, habit in enumerate(incomplete_habits, 1):
                print(f"  {i}. {habit}")
        
        print(f"{'='*70}\n")
        
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")


# ============ EXAMPLE USAGE ============
if __name__ == "__main__":
    # Print today's habits
    print_daily_habits("2025-12-28")
    
    # Print summary for today
    print_daily_habits_summary("2025-12-28")    
    # Print habits for a specific date
    # print_daily_habits("2025-11-27")
    # print_daily_habits_summary("2025-11-27")
