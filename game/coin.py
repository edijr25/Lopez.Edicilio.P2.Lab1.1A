import os
import pygame

from .config import *

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_images):
        super().__init__()

        self.image = pygame.image.load(os.path.join(dir_images, 'coin.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 4

    def update(self):
        self.rect.x -= self.speed

    def stop(self):
        self.kill()