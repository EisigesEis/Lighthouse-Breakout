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

    def move(self, move_x, move_y):
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
            print(f"I collided with the right side at ({self.rect.x},{self.rect.y}) setting {self.speed_x=} to {self.speed_x*-1}.")
            self.speed_x = -abs(self.speed_x)
        # handle collision with roof
        if self.rect.top <= 0:
            print("I am colliding with top of screen.")
            self.speed_y = abs(self.speed_y)
        # handle collision with void (bottom)
        if self.rect.bottom >= screen_height:
            print("I fell off of the map.")
            self.speed_y = -abs(self.speed_y)
            keyboard.wait()

        # handle collision with movingbar
        if self.rect.colliderect(movingbar.rect):
            # check if colliding from the top
            if abs(self.rect.bottom - movingbar.rect.top) < 20 and self.speed_y > 0:
                print(f"I am colliding with the movingbar at {self.rect.x, self.rect.y} :))")
                self.speed_y = -abs(self.speed_y)
                self.speed_x += movingbar.direction
                print(f"{self.speed_x-movingbar.direction} =» {self.speed_x}")
                self.collision['movingbar'] = True
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
                # elif self.speed_x == 0:
                #     self.speed_x += player_movingbar.direction
            # collision from side
            elif move_x:
                self.speed_x *= -1
                
        if move_x and not (self.collision['y'] or self.collision['movingbar']):
            self.rect.x += int(move_x * self.speed_x / abs(self.speed_x))
            self.collision['x'] = False
            print(f"=> moving towards ({self.rect.x},{self.rect.y})")
        if move_y and not self.collision['x']:
            self.rect.y += int(move_y * self.speed_y / abs(self.speed_y))
            self.collision['y'] = False
            self.collision['movingbar'] = False
            print(f"=> moving towards ({self.rect.x},{self.rect.y})")

    def old_move(self, move_x, move_y): # deprecated
        wall_alive = 0 # assume all blocks have been destroyed
        for row in wall.blocks:
            for item in row:
                # check if item was already deleted
                if not item[0]: continue

                # check ball collision with item
                # if self.rect.colliderect(item[0]):
                #     self.collision = True
                #     print(f"ball ({self.rect.x},{self.rect.y}) colliding with block: {item}")
                
                """if move_y:
                        # check collision from above
                        if (abs(self.rect.bottom - item[0].top) < 0 and self.speed_y > 0):
                            # print(f"I vertically collided with the block {item[0]}. Setting {self.speed_y=} to {self.speed_y*-1}")
                            self.speed_y *= -1
                        # check collision below block
                        elif (abs(self.rect.top - item[0].bottom) < 0 and self.speed_y < 0):
                            self.speed_y *= -1
                    
                    if move_x:
                        # check collision from left
                        if (abs(self.rect.left - item[0].left) < 0 and self.speed_x < 0):
                            self.speed_x *= -1
                        # check collision from right
                        elif (abs(self.rect.left - item[0].right < 0 and self.speed_x > 0)):
                            self.speed_x *= -1"""
                    
                    # reduce block's strength
                
                # handle ball collision with item
                # print(f"checking {item[0]=}")
                for x in range(item[0].width):
                    if (self.rect.top, self.rect.x) == (item[0].bottom, x+item[0].x) and self.speed_y < 0: # (y, x)
                        self.speed_y *= -1
                        self.collision = True
                        print(f"I collided with bottom of {item[0]=}")
                    elif (self.rect.bottom, self.rect.x) == (item[0].top, x+item[0].x) and self.speed_y > 0: # (y, x)
                        self.speed_y *= -1
                        self.collision = True
                        print(f"I collided with top of {item[0]=}")
                for y in range(item[0].height):
                    # print(f"({self.rect.y}, {self.rect.right}) ?= ({y}, {item[0].left})")
                    if (self.rect.y, self.rect.right) == (y+item[0].y, item[0].left) and self.speed_x > 0:
                        self.speed_x *= -1
                        self.collision = True
                        print(f"I collided with left of {item[0]=}")
                    elif (self.rect.y, self.rect.left) == (y+item[0].y, item[0].right) and self.speed_x < 0:
                        self.speed_x *= -1
                        self.collision = True
                        print(f"I collided with right of {item[0]=}")

                # handle item interaction on collision with it
                if self.collision:
                    if item[1] > 1: # reduce strength
                        item[1] -= 1
                    else: # delete
                        item[0] = 0

                # check if block still has strength
                if item[0]:
                    wall_alive += 1 # if so, wall has not been destroyed
        
        # if wall has been destroyed, level was finished
        if not wall_alive:
            self.game_over = 1
        
        # handle collision with side walls
        if self.rect.left <= 0:
            self.speed_x = abs(self.speed_x)
        if self.rect.right > screen_width:
            # print(f"I collided with the right side at ({self.rect.x},{self.rect.y}) setting {self.speed_x=} to {self.speed_x*-1}.")
            self.speed_x = -abs(self.speed_x)
        # handle collision with roof
        if self.rect.y <= 0:
            # print("I am colliding with top of screen.")
            self.speed_y = abs(self.speed_y)
        # handle collision with void (bottom)
        if self.rect.bottom >= screen_height:
            print("I fell off of the map.")
            self.game_over = -1
            keyboard.wait() # Add replayability here!!

        # handle collision with movingbar
        if self.rect.colliderect(movingbar.rect):
            self.collision = True
            # check if colliding from the top
            if abs(self.rect.bottom - movingbar.rect.top) < 0 and self.speed_y > 0:
                print(f"I am colliding with the movingbar at {self.rect.x, self.rect.y} :))")
                self.speed_y *= -1
                self.speed_x += movingbar.direction
                if self.speed_x > self.speed_max:
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
        self.speed_x = 4 # speed is frame count at which x or y will be moved
        self.speed_y = -10 # and also the direction in which it will be moved at the frame count
        self.speed_max = 8
        self.collision = {'x':False, 'y':False, 'movingbar':False}
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
    clock.tick(10) # game runs at 60fps

    # ball movement through framecounter logic
    framecounter += 1
    # print(
    #     framecounter,
    #     (framecounter-1) % abs(ball.speed_x) and not (framecounter % abs(ball.speed_x)),
    #     (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
    # )
    # if ball.collision['x']: # collision so ball has to check x and y
    #     ball.collision = False
    #     ball.move(True, True)
    #     ball.collision = False
        # framecounter = 0
    # else: 
    move_y = (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
    move_x = (framecounter-1) % abs(ball.speed_x) and not (framecounter % abs(ball.speed_x)) and not move_y
    ball.move(
        move_x,
        move_y
    )

    if framecounter == abs(ball.speed_y): framecounter = 0
    wall.update_img() # items may have been destroyed or interacted with # only when collision was true
    
    # draw board
    img = wall.img
    img = movingbar.draw(img)
    img = ball.draw(img)

    p.set_image(img)
