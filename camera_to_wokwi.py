
import cv2
import mediapipe as mp
import serial
import time
import math
import os
from collections import deque

# ---------------- CONFIGURATION ----------------

SERIAL_PORT = "COM12"
BAUD_RATE = 115200

EAR_THRESHOLD = 0.21
EYE_CLOSED_TIME = 1.5

YAWN_THRESHOLD = 0.60
YAWN_MIN_TIME = 1.0
YAWNS_FOR_ALERT = 3
YAWN_WINDOW = 60

RECOVERY_TIME = 2.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHWAY_FILE = os.path.join(BASE_DIR, "highway_mode.txt")

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308


# ---------------- DISTANCE ----------------

def distance(p1, p2):
    return math.hypot(
        p1[0] - p2[0],
        p1[1] - p2[1]
    )


# ---------------- EYE DETECTION ----------------

def eye_aspect_ratio(landmarks, eye_points, width, height):
    points = []

    for index in eye_points:
        points.append((
            int(landmarks[index].x * width),
            int(landmarks[index].y * height)
        ))

    vertical1 = distance(points[1], points[5])
    vertical2 = distance(points[2], points[4])
    horizontal = distance(points[0], points[3])

    if horizontal == 0:
        return 0

    return (vertical1 + vertical2) / (2.0 * horizontal)


# ---------------- MOUTH DETECTION ----------------

def mouth_ratio(landmarks, width, height):
    top = (
        int(landmarks[MOUTH_TOP].x * width),
        int(landmarks[MOUTH_TOP].y * height)
    )

    bottom = (
        int(landmarks[MOUTH_BOTTOM].x * width),
        int(landmarks[MOUTH_BOTTOM].y * height)
    )

    left = (
        int(landmarks[MOUTH_LEFT].x * width),
        int(landmarks[MOUTH_LEFT].y * height)
    )

    right = (
        int(landmarks[MOUTH_RIGHT].x * width),
        int(landmarks[MOUTH_RIGHT].y * height)
    )

    horizontal = distance(left, right)

    if horizontal == 0:
        return 0

    return distance(top, bottom) / horizontal


# ---------------- HIGHWAY MODE ----------------

def read_highway_mode():
    try:
        with open(HIGHWAY_FILE, "r") as file:
            mode = file.read().strip().upper()

        if mode == "HIGHWAY":
            return "HIGHWAY"

    except FileNotFoundError:
        pass
    except OSError as error:
        print("Highway file error:", error)

    return "NORMAL"


# ---------------- MAIN PROGRAM ----------------

def main():
    esp = None
    camera = None
    face_mesh = None

    try:
        print("Connecting to ESP32 on", SERIAL_PORT)

        esp = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=0.1,
            write_timeout=2
        )

        # ESP32 may restart when serial connects
        time.sleep(2)
        esp.reset_input_buffer()

        print("ESP32 connected successfully.")

        def send_state(state):
            if esp is not None and esp.is_open:
                esp.write((state + "\n").encode("utf-8"))
                esp.flush()
                print("ESP32 state:", state)

        send_state("NORMAL")

        # Start laptop camera
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            raise RuntimeError(
                "Camera could not open. Check camera permissions."
            )

        # Initialize MediaPipe FaceMesh
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Detection timers
        eye_closed_start = None
        yawn_start = None
        eyes_open_start = None

        # Yawn tracking
        yawn_times = deque()
        total_yawns = 0

        # Alert state
        drowsy_alert = False
        current_state = ""

        print("Camera started. Press Q to quit.")

        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read camera frame.")
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            now = time.time()
            highway_mode = read_highway_mode()

            eye_closed = False
            yawning = False
            ear = 0.0
            mar = 0.0
            face_detected = False

            # ---------------- FACE LANDMARKS ----------------

            if results.multi_face_landmarks:
                face_detected = True
                landmarks = results.multi_face_landmarks[0].landmark

                left_ear = eye_aspect_ratio(
                    landmarks, LEFT_EYE, width, height
                )

                right_ear = eye_aspect_ratio(
                    landmarks, RIGHT_EYE, width, height
                )

                ear = (left_ear + right_ear) / 2.0
                mar = mouth_ratio(landmarks, width, height)

                eye_closed = ear < EAR_THRESHOLD
                yawning = mar > YAWN_THRESHOLD

            # ---------------- EYE-CLOSURE DETECTION ----------------

            if face_detected and eye_closed:
                eyes_open_start = None

                if eye_closed_start is None:
                    eye_closed_start = now

                elif now - eye_closed_start >= EYE_CLOSED_TIME:
                    drowsy_alert = True

            else:
                eye_closed_start = None

                if face_detected:
                    if eyes_open_start is None:
                        eyes_open_start = now
                else:
                    eyes_open_start = None

            # ---------------- YAWN DETECTION AND COUNTING ----------------

            if face_detected and yawning:
                if yawn_start is None:
                    yawn_start = now

            else:
                if yawn_start is not None:
                    duration = now - yawn_start

                    if duration >= YAWN_MIN_TIME:
                        total_yawns += 1
                        yawn_times.append(now)

                        print(
                            "Yawn detected! Total yawns:",
                            total_yawns
                        )

                    yawn_start = None

            # Remove yawns older than 60 seconds
            while yawn_times and now - yawn_times[0] > YAWN_WINDOW:
                yawn_times.popleft()

            # Three detected yawns within 60 seconds trigger an alert
            if len(yawn_times) >= YAWNS_FOR_ALERT:
                drowsy_alert = True

            # ---------------- ALERT RECOVERY ----------------

            if (
                drowsy_alert
                and eyes_open_start is not None
                and now - eyes_open_start >= RECOVERY_TIME
            ):
                drowsy_alert = False
                yawn_times.clear()

                print("Drowsiness alert cleared after recovery.")

            # ---------------- FINAL SYSTEM STATE ----------------

            if drowsy_alert:
                state = "DROWSY"
            elif highway_mode == "HIGHWAY":
                state = "HIGHWAY"
            else:
                state = "NORMAL"

            if state != current_state:
                send_state(state)
                current_state = state

            # ---------------- CAMERA DISPLAY ----------------

            if state == "DROWSY":
                state_color = (0, 0, 255)
            elif state == "HIGHWAY":
                state_color = (0, 191, 255)
            else:
                state_color = (0, 255, 0)

            cv2.putText(
                frame,
                "DriveSense",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "State: " + state,
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                state_color,
                2
            )

            cv2.putText(
                frame,
                f"EAR: {ear:.2f}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"MAR: {mar:.2f}",
                (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Total yawns: {total_yawns}",
                (20, 165),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Yawns in last 60s: {len(yawn_times)}/3",
                (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Highway mode: " + highway_mode,
                (20, 235),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 191, 255) if highway_mode == "HIGHWAY"
                else (255, 255, 255),
                2
            )

            if not face_detected:
                cv2.putText(
                    frame,
                    "No face detected",
                    (20, 275),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 165, 255),
                    2
                )

            cv2.imshow("DriveSense - Drowsiness Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except serial.SerialException as error:
        print("ESP32 serial connection failed:", error)
        print("Check COM12 and close Arduino Serial Monitor.")

    except Exception as error:
        print("DriveSense error:", error)

    finally:
        if esp is not None and esp.is_open:
            try:
                esp.write(b"NORMAL\n")
                esp.flush()
                time.sleep(0.2)
                esp.close()
            except Exception:
                pass

        if camera is not None:
            camera.release()

        if face_mesh is not None:
            face_mesh.close()

        cv2.destroyAllWindows()
        print("DriveSense stopped.")


if __name__ == "__main__":
    main()
