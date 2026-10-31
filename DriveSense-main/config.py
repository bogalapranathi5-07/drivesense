"""
DriveSense Configuration Module
Centralized settings for Driver Vigilance Monitoring, Highway Simulation,
ESP32 Hardware Serial Protocol, and Event Priority.
"""

from dataclasses import dataclass
from typing import Dict, Any

# ==============================================================================
# 1. APPLICATION & SYSTEM CONSTANTS
# ==============================================================================
APP_TITLE = "DriveSense: Intelligent Driver Vigilance Monitoring System"
APP_SUBTITLE = "Webcam Drowsiness Detection & Highway Simulation with ESP32 Telemetry"
APP_VERSION = "1.0.0"
APP_DISCLAIMER = "EDUCATIONAL PROTOTYPE ONLY - NOT A CERTIFIED MEDICAL OR AUTOMOTIVE SAFETY DEVICE"

# UI Theme Colors (Modern Dark Dashboard)
THEME = {
    "bg_dark": "#121418",          # Main window background
    "bg_card": "#1c2128",          # Cards / Panels background
    "bg_input": "#252c37",         # Inputs and canvas background
    "text_primary": "#f0f6fc",     # Primary text (off-white)
    "text_secondary": "#8b949e",   # Secondary text (slate gray)
    "accent_blue": "#388bfd",      # Primary accent
    "accent_cyan": "#39c5cf",      # Telemetry accent
    "status_normal": "#2ea043",    # Green for safe/normal
    "status_warning": "#d29922",   # Yellow/amber for attention
    "status_alert": "#f85149",     # Red for drowsiness alarm
    "status_inactive": "#484f58",  # Inactive / disconnected gray
    "lcd_bg": "#1f3b20",           # LCD screen backlight dark green
    "lcd_fg": "#5af75a",           # LCD dot-matrix glowing green text
    "lcd_border": "#0d1a0e",       # LCD bezel
}

# ==============================================================================
# 2. DROWSINESS DETECTION SETTINGS
# ==============================================================================
# Eye Aspect Ratio (EAR) default threshold
# Below this value, the eye is classified as closed
DEFAULT_EAR_THRESHOLD = 0.22
MIN_EAR_THRESHOLD = 0.15
MAX_EAR_THRESHOLD = 0.35

# Duration of eye closure (in seconds) before triggering drowsiness alert
DEFAULT_EYE_CLOSED_SECONDS = 1.5
MIN_EYE_CLOSED_SECONDS = 0.5
MAX_EYE_CLOSED_SECONDS = 4.0

# Cooldown period (in seconds) after alert trigger to prevent alert spam
ALERT_COOLDOWN_SECONDS = 3.0

# Camera stream parameters
DEFAULT_CAMERA_INDEX = 0
CAMERA_FRAME_WIDTH = 640
CAMERA_FRAME_HEIGHT = 480
CAMERA_FPS_TARGET = 30

# MediaPipe Face Mesh Landmark Indices for Left and Right Eyes
# Standard 6-point EAR calculation landmarks:
# Right eye: [outer_corner, upper_1, upper_2, inner_corner, lower_2, lower_1]
RIGHT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
# Left eye: [outer_corner, upper_1, upper_2, inner_corner, lower_2, lower_1]
LEFT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]

# Audio alert parameters (Windows native winsound)
AUDIO_ALERT_ENABLED = True
AUDIO_ALERT_FREQUENCY = 1600   # Hz
AUDIO_ALERT_DURATION_MS = 500  # Milliseconds

# ==============================================================================
# 3. HIGHWAY SIMULATION SETTINGS
# ==============================================================================
# Road canvas dimensions
SIM_CANVAS_WIDTH = 380
SIM_CANVAS_HEIGHT = 380

# Simulation speed parameters
DEFAULT_SIM_SPEED = 1.0        # Multiplier (1.0 = standard speed)
MIN_SIM_SPEED = 0.5
MAX_SIM_SPEED = 2.5
SIM_FPS = 30                   # Animation refresh rate (frames per second)

# Journey stage distances (in arbitrary journey progress units)
STAGE_APPROACH_DISTANCE = 300  # Approaching highway ramp
STAGE_ENTRY_DISTANCE = 500     # Highway entry point
JOURNEY_TOTAL_DISTANCE = 900   # Completed highway loop

# ==============================================================================
# 4. EVENT PRIORITY DEFINITIONS
# ==============================================================================
# Higher number = higher priority
PRIORITY_DROWSINESS = 100      # Highest: Critical life safety
PRIORITY_HIGHWAY_ENTRY = 50    # Medium: Roadway navigation event
PRIORITY_STATUS_NORMAL = 10    # Low: Routine telemetry

# How long a high-priority warning message stays locked before returning to normal
WARNING_DISPLAY_HOLD_SECONDS = 4.0

# ==============================================================================
# 5. SERIAL COMMUNICATION PROTOCOL (ESP32)
# ==============================================================================
DEFAULT_BAUD_RATE = 115200
AVAILABLE_BAUD_RATES = [9600, 19200, 38400, 57600, 115200]
SERIAL_READ_TIMEOUT = 0.1      # Non-blocking read timeout (seconds)
SERIAL_RECONNECT_DELAY = 2.0   # Delay between reconnect attempts

# Serial message templates (16x2 LCD max width per line is 16 chars)
LCD_MAX_CHARS_PER_LINE = 16

MESSAGE_TEMPLATES = {
    "DROWSINESS": {
        "event": "DROWSINESS",
        "status": "WARNING",
        "line1": "DROWSINESS ALERT",
        "line2": "PULL OVER SAFELY",
        "buzzer": 1            # Buzzer mode 1: Rapid alarm pattern
    },
    "HIGHWAY_ENTRY": {
        "event": "HIGHWAY_ENTRY",
        "status": "WARNING",
        "line1": "HIGHWAY ENTRY",
        "line2": "STAY ALERT! 80KM",
        "buzzer": 2            # Buzzer mode 2: Double alert chime
    },
    "APPROACHING": {
        "event": "HIGHWAY_APPROACH",
        "status": "INFO",
        "line1": "APPROACHING HWY",
        "line2": "PREPARE TO MERGE",
        "buzzer": 0            # Buzzer mode 0: Silent
    },
    "NORMAL": {
        "event": "STATUS",
        "status": "NORMAL",
        "line1": "SYSTEM NORMAL",
        "line2": "DRIVE SAFELY",
        "buzzer": 0
    },
    "NO_FACE": {
        "event": "STATUS",
        "status": "NORMAL",
        "line1": "MONITORING...",
        "line2": "NO FACE DETECTED",
        "buzzer": 0
    },
    "CONNECT_TEST": {
        "event": "TEST",
        "status": "INFO",
        "line1": "DRIVESENSE LINK",
        "line2": "ESP32 CONNECTED",
        "buzzer": 0
    }
}

# ==============================================================================
# 6. ESP32 HARDWARE PIN DEFINITIONS (FOR FIRMWARE COMPILATION)
# ==============================================================================
# Documented standard default pinout for ESP32 DevKit v1
ESP32_PIN_CONFIG = {
    "I2C_SDA": 21,             # Standard default SDA for ESP32
    "I2C_SCL": 22,             # Standard default SCL for ESP32
    "BUZZER_PIN": 18,          # Active / Passive Buzzer GPIO pin
    "BUZZER_ACTIVE_HIGH": True,# True = HIGH is ON, False = LOW is ON
    "LCD_I2C_ADDR": 0x27,      # Most PCF8574 backpacks use 0x27 (or 0x3F)
    "LCD_COLS": 16,
    "LCD_ROWS": 2
}
