"""
config.py - Global constants and configuration for the radio engine.
"""

SERIAL_BAUD_RATE = 9600
SERIAL_READ_TIMEOUT = 1.0
ARDUINO_RESET_WAIT = 2.0      # Seconds to allow bootloader reset
LCD_WRITE_DELAY = 0.05        # Delay between sequential line writes
POLL_INTERVAL = 0.05          # Event loop tick interval
MPV_PROC_STOP_TIMEOUT = 2.0   # Timeout before SIGKILL if mpv hangs
DEFAULT_VOLUME = 85           # Initial playback volume (0-100)