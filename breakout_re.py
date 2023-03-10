from pyghthouse import Pyghthouse, VerbosityLevel
from login import username, token
from breakout_data import levelmap, callback, finish_screen

import pygame
from pygame.locals import *

import numpy as np
import keyboard
from time import sleep, time

# define game variables
screen_width = 28
screen_height = cols = 14
rows = 7
clock = pygame.time.Clock()
fps = 60
colors = {
    "background":[30, 30, 30],
    "block":[
        [220,20,60], # red
        [86, 174, 87], # green
        [69, 177, 232], # blue
        [242, 125, 12], # fire (speeds up ball.speed_x and .speed_y and .max_speed_x)
        [200, 233, 233], # ice (slows down ball.speed_x .speed_y and .max_speed_x)
        [128, 9, 9], # de-buff
        [0, 255, 0], # buff
        [75, 0, 130], # bomb (exploding)
        [142, 135, 124], # grey (unbreakable)
    ],
    "bombs_exploding":[
        [120, 0, 70],
        [170, 33, 60],
        [168, 65, 70],
        [180, 75, 80]
    ],
    "movingbar":[142, 135, 123],
    "ball":[220, 220, 220]
}

class Wall():
    def __init__(self):
        self.width = 2
        self.height = 2
        self.bombs_exploding = [] # holds information of exploding bombs

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
                    # 4 = fire (ball speed-up)
                    # 5 = ice (ball slow-down)
                    # 6 = de-buff
                    # 7 = buff
                    # 8 = bomb (exploding)
                    # 9 = grey (unbreakable)

                    block_individual = [rect, identity]

                    block_row.append(block_individual)
            self.blocks.append(block_row)

    def update_img(self):
        self.img = np.zeros((14, 28, 3)).tolist()

        for row in self.blocks:
            for item in row:
                if item[1]:
                    for y in range(item[0].y, item[0].y + item[0].height):
                        for x in range(item[0].x, item[0].x + item[0].width):
                            self.img[y][x] = colors["block"][item[1]-1]

        for bomb in self.bombs_exploding:
            exploded = bomb.explode()
            if exploded:
                self.bombs_exploding.pop(self.bombs_exploding.index(bomb))
            else:
                self.img = bomb.draw(self.img)

class Movingbar():
    def __init__(self):
        self.reset()
    
    def move(self, direction):
        if (0 <= self.rect.x + direction) and (self.rect.x + direction + self.width-1 <= screen_width-1): # move is within limits?
            self.rect.x += direction
            self.direction = direction

            # ball collision logic
            if ball.collision['movingbar']:
                ball.speed_x += self.direction*2
                if ball.speed_x == 0: # direction reversal
                    ball.speed_x = self.direction*2
                elif ball.speed_x >= ball.speed_max or ball.speed_x <= -ball.speed_max: # too high speed (constant line and errors in framecount logic)
                    ball.speed_x = (ball.speed_max-2) * int(ball.speed_x / abs(ball.speed_x))
    
    def draw(self, img):
        for x in range(self.rect.x, self.rect.x + self.width):
            img[self.rect.y][x] = colors["movingbar"]
        return img

    def reset(self):
        self.height = 1
        self.width = 7
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = 12
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

class Ball():
    def __init__(self, x, y, lives):
        self.reset(x, y, lives)
    
    def draw(self, img):
        # is ball in range of img? may be deprecated!!
        if self.rect.x < 0:
            x = 0
        elif self.rect.x >= screen_width:
            x = screen_width-1
        else:
            x = self.rect.x
        
        if self.collision["movingbar"]:
            img[self.rect.y][x] = [128, 9, 9] # ball turns dark red when affectable by movement of movingbar
        else:
            img[self.rect.y][x] = colors["ball"]
        return img

    def prime_move(self):
        wall_alive = False # assume all items have been destroyed

        # handle collision with items
        for row in wall.blocks:
            for item in row:
                if not item[1]: continue # skip destroyed item
                
                for x in range(item[0].width): # check vertical collision
                    if (self.rect.top, self.rect.x) == (item[0].bottom, x+item[0].x) and self.speed_y < 0: # top of ball collided with items bottom
                        self.speed_y *= -1
                        self.collision['vertical'] = True
                    elif (self.rect.bottom, self.rect.x) == (item[0].top, x+item[0].x) and self.speed_y > 0: # bottom of ball collided with items top
                        self.speed_y *= -1
                        self.collision['vertical'] = True
                for y in range(item[0].height): # check horizontal collision
                    if (self.rect.y, self.rect.right) == (y+item[0].y, item[0].left) and self.speed_x > 0: # right of ball collided with items left 
                        self.speed_x *= -1
                        self.collision['horizontal'] = True
                    elif (self.rect.y, self.rect.left) == (y+item[0].y, item[0].right) and self.speed_x < 0: # left of ball collided with items right
                        self.speed_x *= -1
                        self.collision['horizontal'] = True

                # handle item interaction on collision
                if not item[1] == 9: # inspecting a breakable item
                    if self.collision['horizontal'] or self.collision['vertical']:
                        self.collision['item'] = True
                        if item[1] > 3: # inspecting a one-time use item
                            if item[1] < 6: # inspecting either ice or fire
                                addition = 2 if item[1]-5 else -2
                                ball.speed_x -= addition
                                ball.speed_max -= addition*2
                                ball.speed_y += addition*2
                                if ball.speed_x == 0:
                                    ball.speed_x = -addition
                                # sign = int(ball.speed_x/abs(ball.speed_x))
                            elif item[1] == 8: # inspecting bomb
                                wall.bombs_exploding.append(Bomb(item[0]))
                            
                            item[1] = 0 # item was one-time use, so destruct item
                        elif item[1]: # inspecting strength-based block
                            item[1] -= 1
                    # wall still has health if breakable item has health
                    if not wall_alive and item[1]: wall_alive = True
                self.collision['horizontal'] = False
                self.collision['vertical'] = False

        if not wall_alive: self.game_over = 1; return

        # handle collision with side walls
        if self.rect.left <= 0:
            self.speed_x = abs(self.speed_x)
        if self.rect.right >= screen_width:
            self.speed_x = -abs(self.speed_x)
        # handle collision with roof
        if self.rect.top <= 0:
            self.speed_y = abs(self.speed_y)
        # handle collision with void (bottom)
        if self.rect.bottom >= screen_height:
            sleep(0.2)
            self.lives -= 1
            print(f"{self.lives=}")
            if not self.lives:
                self.game_over = -1
            else: # life was used, ball is reset
                keyboard.unhook_all() # no movingbar movement during paused game
                self.reset(movingbar.rect.x + (int(movingbar.width / 2)), movingbar.rect.y - movingbar.height, self.lives)
                draw_board()
                # draw life bar
                img = p.get_image()
                for y in range(3):
                    for x in range(5):
                        img[y][x] = [50,50,50]
                for x in range(3):
                    if self.lives > x:
                        img[1][x+1] = [255,255,255]
                    else:
                        img[1][x+1] = [220,20,60]
                p.set_image(img)
                keyboard.wait('w')
                keyboard.add_hotkey('d', lambda: movingbar.move(1))
                keyboard.add_hotkey('a', lambda: movingbar.move(-1))
                keyboard.add_hotkey('s', lambda: ball.pause_game())

        # handle collision with movingbar
        if self.rect.colliderect(movingbar.rect):
            # check if colliding from the top
            if self.speed_y > 0:
                self.speed_y = -abs(self.speed_y)
                
                self.collision['movingbar'] = True
                
    def move(self, move_x, move_y):
        if move_x and not self.collision['movingbar']:
            self.rect.x += int(move_x * self.speed_x / abs(self.speed_x))

        if move_y and not self.collision['horizontal']:
            self.rect.y += int(move_y * self.speed_y / abs(self.speed_y))
            self.collision['movingbar'] = False
    
    def reset(self, x, y, lives):
        # self.ball_rad = 1
        # self.x = x - self.ball_rad
        # self.y = y - self.ball_rad
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        self.speed_x = 4 # speed is frame count at which x or y will be moved
        self.speed_y = -10 # and also the direction in which it will be moved at the frame count
        self.speed_max = 10
        self.collision = {'horizontal':False, 'vertical':False, 'item':True, 'movingbar':False}
        self.game_paused = False
        self.lives = lives
        self.game_over = 0

    def pause_game(self):
        self.game_paused = not self.game_paused

class Level_Selection():
    def __init__(self):
        self.max_len = len(levelmap.keys())-1
        self.selected_level = 0
        self.width = 4
        self.y = 5
        self.callback_img = [colors["block"][int(x)-1] if int(x) else [0,0,0] for string in callback for x in string]
        self.draw()
    
    def select(self, k):
        if self.selected_level + k < 0:
            self.selected_level = 0
        elif self.selected_level + k > self.max_len:
            self.selected_level = self.max_len
        else:
            self.selected_level += k

        self.y = 5 + 7 * int(self.selected_level//4) # WHY DOES THIS NEED AN INT CONVERSION???!?
        self.draw()
    
    def confirm(self):
        self.y -= 1
        self.draw()
    
    def draw(self):
        next_img = self.callback_img[:]
        for x in range(self.width):
            next_img[self.y*28 + (self.selected_level - self.selected_level//4*4) * (2 + self.width) + x + 2] = colors["movingbar"]
        p.set_image(next_img)

class Bomb():
    def __init__(self, rect):
        self.state = 0
        self.rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
        self.framecount = 1
    
    def draw(self, img):
        if not self.state: # first explosion state
            for y in range(self.rect.y, self.rect.y+self.rect.height):
                for x in range(self.rect.x, self.rect.x+self.rect.width):
                    img[y][x] = colors["bombs_exploding"][self.state]
        else:
            # color outer edges
            for y in [self.rect.y, self.rect.y+self.rect.height-1]:
                for x in [self.rect.x+1, self.rect.x+self.rect.width-2]:
                    if y >= 0 and x >= 0 and y <= screen_height-1 and x <= screen_width-1: # coloring is within limits
                        img[y][x] = colors["bombs_exploding"][self.state+1]

            # color explosion circle
            center_x = self.rect.x + self.rect.width/4
            center_y = self.rect.y + self.rect.height/4
            radius = self.state*2 # state 1: radius 2; state 2: radius 4
            for y in range(screen_height-1):
                for x in range(screen_width-1):
                    if abs(x - center_x) + abs(y - center_y) <= radius:
                        if int(y + radius/2) < screen_height and int(x + radius/2) < screen_width: # coloring within limits
                            img[int(y + radius/2)][int(x + radius/2)] = colors["bombs_exploding"][self.state]

        return img

    def explode(self):
        self.framecount += 1
        if self.framecount//30: # every 30 frames a new explosion state is reached
            self.framecount = 1
            self.state += 1
            if self.state > 2:
                return True # finished explosion
            self.rect.update(self.rect.x-2, self.rect.y-2, self.rect.width+4, self.rect.height+4)
            
            # explosion collision logic
            for row in wall.blocks:
                for item in row:
                    if item[1] and item[1] != 9: # inspecting healthy breakable item
                        if self.rect.colliderect(item[0]): # colliding with it
                            # if item[1] > 3:
                            if item[1] == 8: # bomb chain reaction
                                wall.bombs_exploding.append(Bomb(item[0]))
                                # item[1] = 0 # one time use item
                            item[1] = 0
                            # item[1] -= 1 # damage strength-based item :)


def draw_board():
    wall.update_img()
    img = wall.img[:]
    img = movingbar.draw(img)
    img = ball.draw(img)
    p.set_image(img)

# initialize pyghthouse
p = Pyghthouse(username, token, verbosity=VerbosityLevel, frame_rate=fps)
p.start()

def delete_session():
    p.close()
    sleep(4)
    quit()
keyboard.add_hotkey('shift', lambda: delete_session()) # for some reason keyboard can't quit the program on keypress


while 1: # outer game loop
    # level selection animations
    selector = Level_Selection()
    keyboard.add_hotkey('a', lambda: selector.select(-1))
    keyboard.add_hotkey('d', lambda: selector.select(1))
    keyboard.wait('w'); selector.confirm(); keyboard.unhook_all(); sleep(0.4)
    
    # create board
    wall = Wall()
    wall.create(levelmap[[key for key in levelmap.keys()][selector.selected_level]])
    wall.update_img()
    movingbar = Movingbar()
    ball = Ball(movingbar.x + (int(movingbar.width / 2)), movingbar.y - movingbar.height, 3)

    # draw board
    draw_board()

    # wait for player to start
    print("\nLevel has been loaded! Press up to begin.")
    keyboard.wait('w')

    # add hotkey listeners
    keyboard.add_hotkey('d', lambda: movingbar.move(1))
    keyboard.add_hotkey('a', lambda: movingbar.move(-1))
    keyboard.add_hotkey('s', lambda: ball.pause_game())

    framecounter = 0 # for operations that happen every n frame
    # main game loop
    while not ball.game_over:
        clock.tick(fps) # ticks at fps the game runs at

        # game pause functionality
        if ball.game_paused:
            keyboard.unhook_all()
            keyboard.wait('w')
            ball.pause_game()
            sleep(0.01)
            keyboard.add_hotkey('d', lambda: movingbar.move(1))
            keyboard.add_hotkey('a', lambda: movingbar.move(-1))
            keyboard.add_hotkey('s', lambda: ball.pause_game())

        # ball movement through framecount logic
        framecounter += 1
        move_y = (framecounter-1) % abs(ball.speed_y) and not (framecounter % abs(ball.speed_y))
        move_x = (framecounter-1) % abs(ball.speed_max - abs(ball.speed_x)) and not (framecounter % abs(ball.speed_max - abs(ball.speed_x))) and not move_y
        ball.prime_move()
        ball.move(move_x, move_y)

        if framecounter == abs(ball.speed_y): framecounter = 0
        
        # draw board
        # if ball.collision['item']: wall.update_img(); ball.collision['item'] = False #conditional drawing leads to ball trace
        draw_board()

    keyboard.unhook_all()
    # display finish screen
    sleep(0.4)
    if ball.game_over > 0: # WIN
        p.set_image([[218,165,32] if int(x) else [0,0,0] for string in finish_screen[ball.game_over] for x in string])
        if ball.game_over > 0: print("You won!")
    else: # LOSS
        p.set_image([[220,20,60] if int(x) else [0,0,0] for string in finish_screen[ball.game_over] for x in string])
        if ball.game_over < 0: print("You lost!")
    sleep(5.3)