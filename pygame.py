import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Initialize Pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Basic 3D Shooter")
pygame.mouse.set_visible(False)  # Hide the mouse cursor

# Initialize OpenGL
glEnable(GL_DEPTH_TEST)
glViewport(0, 0, screen_width, screen_height)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (screen_width / screen_height), 0.1, 50.0)  # Changed far clipping plane
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()

# Set up initial camera position and orientation
camera_x = 0
camera_y = 0
camera_z = 5  # Initial camera Z position
camera_pitch = 0  # Up/down rotation
camera_yaw = -90  # Left/right rotation (starts looking along -Z)
sensitivity = 0.2
move_speed = 0.1
forward_speed = 0
sideways_speed = 0
vertical_speed = 0  # Addded vertical speed


# List to hold bullets
bullets = []
bullet_speed = 0.5
bullet_lifetime = 3  # Time in seconds before bullets disappear

# List to hold enemies
enemies = []
enemy_size = 0.3
enemy_color = (1, 0, 0)  # Red
enemy_speed = 0.02
enemy_spawn_rate = 1  # Enemies per second
last_enemy_spawn_time = 0
enemy_health = 3
player_health = 100
game_over = False

# Function to draw a cube
def draw_cube(x, y, z, size, color=(1, 1, 1)):
    """Draws a cube at the specified coordinates with the given size and color."""
    vertices = [
        (x - size, y - size, z - size),
        (x + size, y - size, z - size),
        (x + size, y + size, z - size),
        (x - size, y + size, z - size),
        (x - size, y - size, z + size),
        (x + size, y - size, z + size),
        (x + size, y + size, z + size),
        (x - size, y + size, z + size),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    glBegin(GL_LINES)
    glColor3fv(color)  # Set the color
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Function to draw a bullet
def draw_bullet(x, y, z):
    """Draws a small sphere representing a bullet."""
    glPushMatrix()
    glTranslatef(x, y, z)
    # Use a quadric to create a sphere.  This is more efficient than drawing polygons manually.
    sphere = gluNewQuadric()
    glColor3f(1, 1, 0)  # Yellow bullets
    gluSphere(sphere, 0.05, 10, 10)  # Radius, slices, stacks
    gluDeleteQuadric(sphere) # Clean up
    glPopMatrix()

# Function to draw an enemy
def draw_enemy(x, y, z, size, color):
    """Draws the enemy.  Now takes a size parameter."""
    draw_cube(x, y, z, size, color)

# Function to calculate distance between two points
def distance(x1, y1, z1, x2, y2, z2):
    """Calculates the Euclidean distance between two 3D points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

def display_game_over():
    """Display a game over message on the screen."""
    font = pygame.font.Font(None, 64)  # Use a larger font size
    text = font.render("Game Over", True, (255, 0, 0))  # Red text
    text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(text, text_rect)

    font2 = pygame.font.Font(None, 32)
    text2 = font2.render(f"Final Score: {pygame.time.get_ticks() // 1000}", True, (255, 255, 255))
    text_rect2 = text2.get_rect(center=(screen_width / 2, screen_height / 2 + 40))  # Positioned below
    screen.blit(text2, text_rect2)

    pygame.display.flip()  # Update the entire display

def display_player_health():
    """Display player's health on the screen."""
    font = pygame.font.Font(None, 32)
    text = font.render(f"Health: {player_health}", True, (0, 255, 0))  # Green text
    text_rect = text.get_rect(topleft=(10, 10))
    screen.blit(text, text_rect)
    pygame.display.flip()

def handle_input():
    """Handles user input for movement and shooting."""
    global camera_yaw, camera_pitch, forward_speed, sideways_speed, vertical_speed

    keys = pygame.key.get_pressed()
    mouse_rel = pygame.mouse.get_rel()

    # Mouse movement for rotation
    camera_yaw += mouse_rel[0] * sensitivity
    camera_pitch -= mouse_rel[1] * sensitivity
    camera_pitch = max(-89, min(89, camera_pitch))  # Clamp vertical rotation

    # Keyboard input for movement
    forward_speed = 0
    sideways_speed = 0
    vertical_speed = 0 #reset

    if keys[K_w]:
        forward_speed = 1
    if keys[K_s]:
        forward_speed = -1
    if keys[K_a]:
        sideways_speed = 1
    if keys[K_d]:
        sideways_speed = -1
    if keys[K_SPACE]:
        vertical_speed = 1
    if keys[K_LSHIFT]:
        vertical_speed = -1

    if keys[K_ESCAPE]:
        pygame.quit()
        quit()

    # Shooting
    if keys[K_LCTRL]:  # Changed to LCTRL
        current_time = pygame.time.get_ticks()
        # Limit fire rate to prevent too many bullets
        if len(bullets) < 10 and (not hasattr(handle_input, 'last_shot_time') or current_time - handle_input.last_shot_time > 100):
            handle_input.last_shot_time = current_time
            bullets.append({
                'x': camera_x,
                'y': camera_y,
                'z': camera_z,
                'yaw': camera_yaw,
                'pitch': camera_pitch,
                'time': current_time
            })

# Function to move the camera
def move_camera():
    """Moves the camera based on current movement speeds and orientation."""
    global camera_x, camera_y, camera_z

    # Calculate forward and sideways movement vectors
    forward_x = math.cos(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
    forward_y = math.sin(math.radians(camera_pitch))
    forward_z = math.sin(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
    sideways_x = math.cos(math.radians(camera_yaw + 90))
    sideways_z = math.sin(math.radians(camera_yaw + 90))

    # Update camera position
    camera_x += (forward_x * forward_speed + sideways_x * sideways_speed) * move_speed
    camera_y += forward_y * forward_speed * move_speed + vertical_speed * move_speed
    camera_z += (forward_z * forward_speed + sideways_z * sideways_speed) * move_speed

def update_bullets():
    """Updates the position of bullets and removes those that have traveled too far."""
    global bullets
    new_bullets = []
    for bullet in bullets:
        # Calculate bullet movement vector
        bullet_x_move = math.cos(math.radians(bullet['yaw'])) * math.cos(math.radians(bullet['pitch'])) * bullet_speed
        bullet_y_move = math.sin(math.radians(bullet['pitch'])) * bullet_speed
        bullet_z_move = math.sin(math.radians(bullet['yaw'])) * math.cos(math.radians(bullet['pitch'])) * bullet_speed

        bullet['x'] += bullet_x_move
        bullet['y'] += bullet_y_move
        bullet['z'] += bullet_z_move
        if pygame.time.get_ticks() - bullet['time'] < bullet_lifetime * 1000:
            new_bullets.append(bullet)
    bullets = new_bullets

def update_enemies():
    """Updates enemy positions and handles collisions with the player."""
    global enemies, player_health, game_over
    new_enemies = []
    for enemy in enemies:
        # Move towards the player
        dx = camera_x - enemy['x']
        dy = camera_y - enemy['y']
        dz = camera_z - enemy['z']
        dist = distance(enemy['x'], enemy['y'], enemy['z'], camera_x, camera_y, camera_z)
        if dist > 0:
            enemy['x'] += (dx / dist) * enemy_speed
            enemy['y'] += (dy / dist) * enemy_speed
            enemy['z'] += (dz / dist) * enemy_speed

        # Check for collision with player (reduce health)
        if dist < 0.5:  # Adjust this threshold as needed
            player_health -= 10  # Adjust damage amount
            enemies.remove(enemy) # remove the enemy
            if player_health <= 0:
                game_over = True
                return

        new_enemies.append(enemy)
    enemies = new_enemies

def handle_bullet_collisions():
    """Handles collisions between bullets and enemies.  Removes hit enemies."""
    global bullets, enemies
    new_bullets = []
    new_enemies = []
    for bullet in bullets:
        bullet_hit = False
        for enemy in enemies:
            if distance(bullet['x'], bullet['y'], bullet['z'], enemy['x'], enemy['y'], enemy['z']) < enemy_size/2: # Radius check.
                enemy['health'] -= 1
                bullet_hit = True
                if enemy['health'] <= 0:
                    enemies.remove(enemy)
                break
        if not bullet_hit:
            new_bullets.append(bullet)
    bullets = new_bullets

def spawn_enemies():
    """Spawns enemies at random locations around the player."""
    global enemies, last_enemy_spawn_time
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_spawn_time > 1000 / enemy_spawn_rate:  #控制生成速率
        last_enemy_spawn_time = current_time
        # Spawn enemies in a sphere around the player
        radius = 10  # Increased radius
        angle_h = random.uniform(0, 2 * math.pi)
        angle_v = random.uniform(-math.pi / 2, math.pi / 2)

        x = camera_x + radius * math.cos(angle_h) * math.cos(angle_v)
        y = camera_y + radius * math.sin(angle_v)
        z = camera_z + radius * math.sin(angle_h) * math.cos(angle_v)
        enemies.append({'x': x, 'y': y, 'z': z, 'size': enemy_size, 'color': enemy_color, 'health': enemy_health})

# Main game loop
running = True
pygame.event.set_grab(True)  # Confine mouse to window
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: #added a pause
                paused = True
                pygame.mouse.set_visible(True)
                while paused:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            paused = False
                            pygame.mouse.set_visible(False)
                        elif event.type == pygame.QUIT:
                            paused = False
                            running = False

    if not game_over:
        handle_input()
        move_camera()
        update_bullets()
        spawn_enemies()
        update_enemies()
        handle_bullet_collisions()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply camera transformations
        glRotatef(camera_pitch, 1, 0, 0)
        glRotatef(camera_yaw, 0, 1, 0)
        glTranslatef(-camera_x, -camera_y, -camera_z)

        # Draw the scene
        # Draw a ground plane
        glColor3f(0.5, 0.5, 0.5)  # Grey ground
        glBegin(GL_QUADS)
        glVertex3f(-10, -0.1, -10)
        glVertex3f(-10, -0.1, 10)
        glVertex3f(10, -0.1, 10)
        glVertex3f(10, -0.1, -10)
        glEnd()

        # Draw the bullets
        for bullet in bullets:
            draw_bullet(bullet['x'], bullet['y'], bullet['z'])

        # Draw the enemies
        for enemy in enemies:
            draw_enemy(enemy['x'], enemy['y'], enemy['z'], enemy['size'], enemy['color'])

        display_player_health() #show player health

        pygame.display.flip()
        pygame.time.tick(60)  # Cap frame rate at 60 FPS

    else:
        display_game_over()
        pygame.time.wait(3000)
        running = False

pygame.quit()
