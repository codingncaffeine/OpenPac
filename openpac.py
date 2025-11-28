import pygame
import sys
import json
import os
import random

pygame.init()
pygame.joystick.init()

# Constants
TILE = 32
WIDTH, HEIGHT = 28, 31
SCREEN_WIDTH = WIDTH * TILE
SCREEN_HEIGHT = HEIGHT * TILE
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

class Controls:
    def __init__(self):
        self.kb = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 
                   'menu': pygame.K_ESCAPE, 'select': pygame.K_RETURN, 'scores': pygame.K_END}
        self.gp = {'up': 11, 'down': 12, 'left': 13, 'right': 14, 'menu': 6, 'select': 0, 'scores': 7}
        if os.path.exists('controls.json'):
            try:
                with open('controls.json', 'r') as f:
                    d = json.load(f)
                    self.kb = d.get('keyboard', self.kb)
                    self.gp = d.get('gamepad', self.gp)
            except: pass

class HighScores:
    def __init__(self):
        self.scores = []
        if os.path.exists('highscores.json'):
            try:
                with open('highscores.json', 'r') as f:
                    self.scores = json.load(f)
            except: pass
    
    def add(self, initials, score):
        self.scores.append({'initials': initials, 'score': score})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        with open('highscores.json', 'w') as f:
            json.dump(self.scores, f)
    
    def get_high(self):
        return self.scores[0]['score'] if self.scores else 0

## Base maze templates - classic Pac-Man style corridors
## These provide the fundamental corridor structure, then we modify details per level
BASE_MAZES = [
    # Maze 0 - Classic layout (no dead ends)
    [
        "############################",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#o####.#####.##.#####.####o#",
        "#.####.#####.##.#####.####.#",
        "#..........................#",
        "#.####.##.########.##.####.#",
        "#.####.##.########.##.####.#",
        "#......##....##....##......#",
        "######.##### ## #####.######",
        "     #.##### ## #####.#     ",
        "     #.##          ##.#     ",
        "     #.## ###--### ##.#     ",
        "######.## #      # ##.######",
        "TTTTTT.   #      #   .TTTTTT",
        "######.## #      # ##.######",
        "     #.## ######## ##.#     ",
        "     #.##          ##.#     ",
        "     #.## ######## ##.#     ",
        "######.## ######## ##.######",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#.####.#####.##.#####.####.#",
        "#o..##.......  .......##..o#",
        "###.##.##.########.##.##.###",
        "#......##.########.##......#",
        "#.######.....##.....######.#",
        "#.######.###.##.###.######.#",
        "#........###.##.###........#",
        "#..........................#",
        "############################",
    ],
    # Maze 1 - More open center (no dead ends)
    [
        "############################",
        "#..........................#",
        "#.####.####..##..####.####.#",
        "#o####.####..##..####.####o#",
        "#..........................#",
        "#.####.##.########.##.####.#",
        "#......##.########.##......#",
        "#.####.##....##....##.####.#",
        "#.####.##### ## #####.####.#",
        "######.##### ## #####.######",
        "     #.##          ##.#     ",
        "     #.##          ##.#     ",
        "     #.## ###--### ##.#     ",
        "######.## #      # ##.######",
        "TTTTTT.   #      #   .TTTTTT",
        "######.## #      # ##.######",
        "     #.## ######## ##.#     ",
        "     #.##          ##.#     ",
        "######.## ######## ##.######",
        "#......## ######## ##......#",
        "#.####.......  .......####.#",
        "#.####.#####.##.#####.####.#",
        "#......#####.##.#####......#",
        "#o####.......  .......####o#",
        "#.####.##.########.##.####.#",
        "#......##.########.##......#",
        "#.####.##....##....##.####.#",
        "#.####.#####.##.#####.####.#",
        "#......#####.##.#####......#",
        "#..........................#",
        "############################",
    ],
    # Maze 2 - Symmetric corridors (no dead ends)
    [
        "############################",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#o####.#####.##.#####.####o#",
        "#..........................#",
        "#.####.##.########.##.####.#",
        "#......##....##....##......#",
        "#.####.##.##.##.##.##.####.#",
        "#.####.##.##.##.##.##.####.#",
        "######.##.## ## ##.##.######",
        "     #.##.##    ##.##.#     ",
        "     #.##          ##.#     ",
        "     #.## ###--### ##.#     ",
        "######.## #      # ##.######",
        "TTTTTT.   #      #   .TTTTTT",
        "######.## #      # ##.######",
        "     #.## ######## ##.#     ",
        "     #.##          ##.#     ",
        "     #.##.##    ##.##.#     ",
        "######.##.## ## ##.##.######",
        "#......##.##.##.##.##......#",
        "#.####.##.##.##.##.##.####.#",
        "#.####.##....##....##.####.#",
        "#o..##.......  .......##..o#",
        "#...##.##.########.##.##...#",
        "#......##.########.##......#",
        "#.####.##....##....##.####.#",
        "#.####.#####.##.#####.####.#",
        "#......#####.##.#####......#",
        "#..........................#",
        "############################",
    ],
    # Maze 3 - Open grid (no dead ends)
    [
        "############################",
        "#..........................#",
        "#.####.####..##..####.####.#",
        "#o####.####..##..####.####o#",
        "#..........................#",
        "#.####.####..##..####.####.#",
        "#......####..##..####......#",
        "#.####.......##.......####.#",
        "#.####.##### ## #####.####.#",
        "######.##### ## #####.######",
        "     #.##          ##.#     ",
        "     #.##          ##.#     ",
        "     #.## ###--### ##.#     ",
        "######.## #      # ##.######",
        "TTTTTT.   #      #   .TTTTTT",
        "######.## #      # ##.######",
        "     #.## ######## ##.#     ",
        "     #.##          ##.#     ",
        "     #.## ######## ##.#     ",
        "######.## ######## ##.######",
        "#..........................#",
        "#.####.####..##..####.####.#",
        "#.####.####..##..####.####.#",
        "#o.........  ..  .........o#",
        "#.####.####..##..####.####.#",
        "#......####..##..####......#",
        "#.####.......##.......####.#",
        "#.####.#####.##.#####.####.#",
        "#......#####.##.#####......#",
        "#..........................#",
        "############################",
    ],
]

def generate_maze(level):
    """Generate a unique maze based on level number. Uses base templates with variations."""
    rng = random.Random(level)  # Seeded RNG for reproducibility
    
    # Select base maze template (cycle through them)
    base_idx = level % len(BASE_MAZES)
    maze = [list(row) for row in BASE_MAZES[base_idx]]
    
    # Ensure proper dimensions
    while len(maze) < HEIGHT:
        maze.append(list('#' * WIDTH))
    for i in range(len(maze)):
        while len(maze[i]) < WIDTH:
            maze[i].append('#')
    
    # The base mazes are carefully designed with no dead ends
    # We avoid random modifications that could create dead ends or trap ghosts
    # Instead, variation comes from cycling through different base mazes
    # and the difficulty scaling (ghost speed, frightened duration, etc.)
    
    # Ensure critical paths are always open
    # Ghost house door
    maze[12][13] = '-'
    maze[12][14] = '-'
    
    # Ghost house interior
    for y in range(13, 16):
        for x in range(11, 17):
            maze[y][x] = ' '
        maze[y][10] = '#'
        maze[y][17] = '#'
    maze[16][10:18] = list('########')
    
    # Tunnel row
    for x in range(0, 6):
        maze[14][x] = 'T'
    for x in range(22, 28):
        maze[14][x] = 'T'
    # Path to tunnels
    maze[14][6] = '.'
    maze[14][7] = '.'
    maze[14][8] = '.'
    maze[14][9] = '.'
    maze[14][18] = '.'
    maze[14][19] = '.'
    maze[14][20] = '.'
    maze[14][21] = '.'
    
    # Spawn area must be clear
    for x in range(11, 17):
        if maze[23][x] not in ' -':
            maze[23][x] = '.'
    
    # Note: Power pellets are already in the base maze templates (marked with 'o')
    # No need to add more - the templates have them in the corners
    
    # Convert to strings
    return [''.join(row) for row in maze]


class Player:
    def __init__(self, x, y, img_path):
        self.x = x
        self.y = y
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.speed = 2
        self.base_speed = 2
        self.speed_test = False  # F12 toggle for 5x speed
        self.img = None
        # Animation frames for each direction
        self.frames_right = []
        self.frames_left = []
        self.frames_up = []
        self.frames_down = []
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 8  # frames between animation changes
        
        try:
            # Load both animation frames
            img_dir = os.path.dirname(img_path)
            img1 = pygame.image.load(img_path).convert_alpha()
            base_img1 = pygame.transform.smoothscale(img1, (TILE-4, TILE-4))
            
            # Try to load second frame
            img_path2 = img_path.replace('.png', '2.png').replace('.gif', '2.png')
            try:
                img2 = pygame.image.load(img_path2).convert_alpha()
                base_img2 = pygame.transform.smoothscale(img2, (TILE-4, TILE-4))
            except:
                base_img2 = base_img1  # fallback to same image
            
            self.img = base_img1
            # Create rotated versions for each direction for both frames
            self.frames_right = [base_img1, base_img2]
            self.frames_left = [pygame.transform.flip(base_img1, True, False),
                               pygame.transform.flip(base_img2, True, False)]
            self.frames_up = [pygame.transform.rotate(base_img1, 90),
                             pygame.transform.rotate(base_img2, 90)]
            self.frames_down = [pygame.transform.rotate(base_img1, -90),
                               pygame.transform.rotate(base_img2, -90)]
        except Exception as e:
            self.img = None
    
    def update(self, maze):
        tile_center_x = (int(self.x) // TILE) * TILE + TILE // 2
        tile_center_y = (int(self.y) // TILE) * TILE + TILE // 2
        
        # Try next direction first
        nx = self.x + self.next_dir[0] * self.speed
        ny = self.y + self.next_dir[1] * self.speed
        if not self.collides(nx, ny, maze):
            # If changing direction, snap to grid ONLY if close to tile center
            if self.next_dir != self.dir:
                if self.next_dir[0] != 0:  # Turning to horizontal, snap Y
                    self.y = tile_center_y
                else:  # Turning to vertical, snap X
                    self.x = tile_center_x
            self.dir = self.next_dir
        
        # Move current direction
        nx = self.x + self.dir[0] * self.speed
        ny = self.y + self.dir[1] * self.speed
        if not self.collides(nx, ny, maze):
            self.x, self.y = nx, ny
        
        # Always keep centered on the perpendicular axis while moving
        # This prevents drifting within the wider tunnel paths
        if self.dir[0] != 0:  # Moving horizontally, force Y to tile center
            self.y = tile_center_y
        elif self.dir[1] != 0:  # Moving vertically, force X to tile center
            self.x = tile_center_x
        
        # Wrap through tunnel
        if self.x < -TILE//2:
            self.x = SCREEN_WIDTH - TILE//2
        elif self.x > SCREEN_WIDTH - TILE//2:
            self.x = -TILE//2 + 1
    
    def collides(self, x, y, maze):
        # Check if the new position would collide
        # Use 7-pixel offset for a slightly forgiving hitbox
        for dx, dy in [(-7,-7), (7,-7), (-7,7), (7,7)]:
            tx = int((x + dx) // TILE)
            ty = int((y + dy) // TILE)
            # Allow wrapping through tunnel (out of bounds horizontally is OK)
            if tx < 0 or tx >= len(maze[0]):
                continue  # Allow horizontal out of bounds (tunnel)
            if 0 <= ty < len(maze) and 0 <= tx < len(maze[0]):
                cell = maze[ty][tx]
                if cell == '#':
                    return True
                # T = tunnel, passable
            elif ty < 0 or ty >= len(maze):
                return True  # Vertical out of bounds is a wall
        return False
    
    def draw(self, screen):
        if self.img and self.frames_right:
            # Update animation timer
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(self.frames_right)
            
            # Choose frame list based on direction
            if self.dir == (1, 0):  # right
                frames = self.frames_right
            elif self.dir == (-1, 0):  # left
                frames = self.frames_left
            elif self.dir == (0, -1):  # up
                frames = self.frames_up
            elif self.dir == (0, 1):  # down
                frames = self.frames_down
            else:
                frames = self.frames_right  # default
            
            img_to_draw = frames[self.anim_frame] if frames else self.img
            screen.blit(img_to_draw, (self.x-TILE//2+2, self.y-TILE//2+2))
        else:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), TILE//2-2)

class Ghost:
    def __init__(self, x, y, img_path, idx):
        self.x = x
        self.y = y
        self.dir = (0, -1)  # Start moving up toward the door
        self.speed = 1.5
        self.idx = idx
        self.mode = 'house'
        # Release ghosts within 5 seconds: first ghost at 1s, last at 5s
        self.release_timer = int(FPS * (1 + idx))  # 60, 120, 180, 240, 300 frames
        # frightened/eaten state
        self.frightened_timer = 0
        self.eaten = False
        self.base_speed = self.speed
        self.frightened_img = None
        try:
            img = pygame.image.load(img_path).convert_alpha()
            self.img = pygame.transform.smoothscale(img, (TILE-4, TILE-4))
            # Create a blue/inverted "frightened" version of the ghost image
            try:
                fright_img = self.img.copy()
                # Apply blue tint by manipulating pixels
                w, h = fright_img.get_size()
                for px in range(w):
                    for py in range(h):
                        r, g, b, a = fright_img.get_at((px, py))
                        # Convert to grayscale then tint blue
                        gray = int(0.3 * r + 0.59 * g + 0.11 * b)
                        fright_img.set_at((px, py), (max(0, gray - 50), max(0, gray - 50), min(255, gray + 100), a))
                self.frightened_img = fright_img
            except Exception:
                pass
        except Exception as e:
            colors = [(255,0,0), (255,184,255), (0,255,255), (255,184,82), (0,255,0)]
            self.img = None
            self.color = colors[idx % 5]
        # ensure a base color is always available (even if image loaded)
        try:
            colors
        except NameError:
            colors = [(255,0,0), (255,184,255), (0,255,255), (255,184,82), (0,255,0)]
        if not hasattr(self, 'color'):
            self.color = colors[idx % 5]
        self.base_color = self.color
    
    def update(self, maze, player_pos):
        # Safety check: if ghost is inside house but in active/frightened mode, switch to leaving
        tx, ty = int(self.x // TILE), int(self.y // TILE)
        if self.mode in ('active', 'frightened') and 12 <= ty <= 16 and 10 <= tx <= 17:
            self.mode = 'leaving'
            
        if self.mode == 'house':
            self.release_timer -= 1
            if self.release_timer <= 0:
                # Time to leave the house - move up toward the door
                self.mode = 'leaving'
                self.dir = (0, -1)  # Move up
            return

        if self.mode == 'leaving':
            # Move to center of door (between columns 13-14), then up and out
            # Door is at row 12, columns 13-14 (the '--' tiles)
            # Row 11 is the open space above the ghost house
            door_x = TILE * 13 + TILE  # center between cols 13-14 (pixel 448)
            row_11_center = TILE * 11 + TILE // 2  # center of row 11 (open corridor)
            
            # Safety: ensure ghost is within house bounds (columns 11-16)
            # If somehow outside, snap to door_x
            house_left = TILE * 11
            house_right = TILE * 17
            if self.x < house_left or self.x > house_right:
                self.x = door_x
            
            # Step 1: Move horizontally to align with door center (while staying at current Y)
            if abs(self.x - door_x) > self.speed:
                if self.x < door_x:
                    self.x += self.speed
                else:
                    self.x -= self.speed
                return  # Don't move up yet
            
            # Snap to door X position
            self.x = door_x
            
            # Step 2: Move up through the door and into row 11
            if self.y > row_11_center:
                self.y -= self.speed
            else:
                # We're out! Snap to row 11 center and become active
                self.y = row_11_center
                self.mode = 'active'
                # Give them a random starting direction (left or right)
                self.dir = random.choice([(-1, 0), (1, 0)])
            return

        # frightened timer handling
        if self.mode == 'frightened':
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = 'active'
                self.speed = self.base_speed

        tx, ty = int(self.x // TILE), int(self.y // TILE)
        aligned = abs(self.x - tx * TILE - TILE//2) < 3 and abs(self.y - ty * TILE - TILE//2) < 3

        if aligned:
            dirs = []
            for d in [(0,-1), (0,1), (-1,0), (1,0)]:
                if d != (-self.dir[0], -self.dir[1]):
                    nx = self.x + d[0] * TILE
                    ny = self.y + d[1] * TILE
                    ntx, nty = int(nx // TILE), int(ny // TILE)
                    
                    # Prevent ghosts from going back into the ghost house area
                    # Ghost house is rows 12-16, columns 10-17
                    if 12 <= nty <= 16 and 10 <= ntx <= 17:
                        continue  # Skip this direction - it leads into the house
                    
                    # Allow tunnel wrapping - if going off edge horizontally, it's valid
                    if ntx < 0 or ntx >= len(maze[0]):
                        dirs.append(d)  # Tunnel wrap is always valid
                    elif not self.collides(nx, ny, maze):
                        dirs.append(d)
            
            if dirs:
                if self.mode == 'frightened':
                    # frightened ghosts move randomly and slower
                    self.speed = max(0.8, self.base_speed * 0.6)
                    self.dir = random.choice(dirs)
                else:
                    if random.random() < 0.7:
                        dx = player_pos[0] - self.x
                        dy = player_pos[1] - self.y
                        if abs(dx) > abs(dy):
                            pref = (1 if dx > 0 else -1, 0)
                        else:
                            pref = (0, 1 if dy > 0 else -1)
                        if pref in dirs:
                            self.dir = pref
                        else:
                            self.dir = random.choice(dirs)
                    else:
                        self.dir = random.choice(dirs)
        
        nx = self.x + self.dir[0] * self.speed
        ny = self.y + self.dir[1] * self.speed
        ntx, nty = int(nx // TILE), int(ny // TILE)
        
        # Prevent active/frightened ghosts from moving into ghost house
        can_move = True
        if self.mode in ('active', 'frightened'):
            if 12 <= nty <= 16 and 10 <= ntx <= 17:
                can_move = False  # Don't move into the house
        
        if can_move and not self.collides(nx, ny, maze):
            self.x, self.y = nx, ny
        
        # Wrap through tunnel
        if self.x < -TILE//2:
            self.x = SCREEN_WIDTH - TILE//2
        elif self.x > SCREEN_WIDTH - TILE//2:
            self.x = -TILE//2 + 1
        
        # Slow down in tunnel (when in T tiles on either edge)
        tx = int(self.x // TILE)
        if tx < 6 or tx >= 22:  # Tunnel area on edges
            self.speed = self.base_speed * 0.5
        elif self.mode != 'frightened':
            self.speed = self.base_speed
    
    def collides(self, x, y, maze):
        tx, ty = int(x // TILE), int(y // TILE)
        # Allow horizontal out of bounds (tunnel wrapping)
        if tx < 0 or tx >= len(maze[0]):
            return False
        if 0 <= ty < len(maze) and 0 <= tx < len(maze[0]):
            cell = maze[ty][tx]
            # Allow ghosts to pass through door tiles ('-') and tunnel ('T')
            if cell in ('-', 'T', ' '):
                return False
            return cell == '#'
        return True
    
    def draw(self, screen):
        if self.img:
            # Use frightened image if available and in frightened mode
            if self.mode == 'frightened' and self.frightened_img:
                screen.blit(self.frightened_img, (self.x-TILE//2+2, self.y-TILE//2+2))
            else:
                screen.blit(self.img, (self.x-TILE//2+2, self.y-TILE//2+2))
        else:
            draw_color = (0, 0, 255) if getattr(self, 'mode', None) == 'frightened' else self.color
            pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), TILE//2-2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Open-Pac")
        self.clock = pygame.time.Clock()
        self.controls = Controls()
        self.hs = HighScores()
        self.state = 'MENU'
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
        self.level = 0
        self.lives = 3
        self.initials = ""
        self.ready_timer = 0  # Timer for READY state auto-continue
        self.high_scores_timer = 0  # Timer for HIGH_SCORES auto-return to menu
        self.frightened_duration = 15 * FPS  # Default, will be adjusted per level
        self.death_timer = 0  # Timer for death animation
        self.death_spin_angle = 0  # Rotation angle during death
        self.flash_timer = 0  # Timer for flashing power pellets
        # assets directory (where sounds/images live)
        self.assets_dir = os.path.dirname(os.path.abspath(__file__))
        # init mixer and load sounds (best-effort)
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.snd_chomp = None
        self.snd_power = None
        self.snd_eatghost = None
        try:
            self.snd_chomp = pygame.mixer.Sound(os.path.join(self.assets_dir, 'chomp.mp3'))
            self.snd_chomp.set_volume(1.3)  # Boost volume by 30%
        except Exception:
            pass
        try:
            self.snd_power = pygame.mixer.Sound(os.path.join(self.assets_dir, 'powerpellet.mp3'))
        except Exception:
            # try alternate names
            try:
                self.snd_power = pygame.mixer.Sound(os.path.join(self.assets_dir, 'power.mp3'))
            except Exception:
                self.snd_power = None
        try:
            self.snd_eatghost = pygame.mixer.Sound(os.path.join(self.assets_dir, 'ghosteatin.mp3'))
        except Exception:
            self.snd_eatghost = None
        try:
            self.snd_death = pygame.mixer.Sound(os.path.join(self.assets_dir, 'pacman_death.mp3'))
        except Exception:
            self.snd_death = None
        
        # Background music tracking
        self.playing_power_music = False

        # Load logo image
        try:
            self.logo_img = pygame.image.load(os.path.join(self.assets_dir, 'openpac_logo.png')).convert_alpha()
        except Exception:
            self.logo_img = None

        # Load arcade font
        self.arcade_font_path = os.path.join(self.assets_dir, 'arcade.ttf')
        try:
            self.arcade_font = pygame.font.Font(self.arcade_font_path, 24)
            self.arcade_font_large = pygame.font.Font(self.arcade_font_path, 48)
            self.arcade_font_small = pygame.font.Font(self.arcade_font_path, 18)
        except Exception:
            self.arcade_font = pygame.font.Font(None, 36)
            self.arcade_font_large = pygame.font.Font(None, 72)
            self.arcade_font_small = pygame.font.Font(None, 28)

        # Load fruit images and setup fruit system
        self.fruit_types = ['cherry', 'apple', 'strawberry', 'orange', 'grapes']
        self.fruit_points = {'cherry': 300, 'apple': 500, 'strawberry': 700, 'orange': 1000, 'grapes': 1500}
        self.fruit_images = {}
        for fruit in self.fruit_types:
            try:
                img = pygame.image.load(os.path.join(self.assets_dir, f'{fruit}.png')).convert_alpha()
                self.fruit_images[fruit] = pygame.transform.smoothscale(img, (TILE-4, TILE-4))
            except Exception:
                self.fruit_images[fruit] = None
        
        # Fruit state
        self.fruit_active = None  # Current fruit type or None
        self.fruit_timer = 0  # Timer for fruit visibility
        self.fruit_cooldown = 0  # Cooldown before next fruit can appear (90 seconds = 5400 frames)
        self.fruit_x = TILE * 14 + TILE // 2  # Center of maze (column 14)
        self.fruit_y = TILE * 17 + TILE // 2  # Below ghost house (row 17)

        # music file (intro)
        self.intro_music = os.path.join(self.assets_dir, 'intro.mp3')
        self.reset_level()
    
    def reset_level(self):
        # Generate unique maze for this level (procedural generation)
        self.maze = [list(row) for row in generate_maze(self.level)]
        img_dir = r"D:\python games\openpac"
        # Find a valid open tile for Pac-Man to start (preferably row 23, col 14)
        pac_start_x, pac_start_y = 14, 23
        found = False
        for y in range(20, HEIGHT):
            if self.maze[y][pac_start_x] in (' ', '.', 'o'):
                pac_start_y = y
                found = True
                break
        if not found:
            # Fallback: find any open tile
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.maze[y][x] in (' ', '.', 'o'):
                        pac_start_x, pac_start_y = x, y
                        found = True
                        break
                if found:
                    break
        self.player = Player(TILE * pac_start_x + TILE // 2, TILE * pac_start_y + TILE // 2, os.path.join(img_dir, 'thepac.png'))
        self.player.next_dir = (0, -1)  # Force movement up at spawn
        # Ghosts start in the house spread across rows 13-14
        # Ghost house interior is columns 11-16, rows 13-15, door at columns 13-14 row 12
        ghost_positions = [
            (13, 13),  # Ghost 0: center, near door (first to exit)
            (14, 13),  # Ghost 1: center right, near door
            (12, 14),  # Ghost 2: left side, middle row
            (15, 14),  # Ghost 3: right side, middle row
            (13, 14),  # Ghost 4: center, middle row
        ]
        self.ghosts = []
        for i in range(5):
            gx, gy = ghost_positions[i]
            ghost = Ghost(TILE * gx + TILE // 2, TILE * gy + TILE // 2, os.path.join(img_dir, f'ghost{i+1}.png'), i)
            self.ghosts.append(ghost)
        
        # Difficulty scaling based on level
        # Ghost speed increases slightly each level (caps at level 20)
        speed_bonus = min(self.level * 0.05, 1.0)  # Max +1.0 speed at level 20
        # Ghost release time decreases each level
        release_multiplier = max(0.3, 1.0 - self.level * 0.03)  # Min 30% of original at level ~23
        # Frightened duration decreases each level (min 5 seconds)
        self.frightened_duration = max(5 * FPS, int((15 - self.level * 0.5) * FPS))
        
        for g in self.ghosts:
            g.base_speed = 1.5 + speed_bonus
            g.speed = g.base_speed
            g.release_timer = int(g.release_timer * release_multiplier)
        
        self.score = getattr(self, 'score', 0)
        # Reset fruit state for new level
        self.fruit_active = None
        self.fruit_timer = 0
        self.fruit_cooldown = random.randint(5 * FPS, 15 * FPS)  # First fruit appears 5-15 seconds into level

    def reset_positions_only(self):
        """Reset player position only without resetting ghosts or maze."""
        img_dir = r"D:\python games\openpac"
        # Find valid spawn for Pac-Man - use fixed position row 23, col 14
        pac_start_x, pac_start_y = 14, 23
        found = False
        for y in range(20, HEIGHT):
            if self.maze[y][pac_start_x] in (' ', '.', 'o'):
                pac_start_y = y
                found = True
                break
        if not found:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.maze[y][x] in (' ', '.', 'o'):
                        pac_start_x, pac_start_y = x, y
                        found = True
                        break
                if found:
                    break
        self.player = Player(TILE * pac_start_x + TILE // 2, TILE * pac_start_y + TILE // 2, os.path.join(img_dir, 'thepac.png'))
        self.player.next_dir = (0, -1)
        # Don't reset ghost positions - just clear frightened mode
        for ghost in self.ghosts:
            ghost.mode = 'active'
            ghost.frightened_timer = 0
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Also check arrow keys in addition to configured bindings
        try:
            up_pressed = keys[self.controls.kb['up']] or keys[pygame.K_UP]
            down_pressed = keys[self.controls.kb['down']] or keys[pygame.K_DOWN]
            left_pressed = keys[self.controls.kb['left']] or keys[pygame.K_LEFT]
            right_pressed = keys[self.controls.kb['right']] or keys[pygame.K_RIGHT]
        except Exception:
            up_pressed = keys[self.controls.kb['up']]
            down_pressed = keys[self.controls.kb['down']]
            left_pressed = keys[self.controls.kb['left']]
            right_pressed = keys[self.controls.kb['right']]
        # Handle movement FIRST, every frame
        if self.state == 'PLAYING':
            moved = False
            # Prefer up/down/left/right state computed above (includes arrows)
            if up_pressed:
                self.player.next_dir = (0, -1)
                moved = True
            elif down_pressed:
                self.player.next_dir = (0, 1)
                moved = True
            elif left_pressed:
                self.player.next_dir = (-1, 0)
                moved = True
            elif right_pressed:
                self.player.next_dir = (1, 0)
                moved = True
            
            if moved:
                pass  # Movement registered
            
            if self.joystick:
                hat = self.joystick.get_hat(0)
                if hat[1] == 1:
                    self.player.next_dir = (0, -1)
                elif hat[1] == -1:
                    self.player.next_dir = (0, 1)
                elif hat[0] == -1:
                    self.player.next_dir = (-1, 0)
                elif hat[0] == 1:
                    self.player.next_dir = (1, 0)
        
        # Then handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if self.state == 'ENTER_INITIALS':
                    if e.key == pygame.K_RETURN and len(self.initials) > 0:
                        self.hs.add(self.initials.upper(), self.score)
                        self.state = 'HIGH_SCORES'
                        self.high_scores_timer = FPS * 5  # Show for 5 seconds then return to menu
                    elif e.key == pygame.K_BACKSPACE:
                        self.initials = self.initials[:-1]
                    elif e.unicode.isalpha() and len(self.initials) < 3:
                        self.initials += e.unicode
                else:
                    # Global/GUI keys
                    if e.key == self.controls.kb['scores']:
                        self.state = 'HIGH_SCORES'
                    elif e.key == self.controls.kb['menu']:
                        if self.state == 'PLAYING':
                            self.state = 'MENU'
                        elif self.state in ['HIGH_SCORES', 'GAME_OVER']:
                            self.state = 'MENU'
                    elif e.key == self.controls.kb['select']:
                        if self.state == 'MENU':
                            self.level = 0
                            self.lives = 3
                            self.score = 0
                            self.reset_level()
                            # Play intro music if available
                            try:
                                if os.path.exists(self.intro_music):
                                    pygame.mixer.music.load(self.intro_music)
                                    pygame.mixer.music.play(-1)
                            except Exception:
                                pass
                            self.state = 'PLAYING'
                        elif self.state == 'READY':
                            self.state = 'PLAYING'
                        elif self.state == 'LEVEL_COMPLETE':
                            self.level += 1
                            self.reset_level()
                            self.state = 'PLAYING'
                    # Immediate movement on KEYDOWN (supports arrows + WASD)
                    if self.state == 'PLAYING':
                        if e.key in (pygame.K_w, pygame.K_UP):
                            self.player.next_dir = (0, -1)
                        elif e.key in (pygame.K_s, pygame.K_DOWN):
                            self.player.next_dir = (0, 1)
                        elif e.key in (pygame.K_a, pygame.K_LEFT):
                            self.player.next_dir = (-1, 0)
                        elif e.key in (pygame.K_d, pygame.K_RIGHT):
                            self.player.next_dir = (1, 0)
                        elif e.key == pygame.K_F12:
                            # Toggle 5x speed test mode
                            self.player.speed_test = not self.player.speed_test
                            if self.player.speed_test:
                                self.player.speed = self.player.base_speed * 5
                            else:
                                self.player.speed = self.player.base_speed
        return True
    
    def update(self):
        # Handle READY state - auto-continue after 2 seconds
        if self.state == 'READY':
            self.ready_timer += 1
            if self.ready_timer >= 2 * FPS:  # 2 seconds
                self.ready_timer = 0
                self.state = 'PLAYING'
            return
        
        # Handle HIGH_SCORES state - auto-return to menu after timer expires
        if self.state == 'HIGH_SCORES' and self.high_scores_timer > 0:
            self.high_scores_timer -= 1
            if self.high_scores_timer <= 0:
                self.state = 'MENU'
                self.initials = ""
            return
        
        # Handle death animation
        if self.state == 'DYING':
            self.death_timer += 1
            self.death_spin_angle += 15  # Spin speed (degrees per frame)
            
            # Stop power pellet music if playing
            if self.playing_power_music:
                try:
                    if self.snd_power:
                        self.snd_power.stop()
                except Exception:
                    pass
                self.playing_power_music = False
            
            # Death animation lasts about 1.5 seconds (90 frames)
            if self.death_timer >= 90:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = 'ENTER_INITIALS' if self.score > 0 else 'GAME_OVER'
                else:
                    # Only reset positions, not the maze (keep pellets as-is)
                    self.reset_positions_only()
                    self.state = 'READY'
                    # Restart intro music
                    try:
                        pygame.mixer.music.load(self.intro_music)
                        pygame.mixer.music.play(-1)
                    except Exception:
                        pass
            return
        
        # Always update flash timer for power pellets
        self.flash_timer += 1
        
        if self.state == 'PLAYING':
            self.player.update(self.maze)
            
            # Collect pellets
            tx = int(self.player.x // TILE)
            ty = int(self.player.y // TILE)
            if 0 <= ty < len(self.maze) and 0 <= tx < len(self.maze[0]):
                if self.maze[ty][tx] == '.':
                    self.maze[ty][tx] = ' '
                    self.score += 10
                    try:
                        if self.snd_chomp:
                            self.snd_chomp.play()
                    except Exception:
                        pass
                elif self.maze[ty][tx] == 'o':
                    # Power pellet
                    self.maze[ty][tx] = ' '
                    self.score += 50
                    try:
                        # Stop any current power pellet sound first, then restart it
                        pygame.mixer.music.stop()
                        if self.snd_power:
                            self.snd_power.stop()  # Stop if already playing to prevent stacking
                            self.snd_power.play(-1)  # Loop the power pellet sound
                            self.playing_power_music = True
                    except Exception:
                        pass
                    # Set ghosts to frightened (duration scales with level)
                    for g in self.ghosts:
                        if g.mode not in ('house', 'eaten'):
                            g.mode = 'frightened'
                            g.frightened_timer = self.frightened_duration
                            g.speed = max(0.8, g.base_speed * 0.6)
                            g.dir = (-g.dir[0], -g.dir[1])
            
            # Fruit system update
            if self.fruit_active:
                # Check if player collected the fruit
                dist = ((self.player.x - self.fruit_x)**2 + (self.player.y - self.fruit_y)**2)**0.5
                if dist < TILE//2:
                    # Collect fruit!
                    self.score += self.fruit_points.get(self.fruit_active, 500)
                    self.fruit_active = None
                    self.fruit_timer = 0
                    self.fruit_cooldown = 90 * FPS  # 1 minute 30 seconds before next fruit
                else:
                    # Fruit disappears after random time (8-12 seconds)
                    self.fruit_timer -= 1
                    if self.fruit_timer <= 0:
                        self.fruit_active = None
                        self.fruit_cooldown = 90 * FPS  # 1 minute 30 seconds before next fruit
            else:
                # Countdown to next fruit appearance
                if self.fruit_cooldown > 0:
                    self.fruit_cooldown -= 1
                else:
                    # Spawn a random fruit
                    self.fruit_active = random.choice(self.fruit_types)
                    self.fruit_timer = random.randint(8 * FPS, 12 * FPS)  # Visible for 8-12 seconds
            
            # Check level complete
            pellets = sum(row.count('.') + row.count('o') for row in self.maze)
            if pellets == 0:
                self.state = 'LEVEL_COMPLETE'
            
            # Update ghosts
            for g in self.ghosts:
                g.update(self.maze, (self.player.x, self.player.y))
                dist = ((g.x - self.player.x)**2 + (g.y - self.player.y)**2)**0.5
                if dist < TILE//2:
                    if g.mode == 'frightened':
                        # Eat ghost: award points and send ghost home
                        self.score += 200
                        try:
                            if self.snd_eatghost:
                                self.snd_eatghost.play()
                        except Exception:
                            pass
                        g.mode = 'house'
                        # Return to center of ghost house (row 13 - closer to door)
                        g.x = TILE * 13 + TILE  # center of house (between cols 13-14)
                        g.y = TILE * 13 + TILE // 2  # row 13 (top of house, near door)
                        g.release_timer = FPS  # Quick re-release (1 second)
                        g.speed = g.base_speed
                    else:
                        # Start death animation
                        self.state = 'DYING'
                        self.death_timer = 0
                        self.death_spin_angle = 0
                        try:
                            if self.snd_death:
                                self.snd_death.play()
                        except Exception:
                            pass
            
            # Check if power pellet music should stop (no more frightened ghosts)
            if self.playing_power_music:
                any_frightened = any(g.mode == 'frightened' for g in self.ghosts)
                if not any_frightened:
                    try:
                        if self.snd_power:
                            self.snd_power.stop()
                        pygame.mixer.music.load(self.intro_music)
                        pygame.mixer.music.play(-1)  # Loop intro music
                    except Exception:
                        pass
                    self.playing_power_music = False
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state in ['PLAYING', 'READY', 'LEVEL_COMPLETE', 'DYING']:
            # Draw maze
            for y, row in enumerate(self.maze):
                for x, cell in enumerate(row):
                    px, py = x * TILE, y * TILE
                    if cell == '#':
                        pygame.draw.rect(self.screen, BLUE, (px, py, TILE, TILE))
                    elif cell == '-':
                        pygame.draw.rect(self.screen, BLUE, (px, py, TILE, TILE))
                    elif cell == '.':
                        pygame.draw.circle(self.screen, WHITE, (px + TILE//2, py + TILE//2), 2)
                    elif cell == 'o':
                        # Flash power pellets (visible for 10 frames, hidden for 5)
                        if (self.flash_timer // 10) % 2 == 0:
                            pygame.draw.circle(self.screen, WHITE, (px + TILE//2, py + TILE//2), 6)
            
            # Draw player (with death spin if dying)
            if self.state == 'DYING':
                # Draw spinning Pac-Man
                if self.player.img:
                    rotated_img = pygame.transform.rotate(self.player.img, self.death_spin_angle)
                    rect = rotated_img.get_rect(center=(int(self.player.x), int(self.player.y)))
                    self.screen.blit(rotated_img, rect)
                else:
                    pygame.draw.circle(self.screen, YELLOW, (int(self.player.x), int(self.player.y)), TILE//2 - 4)
            else:
                self.player.draw(self.screen)
            
            # Only draw ghosts if not dying
            if self.state != 'DYING':
                for g in self.ghosts:
                    g.draw(self.screen)
            
            # Draw fruit if active
            if self.fruit_active and self.fruit_images.get(self.fruit_active):
                fruit_img = self.fruit_images[self.fruit_active]
                self.screen.blit(fruit_img, (self.fruit_x - TILE//2 + 2, self.fruit_y - TILE//2 + 2))
            elif self.fruit_active:
                # Fallback: draw a colored circle if image not loaded
                pygame.draw.circle(self.screen, (255, 0, 100), (int(self.fruit_x), int(self.fruit_y)), TILE//2 - 4)
            
            # HUD - use arcade font, evenly spaced across screen
            # Left: Score | Center: Lives | Right: High Score
            score_txt = self.arcade_font_small.render(f"SCORE: {self.score}", True, WHITE)
            self.screen.blit(score_txt, (20, 8))
            
            lives_txt = self.arcade_font_small.render(f"LIVES: {self.lives}", True, WHITE)
            lives_rect = lives_txt.get_rect(center=(SCREEN_WIDTH//2, 16))
            self.screen.blit(lives_txt, lives_rect)
            
            hs_txt = self.arcade_font_small.render(f"HIGH: {self.hs.get_high()}", True, YELLOW)
            hs_rect = hs_txt.get_rect(right=SCREEN_WIDTH - 20, top=8)
            self.screen.blit(hs_txt, hs_rect)
            
            if self.state == 'READY':
                txt = self.arcade_font_large.render("READY!", True, YELLOW)
                txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(txt, txt_rect)
            elif self.state == 'LEVEL_COMPLETE':
                txt = self.arcade_font_large.render("LEVEL COMPLETE!", True, YELLOW)
                txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(txt, txt_rect)
        
        elif self.state == 'MENU':
            # Draw logo image or fallback to text
            if self.logo_img:
                logo_rect = self.logo_img.get_rect(center=(SCREEN_WIDTH//2, 180))
                self.screen.blit(self.logo_img, logo_rect)
            else:
                txt = self.arcade_font_large.render("OPEN-PAC", True, YELLOW)
                txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 180))
                self.screen.blit(txt, txt_rect)
            
            txt = self.arcade_font.render("Press ENTER to Start", True, WHITE)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 350))
            self.screen.blit(txt, txt_rect)
            
            txt = self.arcade_font.render("Press END for High Scores", True, WHITE)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(txt, txt_rect)
        
        elif self.state == 'ENTER_INITIALS':
            txt = self.arcade_font_large.render("ENTER INITIALS", True, YELLOW)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(txt, txt_rect)
            
            txt = self.arcade_font_large.render(self.initials + "_" * (3 - len(self.initials)), True, WHITE)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 350))
            self.screen.blit(txt, txt_rect)
        
        elif self.state == 'HIGH_SCORES':
            txt = self.arcade_font_large.render("HIGH SCORES", True, YELLOW)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, 70))
            self.screen.blit(txt, txt_rect)
            
            y = 150
            for i, entry in enumerate(self.hs.scores[:10], 1):
                txt = self.arcade_font.render(f"{i}. {entry['initials']} - {entry['score']}", True, WHITE)
                txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, y))
                self.screen.blit(txt, txt_rect)
                y += 45
            
            # Show escape hint
            txt = self.arcade_font_small.render("Press ESC to return to menu", True, (150, 150, 150))
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            self.screen.blit(txt, txt_rect)
        
        elif self.state == 'GAME_OVER':
            txt = self.arcade_font_large.render("GAME OVER", True, (255, 0, 0))
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(txt, txt_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()