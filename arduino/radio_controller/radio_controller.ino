#include <LiquidCrystal.h>

// LCD Pins
const int PIN_LCD_RS = 7;
const int PIN_LCD_EN = 8;
const int PIN_LCD_D4 = 9;
const int PIN_LCD_D5 = 10;
const int PIN_LCD_D6 = 11;
const int PIN_LCD_D7 = 12;

// Control Pins
const int PIN_POT_TUNER = A0;
const int PIN_BTN_CTRL  = 2;

// Tuner Configuration
const int TOTAL_STATIONS          = 8;
const int ADC_JITTER_DEADBAND     = 6;
const unsigned long TUNE_SETTLE_MS = 40;

// Button Timing Configuration
const unsigned long BTN_DEBOUNCE_MS   = 25;
const unsigned long HOLD_INITIAL_MS   = 600; // Hold time before volume cycling starts
const unsigned long HOLD_REPEAT_MS    = 450; // Speed of volume cycling while held

LiquidCrystal lcd(PIN_LCD_RS, PIN_LCD_EN, PIN_LCD_D4, PIN_LCD_D5, PIN_LCD_D6, PIN_LCD_D7);

// Tuner State
int currentStation = -1;
int lastCommittedStation = -1;
int lastRawTuner = -1;
unsigned long settleStartTime = 0;

// Button & Volume State
int currentVol = 100;
bool lastButtonState = HIGH;
unsigned long btnPressStartTime = 0;
unsigned long lastButtonDebounce = 0;
unsigned long lastVolStepTime = 0;
bool isHolding = false;

String serialBuffer = "";

void updateLCD(int line, String text) {
  if (line != 1 && line != 2) return;
  char buffer[17];
  snprintf(buffer, sizeof(buffer), "%-16.16s", text.c_str());
  lcd.setCursor(0, line - 1);
  lcd.print(buffer);
}

void checkTuner() {
  int raw = analogRead(PIN_POT_TUNER);
  if (abs(raw - lastRawTuner) > ADC_JITTER_DEADBAND) {
    lastRawTuner = raw;
    int newIdx = map(raw, 0, 1024, 0, TOTAL_STATIONS);
    if (newIdx >= TOTAL_STATIONS) newIdx = TOTAL_STATIONS - 1;

    if (newIdx != currentStation) {
      currentStation = newIdx;
      settleStartTime = millis();
    }
  }

  if (currentStation != -1 && (millis() - settleStartTime >= TUNE_SETTLE_MS)) {
    if (currentStation != lastCommittedStation) {
      Serial.print("STATION:");
      Serial.println(currentStation);
      lastCommittedStation = currentStation;
    }
  }
}

void cycleVolume() {
  currentVol += 20;
  if (currentVol > 100) currentVol = 20;

  Serial.print("VOL:");
  Serial.println(currentVol);
}

void checkButton() {
  int reading = digitalRead(PIN_BTN_CTRL);

  // Button just pressed down
  if (reading == LOW && lastButtonState == HIGH && (millis() - lastButtonDebounce > BTN_DEBOUNCE_MS)) {
    btnPressStartTime = millis();
    lastButtonDebounce = millis();
    isHolding = false;
  }

  // Button is currently held down
  if (reading == LOW && btnPressStartTime > 0) {
    if (!isHolding && (millis() - btnPressStartTime >= HOLD_INITIAL_MS)) {
      isHolding = true;
      cycleVolume();
      lastVolStepTime = millis();
    } else if (isHolding && (millis() - lastVolStepTime >= HOLD_REPEAT_MS)) {
      cycleVolume();
      lastVolStepTime = millis();
    }
  }

  // Button just released
  if (reading == HIGH && lastButtonState == LOW && (millis() - lastButtonDebounce > BTN_DEBOUNCE_MS)) {
    lastButtonDebounce = millis();
    if (!isHolding && (millis() - btnPressStartTime >= BTN_DEBOUNCE_MS)) {
      Serial.println("CMD:TOGGLE");
    }
    btnPressStartTime = 0;
    isHolding = false;
  }

  lastButtonState = reading;
}

void checkSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        if (serialBuffer.startsWith("L1:")) {
          updateLCD(1, serialBuffer.substring(3));
        } else if (serialBuffer.startsWith("L2:")) {
          updateLCD(2, serialBuffer.substring(3));
        }
        serialBuffer = "";
      }
    } else {
      if (serialBuffer.length() < 32) {
        serialBuffer += c;
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN_CTRL, INPUT_PULLUP);

  lcd.begin(16, 2);
  lcd.clear();
  updateLCD(1, "Retro Radio");
  updateLCD(2, "Waiting for Pi..");

  lastRawTuner = analogRead(PIN_POT_TUNER);
  currentStation = map(lastRawTuner, 0, 1024, 0, TOTAL_STATIONS);
  if (currentStation >= TOTAL_STATIONS) currentStation = TOTAL_STATIONS - 1;

  lastButtonState = digitalRead(PIN_BTN_CTRL);
}

void loop() {
  checkSerial();
  checkTuner();
  checkButton();
}