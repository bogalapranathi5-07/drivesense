
import cv2
import mediapipe as mp
import serial
import time
import math
import os
from collections import deque

# ==========================================
# 1. CONFIGURATION
# ==========================================

SERIAL_PORT = "COM12"
BAUD_RATE = 115200

EAR_THRESHOLD = 0.21
CLOSED_SECONDS = 1.5

YAWN_THRESHOLD = 0.60
YAWN_MIN_SECONDS = 1.0
YAWN_COUNT_LIMIT = 3
YAWN_WINDOW_SECONDS = 60

RECOVERY_SECONDS = 2.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHWAY_FILE = os.path.join(BASE_DIR, "highway_mode.txt")

# ==========================================
# 2. CONNECT TO PHYSICAL ESP32
# ==========================================

print(f"Connecting to ESP32 on {SERIAL_PORT}...")

try:
    esp = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        timeout=1,
        write_timeout=2
    )

    # ESP32 may restart when the serial port opens.
    time.sleep(2)
    esp.reset_input_buffer()

    print("Connected to physical ESP32.")

except serial.SerialException as error:
    print("ERROR: Could not connect to ESP32.")
    print(error)
    print("Check the USB cable, COM port, and Serial Monitor.")
    raise SystemExit(1)

# ==========================================
# 3. INITIALIZE MEDIAPIPE AND CAMERA
# ==========================================

face_mesh = None
camera = None

try:
    mp_face_mesh = mp.solutions.face_mesh

    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open laptop camera.")

except Exception as error:
    print("ERROR initializing camera or MediaPipe:", error)

    if face_mesh is not None:
        face_mesh.close()

    esp.close()
    raise SystemExit(1)

# ==========================================
# 4. FACE LANDMARKS
# ==========================================

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

MOUTH = {
    "top": 13,
    "bottom": 14,
    "left": 78,
    "right": 308
}


def distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2
        + (point1.y - point2.y) ** 2
    )


def calculate_ear(landmarks, eye):
    vertical1 = distance(
        landmarks[eye[1]],
        landmarks[eye[5]]
    )

    vertical2 = distance(
        landmarks[eye[2]],
        landmarks[eye[4]]
    )

    horizontal = distance(
        landmarks[eye[0]],
        landmarks[eye[3]]
    )

    if horizontal == 0:
        return 0

    return (vertical1 + vertical2) / (2 * horizontal)


def calculate_mouth_ratio(landmarks):
    vertical = distance(
        landmarks[MOUTH["top"]],
        landmarks[MOUTH["bottom"]]
    )

    horizontal = distance(
        landmarks[MOUTH["left"]],
        landmarks[MOUTH["right"]]
    )

    if horizontal == 0:
        return 0

    return vertical / horizontal


# ==========================================
# 5. DETECTION VARIABLES
# ==========================================

eyes_closed_start = None
eyes_open_start = None
yawn_start = None

yawn_times = deque()

last_state = None

eye_drowsy = False
yawn_drowsy = False
drowsy_alert = False

average_ear = 0.0
mouth_ratio = 0.0

# ==========================================
# 6. MAIN LOOP
# ==========================================

print("DriveSense started.")
print("Press Q in the camera window to quit.")

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read camera frame.")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = face_mesh.process(rgb_frame)
        current_time = time.time()

        eye_drowsy = False
        yawn_drowsy = False
        face_detected = bool(results.multi_face_landmarks)

        if face_detected:
            landmarks = results.multi_face_landmarks[0].landmark

            # ------------------------------
            # Eye closure detection
            # ------------------------------

            left_ear = calculate_ear(landmarks, LEFT_EYE)
            right_ear = calculate_ear(landmarks, RIGHT_EYE)

            average_ear = (left_ear + right_ear) / 2

            if average_ear < EAR_THRESHOLD:
                if eyes_closed_start is None:
                    eyes_closed_start = current_time

                elif (
                    current_time - eyes_closed_start
                    >= CLOSED_SECONDS
                ):
                    eye_drowsy = True
            else:
                eyes_closed_start = None

            # ------------------------------
            # Yawning detection
            # ------------------------------

            mouth_ratio = calculate_mouth_ratio(landmarks)

            if mouth_ratio > YAWN_THRESHOLD:
                if yawn_start is None:
                    yawn_start = current_time

                elif (
                    current_time - yawn_start
                    >= YAWN_MIN_SECONDS
                ):
                    yawn_times.append(current_time)
                    yawn_start = None
            else:
                yawn_start = None

            # ------------------------------
            # Remove old yawns
            # ------------------------------

            while (
                yawn_times
                and current_time - yawn_times[0]
                > YAWN_WINDOW_SECONDS
            ):
                yawn_times.popleft()

            if len(yawn_times) >= YAWN_COUNT_LIMIT:
                yawn_drowsy = True

            # ------------------------------
            # Display measurements
            # ------------------------------

            cv2.putText(
                frame,
                f"EAR: {average_ear:.2f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Yawns: {len(yawn_times)}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

        else:
            eyes_closed_start = None
            eyes_open_start = None
            yawn_start = None
            average_ear = 0.0
            mouth_ratio = 0.0

        # ==================================
        # 7. READ HIGHWAY MODE
        # ==================================

        try:
            with open(HIGHWAY_FILE, "r") as file:
                highway_mode = file.read().strip().upper()

        except FileNotFoundError:
            highway_mode = "NORMAL"

        # ==================================
        # 8. DROWSINESS ALERT AND RECOVERY
        # ==================================

        if eye_drowsy or yawn_drowsy:
            drowsy_alert = True
            eyes_open_start = None

        elif drowsy_alert:
            if face_detected and average_ear >= EAR_THRESHOLD:
                if eyes_open_start is None:
                    eyes_open_start = current_time

                elif (
                    current_time - eyes_open_start
                    >= RECOVERY_SECONDS
                ):
                    drowsy_alert = False
                    eyes_open_start = None
                    yawn_times.clear()
                    print("Drowsiness alert cleared.")
            else:
                eyes_open_start = None

        # ==================================
        # 9. FINAL STATE DECISION
        # ==================================

        if drowsy_alert:
            state = "DROWSY"
        elif highway_mode == "HIGHWAY":
            state = "HIGHWAY"
        else:
            state = "NORMAL"

        # ==================================
        # 10. SEND STATE TO PHYSICAL ESP32
        # ==================================

        if state != last_state:
            try:
                esp.write((state + "\n").encode("utf-8"))
                esp.flush()

                print("Sent to ESP32:", state)
                last_state = state

            except serial.SerialException as error:
                print("ERROR sending state to ESP32:", error)
                break

        # ==================================
        # 11. DISPLAY STATUS
        # ==================================

        if state == "DROWSY":
            status_text = "DROWSINESS ALERT!"
            status_color = (0, 0, 255)

        elif state == "HIGHWAY":
            status_text = "HIGHWAY AHEAD - STAY ALERT"
            status_color = (0, 165, 255)

        else:
            status_text = "SYSTEM NORMAL"
            status_color = (0, 255, 0)

        cv2.putText(
            frame,
            status_text,
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2
        )

        cv2.imshow(
            "DriveSense - Drowsiness Detection",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    if camera is not None:
        camera.release()

    cv2.destroyAllWindows()

    if face_mesh is not None:
        face_mesh.close()

    # Restore normal hardware state when the program exits.
    try:
        esp.write(b"NORMAL\n")
        esp.flush()
        time.sleep(0.1)
    except (serial.SerialException, OSError):
        pass

    esp.close()

    print("DriveSense stopped.")
