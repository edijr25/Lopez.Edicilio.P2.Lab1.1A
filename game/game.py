import os
import sys,json
import pygame
import random

from .config import *
from .platform import Platform
from .player import Player
from .wall import Wall
from .coin import Coin
from .laser import Laser
from .bird import Bird

class Game:
    def __init__(self):
        pygame.init()

        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.level = 0
        self.running = True
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.playing= False

        self.font = pygame.font.match_font(FONT)
        self.nombre_jugador = None
        self.dir = os.path.dirname(__file__)
        self.dir_sounds = os.path.join(self.dir, 'sources/sounds')
        self.dir_images = os.path.join(self.dir, 'sources/images')
        self.menu_sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'menu_music.mp3'))
        self.game_sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'music_juego.mp3'))
        self.sonido_laser  = pygame.mixer.Sound(os.path.join(self.dir_sounds,'laser.wav'))

        self.wall_speed = 2
        self.coin_speed = 3
        self.bird_speed = 2

    def start(self):
        self.menu()
        self.new()

    def new(self):
        self.menu_sound.stop()
        self.game_sound.play(-1)
        self.score = 0
        if self.level == 0:
            self.wall_speed += 1  # Aumentar la velocidad del muro en 5
            self.coin_speed += 0.5
            self.coin_speed += 0.3
        if self.level == 1:
            self.wall_speed += 2.5  # Aumentar la velocidad del muro en 5
            self.coin_speed += 1
            self.bird_speed += 0.8
        if self.level == 2:
            self.wall_speed += 4 # Aumentar la velocidad del muro en 5
            self.coin_speed += 1.5  
            self.bird_speed += 1.2  
        self.playing = True
        self.background = pygame.image.load(os.path.join(self.dir_images, 'fondo.png'))
        self.wall_speed_increment = 1.5
        self.coin_speed_increment = 1.5
        self.bird_speed_increment = 1
        self.generate_elements()
        self.generate_walls()
        self.generate_bird()
        self.run()

    def generate_elements(self):
        self.platform = Platform()
        self.player = Player(100, self.platform.rect.top - 200, self.dir_images)

        self.sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.birds = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()

        self.sprites.add(self.platform)
        self.sprites.add(self.player)
        self.sprites.add(self.lasers)
        self.sprites.add(self.birds)
        
        self.generate_walls()

    def generate_walls(self):
        last_position = WIDTH + 100

        if not len(self.walls) > 0:
            for w in range(0, MAX_WALLS):
                left = random.randrange(last_position + 200, last_position + 400)
                wall = Wall(left, self.platform.rect.top, self.dir_images)
                last_position = wall.rect.right

                self.sprites.add(wall)
                self.walls.add(wall)
                
            
            self.level = self.level + 1
            self.increase_wall_speed()
            self.generate_coins()
            self.generate_bird()
    
    def increase_wall_speed(self):
        for wall in self.walls:
            wall.vel_x += self.level * self.wall_speed_increment
    
    def increase_coin_speed(self):
        for coin in self.coins:
            coin.speed = self.coin_speed + self.level * self.coin_speed_increment
    
    def increase_bird_speed(self):
        for bird in self.birds:
            bird.speed = self.bird_speed + self.level * self.bird_speed_increment

    def generate_coins(self):
        last_position = WIDTH + 100

        for c in range(0, MAX_COINS):
            pos_x = random.randrange(last_position + 180, last_position + 300)
            coin = Coin(pos_x, 100, self.dir_images)
            last_position = coin.rect.right

            self.sprites.add(coin)
            self.coins.add(coin)
        self.increase_coin_speed()

    def generate_bird(self):
        last_position = WIDTH + 100
        bird_distancia = 250
        for c in range(0, MAX_BIRD):
            pos_x = last_position + bird_distancia
            bird = Bird(pos_x, 120, self.dir_images)
            last_position = bird.rect.right 

            self.sprites.add(bird)
            self.birds.add(bird)
        self.increase_bird_speed()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key== pygame.K_p:
                    self.wait()
                if event.key == pygame.K_SPACE:
                    self.player.disparar(self.sonido_laser, SPEED_LASER, self.sprites, self.lasers)
        
        key = pygame.key.get_pressed()

        if key[pygame.K_RIGHT]or key[pygame.K_d]:
            self.player.update()

        elif key[pygame.K_LEFT] or key[pygame.K_a]:
            self.player.update()

        elif key[pygame.K_UP] or key[pygame.K_w]:
            sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'jump.ogg'))
            sound.play()
            self.player.jump()

        elif key[pygame.K_r] and not self.playing and self.game_over:
            self.wait()

        elif key[pygame.K_ESCAPE] :
            self.running = False
            pygame.quit()
            sys.exit()

          
    def draw(self):
        self.surface.blit(self.background, (0, 0))
        self.draw_text()
        self.sprites.draw(self.surface)
        pygame.display.flip()

    def update(self):
        if not self.playing:
            return

        wall = self.player.collide_with(self.walls)
        if wall:
            if self.player.collide_bottom(wall):
                self.player.skid(wall)
            else:
                self.game_over = True
                self.stop()

        coin = self.player.collide_with(self.coins)
        if coin:
            self.score += 0.5
            coin.kill()
            sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'coin.wav'))
            sound.play()
        
        bird = self.player.collide_with(self.birds)
        if bird:
            self.game_over = True
            self.stop()

        for laser in self.lasers:
            if laser.rect.top <= 0:
                laser.kill()
        
            lista = pygame.sprite.spritecollide(laser, self.birds, True)
            if len(lista):
                self.score += 1
                laser.kill()

        for bird in self.birds:
            if bird.rect.top <= 0:
                bird.kill()
        
            lista = pygame.sprite.spritecollide(bird, self.lasers, True)
            if len(lista):
                bird.kill()

            

        self.sprites.update()
        self.player.validate_platform(self.platform)
        self.update_elements(self.walls)
        self.update_elements(self.coins)
        self.update_elements(self.birds)
        self.update_elements(self.lasers)
        self.generate_walls()


    def update_elements(self, elements):
        for element in elements:
            if not element.rect.right > 0:
                element.kill()

    def stop(self):
        self.game_sound.stop()
        sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'lose.wav'))
        sound.play()
        pygame.mixer.music.stop()  # Detener la música cuando se pierde el juego
        pygame.display.flip()
        self.clock.tick(FPS)
        # Eliminar las monedas
        for coin in self.coins:
            coin.kill()
        # Eliminar los muros
        for wall in self.walls:
            wall.kill()

        for bird in self.birds:
            bird.kill()
        
        for laser in self.lasers:
            laser.kill()

        self.player.stop()
        self.platform.stop()
        self.stop_elements(self.walls)
        self.playing = False
        self.ask_player_name()
        self.guardar_score()
        
    def stop_elements(self, elements):
        for element in elements:
            element.stop()

    def score_format(self):
        return 'Score: {}'.format(self.score)

    def level_format(self):
        return 'Level: {}'.format(self.level)

    def draw_text(self):
        self.display_text(self.score_format(), 36, BLACK, WIDTH // 2, TEXT_POSY)
        self.display_text(self.level_format(), 36, BLACK, 60, TEXT_POSY)

        if not self.playing:
            self.surface.fill(BLACK)
            self.display_text('Perdiste', 60, WHITE, WIDTH // 2, HEIGHT // 2)
            self.display_text('Presiona R para ir al menú', 30, WHITE, WIDTH // 2, 50)

    def display_text(self, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)
        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)
        self.surface.blit(text, rect)

    def menu(self):
        self.menu_sound.stop()
        self.surface.fill(BLACK)
        self.display_text('MENU', 48, WHITE, WIDTH // 2, 20)
        self.display_text('1. Iniciar Juego (Nivel 1)', 36, WHITE, WIDTH // 2, 75)
        self.display_text('2. Iniciar Juego (Nivel 2)', 36, WHITE, WIDTH // 2, 120)
        self.display_text('3. Iniciar Juego (Nivel 3)', 36, WHITE, WIDTH // 2, 170)
        self.display_text('4. Instrucciones', 36, WHITE, WIDTH // 2, 220)
        self.display_text('5. Puntajes', 36, WHITE, WIDTH // 2, 270)
        self.display_text('6. Salir', 36, WHITE, WIDTH // 2, 320)
        self.menu_sound.play(-1)
        pygame.display.flip()

        selected_option = None
        while selected_option == None:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_option = 0  # Iniciar Juego (Nivel 1)
                    elif event.key == pygame.K_2:
                        selected_option = 1  # Iniciar Juego (Nivel 2)
                    elif event.key == pygame.K_3:
                        selected_option = 2  # Iniciar Juego (Nivel 3)
                    elif event.key == pygame.K_4:
                        self.show_instructions()
                    elif event.key == pygame.K_5:
                        self.show_scores()
                    elif event.key == pygame.K_6:
                        self.running = False
                        pygame.quit()
                        sys.exit()

        if selected_option in [0, 1, 2]:
            self.level = selected_option  # Almacena el nivel seleccionado
            self.new()

    def display_multiline_text(self, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)
        lines = text.split('\n')  # Divide el texto en líneas separadas por saltos de línea
        line_height = font.get_linesize()

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            rect = text_surface.get_rect()
            rect.midtop = (pos_x, pos_y + i * line_height)
            self.surface.blit(text_surface, rect)

    def show_instructions(self):
        self.surface.fill(BLACK)
        self.display_multiline_text(INSTRUCCIONES,30,WHITE,WIDTH//2, HEIGHT - 400)
        self.display_text('Presiona cualquier tecla para volver al menú', 30, WHITE, WIDTH // 2, HEIGHT - 50)
        pygame.display.flip()
        self.wait()
        self.menu_sound.stop()
        
    def wait(self):
        wait = True

        while wait:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.playing == False:
                        wait = False
                        self.menu()
                    else:
                        wait = False
                    
    def ask_player_name(self):
        input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = True
        text = ''
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                            self.nombre_jugador = text
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self.surface.fill((30, 30, 30))
            pygame.draw.rect(self.surface, color, input_box, 2)

            font = pygame.font.Font(None, 32)
            input_text = font.render(text, True, color)
            self.surface.blit(input_text, (input_box.x + 5, input_box.y + 5))

            input_box.w = max(200, input_text.get_width() + 10)

            pygame.display.flip()

            self.clock.tick(30)

    def guardar_score(self):
        scores = []
        if os.path.exists('scores.json'):
            with open('scores.json', 'r') as file:
                scores = json.load(file)
        scores.append({'Nombre': self.nombre_jugador, 'Puntuacion': self.score, 'Nivel': self.level})
        with open('scores.json', 'w') as file:
            json.dump(scores, file)

    def load_scores(self):
        if os.path.exists('scores.json'):
            with open('scores.json', 'r') as file:
                scores = json.load(file)
                return scores
        else:
            return []

    def display_scores(self):
        scores = self.load_scores()
        self.surface.fill((30, 30, 30))
        y = 100
        for score in scores:
            text = f"{score['Nombre']}: {score['Puntuacion']} {score['Nivel']}"
            self.display_text(text, 30, WHITE, WIDTH // 2, y)
            y += 50
        pygame.display.flip()

    def run_scores(self):
        self.surface.fill(GREEN_LIGHT)
        self.display_scores()
        pygame.display.flip()
        self.wait()

    def show_scores(self):
            self.surface.fill(BLACK)
            self.display_text('Puntuaciones', 48, WHITE, WIDTH // 2, 50)
            scores = self.load_scores()
            y = 130
            for score in scores:
                text = f"{score['Nombre']}: {score['Puntuacion']} Puntos - Nivel {score['Nivel']}"
                self.display_text(text, 30, WHITE, WIDTH // 2, y)
                y += 50
            pygame.display.flip()
            self.wait()