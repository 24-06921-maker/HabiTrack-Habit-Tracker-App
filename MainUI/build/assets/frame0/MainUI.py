import tkinter as tk
root = tk.Tk()
root.configure(bg="#ECF2FA")

main_frame = tk.Frame(root, bg="#ECF2FA")
main_frame.pack(padx=20, pady=20)
title = tk.Label(
    main_frame,
    text="HabiTrack: Habit Tracker App",
    font=("Helvetica", 24, "bold"),
    bg="#ECF2FA"
)
title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

todo_label = tk.Label(main_frame, text="To-Do List:", bg="#ECF2FA", font=("Helvetica", 18))
remarks_label = tk.Label(main_frame, text="Remarks", bg="#ECF2FA", font=("Helvetica", 18))

todo_label.grid(row=1, column=0, sticky="w")
remarks_label.grid(row=1, column=1, sticky="w")

habits = ["Habit 1: Sample Habit",
          "Habit 2: Sample Habit",
          "Habit 3: Sample Habit"]

for i, h in enumerate(habits, start=2):
    tk.Label(main_frame, text=h, bg="#ECF2FA", font=("Helvetica", 16)).grid(
        row=i, column=0, sticky="w", pady=5)

    tk.Label(main_frame, bg="#B6D1FF", width=4, height=2).grid(
        row=i, column=1, sticky="w", pady=5)
    
pager = tk.Label(main_frame, text="◀ 1/1 ▶", bg="#ECF2FA", font=("Helvetica", 16))
pager.grid(row=6, column=0, columnspan=2, pady=(10, 10))

btn_frame = tk.Frame(main_frame, bg="#ECF2FA")
btn_frame.grid(row=7, column=0, columnspan=2, pady=10)


def printAdd():
    print("Add")

tk.Button(btn_frame, text="Add", width=10, bg="#B6D1FF", command= printAdd()).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Delete", width=10, bg="#B6D1FF").grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="Update", width=10, bg="#B6D1FF").grid(row=0, column=2, padx=10)



root.mainloop() 