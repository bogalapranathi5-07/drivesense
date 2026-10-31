
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------------- PIN CONFIGURATION ----------------

#define LCD_SDA 21
#define LCD_SCL 22

#define RED_LED 18
#define GREEN_LED 19
#define BUZZER 23

#define LCD_ADDRESS 0x27

// ---------------- LCD ----------------

LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);

// ---------------- SYSTEM STATE ----------------

String currentState = "NORMAL";

unsigned long previousBuzzerMillis = 0;
bool buzzerOn = false;

const unsigned long HIGHWAY_BEEP_INTERVAL = 500;
const unsigned long DROWSY_BEEP_INTERVAL = 200;

// ---------------- APPLY SYSTEM STATE ----------------

void setState(String newState) {
  currentState = newState;

  // Reset buzzer when changing states
  buzzerOn = false;
  previousBuzzerMillis = millis();
  digitalWrite(BUZZER, LOW);

  if (currentState == "NORMAL") {
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SYSTEM NORMAL");
    lcd.setCursor(0, 1);
    lcd.print("DRIVE SAFELY");
  }

  else if (currentState == "HIGHWAY") {
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("HIGHWAY AHEAD");
    lcd.setCursor(0, 1);
    lcd.print("STAY ALERT!");
  }

  else if (currentState == "DROWSY") {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("DROWSINESS");
    lcd.setCursor(0, 1);
    lcd.print("PULL OVER!");
  }

  Serial.print("STATE:");
  Serial.println(currentState);
}

// ---------------- SETUP ----------------

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(BUZZER, LOW);

  Wire.begin(LCD_SDA, LCD_SCL);

  lcd.init();
  lcd.backlight();
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("DriveSense");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");

  delay(1000);

  setState("NORMAL");

  Serial.println("DriveSense ready");
}

// ---------------- MAIN LOOP ----------------

void loop() {
  // Receive commands from Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();

    if (command == "NORMAL" ||
        command == "HIGHWAY" ||
        command == "DROWSY") {

      // Drowsiness must take priority over highway mode.
      if (command == "DROWSY") {
        if (currentState != "DROWSY") {
          setState("DROWSY");
        }
      }

      else if (command == "HIGHWAY") {
        if (currentState != "DROWSY" &&
            currentState != "HIGHWAY") {
          setState("HIGHWAY");
        }
      }

      else if (command == "NORMAL") {
        if (currentState != "NORMAL") {
          setState("NORMAL");
        }
      }
    }
  }

  // Select the buzzer pattern
  if (currentState == "NORMAL") {
    buzzerOn = false;
    digitalWrite(BUZZER, LOW);
  }

  else {
    unsigned long interval;

    if (currentState == "DROWSY") {
      interval = DROWSY_BEEP_INTERVAL;
    } else {
      interval = HIGHWAY_BEEP_INTERVAL;
    }

    if (millis() - previousBuzzerMillis >= interval) {
      previousBuzzerMillis = millis();

      buzzerOn = !buzzerOn;
      digitalWrite(BUZZER, buzzerOn ? HIGH : LOW);
    }
  }
}
