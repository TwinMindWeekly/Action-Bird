import pygame
import random
import math
from config import *

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, image, skin_color=None):
        super().__init__()
        self.original_image = image
        if skin_color:
            self.original_image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, skin_color, (17, 17), 17)
            pygame.draw.circle(self.original_image, WHITE, (25, 12), 4)
            pygame.draw.circle(self.original_image, BLACK, (26, 12), 2)
            
        self.image = self.original_image
        self.base_image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.ghost_mode = False
        self.alpha = 255
        self.is_giant = False

    def update(self, state, current_gravity, is_ghost, is_any_warning, is_giant):
        if state == PLAYING:
            self.velocity += current_gravity
            self.rect.y += self.velocity

            center = self.rect.center

            if is_giant:
                if not self.is_giant:
                    self.is_giant = True
                    self.base_image = pygame.transform.scale(self.original_image, (70, 70))
            else:
                if self.is_giant:
                    self.is_giant = False
                    self.base_image = self.original_image.copy()

            angle = max(-70, min(25, -self.velocity * 3))
            self.image = pygame.transform.rotate(self.base_image, angle)
            self.rect = self.image.get_rect(center=center)
            self.mask = pygame.mask.from_surface(self.image)

            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0
            if self.rect.bottom > HEIGHT - 25:
                return True 

            self.ghost_mode = is_ghost
            base_alpha = 150 if self.ghost_mode else 255

            if is_any_warning:
                if (pygame.time.get_ticks() // 100) % 2 == 0:
                    self.alpha = 50
                else:
                    self.alpha = base_alpha
            else:
                self.alpha = base_alpha

            self.image.set_alpha(self.alpha)

        return False

    def jump(self, current_jump_strength):
        self.velocity = current_jump_strength

class Tube(pygame.sprite.Sprite):
    def __init__(self, x, height, is_top, moving=False):
        super().__init__()
        self.image = pygame.Surface((TUBE_WIDTH, height))
        self.image.fill(BLUE)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        
        self.is_top = is_top
        self.is_moving = moving
        self.base_y = 0 if is_top else height + TUBE_GAP
        self.offset = random.uniform(0, math.pi * 2) 
        
        if is_top:
            self.rect = self.image.get_rect(topleft=(x, 0))
        else:
            self.rect = self.image.get_rect(topleft=(x, self.base_y))
        
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, velocity):
        self.rect.x -= velocity
        
        if self.is_moving:
            move_range = 50
            self.rect.y = self.base_y + math.sin(pygame.time.get_ticks() * 0.003 + self.offset) * move_range
            
        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w = random.randint(60, 120)
        h = w // 2
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (255, 255, 255, random.randint(50, 150)) 
        pygame.draw.ellipse(self.image, color, (0, 0, w, h))
        
        self.rect = self.image.get_rect(topleft=(WIDTH + random.randint(0, 100), random.randint(20, 200)))
        self.speed = random.uniform(0.5, 1.5)

    def update(self, current_vel):
        self.rect.x -= self.speed * (current_vel / INITIAL_TUBE_VELOCITY)
        if self.rect.right < 0:
            self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type 
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
        
        if type == 'LASER': color = RED
        elif type == 'GHOST': color = GRAY
        elif type == 'SLOW': color = PURPLE
        elif type == 'GIANT': color = ORANGE
        else: color = WHITE
        
        pygame.draw.circle(self.image, color, (ITEM_SIZE//2, ITEM_SIZE//2), ITEM_SIZE//2)
        font = pygame.font.SysFont('Arial', 18, bold=True)
        text = font.render(type[0], True, WHITE)
        self.image.blit(text, text.get_rect(center=(ITEM_SIZE//2, ITEM_SIZE//2)))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, velocity):
        self.rect.x -= velocity
        if self.rect.right < 0:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        width = WIDTH - start_pos[0]
        self.image = pygame.Surface((width, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, width, 6))
        pygame.draw.rect(self.image, WHITE, (0, 2, width, 2)) 
        self.rect = self.image.get_rect(midleft=start_pos)
        self.life_timer = pygame.time.get_ticks() + 200

    def update(self, bird_rect):
        self.rect.midleft = (bird_rect.right, bird_rect.centery)
        if pygame.time.get_ticks() > self.life_timer:
            self.kill()

class TrailEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 150

    def update(self):
        self.alpha -= 10
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color, font, size=24):
        super().__init__()
        self.font = font
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = -2
        self.alpha = 255

    def update(self):
        self.rect.y += self.velocity
        self.alpha -= 5
        if self.alpha <= 0:
            self.kill()
        else:
            temp_image = self.image.copy()
            temp_image.set_alpha(self.alpha)
            self.image = temp_image

class Missile(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.missile_image = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.missile_image, (150, 150, 150), (10, 5, 25, 10))
        pygame.draw.polygon(self.missile_image, RED, [(35, 5), (40, 10), (35, 15)])
        pygame.draw.polygon(self.missile_image, ORANGE, [(0, 5), (10, 5), (10, 15), (0, 15)])
        
        self.warning_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.warning_image, RED, [(20, 0), (40, 40), (0, 40)])
        pygame.draw.polygon(self.warning_image, YELLOW, [(20, 5), (35, 35), (5, 35)])
        pygame.draw.rect(self.warning_image, RED, (18, 15, 4, 12))
        pygame.draw.rect(self.warning_image, RED, (18, 30, 4, 4))
        
        self.image = self.warning_image
        self.rect = self.image.get_rect(midright=(WIDTH - 10, y))
        self.y_pos = y
        self.speed = 8
        self.warning_timer = 90 # 1.5s warning

    def update(self, current_vel=0):
        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer % 10 < 5:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(0)
                
            if self.warning_timer == 0:
                self.image = self.missile_image
                self.image.set_alpha(255)
                self.rect = self.image.get_rect(midleft=(WIDTH, self.y_pos))
        else:
            self.rect.x -= self.speed + current_vel
            if self.rect.right < 0:
                self.kill()

class EnergyBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PURPLE, (10, 10), 10)
        pygame.draw.circle(self.image, WHITE, (10, 10), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.angle = random.uniform(-0.2, 0.2)

    def update(self, current_vel=0):
        self.rect.x -= self.speed + current_vel
        self.rect.y += self.angle * self.speed
        if self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self._redraw_base()
        
        self.rect = self.image.get_rect(center=(WIDTH + 100, HEIGHT // 2))
        self.target_x = WIDTH - 80
        self.hp = 10
        self.max_hp = 10
        self.move_speed = 2
        self.direction = 1
        self.shoot_timer = 0
        self.hit_timer = 0

    def _redraw_base(self):
        self.image.fill((0,0,0,0))
        pygame.draw.ellipse(self.image, (100, 100, 100), (10, 40, 80, 40))
        pygame.draw.ellipse(self.image, (150, 200, 255), (30, 20, 40, 40))
        pygame.draw.polygon(self.image, RED, [(20, 60), (30, 80), (40, 60)])
        pygame.draw.polygon(self.image, RED, [(60, 60), (70, 80), (80, 60)])

    def update(self, current_vel=0):
        if self.rect.centerx > self.target_x:
            self.rect.x -= 2
        else:
            self.rect.y += self.move_speed * self.direction
            if self.rect.top < 50:
                self.direction = 1
            elif self.rect.bottom > HEIGHT - 50:
                self.direction = -1

        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer % 4 < 2:
                self.image.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                self._redraw_base()
        else:
            self._redraw_base()

    def take_damage(self):
        self.hp -= 1
        self.hit_timer = 20
        return self.hp <= 0

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(3, 8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-3, -1)
        self.vy = random.uniform(-1, 1)
        self.life = 255

    def update(self, current_vel=0):
        self.rect.x += self.vx - current_vel
        self.rect.y += self.vy
        self.life -= 15
        if self.life <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.life)
