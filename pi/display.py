"""
display.py - 1602 LCD Display driver and text formatter.
"""

import time
from typing import TYPE_CHECKING
import config

if TYPE_CHECKING:
    from arduino import ArduinoLink


class LCDDisplay:
    """Manages text formatting and status output to the Arduino 1602 LCD."""

    def __init__(self, arduino_link: "ArduinoLink"):
        self.link = arduino_link

    def write_line(self, line: int, text: str) -> None:
        """Sends a single line to the LCD (strictly bounded to 16 chars)."""
        if line not in (1, 2):
            raise ValueError("LCD only supports line 1 or line 2.")

        # Enforce 16-character width limit
        payload = f"L{line}:{text[:16]}\n"
        self.link.send_raw(payload)
        time.sleep(config.LCD_WRITE_DELAY)

    def display_station(self, name: str, sub: str) -> None:
        """Updates both lines with station metadata."""
        self.write_line(1, name)
        self.write_line(2, sub)

    def show_volume(self, volume: int) -> None:
        """Shows plain volume on L2, e.g. Vol: 85."""
        self.write_line(2, f"Vol: {volume}")

    def set_status(self, status: str) -> None:
        """Sends operational status (PLAYING, STOPPED, ERROR)."""
        self.link.send_raw(f"STATUS:{status.upper()}\n")