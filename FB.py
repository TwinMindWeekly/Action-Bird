import pygame
from random import randint

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
running = True

GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0,0,0)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()

TUBE_VELOCITY = 3
TUBE_WIDTH = 50
TUBE_GAP = 175

tube1_x = 600
tube2_x = 800
tube3_x = 1000

BIRD_X = 50
bird_y = 400
BIRD_WIDTH = 35
BIRD_HEIGHT = 35
bird_drop_velocity = 0
GRAVITY = 0.5

score = 0
font = pygame.font.SysFont('sans', 20)

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False
backfround_image = pygame.image.load("BG2.png")
bird_image = pygame.image.load("FB2.png")
bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))

tube1_height = randint(100, 400)
tube2_height = randint(100, 400)
tube3_height = randint(100, 400)

while running:
    clock.tick(60)
    screen.fill(GREEN)
    screen.blit(backfround_image, (0,0))

    # Draw tube
    tube1_rec = pygame.draw.rect(screen, BLUE, (tube1_x, 0, TUBE_WIDTH, tube1_height))
    tube2_rec = pygame.draw.rect(screen, BLUE, (tube2_x, 0, TUBE_WIDTH, tube2_height))
    tube3_rec = pygame.draw.rect(screen, BLUE, (tube3_x, 0, TUBE_WIDTH, tube3_height))

    # Draw sand
    sand_rec = pygame.draw.rect(screen, YELLOW, (0, 575, 400, 50))

    # Draw bird
    bird_rec = screen.blit(bird_image, (BIRD_X, bird_y))

    # Bird  falls
    bird_y += bird_drop_velocity
    bird_drop_velocity += GRAVITY

    # Move tupe to the left
    tube1_x = tube1_x - TUBE_VELOCITY
    tube2_x = tube2_x - TUBE_VELOCITY
    tube3_x = tube3_x - TUBE_VELOCITY

    # Draw tube inverse
    tube1_rec_inv = pygame.draw.rect(screen, BLUE, (tube1_x, tube1_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube1_height - TUBE_GAP))
    tube2_rec_inv = pygame.draw.rect(screen, BLUE, (tube2_x, tube2_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube2_height - TUBE_GAP))
    tube3_rec_inv = pygame.draw.rect(screen, BLUE, (tube3_x, tube3_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube3_height - TUBE_GAP))

    # Genarate new tubes
    if tube1_x < -TUBE_WIDTH:
        tube1_x = 550
        tube1_height = randint(100, 400)
        tube1_pass = False
    if tube2_x < -TUBE_WIDTH:
        tube2_x = 550
        tube2_height = randint(100, 400)
        tube2_pass = False
    if tube3_x < -TUBE_WIDTH:
        tube3_x = 550
        tube3_height = randint(100, 400)
        tube3_pass = False

    score_txt = font.render("Score : " + str(score),True, BLACK)
    screen.blit(score_txt, (5, 5))

        # Update score
    if tube1_x + TUBE_WIDTH <= BIRD_X and tube1_pass == False:
        score += 1
        tube1_pass = True
    if tube2_x + TUBE_WIDTH <= BIRD_X and tube2_pass == False:
        score += 1
        tube2_pass = True
    if tube3_x + TUBE_WIDTH <= BIRD_X and tube3_pass == False:
        score += 1
        tube3_pass = True
    # Check collision
    for tube in [tube1_rec, tube2_rec, tube3_rec, tube1_rec_inv, tube2_rec_inv, tube3_rec_inv, sand_rec]:
        if bird_rec.colliderect(tube):
            pausing = True
            TUBE_VELOCITY = 0
            bird_drop_velocity = 0

            game_over_txt = font.render("Game over, score: " + str(score), True, BLACK)
            screen.blit(game_over_txt, (100, 300))

            press_space_txt = font.render("Press space to continue", True, BLACK)
            screen.blit(press_space_txt, (100, 350))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if pausing:
                    #Reset
                    bird_y = 400
                    score = 0
                    TUBE_VELOCITY = 3
                    tube1_x = 600
                    tube2_x = 800
                    tube3_x = 1000
                    pausing = False

                bird_drop_velocity = 0
                bird_drop_velocity -= 10

    pygame.display.flip()    

pygame.quit()
    
