
import pygame, os
from .config import *


class Laser(pygame.sprite.Sprite):
    def __init__(self, midBottom: tuple, speed):
        super().__init__()
        
        self.dir = os.path.dirname(__file__)
        dir_images = os.path.join(self.dir, 'sources/images')
        self.image = pygame.image.load(os.path.join(dir_images, 'laser.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = midBottom
        self.rect.y += 40  
        self.vel_x = speed


    def update(self):
        self.rect.x += self.vel_x
    
    def stop(self):
        self.kill()