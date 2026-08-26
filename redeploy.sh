#!/bin/bash
set -e
cd "$(dirname "$0")"

git fetch origin
git reset --hard origin/master

sudo systemctl stop radio.service
arduino-cli compile --upload -b arduino:avr:uno arduino/radio_controller -p /dev/ttyACM0
sudo systemctl start radio.service