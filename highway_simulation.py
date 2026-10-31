
import os
import tkinter as tk
from tkinter import messagebox

try:
    from winotify import Notification
except ImportError:
    Notification = None


# ---------------- SETTINGS ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHWAY_FILE = os.path.join(BASE_DIR, "highway_mode.txt")

TOTAL_DISTANCE = 900
WARNING_DISTANCE = 300
ENTRY_DISTANCE = 500
STEP_DISTANCE = 100

progress = 0
highway_sent = False


# ---------------- COLORS ----------------

BG = "#101820"
PANEL = "#1B2630"
GREEN = "#D8FF52"
WHITE = "#FFFFFF"
MUTED = "#A8B4BF"
AMBER = "#FFBE55"
RED = "#FF7373"


# ---------------- MODE FILE ----------------

def set_highway_mode(mode):
    try:
        with open(HIGHWAY_FILE, "w", encoding="utf-8") as file:
            file.write(mode)
    except OSError as error:
        messagebox.showerror(
            "DriveSense Error",
            f"Could not update highway mode:\n{error}"
        )


def notify_highway():
    if Notification is not None:
        try:
            Notification(
                app_id="DriveSense",
                title="HIGHWAY ENTRY ALERT",
                msg="Highway entry reached. Stay alert!"
            ).show()
        except Exception:
            pass


# ---------------- DISPLAY UPDATE ----------------

def update_display():
    percentage = int(progress / TOTAL_DISTANCE * 100)

    distance_label.config(text=f"{progress:03d}  /  {TOTAL_DISTANCE} UNITS")
    percentage_label.config(text=f"{percentage}% COMPLETE")

    progress_canvas.delete("all")
    width = progress_canvas.winfo_width()

    if width < 2:
        width = 480

    progress_canvas.create_rectangle(
        0, 0, width, 12,
        fill="#2A3541", outline=""
    )
    progress_canvas.create_rectangle(
        0, 0, width * percentage / 100, 12,
        fill=GREEN, outline=""
    )

    if progress < WARNING_DISTANCE:
        status_title.config(text="ROAD CLEAR", fg=GREEN)
        status_description.config(
            text="Maintain awareness. Drive safely."
        )
        status_tag.config(text="NORMAL ROUTE", fg=GREEN)
        status_card.config(bg=PANEL)
        status_icon.config(text="✓", fg=GREEN)

    elif progress < ENTRY_DISTANCE:
        status_title.config(text="HIGHWAY AHEAD", fg=AMBER)
        status_description.config(
            text="Highway approaching. Prepare and stay alert."
        )
        status_tag.config(text="WARNING ZONE", fg=AMBER)
        status_card.config(bg="#382F24")
        status_icon.config(text="!", fg=AMBER)

    else:
        status_title.config(text="HIGHWAY ENTRY", fg=RED)
        status_description.config(
            text="Highway entry reached. Warning state activated."
        )
        status_tag.config(text="HIGHWAY ALERT", fg=RED)
        status_card.config(bg="#3B272B")
        status_icon.config(text="!", fg=RED)

    remaining = max(0, ENTRY_DISTANCE - progress)

    if remaining > 0:
        remaining_label.config(
            text=f"{remaining} units until highway entry"
        )
    else:
        remaining_label.config(text="Highway entry reached")

    advance_button.config(
        state="normal" if progress < TOTAL_DISTANCE else "disabled"
    )


# ---------------- JOURNEY BUTTONS ----------------

def advance_journey():
    global progress, highway_sent

    if progress >= TOTAL_DISTANCE:
        return

    previous_progress = progress
    progress = min(progress + STEP_DISTANCE, TOTAL_DISTANCE)

    # Activate highway mode when the journey reaches 500 units.
    if previous_progress < ENTRY_DISTANCE <= progress and not highway_sent:
        highway_sent = True
        set_highway_mode("HIGHWAY")
        notify_highway()

        event_label.config(
            text="HIGHWAY ENTRY REACHED — HIGHWAY MODE SENT",
            fg=RED
        )

    elif progress >= WARNING_DISTANCE and not highway_sent:
        event_label.config(
            text="HIGHWAY APPROACHING — STAY ALERT",
            fg=AMBER
        )

    else:
        event_label.config(
            text=f"JOURNEY UPDATED — {progress} UNITS",
            fg=GREEN
        )

    update_display()


def reset_journey():
    global progress, highway_sent

    progress = 0
    highway_sent = False

    set_highway_mode("NORMAL")
    event_label.config(
        text="SYSTEM READY — AWAITING JOURNEY",
        fg=GREEN
    )
    update_display()


def close_app():
    set_highway_mode("NORMAL")
    root.destroy()


# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("DriveSense | Highway Simulator")
root.geometry("560x610")
root.minsize(560, 610)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", close_app)


# ---------------- HEADER ----------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=26, pady=(22, 20))

logo = tk.Label(
    header,
    text="DS",
    font=("Segoe UI", 17, "bold"),
    fg="#17251E",
    bg=GREEN,
    padx=10,
    pady=5
)
logo.pack(side="left", padx=(0, 12))

heading = tk.Frame(header, bg=BG)
heading.pack(side="left")

tk.Label(
    heading,
    text="DriveSense",
    font=("Segoe UI", 21, "bold"),
    fg=WHITE,
    bg=BG
).pack(anchor="w")

tk.Label(
    heading,
    text="HIGHWAY JOURNEY SIMULATOR",
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=BG
).pack(anchor="w", pady=(3, 0))

tk.Label(
    header,
    text="● SYSTEM READY",
    font=("Segoe UI", 9, "bold"),
    fg=GREEN,
    bg=BG
).pack(side="right", anchor="center")


# ---------------- STATUS CARD ----------------

status_card = tk.Frame(root, bg=PANEL, padx=20, pady=18)
status_card.pack(fill="x", padx=26)

status_tag = tk.Label(
    status_card,
    text="NORMAL ROUTE",
    font=("Segoe UI", 9, "bold"),
    fg=GREEN,
    bg=status_card["bg"]
)
status_tag.pack(anchor="w")

status_row = tk.Frame(status_card, bg=status_card["bg"])
status_row.pack(fill="x", pady=(12, 4))

status_icon = tk.Label(
    status_row,
    text="✓",
    font=("Segoe UI", 30, "bold"),
    fg=GREEN,
    bg=status_card["bg"]
)
status_icon.pack(side="left", padx=(0, 12))

status_title = tk.Label(
    status_row,
    text="ROAD CLEAR",
    font=("Segoe UI", 25, "bold"),
    fg=GREEN,
    bg=status_card["bg"]
)
status_title.pack(side="left")

status_description = tk.Label(
    status_card,
    text="Maintain awareness. Drive safely.",
    font=("Segoe UI", 11),
    fg=MUTED,
    bg=status_card["bg"],
    wraplength=460,
    justify="left"
)
status_description.pack(anchor="w", pady=(6, 0))


# ---------------- PROGRESS ----------------

progress_panel = tk.Frame(root, bg=PANEL, padx=18, pady=17)
progress_panel.pack(fill="x", padx=26, pady=16)

progress_header = tk.Frame(progress_panel, bg=PANEL)
progress_header.pack(fill="x")

tk.Label(
    progress_header,
    text="JOURNEY PROGRESS",
    font=("Segoe UI", 10, "bold"),
    fg=WHITE,
    bg=PANEL
).pack(side="left")

percentage_label = tk.Label(
    progress_header,
    text="0% COMPLETE",
    font=("Segoe UI", 9, "bold"),
    fg=GREEN,
    bg=PANEL
)
percentage_label.pack(side="right")

distance_label = tk.Label(
    progress_panel,
    text="000  /  900 UNITS",
    font=("Segoe UI", 24, "bold"),
    fg=WHITE,
    bg=PANEL
)
distance_label.pack(anchor="w", pady=(14, 12))

progress_canvas = tk.Canvas(
    progress_panel,
    height=12,
    bg=PANEL,
    highlightthickness=0
)
progress_canvas.pack(fill="x")

milestones = tk.Frame(progress_panel, bg=PANEL)
milestones.pack(fill="x", pady=(12, 0))

tk.Label(
    milestones,
    text="START",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
).pack(side="left")

tk.Label(
    milestones,
    text="WARNING · 300",
    font=("Segoe UI", 9),
    fg=AMBER,
    bg=PANEL
).pack(side="left", expand=True)

tk.Label(
    milestones,
    text="ENTRY · 500",
    font=("Segoe UI", 9),
    fg=RED,
    bg=PANEL
).pack(side="right")

remaining_label = tk.Label(
    root,
    text="500 units until highway entry",
    font=("Segoe UI", 10),
    fg=MUTED,
    bg=BG
)
remaining_label.pack(anchor="w", padx=28, pady=(0, 14))


# ---------------- BUTTONS ----------------

advance_button = tk.Button(
    root,
    text="▶   ADVANCE JOURNEY  +100",
    font=("Segoe UI", 12, "bold"),
    fg="#17251E",
    bg=GREEN,
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
    fg=WHITE,
    bg="#26333D",
    activebackground="#354550",
    activeforeground=WHITE,
    relief="flat",
    cursor="hand2",
    pady=10,
    command=reset_journey
)
reset_button.pack(fill="x", padx=26)


# ---------------- EVENT MESSAGE ----------------

event_panel = tk.Frame(root, bg=PANEL, padx=14, pady=12)
event_panel.pack(fill="x", padx=26, pady=(15, 0))

tk.Label(
    event_panel,
    text="LATEST SYSTEM EVENT",
    font=("Segoe UI", 9, "bold"),
    fg=MUTED,
    bg=PANEL
).pack(anchor="w")

event_label = tk.Label(
    event_panel,
    text="SYSTEM READY — AWAITING JOURNEY",
    font=("Segoe UI", 9, "bold"),
    fg=GREEN,
    bg=PANEL,
    wraplength=470,
    justify="left"
)
event_label.pack(anchor="w", pady=(8, 0))


# ---------------- START ----------------

set_highway_mode("NORMAL")
root.after(100, update_display)
root.mainloop()
