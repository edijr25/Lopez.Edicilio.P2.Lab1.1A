import pygame
import os

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_images):
        super().__init__()

        self.images = [
            pygame.image.load(os.path.join(dir_images, '0.png')).convert_alpha(),
            pygame.image.load(os.path.join(dir_images, '1.png')).convert_alpha(),
            pygame.image.load(os.path.join(dir_images, '2.png')).convert_alpha()
        ]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 4
        self.frame_count = 0
        self.frames_por_imagen = 10

    def update(self):
        self.rect.x -= self.speed
        self.frame_count +=1
        if self.frame_count >= self.frames_por_imagen:
        # Cambiar la imagen del bird a medida que se actualiza
            self.frame_count = 0
            self.image_index = (self.image_index + 1) % len(self.images)
            self.image = self.images[self.image_index]