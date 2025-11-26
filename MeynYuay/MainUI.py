import tkinter as TikiTiki
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import math
import pandas as pd
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime



# First define SCRIPT_DIR
SCRIPT_DIR = Path(__file__).resolve().parent

# Now create the Database folder path
DATABASE_DIR = SCRIPT_DIR / "Database"
DATABASE_DIR.mkdir(exist_ok=True)  # auto-create folder if missing

CSV_PATH = DATABASE_DIR / "habits.csv"
JSON_PATH = DATABASE_DIR / "habits.json"
DB_PATH   = DATABASE_DIR / "habits_pandas.db"


## Initialize the SQLite database and create table if not exists
def init_db():
    """Create SQLite table to store daily habit progress."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            done      INTEGER NOT NULL,   -- 1 = done, 0 = not done
            logged_at TEXT NOT NULL       -- ISO datetime string
        )
    """)
    conn.commit()
    conn.close()
# call it once at startup
init_db()


window = TikiTiki.Tk()
window.title("Habit Tracker Main UI")

HABITS_PER_PAGE = 3

# Habits list (will be loaded from CSV at startup)
habits = []  # start empty; load_habits_csv() will populate it if CSV exists



# Pagination state
current_page = 0
total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))

# Window Size
window.geometry("800x900")
window.resizable(False, False)

# ==== Load images using absolute paths ====
# Compute the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent
BUTTONUI_DIR = SCRIPT_DIR / "ButtonUI"




## Load habits from CSV file 
def load_habits_csv():
   
    global habits, total_pages, current_page

    # If file not present, nothing to load
    if not CSV_PATH.exists():
        return

    try:
        df = pd.read_csv(CSV_PATH)

        # Basic validation: must have 'name'
        if "name" not in df.columns:
            print("habits.csv missing 'name' column — skipping load.")
            return

        # If position exists, restore original order
        if "position" in df.columns:
            df = df.sort_values("position", ignore_index=True)

        # Build the in-memory list: convert done -> bool
        loaded = []
        for _, row in df.iterrows():
            name = row.get("name", "")
            done_val = row.get("done", 0)
            # handle strings ("True"/"False") or numeric 0/1 — be permissive
            done = False
            if isinstance(done_val, str):
                done = done_val.strip().lower() in ("1", "true", "yes", "y")
            else:
                try:
                    done = bool(int(done_val))
                except Exception:
                    done = False
            loaded.append({"name": str(name), "done": done})

        # Replace the global habits and fix pagination state
        habits = loaded
        total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
        # clamp current_page if necessary
        if current_page >= total_pages:
            current_page = max(0, total_pages - 1)

        print(f"Loaded {len(habits)} habits from {CSV_PATH}")

    except Exception as e:
        # show a non-blocking console warning and a user popup
        print("Error loading habits CSV:", e)
        messagebox.showerror("Load error", f"Could not load habits from CSV:\n{e}")





load_habits_csv()


## Loading the images for Button UI
def load_image(filename, subsample_x=2, subsample_y=2):
    """Load an image from ButtonUI folder. Return None if not found."""
    path = BUTTONUI_DIR / filename
    if not path.exists():
        print(f"Warning: Image not found: {path}")
        return None
    try:
        img = TikiTiki.PhotoImage(file=str(path))
        return img.subsample(subsample_x, subsample_y)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

checked_img = load_image("checked.png", 2, 2)
unchecked_img = load_image("uncheck.png", 2, 2)
left_arrow_img = load_image("left.png", 2, 2)
right_arrow_img = load_image("right.png", 2, 2)
delete_img = load_image("delete.png", 3, 3)

if not all([checked_img, unchecked_img, left_arrow_img, right_arrow_img, delete_img]):
    print(f"\nSome images are missing. Expected them in: {BUTTONUI_DIR}")
    print("Files needed: checked.png, uncheck.png, left.png, right.png, delete.png")

# Keep references so garbage collection doesn't drop them
window.checked_img = checked_img if checked_img else None
window.unchecked_img = unchecked_img if unchecked_img else None
window.left_arrow_img = left_arrow_img if left_arrow_img else None
window.right_arrow_img = right_arrow_img if right_arrow_img else None
window.delete_img = delete_img if delete_img else None

# Main Frame
main_frame = TikiTiki.Frame(window, bg="#ECF2FA")
main_frame.pack(fill="both", expand=True)

# Title
title_label = TikiTiki.Label(
    main_frame,
    text="HabiTrack: Habit Tracker App",
    font=("Helvetica", 24, "bold"),
    bg="#ECF2FA",
    fg="#2B4D78"
)
title_label.pack(anchor="w", padx=20, pady=(10, 5))

underline = ttk.Separator(main_frame, orient="horizontal")
underline.pack(fill="x", padx=20, pady=(0, 10))

# Header Frame
header_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
header_frame.pack(fill="x", padx=20)

todo_label = TikiTiki.Label(
    header_frame,
    text="To-Do List:",
    font=("Roboto", 33),
    bg="#ECF2FA",
    fg="#2B4D78"
)
todo_label.pack(side="left")

remarks_label = TikiTiki.Label(
    header_frame,
    text="Remarks",
    font=("Helvetica", 30),
    bg="#ECF2FA",
    fg="#2B4D78"
)
remarks_label.pack(side="left", padx=(100, 0))

# Habits Frame (where rows will be drawn)
habit_list_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
habit_list_frame.pack(fill="x", padx=20, pady=10)

# Delete mode state
delete_mode = False

# --- Functions to render habits and pagination ---

def render_habits():
    """Clear and redraw habit rows for the current page."""
    # remove old rows
    for child in habit_list_frame.winfo_children():
        child.destroy()

    start = current_page * HABITS_PER_PAGE
    end = start + HABITS_PER_PAGE

    for local_index, habit in enumerate(habits[start:end]):
        global_index = start + local_index

        row_frame = TikiTiki.Frame(habit_list_frame, bg="#ECF2FA")
        row_frame.pack(fill="x", pady=8)

        # grid so we can place delete icon (col 0), label (col1), done-image (col2)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, weight=0)

        # If in delete mode, show the delete PNG on the left (clicking it asks for confirmation)
        if delete_mode:
            del_lbl = TikiTiki.Label(
                row_frame,
                image=window.delete_img,
                bg="#ECF2FA",
                bd=0,
                cursor="hand2"
            )
            del_lbl.grid(row=0, column=0, padx=(0, 8))
            del_lbl.image = window.delete_img  # keep ref

            # handler: ask confirmation, delete if yes, refresh
            def ask_delete(event=None, gi=global_index):
                # double-check gi is within range (it might shift if many deletes happen quickly)
                if gi < 0 or gi >= len(habits):
                    return
                name = habits[gi]["name"]
                if messagebox.askyesno("Confirm delete", f"Are you sure you want to delete:\n\n{name}"):
                    # remove the habit
                    del habits[gi]
                    # recalc pages and clamp current_page
                    global total_pages, current_page
                    total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
                    if current_page >= total_pages:
                        current_page = total_pages - 1
                    render_habits()

            del_lbl.bind("<Button-1>", ask_delete)

        else:
            # placeholder to keep alignment when not in delete mode
            spacer = TikiTiki.Frame(row_frame, width=18, bg="#ECF2FA")
            spacer.grid(row=0, column=0, padx=(0, 8))

        # Adjust font size if the habit text is long so it fits the label
        name_text = habit.get("name", "")
        # base size 20, reduce when length exceeds 10 characters
        if len(name_text) > 10:
            # decrease by 1 for every 2 extra characters, clamp at 10
            font_size = max(10, 20 - (len(name_text) - 10) // 2)
        else:
            font_size = 20

        habit_label = TikiTiki.Label(
            row_frame,
            text=name_text,
            font=("Helvetica", font_size),
            bg="#ECF2FA"
        )
        habit_label.grid(row=0, column=1, sticky="w")

        start_img = window.checked_img if habit["done"] else window.unchecked_img

        checkbox_label = TikiTiki.Label(
            row_frame,
            image=start_img,
            bg="#ECF2FA",
            bd=0,
            cursor="hand2"
        )
        checkbox_label.grid(row=0, column=2, padx=100)
        checkbox_label.image = start_img  # keep ref

        def toggle(event, gi=global_index, lbl=checkbox_label):
            # only toggle done when not in delete mode
            if delete_mode:
                return
            if gi < 0 or gi >= len(habits):
                return
            habits[gi]["done"] = not habits[gi]["done"]
            new_img = window.checked_img if habits[gi]["done"] else window.unchecked_img
            lbl.config(image=new_img)
            lbl.image = new_img

        checkbox_label.bind("<Button-1>", toggle)

    update_page_label()

# Pagination frame (img – text – img)
pagination_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
pagination_frame.pack(pady=10)

left_btn = TikiTiki.Label(
    pagination_frame,
    image=left_arrow_img,
    bg="#ECF2FA",
    cursor="hand2"
)
left_btn.grid(row=0, column=0, padx=5)
left_btn.image = left_arrow_img

page_label = TikiTiki.Label(
    pagination_frame,
    text="",
    font=("Helvetica", 16),
    bg="#ECF2FA",
    fg="#2B4D78"
)
page_label.grid(row=0, column=1, padx=5)

right_btn = TikiTiki.Label(
    pagination_frame,
    image=right_arrow_img,
    bg="#ECF2FA",
    cursor="hand2"
)
right_btn.grid(row=0, column=2, padx=5)
right_btn.image = right_arrow_img

def update_page_label():
    global total_pages
    total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
    page_label.config(text=f"{current_page + 1}/{total_pages}")

def go_prev(event=None):
    global current_page
    if current_page > 0:
        current_page -= 1
        render_habits()

def go_next(event=None):
    global current_page
    if current_page < total_pages - 1:
        current_page += 1
        render_habits()

left_btn.bind("<Button-1>", go_prev)
right_btn.bind("<Button-1>", go_next)

# Initial draw
render_habits()

# Buttons
# --- Bottom Button Frame ---
button_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
button_frame.pack(pady=20)

# Shared button style
def create_ui_button(text):
    btn = TikiTiki.Button(
        button_frame,
        text=text,
        font=("Helvetica", 22, "bold"),
        bg="#AFCBFF",
        fg="#2B4D78",
        activebackground="#9EC1FF",
        activeforeground="#2B4D78",
        width=8,
        height=2,
        bd=0,
        relief="flat",
        cursor="hand2"
    )
    btn.pack(side="left", padx=15)
    return btn

add_btn = create_ui_button("Add")
delete_btn = create_ui_button("Delete")
record_btn = create_ui_button("Record")

# Back button: return to Login UI (launches login script and closes this window)
def go_back():
    login_path = SCRIPT_DIR.parent / "LoginUI" / "New folder" / "build" / "gui.py"
    if not login_path.exists():
        messagebox.showerror("Not found", f"Login UI not found at: {login_path}")
        return
    try:
        subprocess.Popen([sys.executable, str(login_path)], cwd=str(login_path.parent))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Login UI: {e}")
        return
    window.destroy()

back_btn = create_ui_button("Back")
back_btn.config(command=go_back)

# --- ADD HABIT: open a Toplevel and add a new habit without closing main window ---
def add_habit():
    # create Toplevel dialog
    add_win = TikiTiki.Toplevel(window)
    add_win.title("Add Habit")
    add_win.geometry("380x200")
    add_win.resizable(False, False)
    add_win.configure(bg="#ECF2FA")

    # modal-like so user focuses on dialog
    add_win.grab_set()

    lbl = TikiTiki.Label(add_win, text="Habit name:", font=("Helvetica", 14), bg="#ECF2FA")
    lbl.pack(anchor="w", padx=12, pady=(12, 4))

    name_var = TikiTiki.StringVar()
    name_entry = TikiTiki.Entry(add_win, textvariable=name_var, font=("Helvetica", 14), width=32)
    name_entry.pack(padx=12)

    done_var = TikiTiki.BooleanVar(value=False)

    # Save handler
    def save_and_close():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Empty name", "Please enter a habit name.")
            return
        # append new habit to the end
        habits.append({"name": name, "done": done_var.get()})
        # update pagination globals properly
        global total_pages, current_page
        total_pages = math.ceil(len(habits) / HABITS_PER_PAGE)
        # show page that contains the new habit (last page)
        current_page = total_pages - 1 if total_pages > 0 else 0
        add_win.destroy()
        render_habits()

    save_btn = TikiTiki.Button(add_win, text="Add Habit", command=save_and_close, width=12)
    save_btn.pack(pady=12)

    name_entry.focus_set()

# Wire Add button to the function
add_btn.config(command=add_habit)

# Toggle delete mode: show/hide left-side delete icons and change button text
def toggle_delete_mode():
    global delete_mode
    delete_mode = not delete_mode
    delete_btn.config(text="Cancel" if delete_mode else "Delete")
    render_habits()

delete_btn.config(command=toggle_delete_mode)

# Placeholder functions for other buttons (you can implement similarly)
def record_habits():
    """
    Show a confirmation dialog with all current habits.
    If confirmed:
      - log each habit (name, done, datetime) into SQLite
      - overwrite CSV with current habit states
    """
    if not habits:
        messagebox.showwarning("No habits", "No habits to record.")
        return

    # Build a formatted list of habits for the confirmation dialog
    habit_list_text = "\n".join(
        [f"{'✓' if h['done'] else '○'} {h['name']}" for h in habits]
    )

    # Show confirmation dialog
    msg = f"Are you sure you want to record these habits?\n\n{habit_list_text}"
    ok = messagebox.askyesno("Confirm Record", msg)

    if not ok:
        return

    # Use one timestamp for this whole "record" action
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 1) Insert into SQLite habit_logs
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        for habit in habits:
            cur.execute(
                "INSERT INTO habit_logs (name, done, logged_at) VALUES (?, ?, ?)",
                (habit["name"], int(habit["done"]), now_str)
            )

        conn.commit()
        conn.close()

        # 2) Overwrite CSV with current habit list + done status
        import csv
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "done"])
            for habit in habits:
                writer.writerow([habit["name"], habit["done"]])

        messagebox.showinfo(
            "Success",
            f"Recorded {len(habits)} habit(s) to CSV and database."
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to record habits:\n{e}")

    # For Debugging: function to get logs for a specific date

def get_logs_for_date(target_date: str):
    """
    Return all habit logs for a specific date.
    target_date format: 'YYYY-MM-DD'
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, done, logged_at
        FROM habit_logs
        WHERE date(logged_at) = ?
        ORDER BY logged_at
    """, (target_date,))

    rows = cur.fetchall()
    conn.close()
    return rows
# Example: print today's logs in the console
today_str = "2025-03-15"
logs = get_logs_for_date(today_str)

print(f"Logs for {today_str}:")
for name, done, logged_at in logs:
    status = "Done" if done == 1 else "Not done"
    print(f"- {name}: {status} at {logged_at}")



record_btn.config(command=record_habits)

window.mainloop()
