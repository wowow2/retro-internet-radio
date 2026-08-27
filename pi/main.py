"""
main.py - Main entrypoint for the Retro Internet Radio daemon.
"""

import sys
import time
from arduino import ArduinoLink
from display import LCDDisplay
from player import RadioPlayer
import stations
import config


def main():
    print("========================================")
    print("      RETRO INTERNET RADIO DAEMON       ")
    print("========================================")

    # Resolve live stream URLs from API / Cache / Fallback
    stations.resolve_all_stations()

    # Instantiate components
    arduino = ArduinoLink()
    lcd = LCDDisplay(arduino)
    player = RadioPlayer(lcd)

    print("\n[SYSTEM] Ready. Waiting for Arduino USB connection...")

    while True:
        # Auto-reconnection handler
        if not arduino.is_connected:
            if arduino.connect():
                lcd.display_station("Radio Ready!", "Turn Dial to Tune")
                lcd.set_status("STOPPED")

        # Process serial commands from Arduino front panel (drain all queued lines per tick)
        if arduino.is_connected:
            pending_vol = None
            vol_done = False

            while True:
                cmd = arduino.read_command()
                if not cmd:
                    break

                if cmd.startswith("STATION:"):
                    try:
                        idx = int(cmd.split(":")[1])
                        player.tune(idx)
                    except (ValueError, IndexError):
                        pass

                elif cmd == "VOL:DONE":
                    pending_vol = None
                    vol_done = True

                elif cmd.startswith("VOL:"):
                    try:
                        pending_vol = int(cmd.split(":")[1])
                    except (ValueError, IndexError):
                        pass

                elif cmd in ("CMD:STOP", "CMD:TOGGLE"):
                    player.toggle()

            if pending_vol is not None:
                player.show_volume(pending_vol)
            elif vol_done:
                player.restore_subtitle()

        # Supervision check
        if player.has_crashed():
            player.handle_crash()

        time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutting down radio...")
        sys.exit(0)