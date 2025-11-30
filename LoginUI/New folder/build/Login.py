import subprocess
import sys
from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


# Compute paths relative to this script's location (works on any device)
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


## Ensure asset path is correct
def relative_to_assets(path: str) -> Path: 
    return ASSETS_PATH / Path(path)

def open_main():
    window.destroy()         # close login window

    # launch MainUI as a separate process
    # Compute path relative to this script (project root is 3 levels up: build -> New folder -> LoginUI -> Habit Track)
    script_dir = Path(__file__).resolve().parent.parent.parent.parent
    mainui_path = script_dir / "MeynYuay" / "MainUI.py"
    mainui_cwd = script_dir / "MeynYuay"

    Popen = subprocess.Popen
    Popen([sys.executable, str(mainui_path)], cwd=str(mainui_cwd))


def open_habit():
    window.destroy()         # close login window

    #Launch Habits as a separate process
    # Compute path relative to this script (project root is 3 levels up: build -> New folder -> LoginUI -> Habit Track)
    script_dir = Path(__file__).resolve().parent.parent.parent.parent
    habitsui_path = script_dir / "Habits_" / "Habits.py"
    habitsui_cwd = script_dir / "Habits_"

    Popen = subprocess.Popen
    Popen([sys.executable, str(habitsui_path)], cwd=str(habitsui_cwd))


def open_progress():

    # Launch ProgressUI as a separate process
    # Compute path relative to this script (project root is 3 levels up: build -> New folder -> LoginUI -> Habit Track)
    script_dir = Path(__file__).resolve().parent.parent.parent.parent
    progress_path = script_dir / "MeynYuay" / "ProgressUI.py"
    progress_cwd = script_dir / "MeynYuay"

    Popen = subprocess.Popen
    Popen([sys.executable, str(progress_path)], cwd=str(progress_cwd))

window = Tk()

window.geometry("600x600")
window.configure(bg = "#F5F7FA")


canvas = Canvas(
    window,
    bg = "#F5F7FA",
    height = 600,
    width = 600,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
login_img = PhotoImage(
    file=relative_to_assets("button_1.png"))


login_button = Button(
    image=login_img,
    borderwidth=0,
    highlightthickness=0,
    command=open_main,
    relief="flat"
)
login_button.place(
    x=150.0,
    y=150.0,
    width=300.0,
    height=72.0
)


## Button for Habits Button

habit_img = PhotoImage(
    file=relative_to_assets("button_2.png"))
habit_btn = Button(
    image=habit_img,
    borderwidth=0,
    highlightthickness=0,
    command=open_habit,
    relief="flat"
)
habit_btn.place(
    x=150.0,
    y=277.0,
    width=300.0,
    height=72.0
)


## Progress Button
progress_Img = PhotoImage(
    file=relative_to_assets("button_3.png"))
progress_btn = Button(
    image=progress_Img,
    borderwidth=0,
    highlightthickness=0,
    command=open_progress,
    relief="flat"
)
progress_btn.place(
    x=150.0,
    y=404.0,
    width=300.0,
    height=72.0
)


canvas.create_rectangle(
    -1.0,
    92.99999994861778,
    600.0000319469182,
    95.0,
    fill="#1B1D25",
    outline="")

canvas.create_text(
    41.0,
    29.0,
    anchor="nw",
    text="HabiTrack: Habit Tracker App",
    fill="#3A5BA0",
    font=("Inter", 35 * -1)
)
window.resizable(False, False)
window.mainloop()
