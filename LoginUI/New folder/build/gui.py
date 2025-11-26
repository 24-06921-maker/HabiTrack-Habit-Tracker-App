import subprocess
import sys
from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


# Compute paths relative to this script's location (works on any device)
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


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
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=open_main,
    relief="flat"
)
button_1.place(
    x=150.0,
    y=150.0,
    width=300.0,
    height=72.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=150.0,
    y=404.0,
    width=300.0,
    height=72.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=150.0,
    y=277.0,
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
