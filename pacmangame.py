from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import uuid

# Camera-related variables
camera_pos = (0, 0, 300)
camera_angle = 0
camera_height = 300
camera_mode = 'third'  # Options: 'third', 'top', 'first'

# Game state variables
player_pos = [50, 50, 20]  # Player position (x, y, z) in maze
player_angle = 0
life = 5
score = 0
bullets_missed = 0
game_over = False
paused = False
special_ability_active = False
special_ability_timer = 0
last_time = time.time()

# Maze and game constants
MAZE_SIZE = 600
WALL_HEIGHT_OUTER = 60
WALL_HEIGHT_INNER = 40
fovY = 90
BULLET_SPEED = 3
ENEMY_SPEED = 0.5
ENEMY_COUNT = 4
POWERUP_COUNT = 2
OBSTACLE_COUNT = 3
OBSTACLE_SPEED = 100
OBSTACLE_SPAWN_INTERVAL = 5

# Game objects
bullets = []  # [x, y, z, angle]
enemies = []  # [x, y, z]
powerups = []  # [x, y, z]
obstacles = []  # [x, y, z, id]
destroyed_paths = []  # [x, y, width, height]
last_obstacle_spawn = time.time()

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

def spawn_powerup():
    """Spawn a power-up at a random valid position."""
    while True:
        x = random.uniform(-290, 290)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 10):
            powerups.append([x, y, 20])
            break

def spawn_obstacle():
    """Spawn a falling obstacle at a random position."""
    while True:
        x = random.uniform(-290, 290)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 20):
            obstacles.append([x, y, 200, str(uuid.uuid4())])
            break

def is_valid_position(x, y, radius):
    """Check if position is valid (no collision with walls or destroyed paths)."""
    for wall in maze_walls:
        x1, y1, x2, y2, _ = wall
        if x1 == x2:  # Vertical wall
            if abs(x - x1) < radius and min(y1, y2) - radius < y < max(y1, y2) + radius:
                return False
        elif y1 == y2:  # Horizontal wall
            if abs(y - y1) < radius and min(x1, x2) - radius < x < max(x1, x2) + radius:
                return False
    for path in destroyed_paths:
        px, py, pw, ph = path
        if px - pw / 2 - radius < x < px + pw / 2 + radius and py - ph / 2 - radius < y < py + ph / 2 + radius:
            return False
    return True

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(0.7, 0.7, 1)  # Light blue
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    """Draw Pacman with animated mouth."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)
    
    if game_over:
        glRotatef(90, 1, 0, 0)
    
    glColor3f(1, 0.5, 0)  # Orange
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

def draw_obstacle(x, y, z):
    """Draw an obstacle as a dark red sphere."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.8, 0.2, 0.2)  # Dark red
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()

def draw_destroyed_path(x, y, width, height):
    """Draw a destroyed path as a dark gray rectangle."""
    glPushMatrix()
    glTranslatef(x, y, 0.1)
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    glBegin(GL_QUADS)
    glVertex3f(-width / 2, -height / 2, 0)
    glVertex3f(width / 2, -height / 2, 0)
    glVertex3f(width / 2, height / 2, 0)
    glVertex3f(-width / 2, height / 2, 0)
    glEnd()
    glPopMatrix()

def draw_maze():
    """Draw the maze walls with brick-like segments."""
    glBegin(GL_QUADS)
    for wall in maze_walls:
        x1, y1, x2, y2, height = wall
        segment_size = 20
        if x1 == x2:  # Vertical wall
            for y in range(int(min(y1, y2)), int(max(y1, y2)), segment_size):
                glColor3f(0, 0.8, 0) if (y // segment_size) % 2 == 0 else glColor3f(0.5, 1, 0.5)
                glVertex3f(x1 - 10, y, 0)
                glVertex3f(x1 + 10, y, 0)
                glVertex3f(x1 + 10, y, height)
                glVertex3f(x1 - 10, y, height)
                glVertex3f(x1 - 10, y, 0)
                glVertex3f(x1 + 10, y, 0)
                glVertex3f(x1 + 10, y + segment_size, 0)
                glVertex3f(x1 - 10, y + segment_size, 0)
        elif y1 == y2:  # Horizontal wall
            for x in range(int(min(x1, x2)), int(max(x1, x2)), segment_size):
                glColor3f(0, 0.8, 0) if (x // segment_size) % 2 == 0 else glColor3f(0.5, 1, 0.5)
                glVertex3f(x, y1 - 10, 0)
                glVertex3f(x, y1 + 10, 0)
                glVertex3f(x, y1 + 10, height)
                glVertex3f(x, y1 - 10, height)
                glVertex3f(x, y1 - 10, 0)
                glVertex3f(x + segment_size, y1 - 10, 0)
                glVertex3f(x + segment_size, y1 + 10, 0)
                glVertex3f(x, y1 + 10, 0)
    glEnd()

def keyboardListener(key, x, y):
    """Handle keyboard inputs."""
    global player_pos, player_angle, paused, camera_mode, special_ability_active, special_ability_timer
    if game_over:
        if key == b'r':
            init_game()
        return
    
    if key == b'p':
        paused = not paused
        return
    
    if paused:
        return
    
    speed = 10 if special_ability_active else 5
    if key == b'w':  # Move forward (mouth direction)
        rad = math.radians(player_angle)
        new_x = player_pos[0] + speed * math.sin(rad)
        new_y = player_pos[1] + speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b's':  # Move backward (opposite mouth direction)
        rad = math.radians(player_angle)
        new_x = player_pos[0] - speed * math.sin(rad)
        new_y = player_pos[1] - speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b'a':  # Rotate left (counterclockwise)
        player_angle = (player_angle - 5) % 360
    if key == b'd':  # Rotate right (clockwise)
        player_angle = (player_angle + 5) % 360
    if key == b'1':
        camera_mode = 'top'
    if key == b'2':
        camera_mode = 'third'
    if key == b' ':
        if not special_ability_active:
            special_ability_active = True
            special_ability_timer = time.time()

def specialKeyListener(key, x, y):
    """Handle arrow keys for camera."""
    global camera_height, camera_angle
    if game_over or paused:
        return
    if key == GLUT_KEY_UP and camera_mode != 'top':
        camera_height = min(camera_height + 10, 600)
    if key == GLUT_KEY_DOWN and camera_mode != 'top':
        camera_height = max(camera_height - 10, 100)
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 5) % 360
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 5) % 360

def mouseListener(button, state, x, y):
    """Handle mouse inputs."""
    global camera_mode
    if game_over or paused:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rad = math.radians(player_angle)
        bx = player_pos[0] + 20 * math.sin(rad)
        by = player_pos[1] + 20 * math.cos(rad)
        bz = player_pos[2]
        bullets.append([bx, by, bz, player_angle])
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == 'third':
            camera_mode = 'first'
        elif camera_mode == 'first':
            camera_mode = 'top'
        else:
            camera_mode = 'third'

def setupCamera():
    """Configure camera projection and view."""
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

def update_game():
    """Update game state."""
    global bullets, enemies, powerups, life, bullets_missed, game_over, score, last_time, obstacles, last_obstacle_spawn, destroyed_paths, special_ability_active, special_ability_timer
    if game_over or paused:
        return
    
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    if current_time - last_obstacle_spawn > OBSTACLE_SPAWN_INTERVAL and len(obstacles) < OBSTACLE_COUNT:
        spawn_obstacle()
        last_obstacle_spawn = current_time
    
    new_bullets = []
    for bullet in bullets:
        bx, by, bz, angle = bullet
        rad = math.radians(angle)
        bx += BULLET_SPEED * math.sin(rad) * dt * 60
        by += BULLET_SPEED * math.cos(rad) * dt * 60
        if -MAZE_SIZE < bx < MAZE_SIZE and -MAZE_SIZE < by < MAZE_SIZE and is_valid_position(bx, by, 5):
            new_bullets.append([bx, by, bz, angle])
        else:
            bullets_missed += 1
            if bullets_missed >= 10:
                game_over = True
    bullets = new_bullets
    
    for enemy in enemies:
        ex, ey, ez = enemy
        dx = player_pos[0] - ex
        dy = player_pos[1] - ey
        dist = math.hypot(dx, dy)
        if dist > 5:
            dx /= dist
            dy /= dist
            new_x = ex + ENEMY_SPEED * dx * dt * 60
            new_y = ey + ENEMY_SPEED * dy * dt * 60
            if is_valid_position(new_x, new_y, 15):
                enemy[0] = new_x
                enemy[1] = new_y
    
    new_obstacles = []
    for obstacle in obstacles:
        ox, oy, oz, oid = obstacle
        oz -= OBSTACLE_SPEED * dt
        if oz <= 0:
            destroyed_paths.append([ox, oy, 20, 20])
        else:
            new_obstacles.append([ox, oy, oz, oid])
    obstacles = new_obstacles
    
    new_enemies = []
    for enemy in enemies:
        ex, ey, ez = enemy
        hit = False
        bullets_to_remove = []
        for bullet in bullets:
            bx, by, bz, _ = bullet
            if math.hypot(bx - ex, by - ey) < 20 and abs(bz - ez) < 20:
                hit = True
                bullets_to_remove.append(bullet)
                score += 10
                break
        if math.hypot(ex - player_pos[0], ey - player_pos[1]) < 35 and abs(ez - player_pos[2]) < 20:
            life -= 1
            hit = True
            if life <= 0:
                game_over = True
        if not hit:
            new_enemies.append(enemy)
        else:
            spawn_enemy()
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    enemies = new_enemies
    
    new_powerups = []
    for powerup in powerups:
        px, py, pz = powerup
        if math.hypot(px - player_pos[0], py - player_pos[1]) < 30 and abs(pz - player_pos[2]) < 20:
            if life < 5:
                life += 1
                spawn_powerup()
        else:
            new_powerups.append(powerup)
    powerups = new_powerups
    
    if special_ability_active and time.time() - special_ability_timer > 5:
        special_ability_active = False

def draw_bullet(x, y, z):
    """Draw a bullet as a yellow cube."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 1, 0)  # Yellow
    scale = 1.0 + 0.2 * math.sin(time.time() * 5)
    glScalef(scale, scale, scale)
    glutSolidCube(8)
    glPopMatrix()

def idle():
    """Update game and redraw."""
    update_game()
    glutPostRedisplay()

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
    for enemy in enemies:
        draw_enemy(*enemy)
    for powerup in powerups:
        draw_powerup(*powerup)
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
    for obstacle in obstacles:
        draw_obstacle(obstacle[0], obstacle[1], obstacle[2])
    
    draw_text(10, 770, f"Lives: {life}")
    draw_text(10, 740, f"Score: {score}")
    draw_text(10, 710, f"Bullets Missed: {bullets_missed}")
    draw_text(10, 680, f"Camera: {'Top-Down' if camera_mode == 'top' else 'Third-Person' if camera_mode == 'third' else 'First-Person'}")
    if paused:
        draw_text(400, 400, "Paused - Press P to Resume")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")
    if special_ability_active:
        draw_text(400, 370, f"Speed Boost: {5 - int(time.time() - special_ability_timer)}s")
    
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
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    init_game()
    
    glutMainLoop()

if __name__ == "__main__":
    main()