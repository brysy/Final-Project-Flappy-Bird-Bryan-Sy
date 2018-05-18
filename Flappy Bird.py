import pygame, os, sys, time
from pygame import *
from time import *

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
GRASS_GREEN = (178, 255, 102)
BLACK = (0, 0, 0)

WIN_WIDTH = 480
WIN_HEIGHT = 448
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

B_WIDTH = 24
B_HEIGHT = 24

JUMP_COUNT = 0
JUMP_HEIGHT = -8

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30
GRAVITY = 6
SCORE = 0
TOP_SCORE = 0
TIMES_VALUE = 32
MULT_VAL = 24
screen_rect = pygame.Rect(0, 0, 480, 320)
START = True
start_text = True
GAME = True
user_input = True


class Camera(object):
    def __init__(self, total_width, total_height):
        self.state = pygame.Rect(0, 0, total_width, total_height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, falcon):
        x = -falcon.rect.x + WIN_WIDTH/2
        y = 0

        # Stop scrolling at left edge
        if x > 0:
            x = 0

        self.state = pygame.Rect(x, y, self.state.width, self.state.height)


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Text:
    def __init__(self, size, text, xpos, ypos):
        self.font = pygame.font.SysFont("comicsansms", size)
        self.font2 = pygame.font.SysFont("comicsansms", 90)
        self.image = self.font.render(text, 1, WHITE)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(xpos - self.rect.width/2, ypos - self.rect.height/2)


class Bird(pygame.sprite.Sprite):
    def __init__(self, container, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.jump = False
        self.reg = True
        self.jump_count = 0
        self.jump_counter = 100
        self.fly = 3
        self.speed = JUMP_HEIGHT
        self.image = pygame.Surface((B_WIDTH, B_HEIGHT)).convert()
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = WIN_WIDTH/3
        self.rect.y = y - self.rect.height/2
        self.bird = pygame.image.load("Flappy Images/Bird.png").convert_alpha()
        self.bird = pygame.transform.scale(self.bird, (B_WIDTH, B_HEIGHT))

    def update(self, entities, camera, score, top_score, flappy, back):
        global SCORE, MULT_VAL, GAME, user_input
        # Loop level
        if self.rect.x > 9280:
            self.rect.x = 1248

        # Scoring
        if self.rect.x > TIMES_VALUE * MULT_VAL:
            SCORE += 1
            MULT_VAL += 7
            if MULT_VAL == 290:
                MULT_VAL = 24

        # Jump method
        if self.jump and self.reg:
            self.jump_counter = 0
            self.jump = False
            self.speed = JUMP_HEIGHT

        if self.jump_counter < -JUMP_HEIGHT:
            self.rect.y += self.speed
            self.speed += .7
        elif self.jump_counter < -JUMP_HEIGHT * 2:
            self.rect.y += self.speed
            self.speed += .7
        else:
            self.rect.y += GRAVITY
        self.rect.x += self.fly

        self.jump_counter += 1

        # Top barrier
        if self.rect.y < 0:
            self.rect.y = 0
        # Bottom barrier
        if self.rect.y > WIN_HEIGHT - 52:
            self.rect.y = WIN_HEIGHT - 52

        # Print platforms
        collisions = pygame.sprite.spritecollide(self, entities, False)

        for hit_obstacle in collisions:
            while self.rect.y < WIN_HEIGHT - 51:
                GAME = False
                self.fly = 0
                self.rect.y += GRAVITY
                self.reg = False
                screen.blit(back, screen_rect)
                for t in entities:
                    screen.blit(t.image, camera.apply(t))
                for p in entities:
                    screen.blit(p.image, camera.apply(p))
                screen.blit(self.bird, camera.apply(self))
                screen.blit(score.image, score.rect)
                screen.blit(top_score.image, top_score.rect)
                pygame.display.update()
            sleep(1)
            while user_input:
                for e in pygame.event.get():
                    if e.type == QUIT: raise SystemExit, "QUIT"
                    if e.type == KEYDOWN:
                        if e.key == K_ESCAPE:
                            raise SystemExit, "QUIT"
                        if e.key == K_SPACE:
                            user_input = False
                            reset(flappy)


class Harm(pygame.sprite.Sprite):
    def __init__(self, x, y, Type):
        pygame.sprite.Sprite.__init__(self)
        self.image = Surface((32, 32))
        if Type == "p":
            self.image = pygame.image.load("Flappy Images/Pipe.png").convert_alpha()
        elif Type == "t":
            self.image = pygame.image.load("Flappy Images/Up_Pipe.png").convert_alpha()
        elif Type == "g":
            self.image = pygame.image.load("Flappy Images/Ground.jpg").convert_alpha()
        elif Type == "b":
            self.image = pygame.image.load("Flappy Images/Down_Pipe.png").convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)


def reset(flappy):
    global GAME, SCORE, TOP_SCORE, START, start_text, user_input, MULT_VAL
    SCORE = 0
    flappy.kill()
    GAME = True
    START = True
    start_text = True
    user_input = True
    MULT_VAL = 24
    main()


def main():
    global cameraX, JUMP_COUNT, START, invulnerable, start_text, SCORE, TOP_SCORE
    pygame.display.set_caption("Flappy Bird Clone")
    timer = pygame.time.Clock()

    bg = Surface((32,32))
    bg.convert()
    bg.fill(BLUE)

    flappy = Bird(screen_rect, 32, 224)
    text = Text(25, 'Flappy Bird, Press Space to Start!', screen_rect.centerx, screen_rect.centery)

    back = pygame.image.load("Flappy Images/Background.jpg").convert_alpha()
    entities = pygame.sprite.Group()

    platforms = []

    x = y = 0
    level = [
        "                       P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P            ",
        "                       P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P",
        "                       P      P      P      P      P      B      P      P      P      P      P      P      B      P      P      P      P      P      P      B      B      P      P      P      P      P      P      P      P      P      P      P      P      P      B      P      P      P      P      P",
        "                       P      P      B      P      P             P      P      P      P      P      P             P      P      B      B      P      P                    P      B      P      B      P      P      B      P      P      P      P      P      B             B      P      P      B      P",
        "                       B      P             P      B             P      B      P      P      B      P             B      P                    P      B                    B             P             P      P             B      B      P      P      P                           B      P             P",
        "                              P             B                    P             P      B             P                    B                    P                                         P             P      B                           P      P      P                                  P             B",
        "                              B                           T      P             B                    B      T                                  B             T      T                    B             B                                  P      P      B             T                    B              ",
        "                                     T                    P      B                                         P                    T      T                    P      P             T             T                    T                    B      P             T      P      T                    T       ",
        "                       T             P             T      P             T                    T             P      T             P      P             T      P      P      T      P             P                    P      T      T             B             P      P      P      T             P       ",
        "                       P             P      T      P      P             P             T      P             P      P      T      P      P             P      P      P      P      P             P             T      P      P      P                           P      P      P      P             P      T",
        "                       P      T      P      P      P      P             P      T      P      P      T      P      P      P      P      P      T      P      P      P      P      P      T      P      T      P      P      P      P                    T      P      P      P      P      T      P      P",
        "                       P      P      P      P      P      P      T      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      T             P      P      P      P      P      P      P      P",
        "                       P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      P      T      P      P      P      P      P      P      P      P",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",]

    # build the level
    for row in level:
        for col in row:
            if col == "P":
                p = Harm(x, y, "p")
                platforms.append(p)
                entities.add(p)
            if col == "T":
                t = Harm(x, y, "t")
                platforms.append(t)
                entities.add(t)
            if col == "G":
                g = Harm(x, y, "g")
                platforms.append(g)
                entities.add(g)
            if col == "B":
                b = Harm(x, y, "b")
                platforms.append(b)
                entities.add(b)
            x += 32
        y += 32
        x = 0

    total_level_width  = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(total_level_width, total_level_height)

    while GAME:
        for e in pygame.event.get():
            if e.type == QUIT: raise SystemExit, "QUIT"
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    raise SystemExit, "ESCAPE"
                elif e.key == K_SPACE:
                    flappy.jump = True
                elif e.key == K_LEFT:
                    flappy.jump = True
                elif e.key == K_RIGHT:
                    flappy.jump = True

            if e.type == KEYUP:
                if e.key == K_SPACE:
                    if flappy.jump:
                        flappy.jump = False
                    if e.key == K_LEFT:
                        if flappy.jump:
                            flappy.jump = False
                    if e.key == K_RIGHT:
                        if flappy.jump:
                            flappy.jump = False

        # Add score
        score = Text(20, "SCORE: " + str(SCORE), 75, 50)
        top_score = Text(20, "TOP SCORE: " + str(TOP_SCORE), screen_rect.width - 100, 50)

        # Update objects
        camera.update(flappy)
        flappy.update(entities, camera, score, top_score, flappy, back)

        # draw background
        screen.blit(back, (0,0))

        # Draw groups
        for t in entities:
            screen.blit(t.image, camera.apply(t))
        for p in entities:
            screen.blit(p.image, camera.apply(p))
        if start_text:
            screen.blit(text.image, text.rect)
        screen.blit(score.image, score.rect)
        screen.blit(flappy.bird, camera.apply(flappy))
        screen.blit(top_score.image, top_score.rect)
        timer.tick(60)
        pygame.display.update()

        if SCORE > TOP_SCORE:
            TOP_SCORE = SCORE

        while START:
            for e in pygame.event.get():
                if e.type == QUIT: raise SystemExit, "QUIT"
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        raise SystemExit, "ESCAPE"
                    if e.key == K_SPACE:
                        START = False
                        flappy.jump = True
                        start_text = False
                    if e.key == K_LEFT:
                        START = False
                        flappy.jump = True
                        start_text = False
                    if e.key == K_RIGHT:
                        START = False
                        flappy.jump = True
                        start_text = False
                if e.type == KEYUP:
                    if e.key == K_SPACE:
                        if flappy.jump:
                            flappy.jump = False
                    if e.key == K_LEFT:
                        if flappy.jump:
                            flappy.jump = False
                    if e.key == K_RIGHT:
                        if flappy.jump:
                            flappy.jump = False

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    main()
