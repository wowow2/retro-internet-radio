"""
stations.py - Radio-Browser API Station Resolver
Resolves live stream URLs from Radio-Browser by UUID, with a local disk
cache and guaranteed fallback URLs so the radio never goes silent.
"""

import requests
import json
import os
from dataclasses import dataclass
from typing import List, Optional, Dict

API_SERVERS = [
    "https://de1.api.radio-browser.info/json",
    "https://de2.api.radio-browser.info/json",
    "https://nl1.api.radio-browser.info/json",
    "https://at1.api.radio-browser.info/json",
]

HEADERS = {
    "User-Agent": "RetroInternetRadio/1.0 (RaspberryPi; Canada)"
}

CACHE_FILE = os.path.expanduser("~/.radio_cache.json")


@dataclass
class RadioStation:
    name: str
    sub: str
    uuid: str
    fallback_url: str
    resolved_url: str = ""

STATION_LIST: List[RadioStation] = [
    RadioStation(
        name="CBC Radio One",
        sub="Canada News",
        uuid="e9e2c2ac-1916-4f2e-a7ba-a3669bea3bcd",
        fallback_url="https://cbcradiolive.akamaized.net/hls/live/2041041/ES_R1MED/master.m3u8",
    ),
    RadioStation(
        name="880 CHED",
        sub="Edm News",
        uuid="961eeb59-0601-11e8-ae97-52543be04c81",
        fallback_url="https://corus.leanstream.co/CHEDAM-MP3",
    ),
    RadioStation(
        name="96.3 The Breeze",
        sub="Classic Pop/Piano",
        uuid="962287f2-0601-11e8-ae97-52543be04c81",
        fallback_url="https://stingray.leanstream.co/CKRAFM-MP3",
    ),
    RadioStation(
        name="CKUA Radio",
        sub="Alberta Eclectic",
        uuid="53291f37-699a-11e9-af37-52543be04c81",
        fallback_url="http://ckua.streamon.fm:8000/CKUA-48k.aac",
    ),
    RadioStation(
        name="SONiC 102.9",
        sub="Edmonton AltRock",
        uuid="a7bff7dc-68b1-11e9-af37-52543be04c81",
        fallback_url="http://rogers-hls.leanstream.co/rogers/edm1029.stream/playlist.m3u8",
    ),
    RadioStation(
        name="BBC World News",
        sub="Global Stories",
        uuid="",
        fallback_url="http://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
    ),
    RadioStation(
        name="NPR / WNYC",
        sub="Stories & Ideas",
        uuid="f34ae431-42cd-4ef1-8a24-f4eca8a70cc1",
        fallback_url="https://fm939.wnyc.org/wnycfm",
    ),
    RadioStation(
        name="Lofi Girl",
        sub="Lofi",
        uuid="56b0652e-f920-423e-aee2-5b72dda4da66",
        fallback_url="http://stream.zeno.fm/f3wvbbqmdg8uv",
    ),
]


def _load_cache() -> Dict[str, str]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: Dict[str, str]) -> None:
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except OSError:
        pass


def _fetch_from_api(uuid: str) -> Optional[str]:
    """Tries each mirror in turn, returns the resolved URL or None."""
    for server in API_SERVERS:
        try:
            resp = requests.get(
                f"{server}/stations/byuuid/{uuid}",
                headers=HEADERS,
                timeout=3,
            )
            data = resp.json() if resp.status_code == 200 else None
            if data:
                return data[0]["url_resolved"]
        except (requests.RequestException, ValueError, KeyError):
            continue
    return None


def _resolve_one(station: RadioStation, cache: Dict[str, str]) -> tuple[str, str]:
    """Resolves a single station's URL. Returns (url, source) where
    source is one of 'API', 'CACHE', 'FALLBACK'. Mutates `cache` in
    place when a fresh API result is found."""
    if station.uuid:
        live_url = _fetch_from_api(station.uuid)
        if live_url:
            cache[station.uuid] = live_url
            return live_url, "API"
        if station.uuid in cache:
            return cache[station.uuid], "CACHE"

    return station.fallback_url, "FALLBACK"


def resolve_all_stations() -> None:
    """Resolves live URLs from the API on boot, falling back to
    cache, then to the guaranteed fallback URL."""
    cache = _load_cache()

    print("[SYSTEM] Resolving live station URLs via Radio-Browser API...")
    for station in STATION_LIST:
        station.resolved_url, source = _resolve_one(station, cache)
        print(f"  [{source}] {station.name:<16} -> {station.resolved_url}")

    _save_cache(cache)


def get_station(index: int) -> Optional[RadioStation]:
    if 0 <= index < len(STATION_LIST):
        return STATION_LIST[index]
    return None


def get_total_stations() -> int:
    return len(STATION_LIST)