
import os
import tkinter as tk
from tkinter import messagebox

try:
    from winotify import Notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False


# ---------------- CONFIGURATION ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHWAY_FILE = os.path.join(BASE_DIR, "highway_mode.txt")

TOTAL_DISTANCE = 900
WARNING_DISTANCE = 300
ENTRY_DISTANCE = 500
STEP_DISTANCE = 100

progress = 0
highway_sent = False
closed = False


# ---------------- HIGHWAY MODE ----------------

def set_highway_mode(mode):
    """Share the highway state with the camera program."""
    try:
        with open(HIGHWAY_FILE, "w", encoding="utf-8") as file:
            file.write(mode)
    except OSError as error:
        messagebox.showerror(
            "File Error",
            f"Could not update highway mode:\n{error}"
        )


def show_notification(title, message):
    if NOTIFICATIONS_AVAILABLE:
        try:
            Notification(
                app_id="DriveSense",
                title=title,
                msg=message
            ).show()
        except Exception:
            pass


# ---------------- UPDATE DISPLAY ----------------

def update_display():
    percentage = min(100, int(progress / TOTAL_DISTANCE * 100))

    progress_text.config(
        text=f"{progress} / {TOTAL_DISTANCE} units"
    )
    percentage_text.config(text=f"{percentage}%")
    progress_canvas.delete("all")

    canvas_width = progress_canvas.winfo_width()
    if canvas_width < 10:
        canvas_width = 440

    progress_canvas.create_rectangle(
        0, 0, canvas_width, 12,
        fill="#2A3541", outline=""
    )

    fill_width = canvas_width * percentage / 100
    progress_canvas.create_rectangle(
        0, 0, fill_width, 12,
        fill="#D8FF52", outline=""
    )

    if progress < WARNING_DISTANCE:
        status_title.config(
            text="ROAD CLEAR",
            fg="#D8FF52"
        )
        status_description.config(
            text="Continue driving safely. No highway warning yet."
        )
        status_icon.config(text="✓", fg="#D8FF52")
        status_card.config(bg="#202D35")

    elif progress < ENTRY_DISTANCE:
        status_title.config(
            text="HIGHWAY AHEAD",
            fg="#FFBE55"
        )
        status_description.config(
            text="Prepare for highway driving. Stay alert."
        )
        status_icon.config(text="!", fg="#FFBE55")
        status_card.config(bg="#382F24")

    else:
        status_title.config(
            text="HIGHWAY ENTRY",
            fg="#FF7373"
        )
        status_description.config(
            text="Highway entry reached. Warning buzzer activated."
        )
        status_icon.config(text="!", fg="#FF7373")
        status_card.config(bg="#3B272B")

    remaining = max(0, ENTRY_DISTANCE - progress)

    if progress < ENTRY_DISTANCE:
        distance_text.config(
            text=f"{remaining} units until highway entry"
        )
    else:
        distance_text.config(
            text="Highway entry reached"
        )

    advance_button.config(
        state="normal" if progress < TOTAL_DISTANCE else "disabled"
    )


# ---------------- JOURNEY CONTROLS ----------------

def advance_journey():
    global progress, highway_sent

    if progress >= TOTAL_DISTANCE:
        return

    previous_progress = progress
    progress = min(progress + STEP_DISTANCE, TOTAL_DISTANCE)

    # Trigger highway mode only once, when crossing 500 units.
    if (
        previous_progress < ENTRY_DISTANCE
        and progress >= ENTRY_DISTANCE
        and not highway_sent
    ):
        highway_sent = True
        set_highway_mode("HIGHWAY")

        show_notification(
            "DriveSense - Highway Alert",
            "Highway entry reached. Stay alert!"
        )

    update_display()


def reset_journey():
    global progress, highway_sent

    progress = 0
    highway_sent = False

    set_highway_mode("NORMAL")
    update_display()


def close_app():
    global closed

    if closed:
        return

    closed = True
    set_highway_mode("NORMAL")
    root.destroy()


# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("DriveSense | Highway Simulator")
root.geometry("540x590")
root.resizable(False, False)
root.configure(bg="#101820")
root.protocol("WM_DELETE_WINDOW", close_app)


# ---------------- HEADER ----------------

header = tk.Frame(root, bg="#101820")
header.pack(fill="x", padx=26, pady=(24, 18))

logo = tk.Label(
    header,
    text="DS",
    font=("Segoe UI", 17, "bold"),
    fg="#17251E",
    bg="#D8FF52",
    width=3,
    height=1
)
logo.pack(side="left", padx=(0, 12))

header_text = tk.Frame(header, bg="#101820")
header_text.pack(side="left")

tk.Label(
    header_text,
    text="DriveSense",
    font=("Segoe UI", 20, "bold"),
    fg="#FFFFFF",
    bg="#101820"
).pack(anchor="w")

tk.Label(
    header_text,
    text="HIGHWAY JOURNEY SIMULATOR",
    font=("Segoe UI", 9, "bold"),
    fg="#A8B4BF",
    bg="#101820"
).pack(anchor="w", pady=(3, 0))

tk.Label(
    header,
    text="SYSTEM READY",
    font=("Segoe UI", 8, "bold"),
    fg="#D8FF52",
    bg="#25342D",
    padx=10,
    pady=7
).pack(side="right")


# ---------------- PROGRESS ----------------

tk.Label(
    root,
    text="JOURNEY PROGRESS",
    font=("Segoe UI", 10, "bold"),
    fg="#A8B4BF",
    bg="#101820"
).pack(anchor="w", padx=28)

progress_row = tk.Frame(root, bg="#101820")
progress_row.pack(fill="x", padx=28, pady=(6, 10))

progress_text = tk.Label(
    progress_row,
    text="0 / 900 units",
    font=("Segoe UI", 22, "bold"),
    fg="#FFFFFF",
    bg="#101820"
)
progress_text.pack(side="left")

percentage_text = tk.Label(
    progress_row,
    text="0%",
    font=("Segoe UI", 13, "bold"),
    fg="#D8FF52",
    bg="#101820"
)
percentage_text.pack(side="right")

progress_canvas = tk.Canvas(
    root,
    height=12,
    bg="#101820",
    highlightthickness=0
)
progress_canvas.pack(fill="x", padx=28)

distance_text = tk.Label(
    root,
    text="500 units until highway entry",
    font=("Segoe UI", 10),
    fg="#A8B4BF",
    bg="#101820"
)
distance_text.pack(anchor="w", padx=28, pady=(8, 22))


# ---------------- STATUS CARD ----------------

status_card = tk.Frame(
    root,
    bg="#202D35",
    padx=17,
    pady=17
)
status_card.pack(fill="x", padx=26)

status_icon = tk.Label(
    status_card,
    text="✓",
    font=("Segoe UI", 26, "bold"),
    fg="#D8FF52",
    bg="#202D35",
    width=2
)
status_icon.pack(side="left", padx=(0, 12))

status_content = tk.Frame(status_card, bg="#202D35")
status_content.pack(side="left", fill="x", expand=True)

status_title = tk.Label(
    status_content,
    text="ROAD CLEAR",
    font=("Segoe UI", 14, "bold"),
    fg="#D8FF52",
    bg="#202D35"
)
status_title.pack(anchor="w")

status_description = tk.Label(
    status_content,
    text="Continue driving safely. No highway warning yet.",
    font=("Segoe UI", 9),
    fg="#E0E6EA",
    bg="#202D35",
    wraplength=365,
    justify="left"
)
status_description.pack(anchor="w", pady=(5, 0))


# ---------------- MILESTONES ----------------

milestones = tk.Frame(root, bg="#101820")
milestones.pack(fill="x", padx=26, pady=20)

for title, distance, color in [
    ("HIGHWAY WARNING", "300 units", "#FFBE55"),
    ("HIGHWAY ENTRY", "500 units", "#FF7373")
]:
    card = tk.Frame(
        milestones,
        bg="#1B2630",
        padx=12,
        pady=12
    )
    card.pack(side="left", fill="both", expand=True, padx=4)

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 8, "bold"),
        fg=color,
        bg="#1B2630"
    ).pack(anchor="w")

    tk.Label(
        card,
        text=distance,
        font=("Segoe UI", 14, "bold"),
        fg="#FFFFFF",
        bg="#1B2630"
    ).pack(anchor="w", pady=(5, 0))


# ---------------- BUTTONS ----------------

advance_button = tk.Button(
    root,
    text="▶   ADVANCE JOURNEY  +100",
    font=("Segoe UI", 11, "bold"),
    fg="#17251E",
    bg="#D8FF52",
    activebackground="#C5EB3F",
    activeforeground="#17251E",
    relief="flat",
    cursor="hand2",
    pady=13,
    command=advance_journey
)
advance_button.pack(fill="x", padx=26, pady=(0, 10))

reset_button = tk.Button(
    root,
    text="↻   RESET JOURNEY",
    font=("Segoe UI", 10, "bold"),
    fg="#FFFFFF",
    bg="#26333D",
    activebackground="#354550",
    activeforeground="#FFFFFF",
    relief="flat",
    cursor="hand2",
    pady=10,
    command=reset_journey
)
reset_button.pack(fill="x", padx=26)

tk.Label(
    root,
    text="Drive safely • Stay alert • DriveSense prototype",
    font=("Segoe UI", 8),
    fg="#758391",
    bg="#101820"
).pack(pady=(15, 10))


# ---------------- START ----------------

set_highway_mode("NORMAL")
root.after(100, update_display)
root.mainloop()

