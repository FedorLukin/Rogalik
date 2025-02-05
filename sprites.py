import pygame


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Plane(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, speed, group):
        super().__init__(group)
        self.image = pygame.image.load('images/1109/plane.png')
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.speed = speed

    def update(self, dt):
        self.rect = self.rect.move((-dt * self.speed, 0))


class Rocket(pygame.sprite.Sprite):
    def __init__(self, vector, directon, surf):
        self.direction = directon
        self.vector = vector
        self.image = surf
        self.rect = self.image.get_rect()
        self.rect.x = vector.x
        self.rect.y = vector.y

    def update(self, dt):
        self.vector += self.direction * dt
        self.rect.center = self.vector

    def draw(self, surface):
        surface.blit(self.image, self.rect)
