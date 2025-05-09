from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import sys

# Game state variables
life = 5
score = 0
bullets_missed = 0
game_over = False
paused = False
camera_mode = 'third'  # Options: 'third', 'top', 'first' (for HUD display)
special_ability_active = False
special_ability_timer = 0
auto_shoot_active = False
auto_shoot_timer = 0
speed_boost_cooldown = 0  # Cooldown timer for speed boost
auto_shoot_cooldown = 0   # Cooldown timer for auto-shoot
last_time = time.time()
COOLDOWN_DURATION = 10  # 10-second cooldown for abilities

def init_game():
    """Initialize or reset game state."""
    global life, score, bullets_missed, game_over, paused, camera_mode, special_ability_active, special_ability_timer, auto_shoot_active, auto_shoot_timer, speed_boost_cooldown, auto_shoot_cooldown
    life = 5
    score = 0
    bullets_missed = 0
    game_over = False
    paused = False
    camera_mode = 'third'
    special_ability_active = False
    special_ability_timer = 0
    auto_shoot_active = False
    auto_shoot_timer = 0
    speed_boost_cooldown = 0
    auto_shoot_cooldown = 0

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

def keyboardListener(key, x, y):
    """Handle keyboard inputs for pause, game over, and special abilities."""
    global paused, special_ability_active, special_ability_timer, auto_shoot_active, auto_shoot_timer
    if game_over:
        if key == b'r':
            init_game()  # Restart game
        return
    
    if key == b'p':
        paused = not paused  # Toggle pause
        return
    
    if paused:
        return
    
    if key == b' ' and not special_ability_active and time.time() >= speed_boost_cooldown:
        special_ability_active = True
        special_ability_timer = time.time()  # Start speed boost
    if key == b'c' and not auto_shoot_active and time.time() >= auto_shoot_cooldown:
        auto_shoot_active = True
        auto_shoot_timer = time.time()  # Start auto-shoot

def update_game():
    """Update special ability timers and cooldowns."""
    global special_ability_active, special_ability_timer, auto_shoot_active, auto_shoot_timer, speed_boost_cooldown, auto_shoot_cooldown, last_time
    if game_over or paused:
        return
    
    current_time = time.time()
    last_time = current_time
    
    if auto_shoot_active:
        if current_time - auto_shoot_timer > 5:  # Auto-shoot lasts 5 seconds
            auto_shoot_active = False
            auto_shoot_cooldown = current_time + COOLDOWN_DURATION  # Start cooldown
    
    if special_ability_active and current_time - special_ability_timer > 5:  # Speed boost lasts 5 seconds
        special_ability_active = False
        speed_boost_cooldown = current_time + COOLDOWN_DURATION  # Start cooldown

def showScreen():
    """Render the HUD with lives, score, bullets missed, camera mode, and states."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Set up 2D projection for text
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Display stats and cooldowns in top-left corner
    draw_text(10, 770, f"Lives: {life}")
    draw_text(10, 740, f"Score: {score}")
    draw_text(10, 710, f"Bullets Missed: {bullets_missed}")
    draw_text(10, 680, f"Camera: {'Top-Down' if camera_mode == 'top' else 'Third-Person' if camera_mode == 'third' else 'First-Person'}")
    if time.time() < speed_boost_cooldown:
        remaining = int(speed_boost_cooldown - time.time())
        draw_text(10, 650, f"Speed Boost Cooldown: {remaining}s")
    if time.time() < auto_shoot_cooldown:
        remaining = int(auto_shoot_cooldown - time.time())
        draw_text(10, 620, f"Auto-Shoot Cooldown: {remaining}s")
    
    # Display active ability timers and states (center of screen)
    if paused:
        draw_text(400, 400, "Paused - Press P to Resume")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")
    if special_ability_active:
        draw_text(400, 370, f"Speed Boost: {5 - int(time.time() - special_ability_timer)}s")
    if auto_shoot_active:
        draw_text(400, 340, f"Auto-Shoot: {5 - int(time.time() - auto_shoot_timer)}s")
    
    glutSwapBuffers()

def idle():
    """Update game and redraw."""
    update_game()
    glutPostRedisplay()
    
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
