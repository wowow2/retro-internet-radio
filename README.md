# Retro Internet Radio

A internet radio built into a 3D-printed enclosure. A
tuning knob and push button on the front panel control an Arduino, which
talks to a Raspberry Pi over USB serial. The Pi resolves live stream URLs
via the [Radio-Browser](https://www.radio-browser.info/) API and plays
audio through `mpv`, with a 1602 character LCD showing the current station.

## Features

- **Analog tuning**: turn a potentiometer to sweep through 8 preset stations
- **Play/pause button**: short press toggles playback; press-and-hold cycles volume
- **1602 LCD**: shows station name/genre, playback status, and a temporary volume readout
- **Resilient stream resolution**: live lookup via Radio-Browser API (4 mirror
  servers), falling back to a guaranteed static stream URL if the API is
  unreachable
- **Instant station switching**: a persistent `mpv` process is controlled over
  a local IPC socket, so changing stations doesn't require restarting playback
- **Auto-reconnect**: the Pi daemon detects Arduino disconnects/reconnects
  without needing a restart
- **3D-printed enclosure**: full OpenSCAD source for the case, back lid, and
  button plunger

## Hardware

| Component                                         | Notes                                        |
|---------------------------------------------------|----------------------------------------------|
| Raspberry Pi (any USB-serial capable model)       | Runs the Python daemon                       |
| Arduino Uno                                       | Front-panel controller                       |
| 1602 character LCD (parallel, HD44780-compatible) | Status display                               |
| Potentiometer                                     | Station tuning dial                          |
| Momentary push button                             | Play/pause + volume                          |
| USB speaker or USB sound card + speaker           | Audio output                                 |
| USB hub                                           | Connects Arduino + audio device to the Pi    |
| Prototype Shield                                  | Allows Arduino to supply power to components |

## Software architecture

```
 Potentiometer -\
 Push Button    ---> Arduino (radio_controller.ino)
 1602 LCD       -/            |
                          USB Serial
                               |
                               v
                      Raspberry Pi (Python daemon)
                               |
                               v
                    mpv (audio playback engine)
                               |
                               v
              Radio-Browser API  -->  fallback URLs
```
he Arduino only handles raw hardware: reading the pot, debouncing the
button, and writing text lines to the LCD. All playback logic such as which
station is active, volume level, error state lives in the Python daemon
on the Pi. The two sides talk over a simple newline-terminated text
protocol at 115200 baud:

| Direction    | Message          | Meaning                                       |
|--------------|------------------|-----------------------------------------------|
| Arduino → Pi | `STATION:<0-7>`  | Tuning dial settled on a new station          |
| Arduino → Pi | `CMD:TOGGLE`     | Button was pressed and released (short press) |
| Arduino → Pi | `VOL:<0-100>`    | Volume step while button is held              |
| Arduino → Pi | `VOL:DONE`       | Button released after a hold                  |
| Pi → Arduino | `L1:<text>`      | Set LCD line 1 (max 16 chars)                 |
| Pi → Arduino | `L2:<text>`      | Set LCD line 2 (max 16 chars)                 |
| Pi → Arduino | `STATUS:<STATE>` | Informational only (PLAYING/STOPPED/ERROR)    |

### File overview

| File                   | Purpose                                                   |
|------------------------|-----------------------------------------------------------|
| `radio_controller.ino` | Arduino firmware — pot/button reading, LCD driver         |
| `main.py`              | Daemon entrypoint and event loop                          |
| `arduino.py`           | Serial discovery, connection, and read/write handling     |
| `display.py`           | Wire-protocol formatter for LCD text                      |
| `player.py`            | `mpv` process supervisor with IPC-based instant switching |
| `stations.py`          | Station list and live URL resolution                      |
| `config.py`            | Shared constants                                          |
| `*.scad`               | OpenSCAD source for the 3D-printed enclosure              |

## Enclosure

The case is designed in OpenSCAD and split into three printable parts:

- `front_body.scad`: main shell with speaker cutout, LCD window, and
  mounting standoffs for the Pi, Arduino, and USB hub
- `back_lid.scad`: snap-fit rear panel with a USB-C power cutout and
  ventilation slots
- `button_plunger.scad`: small part that transfers a front-panel button
  press to an internal microswitch

Open `assembly.scad` in OpenSCAD to preview all three parts together.
Dimensions (box size, wall thickness, hole positions) are centralized in
`config.scad`.

## License

See [LICENSE](LICENSE).