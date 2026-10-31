
import serial
import time

PORT = "COM12"
BAUD_RATE = 115200

try:
    esp32 = serial.Serial(PORT, BAUD_RATE, timeout=1)

    # Allow the ESP32 to restart after serial connection
    time.sleep(2)

    print("Connected to DriveSense ESP32")

    while True:
        command = input(
            "Enter NORMAL, HIGHWAY, or DROWSY (or EXIT): "
        ).strip().upper()

        if command == "EXIT":
            break

        if command in ["NORMAL", "HIGHWAY", "DROWSY"]:
            esp32.write((command + "\n").encode("utf-8"))
            print("Sent:", command)
        else:
            print("Invalid command")

    esp32.close()

except serial.SerialException as error:
    print("Serial connection error:", error)
    print("Check the COM port and close Arduino Serial Monitor.")
