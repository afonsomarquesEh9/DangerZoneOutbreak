import pygame

from code.Enemy import Enemy
from code.Const import ENTITY_SPEED, ENTITY_SHOT_DELAY
from code.EnemyShot import EnemyShot

class Boss(Enemy):

    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.shot_delay = ENTITY_SHOT_DELAY[self.name]
        self.direction = 1
        self.entering = True
        self.target_x = 400  # final position on the screen

    def move(self):
        # entering of right side of the screen
        if self.entering:
            self.rect.x -= ENTITY_SPEED[self.name]


            if self.rect.x <= self.target_x:
                self.rect.x = self.target_x
                self.entering = False

        # vertical movement
        else:
            self.rect.y += ENTITY_SPEED[self.name] * self.direction

            if self.rect.top <= 40:
                self.direction = 1
            elif self.rect.bottom >= 260:
                self.direction = -1

    def shoot(self):
        self.shot_delay -= 1
        if self.shot_delay <= 0:
            self.shot_delay = ENTITY_SHOT_DELAY[self.name]
            if self.health < 1000:
                self.shot_delay = 35
            pygame.mixer.Sound('./asset/bossshot.wav').play()
            return EnemyShot(
                name=f'{self.name}Shot',
                position=(self.rect.centerx, self.rect.centery)
            )