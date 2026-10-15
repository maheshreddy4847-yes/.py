import math
import random
import turtle

screen = turtle.Screen()
screen.setup(width=800, height=800)
screen.bgcolor("black")
screen.tracer(0)

t = turtle.Turtle()
t.hideturtle()
t.speed(0)


def get_heart_point(angle):
    x = 16 * (math.sin(angle) ** 3)
    y = (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))

    return x * 15, y * 15

NUM_DOTS = 300
dots = []
for i in range(NUM_DOTS):
    angle = random.uniform(0, 2 * math.pi)
    x, y = get_heart_point(angle)
    dot = turtle.Turtle()
    dot.hideturtle()
    dot.penup()
    dot.goto(x, y)
    dot.dot(random.random() * 10 + 5, random.choice(["red", "pink", "white"]))
    dots.append(dot)


