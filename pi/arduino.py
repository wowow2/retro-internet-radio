"""
arduino.py - USB Serial link and auto-reconnection manager.
"""

import glob
import time
from typing import Optional
import serial
import config


class ArduinoLink:
    """Manages the USB Serial connection, discovery, and reading from Arduino."""

    def __init__(self, baud_rate: int = config.SERIAL_BAUD_RATE):
        self.baud_rate = baud_rate
        self.ser: Optional[serial.Serial] = None
        self.connected_port: Optional[str] = None

    @staticmethod
    def discover_port() -> Optional[str]:
        """Scans for available Arduino/TTY USB serial devices."""
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        return ports[0] if ports else None

    @property
    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def connect(self) -> bool:
        """Attempts connection and handles bootloader delay. Returns True on success."""
        port = self.discover_port()
        if not port:
            return False

        try:
            self.ser = serial.Serial(
                port,
                self.baud_rate,
                timeout=config.SERIAL_READ_TIMEOUT
            )
            time.sleep(config.ARDUINO_RESET_WAIT)
            self.connected_port = port
            print(f"[SYSTEM] Arduino connected on {port}")
            return True
        except (serial.SerialException, OSError) as e:
            print(f"[ERROR] Failed to connect to {port}: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> None:
        """Safely closes serial interface."""
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.connected_port = None

    def send_raw(self, message: str) -> bool:
        """Sends an encoded message string over the serial connection."""
        if not self.is_connected or not self.ser:
            return False
        try:
            self.ser.write(message.encode('utf-8'))
            return True
        except (serial.SerialException, OSError):
            print("[WARNING] Write failed. Arduino disconnected.")
            self.disconnect()
            return False

    def read_command(self) -> Optional[str]:
        """Polls for an incoming newline-terminated command string."""
        if not self.is_connected or not self.ser:
            return None
        try:
            if self.ser.in_waiting > 0:
                return self.ser.readline().decode('utf-8', errors='ignore').strip()
        except (serial.SerialException, OSError):
            print("[WARNING] Read failed. Arduino disconnected.")
            self.disconnect()
        return None