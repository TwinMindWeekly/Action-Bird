# CLAUDE.md - Action Bird

## Project Overview
Action Bird is a Flappy Bird clone with action/RPG elements built with Python and Pygame. The game features power-ups (Laser, Ghost, Giant, Slow), a skin shop, achievements, and a credits economy.

## Tech Stack
- **Language:** Python 3.8+
- **Framework:** Pygame >= 2.5.2
- **Data Storage:** JSON file (`settings.json`) for game state persistence

## Project Structure
```
Flappy Bird/
├── FB.py                  # Main game file (single-file architecture, ~1050 lines)
├── settings.json          # Player save data (high score, credits, skins, volume)
├── stats.txt              # Legacy stats file (unused by current code)
├── requirements.txt       # Python dependencies (pygame)
├── assets/
│   ├── images/            # BG2.png, FB2.png, FB_red.png, FB_blue.png, banner.png
│   └── sounds/            # wing.wav, laser_shot.wav, explosion.wav, music.mp3, etc.
├── BG2.png                # Root-level fallback copies of assets
├── FB2.png
├── *.wav / *.mp3
├── README.md
└── CONTRIBUTING.md
```

## Architecture
Single-file game (`FB.py`) with the following classes:
- **`Game`** — Main game loop, state machine, rendering, input handling, asset loading
- **`Bird`** — Player character sprite with gravity, jumping, ghost/giant modes
- **`Tube`** — Pipe obstacles (static or oscillating when score > 30)
- **`Item`** — Collectible power-ups (LASER, GHOST, SLOW, GIANT)
- **`Laser`** — Projectile fired by bird (key F)
- **`Cloud`** — Background decoration
- **`TrailEffect`** — Fading trail behind bird during power-ups
- **`FloatingText`** — Animated score/combo popup text
- **`Config`** — Global audio settings (volume, BGM toggle)

## Game States
`LOBBY` → `PLAYING` → `GAME_OVER` (with `SETTINGS`, `SHOP`, `ACHIEVEMENTS` accessible from lobby)

## Key Mechanics
- **Controls:** SPACE to jump, F to shoot laser, mouse for all menus
- **Scoring:** +1 per pipe passed, +2 for near miss (< 10px), combo multiplier for consecutive destructions
- **Power-ups:** 5-second duration, 15% spawn chance, 1.5s warning flash before expiry
- **Difficulty scaling:** Tube velocity increases by 0.5 every 10 points; moving pipes appear after score 30
- **Economy:** Score converts to credits (HS) at game over; used to buy skins in shop
- **Skins:** default (free), red (50 HS), blue (75 HS) — uses palette swap fallback if image missing

## How to Run
```bash
pip install -r requirements.txt
python FB.py
```

## Development Notes
- Asset loading has fallback: checks `assets/images/` first, then root directory
- Sound loading is fault-tolerant (silent `except: pass` on load failure)
- `settings.json` stores all persistent data (high score, credits, unlocked skins, volume settings)
- The game uses pixel-per-pixel color replacement for skin recoloring (`PixelArray`)
- Screen shake effect on pipe destruction (random offset for 10-15 frames)
- Dynamic music volume increases 20% during active power-ups
- Comments in codebase are in Vietnamese

## Constants (tuning)
- Window: 400x600, 60 FPS
- Gravity: 0.4, Jump: -7
- Tube gap: 180px, Tube width: 60px
- Initial tube velocity: 3 (increases over time)
