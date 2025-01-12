from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from math import sin

from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        # self.running = True

        # # groups 
        # self.all_sprites = AllSprites()
        # self.collision_sprites = pygame.sprite.Group()
        # self.bullet_sprites = pygame.sprite.Group()
        # self.enemy_sprites = pygame.sprite.Group()

        # # gun timer
        # self.can_shoot = True
        # self.shoot_time = 0 
        # self.gun_cooldown = 100

        # # enemy timer 
        # self.enemy_event = pygame.event.custom_type()
        # pygame.time.set_timer(self.enemy_event, 300)
        # self.spawn_positions = []
        
        # # audio 
        # self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        # self.shoot_sound.set_volume(0.2)
        # self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('music', 'Main Theme.mp3'))
        self.music.set_volume(0.5)
        self.music.play(loops = -1)

        # setup
        # self.load_images()

        self.state = 'menu'
        self.start_menu()

        # self.setup()

    # def load_images(self):
    #     self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

    #     folders = list(walk(join('images', 'enemies')))[0][1]
    #     self.enemy_frames = {}
    #     for folder in folders:
    #         for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
    #             self.enemy_frames[folder] = []
    #             for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
    #                 full_path = join(folder_path, file_name)
    #                 surf = pygame.image.load(full_path).convert_alpha()
    #                 self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):


        self.state = 'menu'

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0 
        self.gun_cooldown = 100

        # enemy timer 
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []





        
        map = load_pygame('./tiles/рогалик.tmx')

        for x, y, image in map.get_layer_by_name('ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), pygame.transform.scale(image, (32, 32)), self.all_sprites)

        for x, y, image in map.get_layer_by_name('walls').tiles():
            CollisionSprite((x * TILE_SIZE, y * TILE_SIZE), pygame.transform.scale(image, (32, 32)), (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('trees'):
            CollisionSprite((obj.x * 2, obj.y * 2), pygame.transform.scale(obj.image, (32, 32)), (self.all_sprites, self.collision_sprites))
        
        # for obj in map.get_layer_by_name('walls'):
        #     CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # for obj in map.get_layer_by_name('Entities'):
        #     if obj.name == 'Player':
        #         self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
        #         self.gun = Gun(self.player, self.all_sprites)
        #     else:
        #         self.spawn_positions.append((obj.x, obj.y))

        self.player = Player((900, 600), self.all_sprites, self.collision_sprites)


    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.state = False



    def start_menu(self):
        arg_x, arg_y = 0, 0
        background, peter = pygame.image.load('./images/menu/background.png'), pygame.image.load('./images/menu/peter.png')
        while self.state:
            dt = self.clock.tick() / 1200
            arg_x += dt
            arg_y += dt * 5
            dt_x = 100 * sin(arg_x)
            dt_y = 10 * sin(arg_y)
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(background, (-100 + dt_x, 0))
            self.display_surface.blit(peter, (700, 284  + dt_y))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = None
            # self.display_surface.
        

    def run(self):
        while self.state:
            if self.state == 'menu':
                dt = self.clock.tick() / 1000
                # self.display_surface.
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.state = None
                    if event.type == pygame.K_ESCAPE:
                        self.state = 'game'

            if self.state == 'game':
                # dt 
                dt = self.clock.tick() / 2 % 400

                # event loop 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.state = False
                    # if event.type == self.enemy_event:
                    #     Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

                # update 
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()

                # draw
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)            
                # self.all_sprites.draw((600, 600))
                pygame.display.update()

        pygame.quit()


# class Main_menu:
#     def __init__(self):
#         pygame.init()
#         self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
#         self.running = True


if __name__ == '__main__':
    game = Game()
    # game.run()