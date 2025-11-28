# Pac-Man Clone 🟡👻

A fun, from-scratch Pac-Man clone written in Python using **Pygame**.

This project recreates the classic arcade experience with smooth gameplay, original-like ghosts AI (with a bit of personality), power pellets, score tracking, lives, and that satisfying "waka-waka" sound.



<img width="891" height="487" alt="Image" src="https://github.com/user-attachments/assets/1e7e278a-88af-4a9f-b803-f8f27744d551" />

<img width="895" height="989" alt="Image" src="https://github.com/user-attachments/assets/2b51f853-69a4-4c14-933c-b5198c6d1590" />




- Classic Pac-Man gameplay on the original maze layout
- Four unique ghosts with distinct behaviors:
  - Blinky (red) – chases Pac-Man directly
  - Pinky (pink) – ambushes ahead of Pac-Man
  - Inky (cyan) – complex flanking using Blinky’s position
  - Clyde (orange) – sometimes chases, sometimes runs home
  - Scary (Blue) - no idea I'm just making this up
- Scatter and Chase modes + Frightened (blue) mode when eating power pellets
- Power pellet effects, fruit bonuses, and increasing difficulty
- Score, high score, lives, and ready/start screens
- Authentic sound effects and music (optional toggle)
- Clean, well-commented code – perfect for learning game development or AI logic or just goofing around

## Requirements

- Python 3.8+
- Pygame 2.x

## Installation & Running

```bash
# Clone the repository
git clone https://github.com/yourusername/pacman-clone.git
cd pacman-clone

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
pip install pygame

# Run the game!
python main.py

**
Controls

Arrow keys – Move Pac-Man (Up, Down, Left, Right)
ESC – Quit the game
P – Pause / unpause
M – Toggle sound on/off
F12 - 5x pacman speed for testing


