import tkinter as TikiTiki
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import math

window = TikiTiki.Tk()
window.title("Habit Tracker Main UI")

HABITS_PER_PAGE = 3

# Sample Habits Data
habits = [
    {"name": "Sample Habit", "done": False},
    {"name": "Sample Habit", "done": True},
    {"name": "Sample Habit", "done": False},
    {"name": "Sample Habit", "done": True},
    {"name": "Sample Habit", "done": False},
    {"name": "Sample Habit", "done": True},
    {"name": "Sample Habit", "done": False},
]

# Pagination state
current_page = 0
total_pages = max(1, math.ceil(len(habits) / HABITS_PER_PAGE))

# Window Size
window.geometry("600x750")
window.resizable(False, False)

# ==== Load checkbox images ====
# Make sure these paths exist or adjust them
checked_img = TikiTiki.PhotoImage(file="ButtonUI/checked.png").subsample(2, 2)
unchecked_img = TikiTiki.PhotoImage(file="ButtonUI/uncheck.png").subsample(2, 2)

# ==== Load pagination arrow images (change these paths) ====
left_arrow_img = TikiTiki.PhotoImage(file="ButtonUI/left.png").subsample(2, 2)
right_arrow_img = TikiTiki.PhotoImage(file="ButtonUI/right.png").subsample(2, 2)

# ==== Load delete (trash) image ====
delete_img = TikiTiki.PhotoImage(file="ButtonUI/checked.png").subsample(2, 2)

# Keep references so garbage collection doesn't drop them
window.checked_img = checked_img
window.unchecked_img = unchecked_img
window.left_arrow_img = left_arrow_img
window.right_arrow_img = right_arrow_img
window.delete_img = delete_img

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

        habit_label = TikiTiki.Label(
            row_frame,
            text=habit["name"],
            font=("Helvetica", 20),
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
        checkbox_label.grid(row=0, column=2, padx=12)
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
    messagebox.showinfo("Record", "Record functionality not implemented yet.")

record_btn.config(command=record_habits)

window.mainloop()
