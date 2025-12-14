import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import calendar

# Path to the database
SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "Database" / "habits_pandas.db"


class ProgressUI:
    ## Constructor for ProgressUI
    def __init__(self, parent=None, day_click_callback=None):
        ## Create Toplevel if parent provided, else main Tk window
        self.window = tk.Toplevel(parent) if parent else tk.Tk() 
        self.window.title("Habit Progress - Monthly View")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        self.window.configure(bg="#ECF2FA")
        
        # Current month tracking
        self.current_date = datetime.now()


        # If provided, it will be invoked instead of the default popup.
        self.day_click_callback = day_click_callback
        self.setup_ui()
        self.update_month_label()
        self.load_monthly_data()
    
    def setup_ui(self):
        """Create the UI layout."""
        # Title and navigation
        header_frame = tk.Frame(self.window, bg="#ECF2FA")
        header_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        title = tk.Label(
            header_frame,
            text="Monthly Habit Progress",
            font=("Helvetica", 24, "bold"),
            bg="#ECF2FA",
            fg="#2B4D78"
        )
        title.pack(side="left")
        
        # Month/Year navigation
        nav_frame = tk.Frame(header_frame, bg="#ECF2FA")
        nav_frame.pack(side="right")
        

        ## Label to show current month and year
        self.month_label = tk.Label(
            nav_frame,
            text="",
            font=("Helvetica", 14),
            bg="#ECF2FA",
            fg="#2B4D78"
        )
        self.month_label.pack(side="left", padx=10)
        
        prev_btn = tk.Button(
            nav_frame,
            text="← Previous",
            ## Bind to previous month function
            command=self.prev_month,
            font=("Helvetica", 10),
            bg="#AFCBFF",
            fg="#2B4D78",
            relief="flat",
            cursor="hand2"
        )
        ## Pack the button to the left with padding
        prev_btn.pack(side="left", padx=5)
        
        ## Next month button
        next_btn = tk.Button(
            nav_frame,
            text="Next →",
            ## Bind to next month function
            command=self.next_month,
            font=("Helvetica", 10),
            bg="#AFCBFF",
            fg="#2B4D78",
            relief="flat",
            cursor="hand2"
        )
        next_btn.pack(side="left", padx=5)
        
        # Separator line below header
        separator = ttk.Separator(self.window, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=(0, 10))
        
        # Main content frame with two columns
        content_frame = tk.Frame(self.window, bg="#ECF2FA")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side: Calendar
        left_frame = tk.Frame(content_frame, bg="#ECF2FA")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        cal_label = tk.Label(
            left_frame,
            text="Calendar",
            font=("Helvetica", 14, "bold"),
            bg="#ECF2FA",
            fg="#2B4D78"
        )
        cal_label.pack(anchor="w", pady=(0, 10))
        
        # Calendar grid
        self.calendar_frame = tk.Frame(left_frame, bg="white", relief="solid", bd=1)
        self.calendar_frame.pack(fill="both", expand=True)
        
        # Right side: Statistics
        right_frame = tk.Frame(content_frame, bg="#ECF2FA")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        stats_label = tk.Label(
            right_frame,
            text="Monthly Statistics",
            font=("Helvetica", 14, "bold"),
            bg="#ECF2FA",
            fg="#2B4D78"
        )
        stats_label.pack(anchor="w", pady=(0, 10))
        
        self.stats_frame = tk.Frame(right_frame, bg="white", relief="solid", bd=1)
        self.stats_frame.pack(fill="both", expand=True)
        
        # Bottom: Habit breakdown
        breakdown_label = tk.Label(
            ## self.window refers to the main window
            self.window,
            text="Habit Breakdown",
            font=("Helvetica", 14, "bold"),
            bg="#ECF2FA",
            fg="#2B4D78"
        )
        breakdown_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.breakdown_frame = tk.Frame(self.window, bg="white", relief="solid", bd=1)
        self.breakdown_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Scrollbar for breakdown
        scrollbar = ttk.Scrollbar(self.breakdown_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.breakdown_text = tk.Text(
            self.breakdown_frame,
            height=8,
            bg="white",
            fg="#2B4D78",
            font=("Courier", 10),
            yscrollcommand=scrollbar.set
        )
        self.breakdown_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.breakdown_text.yview)
    
    
    ## Load data for the current month using database queries
    def load_monthly_data(self):
        """Load and display data for the current month."""
        ## Display the calendar
        self.display_calendar()
        ## Display statistics
        self.display_statistics()
        ## Display habit breakdow
        self.display_habit_breakdown()

        ## Display monthly completion pie chart
        self.display_monthly_pie_chart()
    
    def display_calendar(self):
        """Display calendar with colored days based on habit logging."""
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Get all logged dates for this month
        logged_dates = self.get_logged_dates()
        
        # Day names
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_frame = tk.Frame(self.calendar_frame, bg="#2B4D78")
        day_frame.pack(fill="x")
        
        for day in days:
            day_lbl = tk.Label(
                day_frame,
                text=day,
                font=("Helvetica", 10, "bold"),
                bg="#2B4D78",
                fg="white",
                width=4,
                height=1
            )
            day_lbl.pack(side="left", fill="both", expand=True)
        
        # Calendar dates
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        for week in cal:
            week_frame = tk.Frame(self.calendar_frame, bg="#ECF2FA")
            week_frame.pack(fill="both", expand=True)
            
            for day in week:
                if day == 0:
                    # Empty cell for days from other months
                    cell = tk.Label(week_frame, text="", bg="#ECF2FA", relief="solid", bd=1)
                else:
                    date_obj = datetime(self.current_date.year, self.current_date.month, day)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    # Check if this day has logged habits
                    if date_str in logged_dates:
                        completion = logged_dates[date_str]["completion_rate"]
                        # Color based on completion
                        if completion == 100:
                            bg_color = "#90EE90"  # Green
                        elif completion >= 50:
                            bg_color = "#FFD700"  # Yellow
                        else:
                            bg_color = "#FFB6C1"  # Light red
                        
                        text = f"{day}\n{completion:.0f}%"
                    else:
                        bg_color = "#E0E0E0"  # Gray (no data)
                        text = str(day)
                    
                    cell = tk.Label(
                        week_frame,
                        text=text,
                        font=("Helvetica", 9),
                        bg=bg_color,
                        fg="#2B4D78",
                        relief="solid",
                        bd=1,
                        width=4,
                        height=3,
                        wraplength=40,
                        cursor="hand2"
                    )
                    # Bind click to this date
                    cell.bind("<Button-1>", lambda e, ds=date_str: self.handle_day_click(ds))
                
                cell.pack(side="left", fill="both", expand=True)

    def handle_day_click(self, date_str: str):
        """Handle click on a calendar day."""
        pass

    def get_logs_for_specific_date(self, date_str: str):
        """Return all logs for a given date (YYYY-MM-DD)."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            cur.execute("""
                SELECT id, name, done, logged_at
                FROM habit_logs
                WHERE DATE(logged_at) = ?
                ORDER BY logged_at
            """, (date_str,))


            conn.close()
            return rows
        except Exception as e:
            print(f"Error querying logs for {date_str}: {e}")
            return []

    def open_day_detail(self, date_str: str):
        """Open a popup listing habit logs for the chosen date."""
        rows = self.get_logs_for_specific_date(date_str)

        detail = tk.Toplevel(self.window)
        detail.title(f"Logs for {date_str}")
        detail.geometry("520x380")
        detail.configure(bg="#ECF2FA")

        lbl = tk.Label(detail, text=f"Habit Logs for {date_str}", font=("Helvetica", 14, "bold"), bg="#ECF2FA")
        lbl.pack(anchor="w", padx=10, pady=(8, 4))

        frame = tk.Frame(detail, bg="white", relief="solid", bd=1)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        txt = tk.Text(frame, wrap="none", bg="white", fg="#2B4D78", font=("Courier", 10))
        txt.pack(fill="both", expand=True, side="left")

        sc = ttk.Scrollbar(frame, command=txt.yview)
        sc.pack(side="right", fill="y")
        txt.config(yscrollcommand=sc.set)

        if not rows:
            txt.insert("end", "No logs for this date.")
        else:
            txt.insert("end", f"{'ID':<5} {'Status':<8} {'Habit Name':<30} {'Logged At':<20}\n")
            txt.insert("end", "-" * 80 + "\n")
            for _id, name, done, logged_at in rows:
                status = 'Done' if done == 1 or done is True else 'Not Done'
                txt.insert("end", f"{_id:<5} {status:<8} {name:<30} {logged_at:<20}\n")

        txt.config(state="disabled")
    
    def display_statistics(self):
        """Display monthly statistics."""
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = self.calculate_monthly_stats()
        
        # Create stat boxes
        stat_data = [
            ("Total Days\nLogged", str(stats['total_days'])),
            ("Avg Completion\nRate", f"{stats['avg_completion']:.1f}%"),
            ("Best Streak", f"{stats['best_streak']} days"),
            ("Total Habits\nLogged", str(stats['total_logs'])),
        ]
        
        for title, value in stat_data:
            stat_box = tk.Frame(self.stats_frame, bg="#F0F0F0", relief="solid", bd=1)
            stat_box.pack(fill="x", padx=10, pady=8)
            
            title_lbl = tk.Label(
                stat_box,
                text=title,
                font=("Helvetica", 10),
                bg="#F0F0F0",
                fg="#666666"
            )
            title_lbl.pack(anchor="w", padx=10, pady=(5, 2))
            
            value_lbl = tk.Label(
                stat_box,
                text=value,
                font=("Helvetica", 18, "bold"),
                bg="#F0F0F0",
                fg="#2B4D78"
            )
            value_lbl.pack(anchor="w", padx=10, pady=(2, 5))
    
    def display_habit_breakdown(self):
        """Display completion stats for each habit."""
        self.breakdown_text.config(state="normal")
        self.breakdown_text.delete("1.0", "end")
        
        habit_stats = self.get_habit_stats()
        
        if not habit_stats:
            self.breakdown_text.insert("end", "No habits logged this month.")
        else:
            # Header
            header = f"{'Habit Name':<35} {'Completed':<12} {'Rate':<10}\n"
            header += "-" * 60 + "\n"
            self.breakdown_text.insert("end", header)
            
            # Sort by completion rate descending
            for habit_name in sorted(habit_stats.keys(), 
                                    key=lambda x: habit_stats[x]['completion_rate'], 
                                    reverse=True):
                stats = habit_stats[habit_name]
                completed = stats['completed']
                total = stats['total']
                rate = stats['completion_rate']
                
                # Progress bar
                bar_length = 20
                filled = int(bar_length * rate / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                line = f"{habit_name:<35} {completed}/{total:<10} {bar} {rate:.1f}%\n"
                self.breakdown_text.insert("end", line)
        
        self.breakdown_text.config(state="disabled")
    
    def get_logged_dates(self):
        """Get all dates with logged habits for current month."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            start_date = datetime(self.current_date.year, self.current_date.month, 1)
            end_date = start_date + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
            
            cur.execute("""
                SELECT DATE(logged_at) as date,
                       COUNT(*) as total,
                       SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed
                FROM habit_logs
                WHERE DATE(logged_at) BETWEEN ? AND ?
                GROUP BY DATE(logged_at)
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            result = {}
            for row in cur.fetchall():
                date_str, total, completed = row
                completion_rate = (completed / total * 100) if total > 0 else 0
                result[date_str] = {
                    "total": total,
                    "completed": completed,
                    "completion_rate": completion_rate
                }
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting logged dates: {e}")
            return {}
    
    def calculate_monthly_stats(self):
        """Calculate monthly statistics."""
        logged_dates = self.get_logged_dates()
        
        if not logged_dates:
            return {
                'total_days': 0,
                'avg_completion': 0.0,
                'best_streak': 0,
                'total_logs': 0
            }
        
        total_days = len(logged_dates)
        avg_completion = sum(d['completion_rate'] for d in logged_dates.values()) / total_days if total_days > 0 else 0
        total_logs = sum(d['total'] for d in logged_dates.values())
        
        # Calculate best streak
        dates = sorted(logged_dates.keys())
        best_streak = 0
        current_streak = 1
        
        for i in range(1, len(dates)):
            curr = datetime.strptime(dates[i], "%Y-%m-%d")
            prev = datetime.strptime(dates[i-1], "%Y-%m-%d")
            if (curr - prev).days == 1:
                current_streak += 1
            else:
                best_streak = max(best_streak, current_streak)
                current_streak = 1
        best_streak = max(best_streak, current_streak)
        
        return {
            'total_days': total_days,
            'avg_completion': avg_completion,
            'best_streak': best_streak,
            'total_logs': total_logs
        }
    
    def get_habit_stats(self):
        """Get completion stats for each habit this month."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            start_date = datetime(self.current_date.year, self.current_date.month, 1)
            end_date = start_date + timedelta(days=32)
            end_date = end_date.replace(day=1) - timedelta(days=1)
            
            cur.execute("""
                SELECT name,
                       COUNT(*) as total,
                       SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed
                FROM habit_logs
                WHERE DATE(logged_at) BETWEEN ? AND ?
                GROUP BY name
                ORDER BY name
            """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            result = {}
            for row in cur.fetchall():
                name, total, completed = row
                completion_rate = (completed / total * 100) if total > 0 else 0
                result[name] = {
                    'total': total,
                    'completed': completed,
                    'completion_rate': completion_rate
                }
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting habit stats: {e}")
            return {}
    
    def calculate_habit_streaks(self):
        """Calculate current streak for each habit (consecutive days with completion = 1)."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Get all habits and their logs, ordered by name and date
            cur.execute("""
                SELECT DISTINCT name
                FROM habit_logs
                ORDER BY name
            """)

                    
            habits = [row[0] for row in cur.fetchall()]
            streaks = {}
            
            for habit in habits:
                # Get all dates this habit was logged and completed, ordered by date
                cur.execute("""
                    SELECT DATE(logged_at) as log_date
                    FROM habit_logs
                    WHERE name = ? AND done = 1
                    ORDER BY logged_at DESC
                """, (habit,))
                
                dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cur.fetchall()]
                
                if not dates:
                    streaks[habit] = 0
                    continue
                
                # Calculate current streak (from today backwards)
                current_streak = 0
                today = datetime.now().date()
                expected_date = today
                
                for log_date in dates:
                    if log_date == expected_date:
                        current_streak += 1
                        expected_date = expected_date - timedelta(days=1)
                    else:
                        break
                
                streaks[habit] = current_streak
            
            conn.close()
            return streaks
        except Exception as e:
            print(f"Error calculating habit streaks: {e}")
            return {}

    
    def display_monthly_pie_chart(self):
        """Display monthly completion pie chart with habit streaks and completion percentage."""
        habit_stats = self.get_habit_stats() ## Get habit stats for the month
        
        if not habit_stats:
            print("No habit data for this month.")
            return
        
        # Calculate overall monthly statistics
        total_completed = sum(stat['completed'] for stat in habit_stats.values())
        total_logged = sum(stat['total'] for stat in habit_stats.values())
        overall_completion = (total_completed / total_logged * 100) if total_logged > 0 else 0
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        fig.suptitle(f"Monthly Habit Progress - {self.current_date.strftime('%B %Y')}", 
                     fontsize=16, fontweight='bold')
        
        # Left pie chart: Overall completion rate
        completion_labels = [f'Completed\n({total_completed}/{total_logged})', 
                            f'Not Completed\n({total_logged - total_completed}/{total_logged})']
        completion_sizes = [total_completed, total_logged - total_completed]
        completion_colors = ['#90EE90', '#FFB6C1']  # Green and Light Red
        
        wedges1, texts1, autotexts1 = ax1.pie(
            completion_sizes,
            labels=completion_labels,
            colors=completion_colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        for autotext in autotexts1:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax1.set_title(f"Overall Completion Rate\n{overall_completion:.1f}%", 
                     fontsize=12, fontweight='bold', pad=15)
        
        # Right pie chart: Per-habit completion breakdown
        habit_names = []
        habit_rates = []
        habit_colors = []
        
        for habit in sorted(habit_stats.keys(), 
                           key=lambda x: habit_stats[x]['completion_rate'], 
                           reverse=True):
            stats = habit_stats[habit]
            rate = stats['completion_rate']
            # Color based on completion rate
            if rate == 100:
                color = '#90EE90'  # Green
            elif rate > 75:
                color = '#FFB6C1'  # Light Red (75% to 100%)
            elif rate >= 50:
                color = '#FFD700'  # Yellow (50% to 75%)
            elif rate > 0:
                color = '#FF8C00'  # Dark Orange (0% to 50%)
            else:
                color = '#FF0000'  # Red (0% completion)
            
            habit_names.append(f"{habit}\n{rate:.0f}%")
            habit_rates.append(rate)  # Use completion rate instead of completed count
            habit_colors.append(color)
        
        wedges2, texts2, autotexts2 = ax2.pie(
            habit_rates,
            labels=habit_names,
            colors=habit_colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 9, 'weight': 'bold'}
        )
        
        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        
        ax2.set_title("Per-Habit Completion", fontsize=12, fontweight='bold', pad=15)
        
        plt.tight_layout()
        plt.show()
    
    def prev_month(self):
        """Navigate to previous month."""
        self.current_date = self.current_date - timedelta(days=1)
        self.current_date = self.current_date.replace(day=1)
        self.update_month_label()
        self.load_monthly_data()
    
    def next_month(self):
        """Navigate to next month."""
        # Go to next month
        ## Next month logic
        ## If current month is December, increment year and set month to January
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_month_label()
        self.load_monthly_data()
    
    def update_month_label(self):
        """Update the month/year label."""
        month_str = self.current_date.strftime("%B %Y")
        self.month_label.config(text=month_str)


def open_progress_ui(parent=None, day_click_callback=None):
    """Open the progress UI window.

    Args:
        parent: optional parent TK widget.
        day_click_callback: optional function called as func(date_str)
            when a calendar day is clicked. If not provided, the default
            internal detail popup will be used.
    """
    ProgressUI(parent, day_click_callback=day_click_callback)



## Make sure this file can be run standalone for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root window
    ProgressUI(root)
    root.mainloop()
