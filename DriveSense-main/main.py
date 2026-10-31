"""
DriveSense: Intelligent Driver Vigilance Monitoring System
Main Application Entry Point

To launch:
    python main.py
Or run:
    run_drivesense.bat
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add current workspace directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_VERSION
from drivesense.gui import DriveSenseDashboard
from drivesense.logger import logger


def main():
    """Application startup function."""
    try:
        # Check Tkinter availability
        root = tk.Tk()
    except Exception as e:
        print(f"FATAL ERROR: Could not initialize Tkinter graphical environment: {e}")
        print("Please ensure you are running on a machine with desktop display support.")
        sys.exit(1)

    try:
        # Create dashboard
        app = DriveSenseDashboard(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nDriveSense terminated by user (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"Unhandled runtime exception: {e}")
        messagebox.showerror(
            "DriveSense Runtime Error",
            f"An unexpected error occurred:\n\n{e}\n\nPlease check the console log for details."
        )


if __name__ == "__main__":
    main()
