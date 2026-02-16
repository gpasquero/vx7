# VX7 - Virtual DX7 Synthesizer

A Python GUI application that emulates the legendary **Yamaha DX7** FM synthesizer, with authentic aesthetics, 6-operator FM synthesis, original factory presets, and optional MIDI support.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-yellow)

## Features

- **6-Operator FM Synthesis** — Full implementation of the DX7's FM engine with all 32 algorithms
- **32 Factory Presets** — Original ROM1A bank: BRASS, STRINGS, PIANO, E.PIANO, ORGAN, BELLS, and more
- **Authentic DX7 GUI** — Dark brown panel, green LCD display, membrane-style buttons, algorithm diagram
- **16-Voice Polyphony** — With voice stealing, just like the original hardware
- **DX7 Envelopes** — 4-rate/4-level envelope generators per operator with accurate rate-to-time curves
- **LFO** — 6 waveforms (Triangle, Saw Down, Saw Up, Square, Sine, Sample & Hold)
- **Optional MIDI Support** — Auto-detects MIDI devices, fully configurable, works without MIDI
- **Computer Keyboard** — Play notes with your QWERTY keyboard (two octaves mapped)
- **On-Screen Keyboard** — 4-octave clickable piano (C2-C6)
- **Real-Time Audio** — Low-latency output (~5.8ms) via PortAudio

## Requirements

- Python 3.10+ with Tkinter (Tk 8.6+)
- macOS, Linux, or Windows

## Installation

```bash
# Clone the repository
git clone https://github.com/gpasquero/vx7.git
cd vx7

# Install dependencies
pip install -r requirements.txt
```

### macOS (with Homebrew)

```bash
brew install python-tk@3.12
/opt/homebrew/bin/python3.12 -m pip install --break-system-packages numpy sounddevice python-rtmidi
```

## Usage

```bash
python main.py
```

Or on macOS with Homebrew Python:

```bash
/opt/homebrew/bin/python3.12 main.py
```

### Keyboard Mapping

| Keys | Notes |
|------|-------|
| `Z S X D C V G B H N J M` | C3 to B3 (lower octave) |
| `Q 2 W 3 E R 5 T 6 Y 7 U` | C4 to B4 (upper octave) |
| `Up / Down arrows` | Previous / Next preset |
| `Escape` | Quit |

### MIDI

MIDI input is optional. If a MIDI controller is connected, VX7 auto-detects it on startup. If `python-rtmidi` is not installed, the app runs normally with the on-screen and computer keyboards.

## Project Structure

```
vx7/
├── main.py              # Entry point + controller
├── requirements.txt     # Dependencies
├── engine/
│   ├── envelope.py      # DX7 4-rate/4-level envelope generator
│   ├── operator.py      # FM operator with KLS, velocity scaling
│   ├── algorithm.py     # All 32 DX7 algorithms + rendering
│   ├── lfo.py           # LFO with 6 waveforms
│   ├── voice.py         # Single voice (6 ops + LFO + algorithm)
│   └── synth.py         # 16-voice polyphonic synthesizer
├── presets/
│   └── factory.py       # 32 ROM1A factory presets
├── gui/
│   ├── styles.py        # Colors, fonts, dimensions
│   ├── display.py       # LCD display emulation (green glow + scanlines)
│   ├── panel.py         # DX7-style control panel
│   └── app.py           # Main application window
├── audio/
│   └── output.py        # Real-time audio output (sounddevice)
└── midi/
    └── handler.py       # Optional MIDI input handler
```

## Factory Presets (ROM1A)

| # | Name | # | Name | # | Name | # | Name |
|---|------|---|------|---|------|---|------|
| 1 | BRASS 1 | 9 | PIANO 2 | 17 | MARIMBA | 25 | PIPES |
| 2 | BRASS 2 | 10 | PIANO 3 | 18 | KOTO | 26 | HARP 1 |
| 3 | BRASS 3 | 11 | E.PIANO 1 | 19 | FLUTE 1 | 27 | GUITAR 1 |
| 4 | STRINGS 1 | 12 | E.PIANO 2 | 20 | FLUTE 2 | 28 | SYN-LEAD |
| 5 | STRINGS 2 | 13 | E.PIANO 3 | 21 | OBOE | 29 | BASS 1 |
| 6 | STRINGS 3 | 14 | HARPSICH | 22 | TRUMPET | 30 | BASS 2 |
| 7 | ORCHSTRA | 15 | CLAV 1 | 23 | ORGAN 1 | 31 | TUB BELL |
| 8 | PIANO 1 | 16 | VIBE | 24 | ORGAN 2 | 32 | BELLS |

## Status

This project is in **beta**. Known issues:
- GUI layout has overlapping elements in some sections (work in progress)
- Preset parameters are approximations of the original DX7 SysEx data
- Some algorithms may need fine-tuning for accuracy

## License

MIT License

## Acknowledgments

Inspired by the Yamaha DX7 (1983), one of the most influential synthesizers ever made.
