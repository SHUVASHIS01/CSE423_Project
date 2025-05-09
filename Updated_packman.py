from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
# Camera-related variables
camera_pos = (0, 0, 300)
camera_angle = 0
camera_height = 300
camera_mode = 'third'
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

# Game objects
bullets = []  # [x, y, z, angle]
obstacles = []  # [x, y, z, id]
destroyed_paths = []  # [x, y, width, height]
last_obstacle_spawn = time.time()

# Game constants
OBSTACLE_COUNT = 3
OBSTACLE_SPEED = 100
OBSTACLE_SPAWN_INTERVAL = 5

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
    """Enhanced camera system with multiple views."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 'third':
        rad = math.radians(camera_angle)
        cx = player_pos[0] + 200 * math.sin(rad)
        cy = player_pos[1] + 200 * math.cos(rad)
        cz = camera_height
        gluLookAt(cx, cy, cz, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)
    elif camera_mode == 'top':
        gluLookAt(0, 0, 600, 0, 0, 0, 0, 1, 0)
    elif camera_mode == 'first':
        rad = math.radians(player_angle)
        cx = player_pos[0] - 30 * math.sin(rad)
        cy = player_pos[1] - 30 * math.cos(rad)
        cz = player_pos[2]
        tx = player_pos[0] + 100 * math.sin(rad)
        ty = player_pos[1] + 100 * math.cos(rad)
        tz = player_pos[2]
        gluLookAt(cx, cy, cz, tx, ty, tz, 0, 0, 1)
    
def spawn_obstacle():
    """Spawn a falling obstacle at a random position."""
    while True:
        x = random.uniform(-290, 290)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 20):
            obstacles.append([x, y, 200, str(uuid.uuid4())])
            break

def draw_obstacle(x, y, z):
    """Draw an obstacle as a dark red sphere."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.8, 0.2, 0.2)  # Dark red
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()

def update_game():
    """Update game state."""
    global bullets, obstacles, last_obstacle_spawn, destroyed_paths
    
    # Obstacle spawning
    current_time = time.time()
    if current_time - last_obstacle_spawn > OBSTACLE_SPAWN_INTERVAL and len(obstacles) < OBSTACLE_COUNT:
        spawn_obstacle()
        last_obstacle_spawn = current_time
    
    # Update obstacles
    new_obstacles = []
    for obstacle in obstacles:
        ox, oy, oz, oid = obstacle
        oz -= OBSTACLE_SPEED * dt
        if oz <= 0:
            destroyed_paths.append([ox, oy, 20, 20])
        else:
            new_obstacles.append([ox, oy, oz, oid])
    obstacles = new_obstacles
    
    # Update bullets
    new_bullets = []
    for bullet in bullets:
        bx, by, bz, angle = bullet
        rad = math.radians(angle)
        bx += BULLET_SPEED * math.sin(rad) * dt * 60
        by += BULLET_SPEED * math.cos(rad) * dt * 60
        if -MAZE_SIZE < bx < MAZE_SIZE and -MAZE_SIZE < by < MAZE_SIZE and is_valid_position(bx, by, 5):
            new_bullets.append([bx, by, bz, angle])
    bullets = new_bullets

def draw_destroyed_path(x, y, width, height):
    """Draw a destroyed path as a dark gray rectangle."""
    glPushMatrix()
    glTranslatef(x, y, 0.1)
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    glBegin(GL_QUADS)
    glVertex3f(-width/2, -height/2, 0)
    glVertex3f(width/2, -height/2, 0)
    glVertex3f(width/2, height/2, 0)
    glVertex3f(-width/2, height/2, 0)
    glEnd()
    glPopMatrix()

def specialKeyListener(key, x, y):
    """Handle arrow keys for camera adjustments."""
    global camera_height, camera_angle
    if key == GLUT_KEY_UP and camera_mode != 'top':
        camera_height = min(camera_height + 10, 600)
    if key == GLUT_KEY_DOWN and camera_mode != 'top':
        camera_height = max(camera_height - 10, 100)
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 5) % 360
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 5) % 360

def mouseListener(button, state, x, y):
    """Handle mouse inputs for shooting and camera cycling."""
    global camera_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Simplified shooting from mouth direction
        rad = math.radians(player_angle)
        bx = player_pos[0] + 20 * math.sin(rad)
        by = player_pos[1] + 20 * math.cos(rad)
        bz = player_pos[2]
        bullets.append([bx, by, bz, player_angle])

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Cycle through camera modes
        if camera_mode == 'third':
            camera_mode = 'first'
        elif camera_mode == 'first':
            camera_mode = 'top'
        else:
            camera_mode = 'third'

def draw_bullet(x, y, z):
    """Draw a bullet as a yellow sphere."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 1, 0)  # Yellow
    gluSphere(gluNewQuadric(), 4, 10, 10)
    glPopMatrix()

def showScreen():
    """Render the game scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    draw_maze()
    for path in destroyed_paths:
        draw_destroyed_path(path[0], path[1], path[2], path[3])
    draw_player()
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
    for obstacle in obstacles:
        draw_obstacle(obstacle[0], obstacle[1], obstacle[2])
    
    glutSwapBuffers()
    
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
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    
    init_game()
    
    glutMainLoop()

if __name__ == "__main__":
    main()
