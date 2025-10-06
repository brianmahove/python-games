import turtle
import time
import random

# Screen setup
screen = turtle.Screen()
screen.title("Tetris Game")
screen.bgcolor("black")
screen.setup(width=600, height=800)  # Increased height for play area
screen.tracer(0)
screen.listen()

# Game constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 20

# Tetromino shapes and colors
shapes = [
    # I-shape
    [[1, 1, 1, 1]],

    # J-shape
    [[1, 0, 0],
     [1, 1, 1]],

    # L-shape
    [[0, 0, 1],
     [1, 1, 1]],

    # O-shape
    [[1, 1],
     [1, 1]],

    # S-shape
    [[0, 1, 1],
     [1, 1, 0]],

    # T-shape
    [[0, 1, 0],
     [1, 1, 1]],

    # Z-shape
    [[1, 1, 0],
     [0, 1, 1]],
]

colors = ["cyan", "blue", "orange", "yellow", "green", "purple", "red"]

# Create the game grid
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

# Function to draw a block at a given position
def draw_block(x, y, color):
    turtle_block = turtle.Turtle()
    turtle_block.speed(0)
    turtle_block.shape("square")
    turtle_block.color(color)
    turtle_block.penup()
    turtle_block.goto(
        (x - GRID_WIDTH // 2) * BLOCK_SIZE + BLOCK_SIZE // 2,
        (GRID_HEIGHT // 2 - y) * BLOCK_SIZE - BLOCK_SIZE // 2,
    )  # Centering and y-axis correction
    return turtle_block

# Function to draw the entire grid
def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                draw_block(x, y, grid[y][x])

# Function to generate a new tetromino
def new_tetromino():
    global current_tetromino, tetromino_x, tetromino_y, tetromino_color
    current_tetromino = random.choice(shapes)
    tetromino_color = colors[shapes.index(current_tetromino)]
    tetromino_x = GRID_WIDTH // 2 - len(current_tetromino[0]) // 2
    tetromino_y = 0
    return [draw_block(tetromino_x + x, tetromino_y + y, tetromino_color)
            for y, row in enumerate(current_tetromino)
            for x, val in enumerate(row) if val]

# Function to move the tetromino down
def move_down():
    global tetromino_y, current_tetromino_blocks
    if is_valid_move(tetromino_x, tetromino_y + 1, current_tetromino):
        tetromino_y += 1
        for block in current_tetromino_blocks:
            block.sety(block.ycor() - BLOCK_SIZE)
    else:
        place_tetromino()
        clear_lines()
        current_tetromino_blocks = new_tetromino() # Spawn next piece
        if not is_valid_move(tetromino_x, tetromino_y, current_tetromino):
            # Game Over: The new piece can't be placed
            global game_over
            game_over = True

# Function to move the tetromino left
def move_left():
    global tetromino_x, current_tetromino_blocks
    if is_valid_move(tetromino_x - 1, tetromino_y, current_tetromino):
        tetromino_x -= 1
        for block in current_tetromino_blocks:
            block.setx(block.xcor() - BLOCK_SIZE)

# Function to move the tetromino right
def move_right():
    global tetromino_x, current_tetromino_blocks
    if is_valid_move(tetromino_x + 1, tetromino_y, current_tetromino):
        tetromino_x += 1
        for block in current_tetromino_blocks:
            block.setx(block.xcor() + BLOCK_SIZE)

# Function to rotate the tetromino
def rotate():
    global current_tetromino, current_tetromino_blocks
    rotated_tetromino = list(zip(*reversed(current_tetromino)))  # Rotate 90 degrees
    if is_valid_move(tetromino_x, tetromino_y, rotated_tetromino):
        current_tetromino = rotated_tetromino
        # Delete old blocks and create new ones
        for block in current_tetromino_blocks:
            block.goto(1000, 1000)  # Move off-screen
        current_tetromino_blocks = [
            draw_block(tetromino_x + x, tetromino_y + y, tetromino_color)
            for y, row in enumerate(current_tetromino)
            for x, val in enumerate(row) if val
        ]

# Function to check if a move is valid
def is_valid_move(new_x, new_y, new_tetromino):
    for y, row in enumerate(new_tetromino):
        for x, val in enumerate(row):
            if val:
                grid_x = new_x + x
                grid_y = new_y + y
                if (
                    grid_x < 0
                    or grid_x >= GRID_WIDTH
                    or grid_y >= GRID_HEIGHT
                    or grid_y < 0 # Allow negative y for entry
                    or (grid_y >= 0 and grid[grid_y][grid_x] != 0) # Only check when y >= 0
                ):
                    return False
    return True

# Function to place the tetromino on the grid
def place_tetromino():
    for y, row in enumerate(current_tetromino):
        for x, val in enumerate(row):
            if val:
                grid[tetromino_y + y][tetromino_x + x] = tetromino_color

# Function to clear completed lines
def clear_lines():
    global score
    lines_cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):  # Iterate from bottom to top
        if all(grid[y]):  # If the entire row is filled
            lines_cleared += 1
            # Remove the completed line and add a new empty line at the top
            del grid[y]
            grid.insert(0, [0] * GRID_WIDTH)
    if lines_cleared:
        score += lines_cleared * lines_cleared * 10  # Score points
        score_display.clear()
        score_display.write(f"Score: {score}", align="center", font=("Courier", 24, "normal"))

# Keyboard bindings
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeypress(move_down, "Down")
screen.onkeypress(rotate, "Up")  # Rotate on up arrow

# Initialize game variables
score = 0
game_over = False
score_display = turtle.Turtle()
score_display.speed(0)
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.goto(0, 350)  # Adjusted position
score_display.write(f"Score: {score}", align="center", font=("Courier", 24, "normal"))

current_tetromino_blocks = new_tetromino() # Generate the first tetromino
tetromino_x = GRID_WIDTH // 2 - len(current_tetromino[0]) // 2
tetromino_y = 0

# Main game loop
while not game_over:
    screen.update()
    draw_grid() #draw the grid
    move_down()
    time.sleep(0.2)  # Adjust for game speed

# Game over message
if game_over:
    game_over_turtle = turtle.Turtle()
    game_over_turtle.speed(0)
    game_over_turtle.color("red")
    game_over_turtle.penup()
    game_over_turtle.hideturtle()
    game_over_turtle.goto(0, 0)
    game_over_turtle.write("Game Over!", align="center", font=("Courier", 30, "bold"))
    screen.update()
    time.sleep(5)  # Keep the message displayed for 5 seconds

screen.mainloop()
