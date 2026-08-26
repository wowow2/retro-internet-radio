/**
 * radio_controller.ino 
 */

#include <LiquidCrystal.h>

const int PIN_LCD_RS = 7;
const int PIN_LCD_EN = 8;
const int PIN_LCD_D4 = 9;
const int PIN_LCD_D5 = 10;
const int PIN_LCD_D6 = 11;
const int PIN_LCD_D7 = 12;

const int PIN_POT_TUNER = A0;
const int PIN_POT_VOL   = A1;
const int PIN_BTN_STOP  = 2;

const int TOTAL_STATIONS       = 8;
const int ADC_JITTER_DEADBAND  = 6;
const unsigned long TUNE_SETTLE_MS  = 40;
const unsigned long BTN_DEBOUNCE_MS = 20;
const unsigned long VOL_THROTTLE_MS = 30;

LiquidCrystal lcd(PIN_LCD_RS, PIN_LCD_EN, PIN_LCD_D4, PIN_LCD_D5, PIN_LCD_D6, PIN_LCD_D7);

int currentStation = -1;
int lastCommittedStation = -1;
int lastRawTuner = -1;
unsigned long settleStartTime = 0;

int lastCommittedVol = -1;
int lastRawVol = -1;
unsigned long lastVolSend = 0;

bool lastButtonState = HIGH;
unsigned long lastButtonDebounce = 0;

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

void checkVolume() {
  if (millis() - lastVolSend < VOL_THROTTLE_MS) return;
  int raw = analogRead(PIN_POT_VOL);
  if (abs(raw - lastRawVol) > ADC_JITTER_DEADBAND) {
    lastRawVol = raw;
    int vol = map(raw, 0, 1023, 0, 100);
    if (abs(vol - lastCommittedVol) >= 2) {
      Serial.print("VOL:");
      Serial.println(vol);
      lastCommittedVol = vol;
      lastVolSend = millis();
    }
  }
}

void checkButton() {
  int reading = digitalRead(PIN_BTN_STOP);
  if (reading != lastButtonState) {
    lastButtonDebounce = millis();
  }
  if ((millis() - lastButtonDebounce) > BTN_DEBOUNCE_MS) {
    static int confirmedState = HIGH;
    if (reading != confirmedState) {
      confirmedState = reading;
      if (confirmedState == LOW) {
        Serial.println("CMD:TOGGLE");
      }
    }
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
  pinMode(PIN_BTN_STOP, INPUT_PULLUP);

  lcd.begin(16, 2);
  lcd.clear();
  updateLCD(1, "Retro Radio");
  updateLCD(2, "Waiting for Pi..");

  lastRawTuner = analogRead(PIN_POT_TUNER);
  currentStation = map(lastRawTuner, 0, 1024, 0, TOTAL_STATIONS);
  if (currentStation >= TOTAL_STATIONS) currentStation = TOTAL_STATIONS - 1;

  lastRawVol = analogRead(PIN_POT_VOL);
  lastButtonState = digitalRead(PIN_BTN_STOP);
}

void loop() {
  checkSerial();
  checkTuner();
  checkVolume();
  checkButton();
}