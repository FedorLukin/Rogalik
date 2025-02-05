import pygame


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        if target_pos[0] in range(640, 4480):
            self.offset.x = -(target_pos[0] - 640)
        else:
            self.offset.x = 0 if target_pos[0] < 640 else -3840
        if target_pos[1] in range(360, 2520):
            self.offset.y = -(target_pos[1] - 360)
        else:
            self.offset.y = 0 if target_pos[1] < 360 else -2160
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]

        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key=lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
