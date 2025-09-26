import pygame

def get_sprite(sheet, x, y, w, h):
    sprite_sheet = sheet
    sprite = pygame.Surface((w, h))
    sprite.set_colorkey((0,255,0))
    sprite.blit(sprite_sheet, (0,0), (x, y, w, h))
    return sprite