# To-Do:
# Unskippable Tasks:
# - Remove ball staggering when colliding with movingbar or block
# - Add more effect from movingbar.direction towards ball movement
#   (allow increase and direction switch while still touching instead of frameskip?)
# - Only call wall.update_img() when block collision happened

# Relevant Tasks:
# - Add functionality for special blocks (grey, fire, de-buff, buff)
# - Add replayability without restarting client (use set_image_callback perhaps? a runner maybe too)
# - Add more Levels and difficulty setting

# Look-Ahead Collision:
# - Optimize collision check to only check in range or route of ball
# - Check if ball collides when speed is applied, not when ball already collided

# minor:
# (- Implement own FPS Clock)
# (- Implement own Rect and Colliderect)

from pyghthouse import Pyghthouse, VerbosityLevel
from login import username, token
from breakout_data import levelmap, callback

import pygame
from pygame.locals import *

import numpy as np
import keyboard
from time import sleep

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
        self.collision = False # deprecated?

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
                if item[0]:
                    # print(f"coloring for {item[0]=}")
                    for y in range(item[0].y, item[0].y + item[0].height):
                        for x in range(item[0].x, item[0].x + item[0].width):
                            # print(f"item ({y}, {x}): {colors['item'][item[1]-1]=}")
                            self.img[y][x] = colors["block"][item[1]-1]

    def update_img(self):
        self.img = np.zeros((14, 28, 3)).tolist()
        # print(self.blocks)

        for row in self.blocks:
            # print(f"checking {row=}")
            for item in row:
                # print({f"-> checking {item=}"})
                if item[1]:
                    # print(f"coloring for {item[0]=}")
                    for y in range(item[0].y, item[0].y + item[0].width):
                        for x in range(item[0].x, item[0].x + item[0].width):
                            # print(f"item ({y}, {x}): {colors['item'][item[1]-1]=}")
                            self.img[y][x] = colors["block"][item[1]-1]

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

    def prime_move(self):
        wall_alive = False # assume all items have been destroyed

        # handle collision with items
        for row in wall.blocks:
            for item in row:
                if not item[1]: continue # skip destroyed item
                
                for x in range(item[0].width):
                    if (self.rect.top, self.rect.x) == (item[0].bottom, x+item[0].x) and self.speed_y < 0:
                        self.speed_y *= -1
                        self.collision['y'] = True
                        print(f"I collided with bottom of {item[0]=}")
                    elif (self.rect.bottom, self.rect.x) == (item[0].top, x+item[0].x) and self.speed_y > 0: # (y, x)
                        self.speed_y *= -1
                        self.collision['y'] = True
                        print(f"I collided with top of {item[0]=}")
                for y in range(item[0].height): # check 
                    if (self.rect.y, self.rect.right) == (y+item[0].y, item[0].left) and self.speed_x > 0:
                        self.speed_x *= -1
                        self.collision['x'] = True
                        print(f"I collided with left of {item[0]=}")
                    elif (self.rect.y, self.rect.left) == (y+item[0].y, item[0].right) and self.speed_x < 0:
                        self.speed_x *= -1
                        self.collision['x'] = True
                        print(f"I collided with right of {item[0]=}")

                # handle item interaction on collision
                if self.collision['x'] or self.collision['y']:
                    wall.collision = True
                    if item[1]:
                        item[1] -= 1
                self.collision['x'] = False
                self.collision['y'] = False
                # determine if item still has health
                if not wall_alive and item[1]: wall_alive = True

        # handle collision with side walls
        if self.rect.left <= 0:
            self.speed_x = abs(self.speed_x)
        if self.rect.right >= screen_width:
            # print(f"I collided with the right side at ({self.rect.x},{self.rect.y}) setting {self.speed_x=} to {self.speed_x*-1}.")
            self.speed_x = -abs(self.speed_x)
        # handle collision with roof
        if self.rect.top <= 0:
            # print("I am colliding with top of screen.")
            self.speed_y = abs(self.speed_y)
        # handle collision with void (bottom)
        if self.rect.bottom >= screen_height:
            # print("I fell off of the map.")
            self.speed_y = -abs(self.speed_y)
            keyboard.wait()

        # handle collision with movingbar
        if self.rect.colliderect(movingbar.rect):
            # check if colliding from the top
            if self.speed_y > 0:
                print(f"I am colliding with the movingbar at {self.rect.x, self.rect.y} :))")
                self.speed_y = -abs(self.speed_y)
                self.speed_x -= movingbar.direction
                print(f"{self.speed_x+movingbar.direction} => {self.speed_x}")
                self.collision['movingbar'] = True

                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x > -self.speed_max:
                    self.speed_x = -self.speed_max
                elif not self.speed_x:
                    self.speed_x = -movingbar.direction
                
    def move(self, move_x, move_y):
        if move_x and not self.collision['movingbar']:
            self.rect.x += int(move_x * self.speed_x / abs(self.speed_x))

        if move_y and not self.collision['x']:
            self.rect.y += int(move_y * self.speed_y / abs(self.speed_y))
            self.collision['movingbar'] = False
    
    def reset(self, x, y):
        # self.ball_rad = 1
        # self.x = x - self.ball_rad
        # self.y = y - self.ball_rad
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        self.speed_x = 4 # speed is frame count at which x or y will be moved
        self.speed_y = -10 # and also the direction in which it will be moved at the frame count
        self.speed_max = 6
        self.collision = {'x':False, 'y':False, 'movingbar':False}
        self.game_over = 0
        # print(f"Ball in {self.y} {self.x}")

# initialize pyghthouse
p = Pyghthouse(username, token, verbosity=VerbosityLevel)
p.start()
callback_img = [[255,255,255] if int(x) else [0,0,0] for string in callback for x in string]
p.set_image(callback_img)

while 1:
    levelmap_keys = "".join([f"{key}, " for key in levelmap])
    level = input(f"Which level do you want to play?\nPossible choices: {levelmap_keys}\n")
    while not level in levelmap.keys(): level = input("Invalid level. Input a valid one:\n")

    # create board
    wall = wall()
    wall.create(levelmap[level])
    wall.update_img()
    movingbar = movingbar()
    ball = ball(movingbar.x + (int(movingbar.width / 2)), movingbar.y - movingbar.height)

    # draw board
    wall.update_img()
    img = wall.img
    img = movingbar.draw(img)
    img = ball.draw(img)
    p.set_image(img)

    # wait for player to start
    print("\nLevel has been loaded! Press up to begin.")
    keyboard.wait('up') # give the paddle a ball start and a reset animation :D

    # add hotkey listeners
    keyboard.add_hotkey('right', lambda: movingbar.move(1))
    keyboard.add_hotkey('left', lambda: movingbar.move(-1))


    framecounter = 0 # for operations that happen every n frame
    # general game loop
    while 1:
        clock.tick(40) # game runs at 60fps

        # ball movement through framecounter logic
        framecounter += 1
        move_y = (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
        move_x = (framecounter-1) % abs(ball.speed_x) and not (framecounter % abs(ball.speed_x)) and not move_y
        ball.prime_move()
        ball.move(move_x, move_y)

        if framecounter == abs(ball.speed_y): framecounter = 0

        # update board on collision
        wall.update_img()
        
        # draw board
        img = wall.img
        img = movingbar.draw(img)
        img = ball.draw(img)

        p.set_image(img)

    keyboard.unhook_all()

