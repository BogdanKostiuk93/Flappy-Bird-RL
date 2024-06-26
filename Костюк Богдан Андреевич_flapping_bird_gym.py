import pygame
import os
import random
import numpy as np
import gym
from gym import spaces
import datetime
import matplotlib.pyplot as plt
import d3rlpy
# from d3rlpy.envs import GymEnv


img_folder = 'imgs'
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bg.png")))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird():
  IMGS = BIRD_IMGS
  # MAX_ROTATION = 25
  # ROT_VEL = 20
  # ANIMATION_TIME = 5

  def __init__(self, x, y,MAX_ROTATION = 25,ROT_VEL = 20,ANIMATION_TIME = 5,JUMP_VEL=-10.5,GRAVITY=1.5):
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.vel = 0
    self.height = self.y
    self.img_count = 0
    self.img = self.IMGS[0]
    self.MAX_ROTATION=MAX_ROTATION
    self.ROT_VEL=ROT_VEL
    self.ANIMATION_TIME=ANIMATION_TIME
    self.JUMP_VEL = JUMP_VEL
    self.GRAVITY = GRAVITY
    # self.GRAVITY = GRAVITY/2 # Приводим к обычной ньютоновской гравитации. Внешний параметр оставляем как есть для совместимости с предыдущей средой


  def jump(self):
    self.vel = self.JUMP_VEL # вверх - отрицательая скорость
    self.tick_count = 0
    self.height = self.y

  def move(self):
    
    # self.vel = self.vel - 2 * self.GRAVITY * self.tick_count
    self.tick_count += 1

    d = self.vel*self.tick_count + self.GRAVITY*self.tick_count**2
    

    if d >= 16:
      d = 16

    if d < 0:
      d -= 2

    self.y = self.y + d

    if d < 0 or self.y < self.height + 50:
      if self.tilt < self.MAX_ROTATION:
        self.tilt = self.MAX_ROTATION

    elif self.tilt > -90: #tilt down
        self.tilt -= self.ROT_VEL

  def draw(self, win):
    self.img_count += 1

    if self.img_count <= self.ANIMATION_TIME:
      self.img = self.IMGS[0]
    elif self.img_count <= self.ANIMATION_TIME*2:
      self.img = self.IMGS[1]
    elif self.img_count <= self.ANIMATION_TIME*3:
      self.img = self.IMGS[2]
    elif self.img_count <= self.ANIMATION_TIME*4:
      self.img = self.IMGS[1]
    elif self.img_count == self.ANIMATION_TIME*4 + 1:
      self.img = self.IMGS[0]
      self.img_count = 0

    if self.tilt <= -80:
      self.img = self.IMGS[1]
      self.img_count = self.ANIMATION_TIME*2

    rotated_image = pygame.transform.rotate(self.img, self.tilt)
    new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
    win.blit(rotated_image, new_rect.topleft)

  def get_mask(self):
    return pygame.mask.from_surface(self.img)

class BirdWithVelocity(Bird):
    def __init__(self, x, y, MAX_ROTATION=25, ROT_VEL=20, ANIMATION_TIME=5, JUMP_VEL=-10.5, GRAVITY=1.5):
        super().__init__(x, y, MAX_ROTATION, ROT_VEL, ANIMATION_TIME, JUMP_VEL, GRAVITY)

    def jump(self):
        self.vel = self.JUMP_VEL  # вверх - отрицательая скорость
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1


        if self.tick_count > 1:
          # Обновление скорости с учетом гравитации
          self.vel += self.GRAVITY/2 # Приводим гравитацию к обычной физической (внешнюю оставим для совместимости с исторической средой)

        if self.vel >= - self.JUMP_VEL:
            self.vel = -self.JUMP_VEL

        # Обновление положения с учетом скорости
        self.y += self.vel

        # if self.y < 0:
        #     self.y = 0
        #     self.vel = 0

        # if self.y + self.img.get_height() >= WIN_HEIGHT:
        #     self.y = WIN_HEIGHT - self.img.get_height()
        #     self.vel = 0

        # Обновление наклона (tilt) птицы в зависимости от скорости
        if self.vel < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        elif self.tilt > -90:
            self.tilt -= self.ROT_VEL



class Pipe:
  # GAP = 250
  # VEL = 5

  def __init__(self, x, VEL=5, GAP=250):
    self.x = x
    self.height = 0
    self.GAP = GAP
    self.VEL = VEL


    self.top = 0
    self.bottom = 0
    self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    self.PIPE_BOTTOM = PIPE_IMG

    self.passed = False
    self.set_height()

  def set_height(self):
    self.height = random.randrange(50,450)
    self.top = self.height - self.PIPE_TOP.get_height()
    self.bottom = self.height + self.GAP

  def move(self):
    self.x -= self.VEL

  def draw(self,win):
    win.blit(self.PIPE_TOP, (self.x,self.top))
    win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

  def collide(self,bird):
    bird_mask = bird.get_mask()
    top_mask = pygame.mask.from_surface(self.PIPE_TOP)
    bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

    top_offset = (self.x - bird.x, self.top - round(bird.y))
    bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

    b_point = bird_mask.overlap(bottom_mask,bottom_offset)
    t_point = bird_mask.overlap(top_mask,top_offset)

    if t_point or b_point:
      return True
    return False


def draw_window(win, bird, pipes, score, WIN_WIDTH):
  win.blit(BG_IMG, (0,0))

  for pipe in pipes:
    pipe.draw(win)

  text = STAT_FONT.render(f'Score {score}',1,(255,255,255))
  win.blit(text, (WIN_WIDTH - 10 - text.get_width(),10))

  bird.draw(win)
  pygame.display.update()


# Изначально смотрит вверх!


class FlappingBirdEnv(gym.Env):
    def __init__(self, VEL=5, GAP=250, MAX_ROTATION=25, ROT_VEL=20, ANIMATION_TIME=5, JUMP_VEL=-10.5, 
                 GRAVITY=1.5, WIN_WIDTH=500, WIN_HEIGHT=800, FPS=20, logs=True, max_score=200, Bird = Bird, Pipe=Pipe):
        super(FlappingBirdEnv, self).__init__()
        self.WIN_WIDTH = WIN_WIDTH
        self.WIN_HEIGHT = WIN_HEIGHT
        self.FPS = FPS
        self.VEL = VEL
        self.GAP = GAP
        self.MAX_ROTATION = MAX_ROTATION
        self.ROT_VEL = ROT_VEL
        self.ANIMATION_TIME = ANIMATION_TIME
        self.JUMP_VEL = JUMP_VEL
        self.GRAVITY = GRAVITY
        self.logs = logs
        self.max_score = max_score
        self.Bird = Bird
        self.Pipe = Pipe

        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()

        self.action_space = spaces.Discrete(2)  # 0: do nothing, 1: jump
        self.observation_space = spaces.Box(low=0, high=255, shape=(3, self.WIN_HEIGHT, self.WIN_WIDTH), dtype=np.uint8)

        self.reset()

    def reset(self):
        self.bird = self.Bird(230, 350, self.MAX_ROTATION, self.ROT_VEL, self.ANIMATION_TIME, self.JUMP_VEL, self.GRAVITY)
        self.pipes = [self.Pipe(730, self.VEL, self.GAP)]
        self.score = 0
        self.done = False
        info = {} # Для своместимость с d3rlpy
        return self._get_observation(), info

    def step(self, action):
        if action == 1:
            self.bird.jump()

        self.bird.move()
        rem = []
        add_pipe = False

        for pipe in self.pipes:
            if pipe.collide(self.bird):
                self.done = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            self.score += 1
            self.pipes.append(Pipe(600, self.VEL, self.GAP))

        for r in rem:
            self.pipes.remove(r)

        if self.bird.y + self.bird.img.get_height() >= self.WIN_HEIGHT or self.bird.y < 0:
            self.done = True

        if self.score >= self.max_score:
            self.done = True

        observation = self._get_observation()

        reward = 0.001
        if not self.done and add_pipe:
          reward = 1

        info = {"score": self.score}

        if self.done and self.logs:
            self._log_game_result()

        
        truncated = False #Для совместимости с d3rply

        # self.render()


        return observation, reward, self.done, truncated, info

    def render(self):
        draw_window(self.win, self.bird, self.pipes, self.score, self.WIN_WIDTH)
        self.clock.tick(self.FPS)

    def _get_observation(self):
        obs = np.array(pygame.surfarray.pixels3d(self.win)).transpose((2, 1, 0))
        return obs
    
    def _log_game_result(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("games_played.txt", "a") as f:
            f.write(f"{timestamp}\t{self.score}\n")

    def close(self):
        pygame.quit()


class FlappingBirdEnvNumerical(FlappingBirdEnv):
    def __init__(self, VEL=5, GAP=250, MAX_ROTATION=25, ROT_VEL=20, ANIMATION_TIME=5, JUMP_VEL=-10.5, 
                 GRAVITY=1.5, WIN_WIDTH=500, WIN_HEIGHT=800, FPS=20, logs=True, max_score=200, Bird = Bird, Pipe=Pipe):
        super(FlappingBirdEnvNumerical, self).__init__(VEL, GAP, MAX_ROTATION, ROT_VEL, ANIMATION_TIME, JUMP_VEL, 
                                                        GRAVITY, WIN_WIDTH, WIN_HEIGHT, FPS, logs, max_score, Bird, Pipe)
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)

    def _get_observation(self):
        e1 = self.bird.y / self.WIN_HEIGHT                    # bird pos (нормализовано)
        e2 = self.bird.vel / (-self.bird.JUMP_VEL)               # bird vel (нормализовано)
        # Найдем ближайшую трубу, которая еще не пройдена
        nearest_pipe = None
        for pipe in self.pipes:
            if pipe.x + pipe.PIPE_TOP.get_width() >= self.bird.x:
                nearest_pipe = pipe
                break
        
        if nearest_pipe is None:
            nearest_pipe = self.pipes[0]

        e3 = (nearest_pipe.x - self.bird.x) / (self.WIN_WIDTH - 50)   # dist to Pipe (нормализовано)
        e4 = nearest_pipe.top / self.WIN_HEIGHT                       # pipe top (нормализовано)
        e5 = nearest_pipe.bottom / self.WIN_HEIGHT                    # pipe bot (нормализовано)
        return np.array([e1, e2, e3, e4, e5], dtype=np.float32)

    def render(self):
        # Не изменяем метод r
        super().render()


# reconstruct full setup from a d3 file
dql_loaded = d3rlpy.load_learnable("simple_bird_numerical_model_196000.d3")


import torch
import matplotlib.pyplot as plt
# Создание среды
env = FlappingBirdEnvNumerical(FPS=60, logs=False, JUMP_VEL= -3, Bird = Bird)

# Тестирование модели
obs, _ = env.reset()
done = False
while not done:
    # Добавляем размерность батча
    obs = np.expand_dims(obs, axis=0)
    action = dql_loaded.predict(obs)[0]
    # print(f'predicted action = {action}')
    obs, reward, done, truncated, info = env.step(action)
    env.render()

    # # Показать изображение наблюдения (опционально)
    # plt.imshow(obs[0,:,:], cmap='gray')  # Используем cmap='gray' для одноцветного изображения
    # plt.axis('off')
    # plt.show()

env.close()


# step_counter = 0
# cum_reward = 0
# if __name__ == "__main__":
#     env = FlappingBirdEnvNumerical(FPS=30,JUMP_VEL=-3,Bird=BirdWithVelocity)
#     episodes = 1
#     for episode in range(episodes):
#         step_counter = 0
#         cum_reward = 0
        
#         obs = env.reset()
#         done = False
#         while not done:
#             action = 0
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                         pygame.quit()
#                         quit()
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if event.button == 1:  # Проверка нажатия левой кнопки мыши
#                         action = 1
#             # action = env.action_space.sample()
#             obs, reward, done, truncated, info = env.step(action)
#             print(obs)
#             step_counter += 1
#             cum_reward += reward
#             env.render()
#         print(f'Number of steps = {step_counter}')
#         print(f'Cumulative reward = {cum_reward}')
#         print(env.FPS)


#         with open("maual-results-FPS.csv", "a") as f:
#             f.write(f"{env.FPS},{step_counter},{cum_reward}\n")
#     env.close()

# # env = FlappingBirdEnv(FPS=30)

# # for _ in range(10):
# #   action = env.action_space.sample()
# #   print(action)