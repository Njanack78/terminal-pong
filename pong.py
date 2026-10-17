import os
import sys
import time
import random
import termios
import tty

WIDTH = 60
HEIGHT = 20
PADDLE_HEIGHT = 5
BALL_CHAR = "●"
PADDLE_CHAR = "█"


def enable_raw_mode():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return old


def restore_mode(old):
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old)


class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = PADDLE_HEIGHT
        self.score = 0

    def move(self, dir_y):
        self.y += dir_y
        self.y = max(1, min(self.y, HEIGHT - self.height - 1))


class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def update(self, left_paddle, right_paddle):
        self.x += self.dx
        self.y += self.dy

        if self.y <= 1 or self.y >= HEIGHT - 2:
            self.dy *= -1
            self.y += self.dy

        # left paddle collision
        if self.x == left_paddle.x + 1 and left_paddle.y <= self.y <= left_paddle.y + left_paddle.height - 1:
            self.dx = 1
            self.dy += random.choice([-1, 0, 1])
            self.x += 1

        # right paddle collision
        if self.x == right_paddle.x - 1 and right_paddle.y <= self.y <= right_paddle.y + right_paddle.height - 1:
            self.dx = -1
            self.dy += random.choice([-1, 0, 1])
            self.x -= 1

        if self.x < 0:
            right_paddle.score += 1
            self.reset()
        elif self.x > WIDTH - 1:
            left_paddle.score += 1
            self.reset()

        if self.dy > 2:
            self.dy = 2
        elif self.dy < -2:
            self.dy = -2


def draw_board(left_paddle, right_paddle, ball):
    os.system("clear")
    board = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        board[y][WIDTH // 2] = "│"

    for y in range(left_paddle.y, left_paddle.y + left_paddle.height):
        board[y][left_paddle.x] = PADDLE_CHAR
    for y in range(right_paddle.y, right_paddle.y + right_paddle.height):
        board[y][right_paddle.x] = PADDLE_CHAR

    if 0 <= ball.x < WIDTH and 0 <= ball.y < HEIGHT:
        board[ball.y][ball.x] = BALL_CHAR

    score_line = f"Player 1: {left_paddle.score}   Player 2: {right_paddle.score}"
    for i, ch in enumerate(score_line):
        if i < WIDTH:
            board[0][i] = ch

    for row in board:
        print("".join(row))


def main():
    old = enable_raw_mode()
    left_paddle = Paddle(2, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WIDTH - 3, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    last_time = time.time()
    move_speed = 0.08

    try:
        while True:
            key = ""
            if sys.stdin.isatty():
                key = sys.stdin.read(1)

            if key == "w":
                left_paddle.move(-1)
            elif key == "s":
                left_paddle.move(1)
            elif key == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    right_paddle.move(-1)
                elif seq == "[B":
                    right_paddle.move(1)

            if time.time() - last_time >= move_speed:
                ball.update(left_paddle, right_paddle)
                last_time = time.time()

            draw_board(left_paddle, right_paddle, ball)

            if left_paddle.score >= 5 or right_paddle.score >= 5:
                print("\nGame over!")
                break

            time.sleep(0.02)
    finally:
        restore_mode(old)


if __name__ == "__main__":
    main()
