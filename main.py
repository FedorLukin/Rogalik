from pytmx.util_pygame import load_pygame
from math import sin, degrees, atan2
from groups import AllSprites
from player import Player
from random import randint
from sprites import *

import sys
import pygame


class Game:
    def __init__(self) -> None:
        """
        Инициализация основных переменных, создание спрайтов и игровой карты.
        """
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)
        pygame.display.set_caption('Peter the sigma')
        self.music_channel = pygame.mixer.Channel(0)
        self.sound_channel = pygame.mixer.Channel(1)
        self.display_surface = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 64)
        self.state = 'menu'
        self.dialog = 0
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        map = load_pygame('./tiles/рогалик.tmx')
        for x, y, image in map.get_layer_by_name('ground').tiles():
            Sprite((x * 32, y * 32), pygame.transform.scale(image, (32, 32)), self.all_sprites)

        for x, y, image in map.get_layer_by_name('walls').tiles():
            CollisionSprite((x * 32, y * 32), pygame.transform.scale(image, (32, 32)),
                            (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('trees'):
            CollisionSprite((obj.x * 2, obj.y * 2), pygame.transform.scale(obj.image, (32, 32)),
                            (self.all_sprites, self.collision_sprites))

        self.player = Player((900, 600), self.all_sprites, self.collision_sprites)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def game(self) -> None:
        """
        Основная часть игры, запускает катсцены по мере прохождения игры.
        """
        music = pygame.mixer.Sound('music/MainTheme.mp3')
        self.music_channel.play(music, loops=-1)
        list_image1 = pygame.image.load('images/misc/list1.png')
        list_image2 = pygame.image.load('images/misc/list2.png')
        while True:
            if self.player.rect.x in range(2630, 2690) and self.player.rect.y in range(1200, 1230) and self.dialog == 0:
                self.music_channel.pause()
                self.cutscene_1()
                self.music_channel.unpause()
            if self.player.rect.x in range(2990, 3310) and self.player.rect.y in range(2430, 2440) and self.dialog == 1:
                self.music_channel.stop()
                self.cutscene_2()
                self.state = 'mini_game'
                return

            dt = self.clock.tick() / 1000
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.player.rect.center)
            self.display_surface.blit(list_image1, (0, 550)) if self.dialog == 0\
                else self.display_surface.blit(list_image2, (0, 550))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

    def cutscene_1(self) -> None:
        """
        Катсцена №1, по завершении игрок получает новое задание.
        """
        channel = pygame.mixer.Channel(1)
        channel.play(pygame.mixer.Sound('music/Dialog1.mp3'))
        background = pygame.image.load('images/misc/Cutscene1.png')
        self.display_surface.blit(background, (0, 0))
        pygame.display.update()

        while channel.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

        self.dialog += 1
        self.clock.tick()

    def cutscene_2(self) -> None:
        """
        Катсцена №2, по  завершении запускает мини-игру.
        """
        pygame.mixer.music.load('music/Dialog2.mp3')
        pygame.mixer.music.play(loops=0)
        background = pygame.image.load('images/misc/Cutscene2.png')
        self.display_surface.blit(background, (0, 0))
        pygame.display.update()

        while pygame.mixer.music.get_pos() != -1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

        self.dialog += 1

    def mini_game(self) -> None:
        """
        Мини-игра необходимая для завершения игры.
        """
        # кастомный курсор-прицел
        cursor_image = pygame.image.load('images/misc/pricel1.png')
        cursor_image = pygame.transform.scale(cursor_image, (20, 20))
        color_cursor = pygame.cursors.Cursor((10, 10), cursor_image)
        pygame.mouse.set_cursor(color_cursor)

        # загрузка изображений
        detonation = pygame.image.load('images/1109/explosion.png')
        rocket_image = pygame.image.load('images/1109/rocket.png')
        background1 = pygame.image.load('images/1109/background.png')
        background2 = pygame.image.load('images/1109/background1.png')
        ded = pygame.image.load('images/1109/ded.png'),
        plane_explosion_image = pygame.image.load('images/1109/explosion1.png')

        # загрузка музыки и звуков
        launch_sound = pygame.mixer.Sound('music/launch.mp3')
        explosion_sound = pygame.mixer.Sound('music/plane_explosion.mp3')
        pygame.mixer.music.load('music/R32200G.mp3')
        pygame.mixer.music.play()
        explosion_sound.set_volume(0.3)
        launch_sound.set_volume(0.2)

        # основные переменные
        launched_rocket, target_vector = None, None
        planes = pygame.sprite.Group()
        planes_count = 0
        explosions = []

        while True:
            dt = self.clock.tick() / 200
            time = pygame.mixer.music.get_pos() // 1000

            # конец игры
            if planes_count > 1 or time == -1:
                pygame.mixer.music.stop()
                self.end_game('lose') if planes_count > 1 else self.end_game('win')

            # рендер фона и взрывов
            self.display_surface.blit(background1, (0, 0)) if planes_count == 0\
                else self.display_surface.blit(background2, (0, 0))
            self.display_surface.blit(ded, (60, 550))
            pygame.draw.line(self.display_surface, 'GRAY', (600, 0), (600, 720), 1)
            for explosion in explosions:
                self.display_surface.blit(plane_explosion_image, explosion[0])
                explosion[1] -= dt
                if explosion[1] <= 0:
                    explosions.remove(explosion)

            # рендер выпущенной ракеты
            if launched_rocket:
                if launched_rocket.vector.x < 400:
                    self.display_surface.blit(detonation, (-38, 575))
                if launched_rocket.vector.x < 1280 and launched_rocket.vector.y > 0:
                    launched_rocket.draw(self.display_surface)
                    launched_rocket.update(dt)
                else:
                    launched_rocket = None

            # рендер самолётов и коллизия с ракетойы
            if planes:
                for plane in planes:
                    if plane.rect.clipline((380, 0), (380, 720)):
                        planes_count += 1
                        explosion_sound.play()
                        planes.remove(plane)
                    if launched_rocket:
                        crushed_planes = pygame.sprite.spritecollide(launched_rocket, planes, False)
                        for plane in crushed_planes:
                            if plane.rect.x >= 500:
                                explosion_sound.play()
                                explosions.append([(plane.rect.x, plane.rect.y), 2])
                                launched_rocket = None
                                planes.remove(plane)

                planes.draw(self.display_surface)
                planes.update(dt)

            # случайная генерация самолётов
            if randint(1, 950 - time * 10) == 17:
                if len(planes) <= 3:
                    speed = randint(150, 250)
                    Plane(1280, randint(20, 500), speed, planes)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                # запуск ракеты при клике мышью
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    target_x, target_y = pygame.mouse.get_pos()
                    if target_x >= 600 and not launched_rocket:
                        target_vector, rocket_vector = pygame.Vector2(target_x, target_y), pygame.Vector2(205, 555)
                        direction = target_vector - rocket_vector
                        ang = degrees(atan2(rocket_vector.y - target_vector.y, target_vector.x - rocket_vector.x))
                        rotated_rocket = pygame.transform.rotate(rocket_image, ang)
                        launched_rocket = Rocket(rocket_vector, direction, rotated_rocket)
                        launch_sound.play()

    def menu(self) -> None:
        """
        Главное меню игры, появляется при запуске игры.
        """
        arg_x, arg_y = 0, 0
        music = pygame.mixer.Sound('music/MenuTheme.mp3')
        self.music_channel.play(music, loops=-1)
        background = pygame.image.load('./images/menu/background.png')
        peter, title = pygame.image.load('./images/menu/peter.png'), pygame.image.load('./images/menu/title.png')
        text = self.font.render('press f to play petersigma', False, (255, 255, 255))

        while True:
            dt = self.clock.tick() / 1200
            arg_x += dt
            arg_y += dt * 5
            dt_x = 100 * sin(arg_x)
            dt_y = 10 * sin(arg_y)
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(background, (-100 + dt_x, 0))
            self.display_surface.blit(peter, (700, 284 + dt_y))
            self.display_surface.blit(title, (50, 50))
            self.display_surface.blit(text, (95, 435))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                # запуск игры при нажатии
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.music_channel.stop()
                        self.state = 'game'
                        return

    def end_game(self, scenary: str) -> None:
        match scenary:
            case 'win':
                background_image = pygame.image.load('images/1109/GoodEnding.png')
                pygame.mixer.music.load('music/GoodEnding.mp3')
            case 'lose':
                background_image = pygame.image.load('images/1109/BadEnding.png')
                pygame.mixer.music.load('music/BadEnding.mp3')
                pygame.mixer.music.set_volume(0.4)
        self.display_surface.blit(background_image, (0, 0))
        pygame.display.update()
        pygame.mixer.music.play()
        timer = 60
        while True:
            dt = self.clock.tick() / 200
            timer -= dt
            if timer <= 0:
                self.terminate()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

    def run(self) -> None:
        while True:
            match self.state:
                case 'menu': self.menu()
                case 'game': self.game()
                case 'mini_game': self.mini_game()


if __name__ == '__main__':
    game = Game()
    game.run()
