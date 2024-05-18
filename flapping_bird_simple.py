import pygame
import os
import random
pygame.font.init()

# левый верхний угол - (0,0)
WIN_WIDTH = 500
WIN_HEIGHT = 800
FPS = 30

img_folder = 'imgs'
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_folder,"bg.png")))

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


  def jump(self):
    self.vel = self.JUMP_VEL # вверх - отрицательая скорость
    self.tick_count = 0
    self.height = self.y

  def move(self):
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


def draw_window(win, bird, pipes, score):
  win.blit(BG_IMG, (0,0))

  for pipe in pipes:
    pipe.draw(win)

  text = STAT_FONT.render(f'Score {score}',1,(255,255,255))
  win.blit(text, (WIN_WIDTH - 10 - text.get_width(),10))

  bird.draw(win)
  pygame.display.update()


# Изначально смотрит вверх!

def main():
  bird = Bird(230,350)
  pipes = [Pipe(730)]
  win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
  pygame.display.set_caption("Flappy Bird")
  clock = pygame.time.Clock()

  run = True
  
  score = 0

  while run:
    clock.tick(FPS)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

      elif event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1:  # Проверка нажатия левой кнопки мыши
              bird.jump()

    add_pipe = False
    rem = []
    for pipe in pipes:
      if pipe.collide(bird):
        run = False  # Stop the game if there's a collision
        break

      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)
      
      if not pipe.passed and pipe.x < bird.x:
        pipe.passed = True
        add_pipe = True


      pipe.move()


    if bird.y + bird.img.get_height() >= WIN_HEIGHT or bird.y < 0:
      run = False
      break

    if not run:
      break

    if add_pipe:
      score += 1
      pipes.append(Pipe(600))

    for r in rem:
      pipes.remove(r)

    if bird.y + bird.img.get_height() >= WIN_HEIGHT:
      pass



    bird.move()
    draw_window(win, bird, pipes,score)

  
  # Display the final score
  text = STAT_FONT.render(f'Final Score: {score}', 1, (255, 255, 255))
  win.blit(text, (WIN_WIDTH // 2 - text.get_width() // 2, WIN_HEIGHT // 2 - text.get_height() // 2))
  pygame.display.update()
  # pygame.time.delay(3000)  # Delay to allow the player to see the score

  # pygame.quit()
  # quit()

  # Wait for left mouse button click to restart
  waiting = True
  while waiting:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              waiting = False
              pygame.quit()
              quit()
          if event.type == pygame.MOUSEBUTTONDOWN:
              if event.button == 1:  # Проверка нажатия левой кнопки мыши
                  waiting = False

  main()







if __name__ == "__main__":
  main()