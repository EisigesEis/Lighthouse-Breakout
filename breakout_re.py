# To-Do:
# - Implement own FPS Clock
# - Implement own Rect and Colliderect

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
                    # print(f"coloring for block[0]:")
                    for y in range(block[0].y, block[0].y + block[0].height):
                        for x in range(block[0].x, block[0].x + block[0].width):
                            # print(f"Block ({y}, {x}): {colors['block'][block[1]-1]=}")
                            self.img[y][x] = colors["block"][block[1]-1]

    def update_img(self):
        self.img = np.zeros((14, 28, 3)).tolist()
        for row in self.blocks:
            for block in row:
                if block[0]:
                    # print(f"coloring for block[0]:")
                    for y in range(block[0].y, block[0].y + block[0].height):
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
        self.speed = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

class ball():
    def __init__(self, x, y):
        self.reset(x, y)
    
    def draw(self, img):
        print(f"Ball in {self.rect.y} {self.rect.x}")
        img[self.rect.y][self.rect.x] = colors["ball"]
        return img

    def move(self):
        # collision threshhold
        collision_thresh = 1

        # start off with assuming that the wall has been destroyed completely
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                # check collision
                if self.rect.colliderect(item[0]):
                    # check if collision was from above or below
                    if (abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0) or (abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0):
                        self.speed_y *= -1
                    # check if collision was from right or left
                    if (abs(self.rect.left - item[0].left) < collision_thresh and self.speed_x < 0) or (abs(self.rect.left - item[0].right < collision_thresh and self.speed_x > 0)):
                        self.speed_x *= -1
    	            # reduce block's strength by doing damage to it
                    # optimization: check if blocks are accessible for ball?
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)
                
                # check if blocks still exist, set wall_destroyed accordingly
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                # increase item counter
                item_count += 1
            # increase row counter
            row_count += 1
        # after iterating through all blocks, check if wall is destroyed
        if wall_destroyed == 1:
            self.game_over = 1

        # check collision with side walls
        if self.rect.left <= 0 or self.rect.right >= screen_width-1:
            self.speed_x *= -1
        
        # check for collision with top and bottom of screen
        if self.rect.top <= 0:
            print("I am colliding with top of screen.")
            self.speed_y *= -1
        if self.rect.bottom >= screen_height-1:
            # print("I fell off of the map.")
            # self.game_over = -1
            # return
            self.speed_y *= -1

        # check for collision with movingbar
        print(f"{movingbar.rect}")
        print(f"{self.rect.colliderect(movingbar.rect)}")
        if self.rect.colliderect(movingbar.rect):
            # check if colliding from the top
            if abs(self.rect.bottom - movingbar.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += movingbar.direction
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
                # elif self.speed_x == 0:
                #     self.speed_x += player_movingbar.direction
            else:
                self.speed_x *= -1

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over
    
    def reset(self, x, y):
        # self.ball_rad = 1
        # self.x = x - self.ball_rad
        # self.y = y - self.ball_rad
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 0, 0)
        self.speed_x = 1
        self.speed_y = -1
        self.speed_max = 7
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
keyboard.wait('up')

# add hotkey listeners
keyboard.add_hotkey('right', lambda: movingbar.move(1))
keyboard.add_hotkey('left', lambda: movingbar.move(-1))

# general game loop
while 1:
    clock.tick(15) # game runs at 60fps

    # ball movement
    ball.move()
    
    # draw board
    wall.update_img()
    img = wall.img
    img = movingbar.draw(img)
    img = ball.draw(img)

    p.set_image(img)
