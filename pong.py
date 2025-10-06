import turtle
import time

# Screen setup
screen = turtle.Screen()
screen.title("Pong Game")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0)  # Turns off screen updates to speed up drawing

# Paddle A
paddle_a = turtle.Turtle()
paddle_a.speed(0)  # Fastest possible speed
paddle_a.shape("square")
paddle_a.color("white")
paddle_a.shapesize(stretch_wid=5, stretch_len=1)  # 5 times wider, 1 times longer
paddle_a.penup()  # Don't draw when moving
paddle_a.goto(-350, 0)  # Start at the left side

# Paddle B
paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape("square")
paddle_b.color("white")
paddle_b.shapesize(stretch_wid=5, stretch_len=1)
paddle_b.penup()
paddle_b.goto(350, 0)  # Start at the right side

# Ball
ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("red")
ball.penup()
ball.goto(0, 0)
ball.dx = 0.2  # Initial x-direction speed (positive = right)
ball.dy = -0.2 # Initial y-direction speed (negative = down)

# Score
score_a = 0
score_b = 0
score_display = turtle.Turtle()
score_display.speed(0)
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.goto(0, 260)  # Position at the top center
score_display.write("Player A: 0  Player B: 0", align="center", font=("Courier", 24, "normal"))

# Function to move paddle A up
def paddle_a_up():
    y = paddle_a.ycor()  # Get current y coordinate
    y += 20  # Move up by 20 pixels
    paddle_a.sety(y)  # Set the new y coordinate

# Function to move paddle A down
def paddle_a_down():
    y = paddle_a.ycor()
    y -= 20
    paddle_a.sety(y)

# Function to move paddle B up
def paddle_b_up():
    y = paddle_b.ycor()
    y += 20
    paddle_b.sety(y)

# Function to move paddle B down
def paddle_b_down():
    y = paddle_b.ycor()
    y -= 20
    paddle_b.sety(y)

# Keyboard bindings
screen.listen()  # Listen for keyboard input
screen.onkeypress(paddle_a_up, "w")  # When 'w' is pressed, call paddle_a_up
screen.onkeypress(paddle_a_down, "s")  # When 's' is pressed, call paddle_a_down
screen.onkeypress(paddle_b_up, "Up")    # Up arrow for paddle B
screen.onkeypress(paddle_b_down, "Down")  # Down arrow for paddle B

# Main game loop
while True:
    screen.update()  # Update the screen

    # Move the ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Border checking
    if ball.ycor() > 290:  # Top border
        ball.sety(290)
        ball.dy *= -1  # Reverse y direction (bounce)
    elif ball.ycor() < -290:  # Bottom border
        ball.sety(-290)
        ball.dy *= -1

    if ball.xcor() > 390:  # Right border (Player A scores)
        ball.goto(0, 0)  # Reset ball to center
        ball.dx *= -1  # Reverse x direction
        score_a += 1
        score_display.clear()  # Clear previous score
        score_display.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 24, "normal"))
    elif ball.xcor() < -390:  # Left border (Player B scores)
        ball.goto(0, 0)
        ball.dx *= -1
        score_b += 1
        score_display.clear()
        score_display.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 24, "normal"))

    # Paddle and ball collisions
    if (ball.xcor() > 340 and ball.xcor() < 350) and (ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
        ball.setx(340)  # Force the ball to the edge of the paddle
        ball.dx *= -1.1 # Reverse x direction and increase speed
    elif (ball.xcor() < -340 and ball.xcor() > -350) and (ball.ycor() < paddle_a.ycor() + 50 and ball.ycor() > paddle_a.ycor() - 50):
        ball.setx(-340)
        ball.dx *= -1.1

    time.sleep(0.005) # সামান্য ডিলে যোগ করা হয়েছে গেম স্পীড কন্ট্রোল করার জন্য
