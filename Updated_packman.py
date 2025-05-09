from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Game state variables
player_pos = [50, 50, 20]  # Player position (x, y, z) in maze
player_angle = 0
life = 5
score = 0
game_over = False

# Maze and game constants
MAZE_SIZE = 600
WALL_HEIGHT_OUTER = 60
WALL_HEIGHT_INNER = 40
fovY = 90
BULLET_SPEED = 3

# Maze layout: [x1, y1, x2, y2, height]
maze_walls = [
    # Outer walls
    [-300, -300, 300, -300, WALL_HEIGHT_OUTER],  # Bottom
    [-300, 300, 300, 300, WALL_HEIGHT_OUTER],    # Top
    [-300, -300, -300, 300, WALL_HEIGHT_OUTER],  # Left
    [300, -300, 300, 300, WALL_HEIGHT_OUTER],    # Right
    # Inner walls (cross shape)
    [-150, 0, 150, 0, WALL_HEIGHT_INNER],        # Horizontal
    [0, -150, 0, 150, WALL_HEIGHT_INNER],        # Vertical
]
def init_game():
    """Initialize or reset game state."""
    global player_pos, player_angle, life, score, bullets_missed, game_over, bullets, enemies, powerups, camera_mode, camera_height, camera_angle, paused, obstacles, destroyed_paths, last_obstacle_spawn, special_ability_active, special_ability_timer
    player_pos = [50, 50, 20]
    player_angle = 0
    life = 5
    score = 0
    bullets_missed = 0
    game_over = False
    paused = False
    camera_mode = 'third'
    camera_height = 300
    camera_angle = 0
    special_ability_active = False
    special_ability_timer = 0
    bullets = []
    enemies = []
    powerups = []
    obstacles = []
    destroyed_paths = []
    last_obstacle_spawn = time.time()
    for _ in range(ENEMY_COUNT):
        spawn_enemy()
    for _ in range(POWERUP_COUNT):
        spawn_powerup()
def spawn_enemy():
    """Spawn an enemy at a random valid position."""
    while True:
        x = random.uniform(-290, 290)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 20) and math.hypot(x - player_pos[0], y - player_pos[1]) > 100:
            enemies.append([x, y, 20])
            break
def is_valid_position(x, y, radius):
    """Check if position is valid (no collision with walls)."""
    for wall in maze_walls:
        x1, y1, x2, y2, _ = wall
        if x1 == x2:  # Vertical wall
            if abs(x - x1) < radius and min(y1, y2) - radius < y < max(y1, y2) + radius:
                return False
        elif y1 == y2:  # Horizontal wall
            if abs(y - y1) < radius and min(x1, x2) - radius < x < max(x1, x2) + radius:
                return False
    return True

def draw_maze():
    """Draw the maze walls with brick-like segments."""
    glBegin(GL_QUADS)
    for wall in maze_walls:
        x1, y1, x2, y2, height = wall
        segment_size = 20  # Size of brick segments
        if x1 == x2:  # Vertical wall
            for y in range(int(min(y1, y2)), int(max(y1, y2)), segment_size):
                # Alternate colors for brick effect
                glColor3f(0, 0.8, 0) if (y // segment_size) % 2 == 0 else glColor3f(0.5, 1, 0.5)
                glVertex3f(x1 - 10, y, 0)
                glVertex3f(x1 + 10, y, 0)
                glVertex3f(x1 + 10, y, height)
                glVertex3f(x1 - 10, y, height)
        elif y1 == y2:  # Horizontal wall
            for x in range(int(min(x1, x2)), int(max(x1, x2)), segment_size):
                glColor3f(0, 0.8, 0) if (x // segment_size) % 2 == 0 else glColor3f(0.5, 1, 0.5)
                glVertex3f(x, y1 - 10, 0)
                glVertex3f(x, y1 + 10, 0)
                glVertex3f(x, y1 + 10, height)
                glVertex3f(x, y1 - 10, height)
    glEnd()

def draw_player():
    """Draw Pacman with animated mouth."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)
    
    glColor3f(1, 1, 0)  # Yellow
    mouth_angle = 45 + 15 * math.sin(time.time() * 5)
    quad = gluNewQuadric()
    gluPartialDisk(quad, 0, 20, 20, 20, mouth_angle / 2, 360 - mouth_angle)
    glPopMatrix()
def draw_enemy(x, y, z):
    """Draw an enemy as a purple sphere."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.5, 0, 0.5)  # Purple
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()
def draw_powerup(x, y, z):
    """Draw a power-up as a cyan cube."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0, 1, 1)  # Cyan
    scale = 1.0 + 0.2 * math.sin(time.time() * 5)
    glScalef(scale, scale, scale)
    glutSolidCube(10)
    glPopMatrix()

def keyboardListener(key, x, y):
    """Handle keyboard inputs for Pac-Man movement."""
    global player_pos, player_angle
    if game_over:
        if key == b'r':
            init_game()
        return
    
    speed = 5
    if key == b'w':  # Move forward
        rad = math.radians(player_angle)
        new_x = player_pos[0] + speed * math.sin(rad)
        new_y = player_pos[1] + speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b's':  # Move backward
        rad = math.radians(player_angle)
        new_x = player_pos[0] - speed * math.sin(rad)
        new_y = player_pos[1] - speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b'a':  # Turn left
        player_angle = (player_angle + 5) % 360
    if key == b'd':  # Turn right
        player_angle = (player_angle - 5) % 360

def setupCamera():
    """Configure camera projection and view."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    rad = math.radians(player_angle)
    cx = player_pos[0] + 200 * math.sin(rad)
    cy = player_pos[1] + 200 * math.cos(rad)
    cz = 300
    gluLookAt(cx, cy, cz, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Pacman")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glDisable(GL_LIGHTING)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutIdleFunc(idle)
    
    init_game()
    
    glutMainLoop()

if __name__ == "__main__":
    main()
