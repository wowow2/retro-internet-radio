"""
config.py - Global constants and configuration for the radio engine.
"""

SERIAL_BAUD_RATE = 115200
SERIAL_READ_TIMEOUT = 1.0
ARDUINO_RESET_WAIT = 2.0      # Seconds to allow bootloader reset
LCD_WRITE_DELAY = 0.05        # Delay between sequential line writes
POLL_INTERVAL = 0.02          # Event loop tick interval (20ms, was 50ms, reduces button/knob latency)
MPV_PROC_STOP_TIMEOUT = 2.0   # Timeout before SIGKILL if mpv hangs
DEFAULT_VOLUME = 40          # Initial playback volume (0-100)
VOLUME_DISPLAY_TIMEOUT = 1.5  # Seconds to show volume on L2 before restoring station info