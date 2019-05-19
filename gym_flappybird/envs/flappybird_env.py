import pygame
import random
import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding


#TODO Human/Not Human Mode
#TODO Define image_load function

FPS                 = 60
BACKGROUND          = pygame.image.load("assets/background.png")
BIRD                = {
    "up"    : pygame.image.load("assets/00.png"),
    "mid"   : pygame.image.load("assets/11.png"),
    "down"  : pygame.image.load("assets/22.png")
}
BASE                = {
    "1"     : pygame.image.load("assets/base.png"),
    "2"     : pygame.image.load("assets/base.png")
}
PIPE                = {
    "bottom": pygame.image.load("assets/bottom3.png"),
    "top"   : pygame.image.load("assets/top3.png")
}
NUMBER              = [
        pygame.image.load('assets/0.png'),
        pygame.image.load('assets/1.png'),
        pygame.image.load('assets/2.png'),
        pygame.image.load('assets/3.png'),
        pygame.image.load('assets/4.png'),
        pygame.image.load('assets/5.png'),
        pygame.image.load('assets/6.png'),
        pygame.image.load('assets/7.png'),
        pygame.image.load('assets/8.png'),
        pygame.image.load('assets/9.png')
]
BASE_WIDTH          = BASE["1"].get_width()
BASE_HEIGHT         = BASE["1"].get_height()
SCREEN_WIDTH        = BACKGROUND.get_width()
SCREEN_HEIGHT       = BACKGROUND.get_height()
BIRD_WIDTH          = BIRD["up"].get_width()
BIRD_HEIGHT         = BIRD["up"].get_height()
PIPE_WIDTH          = PIPE["bottom"].get_width()
PIPE_HEIGHT         = PIPE["bottom"].get_height()
GAP_SİZE            = 190

class FlappyBirdEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.init()
    def __init__(self):
        self.reset()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=np.array([0,0]), high=np.array([SCREEN_HEIGHT / 2 - 100, SCREEN_HEIGHT - BASE_HEIGHT - 100]), dtype=np.float32)
    def step(self, action):
        if action:
            self.velocity_y = 1
            self.up_S = 1
        if self.up_S >= 10: #10
            if self.bird_position["y"] + BASE_HEIGHT + BIRD_HEIGHT < SCREEN_HEIGHT:
                self.bird_position["y"] = int(self.bird_position["y"] + self.velocity_y)
                self.velocity_y += self.acceleration_y
                reward = 0.1
        else:
            self.bird_position["y"] -= 4  # 7
            self.up_S += 1
            reward = 0.1
        self.move_pipe()
        done = self.check_pipe_collision()
        if not done and self.check_score(): reward = 1
        elif done: reward = -1
        if self.bird_position["x"] < self.pipe_position[0]["x"]:
            obj = [self.pipe_position[0]["x"] - self.bird_position["x"],
                   self.pipe_position[0]["y"]- self.bird_position["y"]]
        else:
            obj = [self.pipe_position[1]["x"] - self.bird_position["x"],
                   self.pipe_position[1]["y"] - self.bird_position["y"]]
        return obj, reward, done, {}
    def reset(self):
        self.score = 0
        self.score_flag = True
        self.acceleration_y = 0.3
        self.velocity_x = 2
        self.velocity_y = 0.5
        self.base_position = [
            {
                "x": 0,
                "y": SCREEN_HEIGHT - BASE_HEIGHT
            },
            {
                "x": SCREEN_WIDTH,
                "y": SCREEN_HEIGHT - BASE_HEIGHT
            }
        ]
        self.pipe_position = [
            {
                "x": SCREEN_WIDTH,
                "y": self.random_pipe()
            },
            {
                "x": SCREEN_WIDTH,
                "y": self.random_pipe()
            },
            {
                "x": SCREEN_WIDTH,
                "y": self.random_pipe()
            }
        ]
        self.bird_position = {
            "x": 30,
            "y": 250
        }
        self.up_S = 10
        return [self.pipe_position[0]["x"] - self.bird_position["x"],
                   self.pipe_position[0]["y"]- self.bird_position["y"]]
    def render(self, mode='human', close=False):
        self.change_bird_index()
        self.move_base()

        self.screen.blit(BACKGROUND, (0, 0))
        #TODO pygame.draw.line(self.screen, (255,0,0),(self.bird_position.values()), ())
        for i in range(0, 3):
            self.screen.blit(PIPE["bottom"], (self.pipe_position[i]["x"], self.pipe_position[i]["y"]))
            self.screen.blit(PIPE["top"],
                             (self.pipe_position[i]["x"], self.pipe_position[i]["y"] - GAP_SİZE - PIPE_HEIGHT))
        self.screen.blit(BASE["1"], (self.base_position[0]["x"], self.base_position[0]["y"]))
        self.screen.blit(BASE["2"], (self.base_position[1]["x"], self.base_position[1]["y"]))
        self.screen.blit(BIRD[list(BIRD.keys())[self.bird_index[1] % 3]],
                         (self.bird_position["x"], self.bird_position["y"]))
        number_width = 0
        total_width = sum([i.get_width() for i in self.show_score()])
        for i in self.show_score():
            self.screen.blit(i, ((SCREEN_WIDTH - total_width) / 2 + number_width, 120))
            number_width += i.get_width()
        pygame.display.update()
        self.clock.tick(FPS)

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    bird_index = [1, 1]
    def change_bird_index(self):
        if self.bird_index[0] == 31:
            self.bird_index = [1, 1]
        else:
            if self.bird_index[0] % 10 == 0:
                self.bird_index[1] += 1
                self.bird_index[0] += 1
            else:
                self.bird_index[0] += 1

    def move_base(self):
        if self.base_position[0]["x"] + BASE_WIDTH <= 0:
            self.base_position[0]["x"] = SCREEN_WIDTH
            self.base_position[1]["x"] = 0
        elif self.base_position[1]["x"] + BASE_WIDTH <= 0:
            self.base_position[1]["x"] = SCREEN_WIDTH
            self.base_position[0]["x"] = 0
        else:
            self.base_position[0]["x"] -= self.velocity_x
            self.base_position[1]["x"] -= self.velocity_x

    def random_pipe(self):
        return random.randint(SCREEN_HEIGHT / 2 - 100, SCREEN_HEIGHT - BASE_HEIGHT - 100)

    def move_pipe(self):
        if self.pipe_position[0]["x"] <= SCREEN_WIDTH / 2:
            self.pipe_position[1]["x"] -= self.velocity_x
        if self.pipe_position[0]["x"] <= 0:
            self.pipe_position[2]["x"] -= self.velocity_x
        self.pipe_position[0]["x"] -= self.velocity_x
        if self.pipe_position[0]["x"] <= 0 - PIPE_WIDTH:
            self.pipe_position.append({
                "x": SCREEN_WIDTH,
                "y": self.random_pipe()
            })
            self.pipe_position.pop(0)
            self.score_flag = True

    def check_score(self):
        if self.score_flag:
            if self.bird_position["x"] >= self.pipe_position[0]["x"]:
                self.score += 1
                self.score_flag = False
                self.show_score()
                return True

    def check_pipe_collision(self):
        if self.bird_position["x"] + BIRD_WIDTH >= self.pipe_position[0]["x"] and self.bird_position["x"] <= self.pipe_position[0]["x"] + PIPE_WIDTH:
            if self.bird_position["y"] + BIRD_HEIGHT >= self.pipe_position[0]["y"] or self.bird_position["y"] <= self.pipe_position[0]["y"] - GAP_SİZE:
                return True
            else:
                return False
        elif self.bird_position["y"] + BASE_HEIGHT + BIRD_HEIGHT > SCREEN_HEIGHT:
            return True
        elif self.bird_position["y"] <= 0:
            return True
        else:
            return False
    def show_score(self):
        score_lenght = len(str(self.score))
        numbers = []
        for i in range(score_lenght):
            numbers.append(NUMBER[int(str(self.score)[i])])
        return numbers
