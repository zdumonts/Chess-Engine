import pygame

BASE_IMG_PATH = "src/data/pieces/"
WHITE = (255,255,255)
SIZE = (75, 75)

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img = pygame.Surface.convert_alpha(img)
    img = pygame.transform.scale(img, (SIZE))
    return img