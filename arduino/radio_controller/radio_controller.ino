#include <LiquidCrystal.h>


// Pin Assignments
const int PIN_LCD_RS = 7;
const int PIN_LCD_EN = 8;
const int PIN_LCD_D4 = 9;
const int PIN_LCD_D5 = 10;
const int PIN_LCD_D6 = 11;
const int PIN_LCD_D7 = 12;

const int PIN_POT_TUNER = A0;
const int PIN_BTN_CTRL  = 2;

// Tuner Configuration
const int TOTAL_STATIONS           = 8;
const int ADC_MAX_VALUE            = 1023;
const int ADC_JITTER_DEADBAND      = 6;
const unsigned long TUNE_SETTLE_MS = 40;

// Button Timing Configuration
const unsigned long BTN_DEBOUNCE_MS = 35;
const unsigned long HOLD_INITIAL_MS = 700;
const unsigned long HOLD_REPEAT_MS  = 400;

// Volume Configuration
const int VOL_MIN  = 5;
const int VOL_MAX  = 100;
const int VOL_STEP = 5;

// LCD / Serial Line Buffer Configuration
const int LCD_COLS         = 16;
const int LCD_ROWS         = 2;
const int SERIAL_LINE_MAX  = 32;
LiquidCrystal lcd(PIN_LCD_RS, PIN_LCD_EN, PIN_LCD_D4, PIN_LCD_D5, PIN_LCD_D6, PIN_LCD_D7);

// Tuner State
int currentStation      = -1;
int lastCommittedStation = -1;
int lastRawTuner        = -1;
unsigned long settleStartTime = 0;

// Button & Volume State
int currentVol = 100;
bool lastButtonState = HIGH;
bool buttonIsDown     = false;
bool isHolding        = false;
unsigned long btnPressStartTime  = 0;
unsigned long lastButtonDebounce = 0;
unsigned long lastVolStepTime    = 0;

// Serial Line Buffer
char serialLine[SERIAL_LINE_MAX + 1];
uint8_t serialLineLen = 0;


// LCD Helpers
void updateLCD(int line, const char* text) {
  if (line != 1 && line != 2) return;
  char buffer[LCD_COLS + 1];
  snprintf(buffer, sizeof(buffer), "%-*.*s", LCD_COLS, LCD_COLS, text);
  lcd.setCursor(0, line - 1);
  lcd.print(buffer);
}


// Tuner Logic
void checkTuner() {
  int raw = analogRead(PIN_POT_TUNER);

  if (abs(raw - lastRawTuner) > ADC_JITTER_DEADBAND) {
    lastRawTuner = raw;
    int newIdx = map(raw, 0, ADC_MAX_VALUE, 0, TOTAL_STATIONS);
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

// Volume Logic
void cycleVolume() {
  currentVol += VOL_STEP;
  if (currentVol > VOL_MAX) currentVol = VOL_MIN;

  Serial.print("VOL:");
  Serial.println(currentVol);
}

// Button Logic (press / hold-to-repeat / release)
void checkButton() {
  int reading = digitalRead(PIN_BTN_CTRL);
  unsigned long now = millis();

  // Button just pressed down
  if (reading == LOW && lastButtonState == HIGH && (now - lastButtonDebounce > BTN_DEBOUNCE_MS)) {
    btnPressStartTime  = now;
    lastButtonDebounce = now;
    buttonIsDown = true;
    isHolding    = false;
  }

  // Button is currently held down
  if (reading == LOW && buttonIsDown) {
    if (!isHolding && (now - btnPressStartTime >= HOLD_INITIAL_MS)) {
      isHolding = true;
      cycleVolume();
      lastVolStepTime = now;
    } else if (isHolding && (now - lastVolStepTime >= HOLD_REPEAT_MS)) {
      cycleVolume();
      lastVolStepTime = now;
    }
  }

  // Button just released
  if (reading == HIGH && lastButtonState == LOW && (now - lastButtonDebounce > BTN_DEBOUNCE_MS)) {
    lastButtonDebounce = now;

    if (isHolding) {
      Serial.println("VOL:DONE");
    } else {
      Serial.println("CMD:TOGGLE");
    }

    buttonIsDown = false;
    isHolding    = false;
  }

  lastButtonState = reading;
}

// Serial Command Parsing (expects "L1:<text>" / "L2:<text>" lines)
void checkSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (serialLineLen > 0) {
        serialLine[serialLineLen] = '\0';

        if (strncmp(serialLine, "L1:", 3) == 0) {
          updateLCD(1, serialLine + 3);
        } else if (strncmp(serialLine, "L2:", 3) == 0) {
          updateLCD(2, serialLine + 3);
        }

        serialLineLen = 0;
      }
    } else if (serialLineLen < SERIAL_LINE_MAX) {
      serialLine[serialLineLen++] = c;
    }
  }
}

// Setup / Loop
void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN_CTRL, INPUT_PULLUP);

  lcd.begin(LCD_COLS, LCD_ROWS);
  lcd.clear();
  updateLCD(1, "Retro Radio");
  updateLCD(2, "Waiting for Pi..");

  lastRawTuner = analogRead(PIN_POT_TUNER);
  currentStation = map(lastRawTuner, 0, ADC_MAX_VALUE, 0, TOTAL_STATIONS);
  if (currentStation >= TOTAL_STATIONS) currentStation = TOTAL_STATIONS - 1;

  lastButtonState = digitalRead(PIN_BTN_CTRL);
}

void loop() {
  checkSerial();
  checkTuner();
  checkButton();
}