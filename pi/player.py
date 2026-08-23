"""
player.py - Audio streaming lifecycle and mpv process supervisor.
"""

import subprocess
from typing import Optional
import config
from display import LCDDisplay
import stations


class RadioPlayer:
    """Owns mpv audio streaming process lifecycle and station switching."""

    def __init__(self, lcd: LCDDisplay):
        self.lcd = lcd
        self.proc: Optional[subprocess.Popen] = None
        self.station_idx: int = -1

    def is_playing(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def has_crashed(self) -> bool:
        """True if playback was expected but the process died unexpectedly."""
        return self.proc is not None and self.proc.poll() is not None

    def stop(self) -> None:
        """Stops active audio stream."""
        if not self.proc:
            return
        self.proc.terminate()
        try:
            self.proc.wait(timeout=config.MPV_PROC_STOP_TIMEOUT)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.proc = None
        self.lcd.set_status("STOPPED")

    def _launch_stream(self, url: str) -> bool:
        try:
            self.proc = subprocess.Popen([
                "mpv",
                "--no-video",
                f"--volume={config.DEFAULT_VOLUME}",
                url
            ])
            return True
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f"[ERROR] Failed to spawn mpv: {e}")
            self.proc = None
            return False

    def handle_crash(self) -> None:
        """Cleans up internal state if mpv died unexpectedly."""
        station = stations.get_station(self.station_idx)
        name = station.name if station else "Unknown"
        print(f"[WARNING] mpv exited unexpectedly while playing: {name}")
        self.proc = None
        self.lcd.set_status("ERROR")

    def tune(self, index: int) -> None:
        """Tunes to a station by index and updates LCD & player state."""
        total = stations.get_total_stations()
        if index < 0 or index >= total:
            return
        if index == self.station_idx and self.is_playing():
            return  # Already playing this preset

        station = stations.get_station(index)
        if not station or not station.resolved_url:
            print(f"[ERROR] No stream URL resolved for index {index}")
            self.lcd.display_station("Station Error", "No Stream URL")
            self.lcd.set_status("ERROR")
            return

        print(f"\n[RADIO] Tuning to [{index + 1}/{total}]: {station.name} ({station.sub})")
        print(f"        Stream: {station.resolved_url}")

        self.stop()
        self.lcd.display_station(station.name, station.sub)

        if not self._launch_stream(station.resolved_url):
            self.lcd.set_status("ERROR")
            return

        self.station_idx = index
        self.lcd.set_status("PLAYING")