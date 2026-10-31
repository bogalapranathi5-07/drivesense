# DriveSense: Intelligent Driver Vigilance Monitoring System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%2016x2%20I2C%20LCD%20%7C%20Buzzer-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-orange.svg)]()

> **Educational Demonstration Prototype**: DriveSense is designed for college engineering capstone projects and academic demonstrations. It is not certified for commercial automotive safety or medical diagnosis.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Software Installation & Setup](#3-software-installation--setup)
4. [Running the Application](#4-running-the-application)
5. [Demonstrating Without Hardware (Simulation Mode)](#5-demonstrating-without-hardware-simulation-mode)
6. [Hardware Wiring & Setup Guide](#6-hardware-wiring--setup-guide)
7. [Uploading ESP32 Firmware](#7-uploading-esp32-firmware)
8. [I²C LCD Troubleshooting & Address Detection](#8-ic-lcd-troubleshooting--address-detection)
9. [Event Priority & Protocol Specification](#9-event-priority--protocol-specification)
10. [Troubleshooting & Common Errors](#10-troubleshooting--common-errors)
11. [Hardware vs. Software Feature Matrix](#11-hardware-vs-software-feature-matrix)
12. [Project File Structure](#12-project-file-structure)

---

## 1. Project Overview

**DriveSense** combines computer-vision driver monitoring with an interactive simulated highway environment and real-time physical telemetry via an **ESP32 microcontroller**:

1. **Webcam Driver Vigilance Monitoring**:
   - Uses OpenCV and MediaPipe Face Mesh / FaceLandmarker to detect 478 3D facial landmarks.
   - Computes **Eye Aspect Ratio (EAR)** across both eyes in real time.
   - Detects prolonged eye closure beyond a configurable duration (default 1.5s) and threshold (default 0.22).
   - Triggers instantaneous visual dashboard warnings and non-blocking audible computer alarms (`winsound`).

2. **Simulated Highway Journey**:
   - A native 2.5D perspective road animation running inside the Tkinter desktop GUI without external game engines or internet assets.
   - Simulates transitions from rural/normal roads to approaching ramps, highway merge points (speed limit 80 km/h), and high-speed cruising.
   - Features manual event triggers (`⚡ TRIGGER HIGHWAY ENTRY NOW`) designed specifically for viva/faculty demonstrations.

3. **ESP32 Hardware Telemetry**:
   - Transmits newline-terminated JSON packets across USB-Serial to an ESP32 board.
   - Updates a 16×2 I²C LCD with two-line status alerts.
   - Drives a hardware buzzer using prioritized, non-blocking audio pulse patterns.
   - Built-in safety watchdogs prevent endless buzzing and manage host disconnects safely.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Computer ["Host Laptop (Python 3.10+)"]
        Webcam["Laptop Webcam"] -->|RGB Frames| CV["OpenCV & MediaPipe"]
        CV -->|EAR & Closure Time| Drowsy["Drowsiness Engine"]
        
        Sim["Highway Canvas Engine"] -->|Road Events| EvMgr["Event Manager (Priority Queue)"]
        Drowsy -->|Drowsiness Alert (Pri: 100)| EvMgr
        
        EvMgr -->|Live Updates| GUI["Tkinter Dark Dashboard"]
        EvMgr -->|JSON Packets| Serial["PySerial Manager"]
    end

    subgraph ESP32 ["Embedded System (ESP32 DevKit)"]
        Serial -->|USB Serial @ 115200| InoParser["Arduino C++ JSON Parser"]
        InoParser -->|I2C SDA:21 SCL:22| LCD["16x2 I2C LCD Display"]
        InoParser -->|GPIO 18| Buzzer["Active / Passive Buzzer"]
        InoParser -->|Serial ACK| Serial
    end
```

### Event Priority Hierarchy
| Event Type | Priority Level | LCD Line 1 / Line 2 | Buzzer Pattern | Behavior on Conflict |
| :--- | :---: | :--- | :--- | :--- |
| **Drowsiness Alert** | **100 (Highest)** | `DROWSINESS ALERT`<br>`PULL OVER SAFELY` | Mode 1: Rapid Pulsing Alarm | Immediately preempts all other messages and holds until driver reopens eyes. |
| **Highway Entry** | **50 (Medium)** | `HIGHWAY ENTRY`<br>`STAY ALERT! 80KM` | Mode 2: Double Chime | Triggers warning chime; if drowsiness occurs simultaneously, drowsiness takes the LCD while Highway Entry is logged. |
| **Approaching Ramp** | **30 (Info)** | `APPROACHING HWY`<br>`PREPARE TO MERGE` | Mode 0: Silent | Informs driver of upcoming merge zone. |
| **Normal Status** | **10 (Routine)** | `SYSTEM NORMAL`<br>`DRIVE SAFELY` | Mode 0: Silent | Will NOT overwrite an active warning until warning hold timer (4.0s) has expired. |

---

## 3. Software Installation & Setup

### Prerequisites
- **Operating System**: Windows 10 or 11 (64-bit).
- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
  > *During Python installation, ensure the checkbox **"Add python.exe to PATH"** is selected.*

### Step 1: Open Terminal in Workspace
Open Windows PowerShell or Command Prompt in the project folder:
```powershell
cd "c:\Users\Ruchi Purwar\Downloads\esa_pjt"
```

### Step 2: (Optional but Recommended) Create a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Python Libraries
Run the following command to install all verified dependencies:
```powershell
pip install -r requirements.txt
```

Verify that all packages imported cleanly:
```powershell
python -c "import cv2, mediapipe, serial, PIL; print('All packages ready!')"
```

---

## 4. Running the Application

### Method A: One-Click Windows Launcher (Beginner-Friendly)
Double-click the included batch script:
```text
run_drivesense.bat
```
This launcher automatically verifies your Python environment, installs any missing packages, and launches the dashboard. If an error occurs, it pauses the console so you can view diagnostic logs.

### Method B: Launching via Command Line
```powershell
python main.py
```

---

## 5. Demonstrating Without Hardware (Simulation Mode)

You can present and test the entire project **without connecting any physical microcontroller**:

1. Launch `python main.py`.
2. Look at the top right header: it will indicate `⚡ ESP32: VIRTUAL MODE`.
3. In the right panel under **16×2 I²C LCD Screen Preview**, observe the simulated LCD.
4. **Test Drowsiness Detection**:
   - Click **▶ Start Camera**.
   - Look at the webcam. Close your eyes for ~1.5 seconds.
   - Observe the live EAR meter drop into the red zone.
   - The laptop will emit an audible beep, the status badge turns Red (`⚠ CRITICAL: DROWSINESS WARNING!`), and the simulated LCD displays:
     ```text
     DROWSINESS ALERT
     PULL OVER SAFELY
     ```
   - Reopen your eyes: vigilance is restored and normal status returns.
5. **Test Highway Simulation**:
   - Click **▶ Start Journey**.
   - Watch the animated 2.5D road shift lanes and advance distance.
   - Or, immediately click the amber **⚡ TRIGGER HIGHWAY ENTRY NOW** button.
   - The overhead sign flashes amber, and the simulated LCD updates with a double chime indicator:
     ```text
     HIGHWAY ENTRY
     STAY ALERT! 80KM
     ```
6. **Test Priority Preemption**:
   - Click **⚡ TRIGGER HIGHWAY ENTRY NOW** and close your eyes at the same time.
   - Observe that the drowsiness warning immediately overrides the LCD display, while both events are recorded with exact timestamps in the **Event Log**.

---

## 6. Hardware Wiring & Setup Guide

### Hardware Components
1. **ESP32 DevKit v1** (30-pin or 38-pin).
2. **16×2 Character LCD with I²C Backpack** (PCF8574 chip).
3. **5V Piezo Buzzer** (Active buzzer recommended for direct tone drive).
4. **Micro-USB to USB-A Cable** (Data cable, not power-only).
5. **Jumper Wires & Breadboard**.

---

### ⚠️ Critical Voltage Safety Warning (Read Before Connecting)
> [!CAUTION]
> **ESP32 GPIO pins operate at 3.3V logic and are NOT 5V tolerant!**
> 
> Most 16×2 I²C LCD backpacks require 5V VCC for proper contrast and backlight.
> Many cheap I²C backpacks have onboard pull-up resistors connected directly to VCC (5V). If you connect SDA and SCL directly to the ESP32 while the LCD is powered with 5V, these pull-ups can leak 5V into ESP32 GPIO 21 and 22, potentially damaging your microcontroller over time.

#### Safe Wiring Recommendations:
- **Best Practice**: Use a **3.3V-to-5V bidirectional I²C logic level shifter** between the ESP32 and LCD backpack.
- **Alternative**: Power the LCD module from the ESP32 `3V3` pin first. Many modern PCF8574 backpacks will display clearly if the blue potentiometer on the back is adjusted. If the contrast is sufficient, you can safely connect SDA/SCL directly to GPIO 21/22 without any level shifter!

---

### Wiring Pinout Diagram

| Component Pin | Connect To ESP32 Pin | Wire Color (Suggested) | Notes |
| :--- | :--- | :--- | :--- |
| **LCD GND** | `GND` | Black | Common Ground |
| **LCD VCC** | `VIN` (5V from USB) or `3V3` | Red | See Voltage Warning above |
| **LCD SDA** | `GPIO 21` | Blue / Green | ESP32 Default Hardware I²C SDA |
| **LCD SCL** | `GPIO 22` | Yellow | ESP32 Default Hardware I²C SCL |
| **Buzzer (+)** | `GPIO 18` | Orange | Configurable in firmware & config.py |
| **Buzzer (-)** | `GND` | Black | Common Ground |

```
                 +-----------------------+
                 |     ESP32 DevKit      |
                 |                       |
                 |  [GPIO 21] ------> SDA (16x2 LCD)
                 |  [GPIO 22] ------> SCL (16x2 LCD)
                 |  [GPIO 18] ------> (+) (Buzzer)
                 |  [  GND  ] ------> GND (Common)
                 |  [  VIN  ] ------> VCC (5V from USB)
                 +-----------------------+
```

---

## 7. Uploading ESP32 Firmware

### Step 1: Install Arduino IDE
Download and install [Arduino IDE 2.x](https://www.arduino.cc/en/software).

### Step 2: Install ESP32 Board Package
1. In Arduino IDE, open **File > Preferences**.
2. Add the following URL into **Additional Boards Manager URLs**:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Open **Tools > Board > Boards Manager...**, search for `esp32` by Espressif Systems, and click **Install**.

### Step 3: Install the LiquidCrystal_I2C Library
1. In Arduino IDE, go to **Sketch > Include Library > Manage Libraries...**.
2. Search for `LiquidCrystal I2C` by **Frank de Brabander**.
3. Click **Install**.

### Step 4: Open Sketch and Select Board
1. Open the file [`firmware/drivesense_esp32.ino`](file:///c:/Users/Ruchi%20Purwar/Downloads/esa_pjt/firmware/drivesense_esp32.ino).
2. Go to **Tools > Board > esp32 > DOIT ESP32 DEVKIT V1** (or match your exact board model).
3. Connect your ESP32 to your PC via USB cable.
4. Go to **Tools > Port** and select your ESP32 COM port (e.g., `COM3`, `COM4`).
5. Click **Upload** (arrow icon).
   *(If the IDE gets stuck at `Connecting...`, press and hold the **BOOT** button on the ESP32 until uploading begins).*

---

## 8. I²C LCD Troubleshooting & Address Detection

Most 16×2 I²C backpacks use address `0x27`. Some use `0x3F`.

### How to Verify or Find Your LCD Address:
If your LCD turns on (blue backlight) but does not display letters:
1. Turn the **blue contrast potentiometer** on the back of the backpack with a small screwdriver until characters appear.
2. If text still does not appear, your module may be using address `0x3F`.
3. In [`firmware/drivesense_esp32.ino`](file:///c:/Users/Ruchi%20Purwar/Downloads/esa_pjt/firmware/drivesense_esp32.ino#L45), change:
   ```cpp
   #define LCD_I2C_ADDR 0x3F
   ```
   and re-upload.

---

## 9. Event Priority & Protocol Specification

### Serial Protocol Format
Packets are transmitted as single-line, newline-delimited JSON objects encoded in UTF-8:

```json
{"event": "DROWSINESS", "status": "WARNING", "line1": "DROWSINESS ALERT", "line2": "PULL OVER SAFELY", "buzzer": 1}\n
```

### Protocol Fields:
- `"event"`: String event tag (`DROWSINESS`, `HIGHWAY_ENTRY`, `HIGHWAY_APPROACH`, `STATUS`, `CONNECT`).
- `"status"`: State string (`WARNING`, `INFO`, `NORMAL`).
- `"line1"`: Maximum 16 characters for top row of LCD.
- `"line2"`: Maximum 16 characters for bottom row of LCD.
- `"buzzer"`: Integer buzzer pattern code:
  - `0`: Silent (turn off buzzer).
  - `1`: High-priority rapid pulsation (120ms ON / 80ms OFF).
  - `2`: Highway entry double chime (180ms ON / 120ms OFF / 250ms ON).

---

## 10. Troubleshooting & Common Errors

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **"Could not open camera index 0"** | Camera occupied by Zoom/Teams or blocked by Windows Privacy | Close background video applications. In Windows Settings, enable **Camera access** for desktop apps. Try camera index `1` in the spinbox. |
| **"Serial Connection Error" / COM Port not found** | Missing CH340 or CP2102 USB-to-UART driver | Install the driver for your ESP32's USB chip: [Silicon Labs CP210x](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) or [WCH CH340](http://www.wch-ic.com/downloads/CH341SER_EXE.html). |
| **LCD displays black boxes only** | Contrast potentiometer out of calibration | Gently turn the blue trimpot on the back of the LCD backpack clockwise or counter-clockwise until text is visible. |
| **Buzzer stays on continuously** | Inverted buzzer polarity | Change `#define BUZZER_ACTIVE_HIGH false` in [`drivesense_esp32.ino`](file:///c:/Users/Ruchi%20Purwar/Downloads/esa_pjt/firmware/drivesense_esp32.ino#L51) and re-upload. DriveSense also has an automated 3.5s safety cutoff. |
| **False drowsiness alarms** | Glasses reflection or head tilt causing low EAR | Adjust the **EAR Threshold** slider down slightly (e.g., from `0.22` to `0.20`), or increase the **Alert Duration Trigger** to `2.0s`. |

---

## 11. Hardware vs. Software Feature Matrix

| Feature | Software-Only Mode (No ESP32) | With ESP32 Hardware Connected |
| :--- | :---: | :---: |
| **Webcam Face & Eye Landmark Detection** | ✅ Full Support | ✅ Full Support |
| **Eye Aspect Ratio (EAR) Calculation** | ✅ Full Support | ✅ Full Support |
| **Computer Audible Alert (`winsound`)** | ✅ Full Support | ✅ Full Support |
| **Highway Animation & Milestone Triggers** | ✅ Full Support | ✅ Full Support |
| **Event Priority Preemption System** | ✅ Full Support | ✅ Full Support |
| **Event Log & Diagnostics Console** | ✅ Full Support | ✅ Full Support |
| **Simulated 16×2 LCD Screen Preview** | ✅ Full Support | ✅ Full Support |
| **Physical 16×2 I²C Character LCD** | ❌ Requires ESP32 | ✅ Full Support |
| **Physical External Piezo Buzzer** | ❌ Requires ESP32 | ✅ Full Support |

---

## 12. Project File Structure

```text
DriveSense/
├── main.py                     # Primary desktop application entry point
├── config.py                   # Central system configuration & thresholds
├── requirements.txt            # Python package dependencies
├── run_drivesense.bat          # One-click Windows launch script
├── README.md                   # Complete system documentation & viva guide
├── drivesense/                 # Core Python application package
│   ├── __init__.py             # Package declaration
│   ├── gui.py                  # Tkinter dark dashboard with simulated LCD
│   ├── drowsiness.py           # MediaPipe FaceLandmarker EAR drowsiness engine
│   ├── highway_simulation.py   # 2.5D native canvas highway journey engine
│   ├── serial_manager.py       # PySerial communication & simulation manager
│   ├── event_manager.py        # Priority queue, warning hold timers & LCD sanitizer
│   └── logger.py               # Thread-safe event logger with GUI callbacks
├── firmware/                   # Microcontroller firmware
│   └── drivesense_esp32.ino    # Arduino C++ sketch with non-blocking buzzer & JSON parser
├── models/                     # Offline Computer Vision models
│   └── face_landmarker.task    # Google MediaPipe 478-landmark offline bundle
└── tests/                      # Automated test suite (pytest)
    ├── test_event_manager.py   # Tests priority arbitration & warning hold locks
    ├── test_message_protocol.py# Tests JSON serialization & ESP32 parser
    └── test_drowsiness_logic.py# Tests EAR math & distance algorithms
```

---

## Verification & Automated Tests
To run the automated test suite locally:
```powershell
python -m pytest tests/
```
Output:
```text
tests\test_drowsiness_logic.py ....                                      [ 33%]
tests\test_event_manager.py .....                                        [ 75%]
tests\test_message_protocol.py ...                                       [100%]
============================= 12 passed in 2.25s ==============================
```
