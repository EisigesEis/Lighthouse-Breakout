# To-Do:
# Unskippable Tasks:
# - Move x of ball at different frametime than y according to ball.speed_x
# - Fix wall sticking and roof jumping

# Relevant Tasks:
# - Allow movement every 2nd 3rd or 4th frame.... :/
# - Add functionality for special blocks (grey, fire, de-buff, buff)
# - Add replayability without restarting client
# - Add more Levels and difficulty setting

# Look-Ahead Collision:
# - Optimize collision check to only check in range or route of ball
# - Check if ball collides when speed is applied, not when ball already collided

# minor:
# (- Implement own FPS Clock)
# (- Implement own Rect and Colliderect)

from pyghthouse import Pyghthouse, VerbosityLevel
from login import username, token
from breakout_data import levelmap

import pygame
from pygame.locals import *

import numpy as np
import keyboard

# define game variables
screen_width = 28
screen_height = cols = 14
rows = 7
clock = pygame.time.Clock()
fps = 60
colors = {
    "background":[30, 30, 30],
    "block":[
        [242, 85, 96], # red
        [86, 174, 87], # green
        [69, 177, 232], # blue
        [255, 255, 255], # grey (unbreakable)
        [], # fire (exploding)
        [], # de-buff
        [] # buff
    ],
    "movingbar":[142, 135, 123],
    "ball":[220, 220, 220]
}

class wall():
    def __init__(self):
        self.width = 2
        self.height = 2

    def create(self, block_data: list):
        self.blocks = []
        # define empty list for individual block
        block_individual = []
        for row in range(rows):
            # reset block row list
            block_row = []
            for col in range(cols):
                # generate block data for individual block: pygame rectangle and type
                if int(block_data[row][col]):
                    block_y = row * self.height
                    block_x = col * self.width
                    rect = pygame.Rect(block_x, block_y, self.width, self.height)
                    
                    identity = int(block_data[row][col])
                    # 1 = red (strength 1)
                    # 2 = green (strength 2)
                    # 3 = blue (strength 3)
                    # 4 = grey (unbreakable)
                    # 5 = fire (exploding)
                    # 6 = de-buff
                    # 7 = buff

                    block_individual = [rect, identity]

                    block_row.append(block_individual)
            self.blocks.append(block_row)
        # print(self.blocks)
        
    def draw(self): # deprecated
        for row in self.blocks:
            for block in row:
                if block[0]:
                    # print(f"coloring for {block[0]=}")
                    for y in range(block[0].y, block[0].y + block[0].height):
                        for x in range(block[0].x, block[0].x + block[0].width):
                            # print(f"Block ({y}, {x}): {colors['block'][block[1]-1]=}")
                            self.img[y][x] = colors["block"][block[1]-1]

    def update_img(self):
        self.img = np.zeros((14, 28, 3)).tolist()
        # print(self.blocks)

        for row in self.blocks:
            # print(f"checking {row=}")
            for block in row:
                # print({f"-> checking {block=}"})
                if block[0]:
                    # print(f"coloring for {block[0]=}")
                    for y in range(block[0].y, block[0].y + block[0].width):
                        for x in range(block[0].x, block[0].x + block[0].width):
                            # print(f"Block ({y}, {x}): {colors['block'][block[1]-1]=}")
                            self.img[y][x] = colors["block"][block[1]-1]

class movingbar():
    def __init__(self):
        self.reset()
    
    def move(self, direction):
        if (0 <= self.rect.x + direction) and (self.rect.x + direction + self.width-1 <= screen_width-1): # move is within limits?
            # print(f"move {self.x} to {self.x+x} is valid")
            self.rect.x += direction
            self.direction = direction
    
    def draw(self, img):
        for x in range(self.rect.x, self.rect.x + self.width):
            # print(f"I'm in [{self.y}][{x}]")
            img[self.rect.y][x] = colors["movingbar"]
        return img

    def reset(self):
        self.height = 1
        self.width = 7
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = 12
        self.speed = 6 # deprecated
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

class ball():
    def __init__(self, x, y):
        self.reset(x, y)
    
    def draw(self, img):
        # print(f"Ball in {self.rect.y} {self.rect.x}")

        # is ball in range of img? (Add look-ahead collision!!!)
        if self.rect.x < 0:
            x = 0
        elif self.rect.x >= screen_width:
            x = screen_width-1
        else:
            x = self.rect.x
        
        img[self.rect.y][x] = colors["ball"]
        return img

    def move(self, move_x, move_y):
        collision_threshhold = 1 # may be deprecated due to pixelation

        wall_alive = 0 # assume all blocks have been destroyed
        for row in wall.blocks:
            for item in row:
                # check if item was deleted
                if not item[0]: continue

                # check ball collision with blocks
                if self.rect.colliderect(item[0]):
                    print(f"ball ({self.rect.x},{self.rect.y}) colliding with block: {item}")
                    # check if collision was from above or below
                    if move_y and (abs(self.rect.bottom - item[0].top) < 5 and self.speed_y > 0) or (abs(self.rect.top - item[0].bottom) < 5 and self.speed_y < 0):
                        print(f"I vertically collided with the block {item[0]}. Setting {self.speed_y=} to {self.speed_y*-1}")
                        self.speed_y *= -1
                    # check if collision was from right or left
                    if move_x and (abs(self.rect.left - item[0].left) < 5 and self.speed_x < 0) or (abs(self.rect.left - item[0].right < 5 and self.speed_x > 0)):
                        self.speed_x *= -1
                    
                    # reduce block's strength
                    if item[1] > 1:
                        item[1] -= 1
                    else:
                        item[0] = 0
                    
                # check if block still has strength
                if item[0]:
                    wall_alive += 1 # if so, wall has not been destroyed
        
        # if wall has been destroyed, level was finished
        if not wall_alive:
            self.game_over = 1
        
        # handle collision with side walls
        if move_x and self.rect.left <= 0 or self.rect.right > screen_width:
            print(f"I collided with the right side... setting {self.speed_x=} to {self.speed_x*-1}.")
            self.speed_x *= -1
        # handle collision with roof
        if move_y and self.rect.top <= 1:
            print("I am colliding with top of screen.")
            self.speed_y *= -1
        # handle collision with void (bottom)
        if self.rect.bottom >= screen_height:
            print("I fell off of the map.")
            self.game_over = -1
            keyboard.wait() # Add replayability here!!

        # handle collision with movingbar
        if self.rect.colliderect(movingbar.rect):
            # check if colliding from the top
            if move_y and abs(self.rect.bottom - movingbar.rect.top) < 5 and self.speed_y > 0:
                print(f"I am colliding with the movingbar at {self.rect.x, self.rect.y} :))")
                self.speed_y *= -1
                self.speed_x += movingbar.direction
                if self.speed_x < self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
                # elif self.speed_x == 0:
                #     self.speed_x += player_movingbar.direction
            elif move_x:
                self.speed_x *= -1
        
        self.rect.x += move_x * self.speed_x / abs(self.speed_x)
        self.rect.y += move_y * self.speed_y / abs(self.speed_y)

        return self.game_over
    
    def reset(self, x, y):
        # self.ball_rad = 1
        # self.x = x - self.ball_rad
        # self.y = y - self.ball_rad
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        self.speed_x = 5 # speed is frame count at which x or y will be moved
        self.speed_y = -25 # and also the direction in which it will be moved at the frame count
        self.speed_max = 10
        self.game_over = 0
        # print(f"Ball in {self.y} {self.x}")

# create board
wall = wall()
wall.create(levelmap['A'])
wall.update_img()
movingbar = movingbar()
ball = ball(movingbar.x + (int(movingbar.width / 2)), movingbar.y - movingbar.height)

# initialize pyghthouse
p = Pyghthouse(username, token, verbosity=VerbosityLevel)
p.start()

# draw board
wall.update_img()
img = wall.img
img = movingbar.draw(img)
img = ball.draw(img)
p.set_image(img)



# wait for player to start
keyboard.wait('up') # give the paddle a ball start and a reset animation :D

# add hotkey listeners
keyboard.add_hotkey('right', lambda: movingbar.move(1))
keyboard.add_hotkey('left', lambda: movingbar.move(-1))


framecounter = 0 # for operations that happen every n frame
# general game loop
while 1:
    clock.tick(30) # game runs at 60fps

    # ball movement through framecounter logic
    framecounter += 1
    print(
        framecounter,
        (framecounter-1) % abs(ball.speed_x) and not (framecounter % abs(ball.speed_x)),
        (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
    )

    ball.move(
        (framecounter-1) % abs(ball.speed_x) and not (framecounter % abs(ball.speed_x)),
        (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
    )
    if framecounter == abs(ball.speed_y): framecounter = 0
    wall.update_img() # items may have been destroyed or interacted with
    
    # draw board
    img = wall.img
    img = movingbar.draw(img)
    img = ball.draw(img)

    p.set_image(img)
