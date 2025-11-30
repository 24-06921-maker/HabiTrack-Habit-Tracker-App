import tkinter as TikiTiki
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import math
import pandas as pd
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import csv

# -------------------- Paths & Configuration --------------------
SCRIPT_DIR = Path(__file__).resolve().parent

# Go up one level to "Habit Track" folder, then into MeynYuay
PROJECT_ROOT = SCRIPT_DIR.parent
MEINYUAY_DIR = PROJECT_ROOT / "MeynYuay"

# Database folder is inside MeynYuay
DATABASE_DIR = MEINYUAY_DIR / "Database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# CSV file for habits
CSV_PATH = DATABASE_DIR / "habits.csv"

# Button images live in MeynYuay / ButtonUI
BUTTONUI_DIR = MEINYUAY_DIR / "ButtonUI"

# UI constants
HABITS_PER_PAGE = 5

# -------------------- Tkinter window --------------------
window = TikiTiki.Tk()
window.title("HabiTrack - Habit Tracker App")
window.geometry("800x900")
window.resizable(False, False)

# -------------------- Image loader (robust) --------------------
def find_image_file(dirpath: Path, basename: str):
    """Case-insensitive search for basename in dirpath with common extensions.
       Returns Path or None."""
    if not dirpath.exists():
        return None
    lower = basename.lower()
    exts = ["png", "gif", "jpg", "jpeg", "bmp"]
    # direct matches and ext matches
    for f in dirpath.iterdir():
        if not f.is_file():
            continue
        if f.name.lower() == basename.lower():
            return f
        for ext in exts:
            if f.name.lower() == f"{lower}.{ext}":
                return f
    # contains match (e.g., arrow_left.png)
    for f in dirpath.iterdir():
        if not f.is_file():
            continue
        if lower in f.name.lower():
            return f
    return None

def load_image_safe(basename, subsample_x=2, subsample_y=2):
    """Return a PhotoImage or None if not found. Accepts base name without extension."""
    f = find_image_file(BUTTONUI_DIR, basename)
    if not f:
        print(f"Warning: Image not found (searched): {BUTTONUI_DIR}/{basename}.*")
        # debug listing
        try:
            print("ButtonUI files:", [p.name for p in BUTTONUI_DIR.iterdir()])
        except Exception:
            pass
        return None
    try:
        img = TikiTiki.PhotoImage(file=str(f))
        try:
            return img.subsample(subsample_x, subsample_y)
        except Exception:
            return img
    except Exception as e:
        print(f"Error loading image {f}: {e}")
        return None

# tiny placeholders so UI doesn't break when images are missing
def make_placeholder_arrow(direction="left"):
    img = TikiTiki.PhotoImage(width=28, height=28)
    img.put("white", to=(0,0,27,27))
    # simple line/triangle
    if direction == "left":
        for i in range(8,20):
            img.put("black", to=(i, 14 - (i//6), i, 14 - (i//6)))
    else:
        for i in range(8,20):
            img.put("black", to=(i, 14 + (i//6), i, 14 + (i//6)))
    return img

def make_placeholder_delete():
    img = TikiTiki.PhotoImage(width=28, height=28)
    img.put("white", to=(0,0,27,27))
    for i in range(8,20):
        img.put("black", to=(i,i,i,i))
        img.put("black", to=(i,27-i,i,27-i))
    return img

# attempt loading (base names)
left_arrow_img = load_image_safe("left", 2, 2)
right_arrow_img = load_image_safe("right", 2, 2)
delete_img = load_image_safe("delete", 3, 3)

if left_arrow_img is None:
    left_arrow_img = make_placeholder_arrow("left")
    print("Using placeholder left arrow.")
if right_arrow_img is None:
    right_arrow_img = make_placeholder_arrow("right")
    print("Using placeholder right arrow.")
if delete_img is None:
    delete_img = make_placeholder_delete()
    print("Using placeholder delete icon.")

# keep references to avoid GC
window.left_arrow_img = left_arrow_img
window.right_arrow_img = right_arrow_img
window.delete_img = delete_img

# -------------------- UI skeleton --------------------
main_frame = TikiTiki.Frame(window, bg="#ECF2FA")
main_frame.pack(fill="both", expand=True)

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

header_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
header_frame.pack(fill="x", padx=20)

todo_label = TikiTiki.Label(
    header_frame,
    text="To-Do List:",
    font=("Roboto", 40),
    bg="#ECF2FA",
    fg="#2B4D78"
)
todo_label.pack(side="left")

habit_list_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
habit_list_frame.pack(fill="x", padx=20, pady=10)

# pagination frame is created later after images are ready
pagination_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
pagination_frame.pack(pady=10)

# -------------------- State --------------------
habits = []  # list of {"name": ...}
current_page = 0
total_pages = 1
delete_mode = False



# File Handling Functions
# -------------------- CSV master/log handling --------------------
def load_habits_csv():
    """Load habit list from CSV if exists."""
    global habits, total_pages, current_page
    habits = []
    if CSV_PATH.exists():
        try:
            df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
            # Expect header 'name' or first column is names
            if "name" in df.columns:
                names = df["name"].tolist()
            else:
                first_col = df.columns[0]
                names = df[first_col].tolist()
            loaded = []
            for n in names:
                nm = str(n).strip()
                if nm:
                    loaded.append({"name": nm})
            habits = loaded
            total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
            if current_page >= total_pages:
                current_page = max(0, total_pages - 1)
            print(f"Loaded {len(habits)} habits from: {CSV_PATH}")
            return
        except Exception as e:
            print("Error loading master CSV:", e)

    # fallback: try legacy 'habits.csv' (if user used old single-file)
    legacy = DATABASE_DIR / "habits.csv"
    if legacy.exists():
        try:
            df = pd.read_csv(legacy, dtype=str, keep_default_na=False)
            # try to extract names heuristically
            if "name" in df.columns:
                names = df["name"].tolist()
            elif "date" in df.columns and "name" in df.columns:
                names = df["name"].unique().tolist()
            else:
                first_col = df.columns[0]
                names = df[first_col].tolist()
            loaded = []
            for n in names:
                nm = str(n).strip()
                if nm:
                    loaded.append({"name": nm})
            habits = loaded
            total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
            if current_page >= total_pages:
                current_page = max(0, total_pages - 1)
            print(f"Loaded {len(habits)} habits from legacy file: {legacy}")
            return
        except Exception as e:
            print("Error loading legacy CSV:", e)

    # if nothing found, start empty
    total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
    print("No master file found; starting with empty habit list.")

def save_habits_csv():
    """Save full habit list to CSV, overwriting."""
    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "done"])
            for h in habits:
                writer.writerow([h["name"], "True" if h.get("done") else "False"])
        print(f"Habit list saved to {CSV_PATH}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save habits:\n{e}")

# -------------------- Render functions --------------------
def render_habits():
    for child in habit_list_frame.winfo_children():
        child.destroy()

    start = current_page * HABITS_PER_PAGE
    end = start + HABITS_PER_PAGE

    for local_index, habit in enumerate(habits[start:end]):
        global_index = start + local_index

        row_frame = TikiTiki.Frame(habit_list_frame, bg="#ECF2FA")
        row_frame.pack(fill="x", pady=8)
        row_frame.grid_columnconfigure(0, weight=0)
        row_frame.grid_columnconfigure(1, weight=1)

        if delete_mode:
            del_lbl = TikiTiki.Label(row_frame, image=window.delete_img, bg="#ECF2FA", bd=0, cursor="hand2")
            del_lbl.grid(row=0, column=0, padx=(0, 8))
            del_lbl.image = window.delete_img

            def ask_delete(event=None, gi=global_index):
                if gi < 0 or gi >= len(habits):
                    return
                name = habits[gi]["name"]
                if messagebox.askyesno("Confirm delete", f"Are you sure you want to delete:\n\n{name}"):
                    del habits[gi]
                    save_habits_csv()
                    global total_pages, current_page
                    total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
                    if current_page >= total_pages:
                        current_page = total_pages - 1
                    render_habits()

            del_lbl.bind("<Button-1>", ask_delete)
        else:
            spacer = TikiTiki.Frame(row_frame, width=18, bg="#ECF2FA")
            spacer.grid(row=0, column=0, padx=(0, 8))

        name_text = habit.get("name", "")
        if len(name_text) > 10:
            font_size = max(20, 30 - (len(name_text) - 20) // 2)
        else:
            font_size = 40

        habit_label = TikiTiki.Label(row_frame, text=name_text, font=("Helvetica", font_size), bg="#ECF2FA")
        habit_label.grid(row=0, column=1, sticky="w")

    update_page_label()

# -------------------- Pagination widgets --------------------
left_btn = TikiTiki.Label(pagination_frame, image=left_arrow_img, bg="#ECF2FA", cursor="hand2")
left_btn.grid(row=0, column=0, padx=5)
left_btn.image = left_arrow_img

page_label = TikiTiki.Label(pagination_frame, text="", font=("Helvetica", 16), bg="#ECF2FA", fg="#2B4D78")
page_label.grid(row=0, column=1, padx=5)

right_btn = TikiTiki.Label(pagination_frame, image=right_arrow_img, bg="#ECF2FA", cursor="hand2")
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

# -------------------- Buttons --------------------
button_frame = TikiTiki.Frame(main_frame, bg="#ECF2FA")
button_frame.pack(pady=20)

def create_ui_button(text):
    btn = TikiTiki.Button(button_frame, text=text, font=("Helvetica", 22, "bold"),
                          bg="#AFCBFF", fg="#2B4D78", activebackground="#9EC1FF",
                          activeforeground="#2B4D78", width=8, height=2, bd=0,
                          relief="flat", cursor="hand2")
    btn.pack(side="left", padx=15)
    return btn

add_btn = create_ui_button("Add")
delete_btn = create_ui_button("Delete")
record_btn = create_ui_button("Record")
back_btn = create_ui_button("Back")

# Back behavior (attempt to open Login UI as before)
def go_back():
    login_path = SCRIPT_DIR.parent / "LoginUI" / "New folder" / "build" / "Login.py"
    if not login_path.exists():
        messagebox.showerror("Not found", f"Login UI not found at: {login_path}")
        return
    try:
        subprocess.Popen([sys.executable, str(login_path)], cwd=str(login_path.parent))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Login UI: {e}")
        return
    window.destroy()

back_btn.config(command=go_back)

# -------------------- Add habit dialog --------------------
def add_habit():
    add_win = TikiTiki.Toplevel(window)
    add_win.title("Add Habit")
    add_win.geometry("380x200")
    add_win.resizable(False, False)
    add_win.configure(bg="#ECF2FA")
    add_win.grab_set()

    lbl = TikiTiki.Label(add_win, text="Habit name:", font=("Helvetica", 14), bg="#ECF2FA")
    lbl.pack(anchor="w", padx=12, pady=(12, 4))

    name_var = TikiTiki.StringVar()
    name_entry = TikiTiki.Entry(add_win, textvariable=name_var, font=("Helvetica", 14), width=32)
    name_entry.pack(padx=12)

    def save_and_close():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Empty name", "Please enter a habit name.")
            return
        # append to memory and CSV
        habits.append({"name": name})
        save_habits_csv()
        global total_pages, current_page
        total_pages = math.ceil(len(habits) / HABITS_PER_PAGE)
        current_page = total_pages - 1 if total_pages > 0 else 0
        add_win.destroy()
        render_habits()

    save_btn = TikiTiki.Button(add_win, text="Add Habit", command=save_and_close, width=12)
    save_btn.pack(pady=12)
    name_entry.focus_set()

add_btn.config(command=add_habit)

# -------------------- Toggle delete mode --------------------
def toggle_delete_mode():
    global delete_mode
    delete_mode = not delete_mode
    delete_btn.config(text="Cancel" if delete_mode else "Delete")
    render_habits()

delete_btn.config(command=toggle_delete_mode)

# -------------------- Record habits (update CSV) --------------------
def record_habits():
    """Save current habits to CSV, adding new ones and updating existing ones."""
    if not habits:
        messagebox.showwarning("No habits", "No habits to record.")
        return

    habit_list_text = "\n".join([f"{'✓' if h.get('done') else '○'} {h['name']}" for h in habits])
    msg = f"Are you sure you want to record these habits?\n\n{habit_list_text}"
    ok = messagebox.askyesno("Confirm Record", msg)
    if not ok:
        return

    try:
        # Load existing habits from CSV if it exists
        existing = {}
        if CSV_PATH.exists():
            try:
                df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
                for _, row in df.iterrows():
                    existing[row.get("name", "")] = row.get("done", "False")
            except Exception:
                existing = {}

        # Merge: update with current habits, keep any that aren't in the current list
        merged = existing.copy()
        for h in habits:
            merged[h["name"]] = "True" if h.get("done") else "False"

        # Write back to CSV
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "done"])
            for name, done_str in merged.items():
                writer.writerow([name, done_str])

        messagebox.showinfo("Success", f"Recorded {len(habits)} habit(s) to:\n{CSV_PATH}")
        print(f"Updated habit list: {CSV_PATH}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to record habits: {e}")

record_btn.config(command=record_habits)

# -------------------- Startup: load master and render --------------------
load_habits_csv()
total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))
update_page_label()
render_habits()

window.mainloop()
