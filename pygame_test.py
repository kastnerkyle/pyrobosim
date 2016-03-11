import pygame
pygame.init()

screen = pygame.display.set_mode((640, 480))

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 255))

box = pygame.Surface((25, 25))
box = box.convert()
box.fill((255, 0, 0))

box_x = 200
box_y = 200

clock = pygame.time.Clock()
playing = True

while playing:
    clock.tick(30)
    for event in pygame.event.get():
        print(event)
        if event.type == pygame.QUIT:
            playing = False
        keys = pygame.key.get_pressed()
        print(keys)
        if keys[pygame.K_UP]:
            box_y -= 5
        if keys[pygame.K_DOWN]:
            box_y += 5
        if keys[pygame.K_LEFT]:
            box_x -= 5
        if keys[pygame.K_RIGHT]:
            box_x += 5
    screen.blit(background, (0, 0))
    screen.blit(box, (box_x, box_y))
    pygame.display.flip()
