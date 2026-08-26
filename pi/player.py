"""
player.py - Ultra-Low-Latency mpv process supervisor with instant IPC switching.
"""

import subprocess
import json
import socket
import os
import time
from typing import Optional
import config
from display import LCDDisplay
import stations

MPV_SOCKET = "/tmp/mpv-socket"


class RadioPlayer:
    def __init__(self, lcd: LCDDisplay):
        self.lcd = lcd
        self.proc: Optional[subprocess.Popen] = None
        self.station_idx: int = -1
        self._is_paused: bool = False
        self.volume = config.DEFAULT_VOLUME
        self._overlay_until: float = 0.0
        self._saved_sub: str = ""
        self._overlay_active: bool = False

    def _send_ipc(self, command: list) -> bool:
        """Sends an instant JSON command to running mpv process (<5ms)."""
        if not os.path.exists(MPV_SOCKET):
            return False
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(0.2)
                client.connect(MPV_SOCKET)
                payload = json.dumps({"command": command}) + "\n"
                client.sendall(payload.encode('utf-8'))
            return True
        except Exception:
            return False

    def is_playing(self) -> bool:
        return self.proc is not None and self.proc.poll() is None and not self._is_paused

    def has_crashed(self) -> bool:
        return self.proc is not None and self.proc.poll() is not None

    def stop(self) -> None:
        """Instantly pauses playback via IPC."""
        if self._send_ipc(["set_property", "pause", True]):
            self._is_paused = True
        elif self.proc:
            self.proc.terminate()
            self.proc = None
        self._overlay_active = False
        self.lcd.set_status("STOPPED")

    def _spawn_mpv(self, url: str) -> bool:
        if os.path.exists(MPV_SOCKET):
            try:
                os.remove(MPV_SOCKET)
            except OSError:
                pass

        # Low-latency streaming flags: skips probing delays & optimizes ALSA buffer
        cmd = [
            "mpv",
            "--no-video",
            f"--input-ipc-server={MPV_SOCKET}",
            f"--volume={self.volume}",
            "--ao=alsa",
            "--audio-device=alsa/plughw:Loopback,0,0",
            "--audio-format=s16",
            "--demuxer-lavf-probesize=32768",
            "--demuxer-lavf-analyzeduration=0.2",
            "--cache=yes",
            "--cache-secs=2",
            url
        ]

        try:
            self.proc = subprocess.Popen(cmd)
            self._is_paused = False
            return True
        except Exception as e:
            print(f"[ERROR] Failed to spawn mpv: {e}")
            self.proc = None
            return False

    def _snapshot_sub(self, sub: str) -> None:
        self._saved_sub = sub

    def handle_crash(self) -> None:
        station = stations.get_station(self.station_idx)
        name = station.name if station else "Unknown"
        print(f"[WARNING] Stream connection lost for: {name}")
        self.proc = None
        self._is_paused = False
        self._overlay_active = False
        self.lcd.set_status("ERROR")

    def tune(self, index: int, force: bool = False) -> None:
        total = stations.get_total_stations()
        if index < 0 or index >= total:
            return
        if index == self.station_idx and self.is_playing() and not force:
            return

        station = stations.get_station(index)
        if not station or not station.resolved_url:
            self.lcd.display_station("Station Error", "No Stream URL")
            self._snapshot_sub("No Stream URL")
            self._overlay_active = False
            self.lcd.set_status("ERROR")
            return

        self.lcd.display_station(station.name, station.sub)
        self._snapshot_sub(station.sub)
        self._overlay_active = False
        self.station_idx = index
        self.lcd.set_status("PLAYING")

        if self.proc and self.proc.poll() is None:
            if self._send_ipc(["loadfile", station.resolved_url, "replace"]):
                self._send_ipc(["set_property", "pause", False])
                self._is_paused = False
                return

        # 3. Otherwise spawn fresh mpv
        self._spawn_mpv(station.resolved_url)

    def toggle(self) -> None:
        """play/pause toggle"""
        if self.is_playing():
            self._send_ipc(["set_property", "pause", True])
            self._is_paused = True
            station = stations.get_station(self.station_idx)
            name = station.name if station else "Retro Radio"
            self.lcd.display_station(name, "* Paused *")
            self._snapshot_sub("* Paused *")
            self._overlay_active = False
        else:
            if self.proc and self.proc.poll() is None:
                self._send_ipc(["set_property", "pause", False])
                self._is_paused = False
                station = stations.get_station(self.station_idx)
                if station:
                    self.lcd.display_station(station.name, station.sub)
                    self._snapshot_sub(station.sub)
                    self._overlay_active = False
            else:
                target_idx = self.station_idx if self.station_idx >= 0 else 0
                self.tune(target_idx, force=True)

    def set_volume(self, level: int) -> None:
        """Instantly changes volume over IPC socket without pausing audio."""
        self.volume = max(0, min(100, level))
        self._send_ipc(["set_property", "volume", self.volume])

    def show_volume(self, level: int) -> None:
        """Sets volume and shows plain Vol: <level> on L2 for VOLUME_DISPLAY_TIMEOUT."""
        self.set_volume(level)
        self._overlay_active = True
        self._overlay_until = time.monotonic() + config.VOLUME_DISPLAY_TIMEOUT
        self.lcd.show_volume(self.volume)

    def tick(self) -> None:
        """Restores L2 after volume overlay expires. Call every main loop."""
        if self._overlay_active and time.monotonic() >= self._overlay_until:
            self._overlay_active = False
            if self._is_paused:
                restore = "* Paused *"
            elif self._saved_sub:
                restore = self._saved_sub
            else:
                station = stations.get_station(self.station_idx)
                restore = station.sub if station else "Turn Dial to Tune"
            if self.lcd.link.is_connected:
                self.lcd.write_line(2, restore)