import pygame
import random
import math
import os
import json

# --- Cấu hình & Hằng số ---
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.4
JUMP_STRENGTH = -7
INITIAL_TUBE_VELOCITY = 3
TUBE_WIDTH = 60
TUBE_GAP = 180
ITEM_SIZE = 30
ITEM_CHANCE = 0.15  # 15% tỷ lệ xuất hiện vật phẩm
POWERUP_DURATION = 5000  # 5 giây (ms)
WARNING_TIME = 1500  # 1.5 giây (ms) cảnh báo hết giờ

# Thư mục tài nguyên
ASSETS_DIR = "assets"
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SND_DIR = os.path.join(ASSETS_DIR, "sounds")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 220, 0)
GRAY = (150, 150, 150)
PURPLE = (180, 50, 255)
ORANGE = (255, 120, 0)

# Trạng thái Game
LOBBY = "LOBBY"
PLAYING = "PLAYING"
GAME_OVER = "GAME_OVER"
SETTINGS = "SETTINGS"
SHOP = "SHOP"
ACHIEVEMENTS = "ACHIEVEMENTS"

class Config:
    def __init__(self):
        self.master_volume = 1.0  # 0% - 100% (0.0 - 1.0)
        self.bgm_enabled = True

config = Config()

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, image, skin_color=None):
        super().__init__()
        self.original_image = image
        if skin_color:
            # Tạo skin từ màu sắc (nếu không có ảnh)
            self.original_image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, skin_color, (17, 17), 17)
            # Thêm mắt cho vui
            pygame.draw.circle(self.original_image, WHITE, (25, 12), 4)
            pygame.draw.circle(self.original_image, BLACK, (26, 12), 2)
            
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.ghost_mode = False
        self.alpha = 255

    def update(self, state, current_gravity, is_ghost, is_any_warning, is_giant):
        if state == PLAYING:
            self.velocity += current_gravity
            self.rect.y += self.velocity
            
            # Cập nhật kích thước khi ở chế độ Giant
            if is_giant:
                if self.image.get_width() == 35: # Chỉ scale nếu chưa to
                    new_size = (70, 70)
                    self.image = pygame.transform.scale(self.original_image, new_size)
                    self.rect = self.image.get_rect(center=self.rect.center)
                    self.mask = pygame.mask.from_surface(self.image)
            else:
                if self.image.get_width() == 70: # Thu nhỏ lại nếu hết mode
                    new_size = (35, 35)
                    self.image = pygame.transform.scale(self.original_image, new_size)
                    self.rect = self.image.get_rect(center=self.rect.center)
                    self.mask = pygame.mask.from_surface(self.image)

            # Giới hạn biên
            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0
            if self.rect.bottom > HEIGHT - 25:
                return True # Rơi xuống đất
            
            self.ghost_mode = is_ghost
            base_alpha = 150 if self.ghost_mode else 255
            
            # Nhấp nháy nếu có bất kỳ hiệu ứng nào sắp hết giờ
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
        self.offset = random.uniform(0, math.pi * 2) # Độ lệch pha ngẫu nhiên
        
        if is_top:
            self.rect = self.image.get_rect(topleft=(x, 0))
        else:
            self.rect = self.image.get_rect(topleft=(x, self.base_y))
        
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, velocity):
        self.rect.x -= velocity
        
        # Logic dao động lên xuống
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
        color = (255, 255, 255, random.randint(50, 150)) # Alpha ngẫu nhiên
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
        self.type = type # 'LASER', 'GHOST', 'SLOW', 'GIANT'
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
        # Tia laser bắt đầu từ miệng chim và kéo dài hết màn hình theo chiều ngang
        width = WIDTH - start_pos[0]
        self.image = pygame.Surface((width, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, width, 6))
        pygame.draw.rect(self.image, WHITE, (0, 2, width, 2)) # Lõi sáng
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
            # Tạo bản sao có hỗ trợ alpha
            temp_image = self.image.copy()
            temp_image.set_alpha(self.alpha)
            self.image = temp_image

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Action Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.medium_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.large_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Load assets
        self.bg_img = self.load_image("BG2.png", (WIDTH, HEIGHT))
        self.bird_img = self.load_image("FB2.png", (35, 35))

        # Load sounds safely
        self.sounds = {}
        self.sounds['wing'] = self.load_sound('wing.wav')
        self.sounds['laser'] = self.load_sound('laser_shot.wav')
        self.sounds['collect'] = self.load_sound('powerup_collect.wav')
        self.sounds['explosion'] = self.load_sound('explosion.wav')
        self.sounds['game_over'] = self.load_sound('game_over.wav')
        
        # Safe loading cho Music
        music_paths = [os.path.join(SND_DIR, 'music.mp3'), 'music.mp3']
        self.music_file = next((p for p in music_paths if os.path.exists(p)), None)

        self.load_stats()
        self.new_record_flag = False # Đánh dấu nếu vừa đạt kỷ lục mới
        self.reset_game()

    def handle_game_over(self):
        """Xử lý tất cả logic khi kết thúc ván chơi"""
        if self.state != GAME_OVER:
            self.state = GAME_OVER
            self.play_sound('game_over')
            if self.music_file: pygame.mixer.music.fadeout(500)
            
            # Cập nhật High Score và lưu dữ liệu ngay lập tức
            if self.score > self.stats['high_score']:
                self.stats['high_score'] = self.score
                self.new_record_flag = True
            
            # Quy đổi điểm thành tiền (HS Credits) - Chỉ cộng 1 lần
            if not self.reward_given:
                self.stats['total_credits'] += self.score
                self.reward_given = True
            
            self.save_stats()

    def get_skin_image(self, skin_key):
        """Lấy ảnh chim: Ưu tiên file ảnh rời -> Fallback sang Palette Swap chuyên nghiệp"""
        if skin_key == 'default':
            return self.bird_img
            
        # 1. Ưu tiên load file ảnh thật (ví dụ: FB_red.png)
        filename = f"FB_{skin_key}.png"
        paths = [os.path.join(IMG_DIR, filename), filename]
        current_path = next((p for p in paths if os.path.exists(p)), None)
        
        if current_path:
            try:
                img = pygame.image.load(current_path).convert_alpha()
                return pygame.transform.scale(img, (35, 35))
            except: pass
            
        # 2. Fallback: Palette Swap (Thay màu thân, giữ mắt và mỏ)
        target_color = None
        if skin_key == 'red': target_color = (255, 50, 50)
        elif skin_key == 'blue': target_color = (50, 150, 255)
        
        if target_color:
            # Tạo bản sao và xử lý từng pixel
            new_surf = self.bird_img.copy()
            pixels = pygame.PixelArray(new_surf)
            
            # Màu vàng đặc trưng của chim gốc (FB2.png thường có màu vàng ~ (255, 200, 0))
            # Chúng ta sẽ thay đổi các pixel có sắc độ vàng
            for x in range(new_surf.get_width()):
                for y in range(new_surf.get_height()):
                    curr_color = new_surf.unmap_rgb(pixels[x, y])
                    # Nếu là màu vàng (R cao, G cao, B thấp) thì mới nhuộm
                    # Mở rộng dải màu một chút để phù hợp với đồ họa pixel art mới
                    if curr_color.r > 120 and curr_color.g > 80 and curr_color.b < 100:
                        # Giữ lại độ sáng tương đối bằng cách nhân tỉ lệ
                        factor = curr_color.r / 255
                        pixels[x, y] = (int(target_color[0] * factor), 
                                        int(target_color[1] * factor), 
                                        int(target_color[2] * factor))
            del pixels # Cần giải phóng PixelArray để unlock Surface
            return new_surf
            
        return self.bird_img

    def apply_current_skin(self):
        """Cập nhật hình ảnh chim ngay lập tức cho các đối tượng hiện có"""
        new_img = self.get_skin_image(self.stats['current_skin'])
        if hasattr(self, 'bird'):
            self.bird.original_image = new_img
            self.bird.image = new_img
            # Nếu đang có powerup thì có thể cần scale lại
            if 'GIANT' in self.active_powerups:
                self.bird.image = pygame.transform.scale(new_img, (70, 70))
            self.bird.mask = pygame.mask.from_surface(self.bird.image)

    def load_stats(self):
        self.stats = {
            'high_score': 0,
            'total_credits': 0,
            'total_destroyed': 0,
            'total_ghost_passes': 0,
            'total_giant_uses': 0,
            'current_skin': 'default',
            'unlocked_skins': ['default'],
            'master_volume': 1.0,
            'bgm_enabled': True
        }
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    data = json.load(f)
                    self.stats.update(data)
                    # Áp dụng ngay cài đặt volume
                    config.master_volume = self.stats.get('master_volume', 1.0)
                    config.bgm_enabled = self.stats.get('bgm_enabled', True)
            except: pass

    def save_stats(self):
        try:
            # Cập nhật volume vào stats trước khi lưu
            self.stats['master_volume'] = config.master_volume
            self.stats['bgm_enabled'] = config.bgm_enabled
            with open('settings.json', 'w') as f:
                json.dump(self.stats, f, indent=4)
        except: pass

    def load_image(self, filename, scale=None):
        """Tải ảnh từ thư mục assets/images hoặc thư mục gốc"""
        paths = [os.path.join(IMG_DIR, filename), filename]
        for p in paths:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    if scale:
                        img = pygame.transform.scale(img, scale)
                    return img
                except: pass
        
        # Fallback nếu không tìm thấy
        fallback = pygame.Surface(scale if scale else (35, 35))
        fallback.fill(RED)
        return fallback

    def load_sound(self, filename):
        """Tải âm thanh từ thư mục assets/sounds hoặc thư mục gốc"""
        paths = [os.path.join(SND_DIR, filename), filename]
        for p in paths:
            if os.path.exists(p):
                try:
                    return pygame.mixer.Sound(p)
                except: pass
        return None

    def play_sound(self, key):
        if key in self.sounds and self.sounds[key]:
            # Tăng âm lượng nếu đang có combo cao hoặc trạng thái đặc biệt
            vol_mult = 1.0
            if self.combo_count > 3: vol_mult = 1.2
            self.sounds[key].set_volume(config.master_volume * vol_mult)
            self.sounds[key].play()

    def update_volumes(self):
        """Cập nhật âm lượng cho nhạc nền ngay lập tức"""
        now = pygame.time.get_ticks()
        is_powerup = any(v > now for v in self.active_powerups.values())
        
        # Tăng 20% âm lượng nếu đang có vật phẩm (Dynamic Music)
        base_vol = 0.5 if not is_powerup else 0.6
        
        if config.bgm_enabled:
            pygame.mixer.music.set_volume(base_vol * config.master_volume)
        else:
            pygame.mixer.music.set_volume(0)

    def draw_button(self, text, x, y, w, h, base_color, hover_color, action=None):
        mouse = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, w, h)
        is_hover = rect.collidepoint(mouse)
        
        color = hover_color if is_hover else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=10)
        
        text_surf = self.font.render(text, True, WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
        
        return is_hover # Trả về True nếu chuột đang đè lên nút

    def reset_game(self):
        self.state = LOBBY
        self.score = 0
        self.tube_velocity = INITIAL_TUBE_VELOCITY
        
        # Lấy ảnh chim dựa trên skin đã chọn
        bird_skin = self.get_skin_image(self.stats['current_skin'])
        self.bird = Bird(50, HEIGHT // 2, bird_skin)
        self.all_sprites = pygame.sprite.Group(self.bird)
        self.tubes = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()
        self.tube_timer = 0
        self.cloud_timer = 0
        
        self.active_powerups = {}
        self.shake_timer = 0
        
        # Combo & Skills
        self.combo_count = 0
        self.last_destruction_time = 0
        self.near_miss_tubes = set() # Lưu ID cặp ống đã tính near miss
        self.reward_given = False # Cờ ghi nhận đã cộng tiền ván này chưa
        
        # Stats tracking already loaded in Game.__init__
        
        # Stop music or set to menu mode
        if self.music_file:
            pygame.mixer.music.stop()

    def spawn_tubes(self):
        h = random.randint(100, 300)
        
        # Quyết định xem ống có di chuyển không (khi score > 30)
        is_moving = False
        if self.score > 30 and random.random() < 0.6: # 60% tỷ lệ di động
            is_moving = True
            
        top_tube = Tube(WIDTH, h, True, is_moving)
        bottom_tube = Tube(WIDTH, h, False, is_moving)
        # Gắn ID cặp ống để tính điểm đồng bộ
        pair_id = pygame.time.get_ticks()
        top_tube.pair_id = pair_id
        bottom_tube.pair_id = pair_id
        
        self.tubes.add(top_tube, bottom_tube)
        self.all_sprites.add(top_tube, bottom_tube)
        
        if random.random() < ITEM_CHANCE:
            item_type = random.choice(['LASER', 'GHOST', 'SLOW', 'GIANT'])
            item = Item(WIDTH + TUBE_WIDTH//2, h + TUBE_GAP//2, item_type)
            self.items.add(item)
            self.all_sprites.add(item)

    def handle_powerup(self, type):
        self.active_powerups[type] = pygame.time.get_ticks() + POWERUP_DURATION
        self.play_sound('collect')
        if type == 'GIANT':
            self.stats['total_giant_uses'] += 1
        self.update_volumes()

    def shoot_laser(self):
        if 'LASER' in self.active_powerups:
            self.play_sound('laser')
            # Tạo tia laser từ tâm chim
            new_laser = Laser((self.bird.rect.right, self.bird.rect.centery))
            self.lasers.add(new_laser)
            self.all_sprites.add(new_laser)
            
            # Kiểm tra va chạm tia laser với ống
            hit_tubes = pygame.sprite.spritecollide(new_laser, self.tubes, True)
            if hit_tubes:
                now = pygame.time.get_ticks()
                # Destruction Combo Logic
                if now - self.last_destruction_time < 2000:
                    self.combo_count += 1
                else:
                    self.combo_count = 1
                self.last_destruction_time = now
                
                # Plus score based on combo
                self.score += 1 * self.combo_count
                self.stats['total_destroyed'] += len(hit_tubes)
                
                if self.combo_count > 1:
                    ft = FloatingText(self.bird.rect.right, self.bird.rect.top - 20, f"COMBO X{self.combo_count}", RED, self.medium_font)
                    self.floating_texts.add(ft)
                    self.all_sprites.add(ft)

                self.play_sound('explosion')
                self.shake_timer = 15
                pygame.time.delay(50) # Hit Stop

    def draw_ui(self):
        if self.state == PLAYING:
            # Score
            score_surf = self.font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_surf, (10, 10))
            
            # Power-ups indicators stacked
            y_offset = 40
            now = pygame.time.get_ticks()
            
            # Combo Display
            if self.combo_count > 1:
                combo_surf = self.medium_font.render(f"COMBO X{self.combo_count}", True, YELLOW)
                # Hiệu ứng nhấp nháy cho combo
                if (now // 100) % 2 == 0:
                    combo_surf = self.medium_font.render(f"COMBO X{self.combo_count}", True, RED)
                self.screen.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, 50))

            for ptype, end_time in list(self.active_powerups.items()):
                time_left = end_time - now
                if time_left > 0:
                    remaining = time_left / POWERUP_DURATION
                    
                    if ptype == 'LASER': color = RED
                    elif ptype == 'GHOST': color = GRAY
                    elif ptype == 'SLOW': color = PURPLE
                    elif ptype == 'GIANT': color = ORANGE
                    else: color = WHITE
                    
                    # Stamina bar dưới chân chim nếu là GIANT
                    if ptype == 'GIANT':
                        bar_width = 60
                        bar_height = 8
                        bar_x = self.bird.rect.centerx - bar_width // 2
                        bar_y = self.bird.rect.bottom + 5
                        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
                        pygame.draw.rect(self.screen, ORANGE, (bar_x + 1, bar_y + 1, (bar_width - 2) * remaining, bar_height - 2))
                        
                        # Cảnh báo stamina thấp
                        if time_left < WARNING_TIME:
                            if (now // 100) % 2 == 0:
                                pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height), 2)
                    
                    draw_row = True
                    if time_left < WARNING_TIME:
                        if (now // 100) % 2 == 0:
                            draw_row = False
                    
                    if draw_row:
                        pygame.draw.rect(self.screen, BLACK, (10, y_offset, 100, 10), 2)
                        pygame.draw.rect(self.screen, color, (12, y_offset + 2, 96 * remaining, 6))
                        type_surf = self.font.render(ptype, True, color)
                        self.screen.blit(type_surf, (120, y_offset - 5))
                    y_offset += 25

    def draw_lobby(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        title = self.large_font.render("ACTION BIRD", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 100)))
        
        # High Score in Lobby
        hs_color = WHITE
        if self.new_record_flag:
            # Nhấp nháy màu vàng nếu vừa phá kỷ lục
            hs_color = YELLOW if (pygame.time.get_ticks() // 200) % 2 == 0 else WHITE
            
        hs_surf = self.medium_font.render(f"BEST: {self.stats['high_score']}", True, hs_color)
        self.screen.blit(hs_surf, hs_surf.get_rect(center=(WIDTH//2, 160)))
        
        self.draw_button("PLAY", WIDTH//2 - 60, 250, 120, 50, BLUE, (100, 180, 255))
        self.draw_button("SETTINGS", WIDTH//2 - 60, 320, 120, 50, GRAY, (180, 180, 180))
        
        # Hàng nút dưới
        self.draw_button("SHOP", WIDTH//2 - 125, 390, 120, 50, PURPLE, (200, 100, 255))
        self.draw_button("AWARDS", WIDTH//2 + 5, 390, 120, 50, ORANGE, (255, 180, 50))

    def draw_settings(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 30, 30, 220))
        self.screen.blit(overlay, (0, 0))
        
        title = self.medium_font.render("SETTINGS", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 80)))
        
        # Volume Control
        vol_label = self.font.render(f"Master Volume: {int(config.master_volume * 100)}%", True, WHITE)
        self.screen.blit(vol_label, (50, 180))
        
        self.draw_button("-", 260, 175, 30, 30, RED, (255, 100, 100))
        self.draw_button("+", 320, 175, 30, 30, BLUE, (100, 200, 255))
            
        # BGM Toggle
        bgm_label = self.font.render("Background Music:", True, WHITE)
        self.screen.blit(bgm_label, (50, 250))
        bgm_status = "ON" if config.bgm_enabled else "OFF"
        bgm_color = BLUE if config.bgm_enabled else RED
        self.draw_button(bgm_status, 260, 245, 90, 40, bgm_color, (150, 150, 255))

        self.draw_button("BACK", WIDTH//2 - 50, 450, 100, 40, GRAY, (200, 200, 200))

    def draw_shop(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 0, 50, 230))
        self.screen.blit(overlay, (0, 0))
        
        title = self.medium_font.render("SHOP", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
        
        # Hiển thị "tiền" (High Score)
        money_surf = self.font.render(f"Credits: {self.stats['total_credits']} HS", True, WHITE)
        self.screen.blit(money_surf, (WIDTH - 180, 20))

        y = 120
        # Skins
        self.screen.blit(self.font.render("--- SKINS ---", True, BLUE), (50, y))
        
        # 1. Original Skin
        orig_label = "ORIGINAL"
        if self.stats['current_skin'] == 'default': 
            orig_label = "[ EQUIPPED ]"
            btn_color = GRAY
        else:
            orig_label = "ORIGINAL - [ SELECT ]"
            btn_color = BLUE
            
        if self.draw_button(orig_label, 50, y + 30, 300, 40, btn_color, WHITE):
            pass
            
        y += 60
        # 2. Red Bird
        red_label = "Red Bird - 50 HS"
        if self.stats['current_skin'] == 'red': 
            red_label = "[ EQUIPPED ]"
            btn_color = GRAY
        elif 'red' in self.stats['unlocked_skins']: 
            red_label = "Red Bird - [ SELECT ]"
            btn_color = ORANGE
        else:
            btn_color = (150, 50, 50) # Màu đỏ tối nếu chưa mua
            if self.stats['total_credits'] < 50: btn_color = GRAY
            
        self.draw_button(red_label, 50, y + 30, 300, 40, btn_color, RED)
        
        y += 60
        # 3. Blue Bird
        blue_label = "Blue Bird - 75 HS"
        if self.stats['current_skin'] == 'blue':
            blue_label = "[ EQUIPPED ]"
            btn_color = GRAY
        elif 'blue' in self.stats['unlocked_skins']:
            blue_label = "Blue Bird - [ SELECT ]"
            btn_color = BLUE
        else:
            btn_color = (0, 50, 150)
            if self.stats['total_credits'] < 75: btn_color = GRAY
        self.draw_button(blue_label, 50, y + 30, 300, 40, btn_color, BLUE)
        
        y += 100
        # Upgrades Placeholder
        self.screen.blit(self.font.render("--- UPGRADES ---", True, YELLOW), (50, y))
        self.draw_button("Longer Giant - 100 HS", 50, y + 30, 300, 40, GRAY, GRAY)
        
        y += 100
        # Auras Placeholder
        self.screen.blit(self.font.render("--- AURAS ---", True, PURPLE), (50, y))
        self.draw_button("Fire Aura - 200 HS", 50, y + 30, 300, 40, GRAY, GRAY)
        
        if self.draw_button("BACK", WIDTH//2 - 50, 520, 100, 40, GRAY, (200, 200, 200)):
            pass

    def draw_achievements(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 230))
        self.screen.blit(overlay, (0, 0))
        
        title = self.medium_font.render("ACHIEVEMENTS", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
        
        # List achievements
        achievements = [
            ("Tube Hunter", f"Destroy {self.stats['total_destroyed']}/100 Pipes", self.stats['total_destroyed'] >= 100),
            ("Ghost Student", f"Ghost Pass {self.stats['total_ghost_passes']}/20 Times", self.stats['total_ghost_passes'] >= 20),
            ("The Giant", f"Use Giant {self.stats['total_giant_uses']}/10 Times", self.stats['total_giant_uses'] >= 10)
        ]
        
        y = 150
        for name, desc, unlocked in achievements:
            color = YELLOW if unlocked else GRAY
            name_surf = self.font.render(name, True, color)
            desc_surf = self.font.render(desc, True, WHITE)
            self.screen.blit(name_surf, (50, y))
            self.screen.blit(desc_surf, (50, y + 25))
            if unlocked:
                pygame.draw.circle(self.screen, YELLOW, (30, y + 12), 5)
            y += 80
            
        self.draw_button("BACK", WIDTH//2 - 50, 520, 100, 40, GRAY, (200, 200, 200))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            
            # --- Xử lý Sự kiện ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        mouse_pos = event.pos
                        
                        if self.state == LOBBY:
                            self.new_record_flag = False # Reset cờ kỷ lục khi vào chơi
                            # PLAY button
                            if pygame.Rect(WIDTH//2 - 60, 250, 120, 50).collidepoint(mouse_pos):
                                self.state = PLAYING
                                self.update_volumes()
                                if self.music_file and config.bgm_enabled:
                                    try:
                                        pygame.mixer.music.load(self.music_file)
                                        pygame.mixer.music.play(-1)
                                    except: pass
                            # SETTINGS button
                            elif pygame.Rect(WIDTH//2 - 60, 320, 120, 50).collidepoint(mouse_pos):
                                self.state = SETTINGS
                            # SHOP button
                            elif pygame.Rect(WIDTH//2 - 125, 390, 120, 50).collidepoint(mouse_pos):
                                self.state = SHOP
                            # AWARDS button
                            elif pygame.Rect(WIDTH//2 + 5, 390, 120, 50).collidepoint(mouse_pos):
                                self.state = ACHIEVEMENTS


                        elif self.state == SETTINGS:
                            # Volume -
                            if pygame.Rect(260, 175, 30, 30).collidepoint(mouse_pos):
                                config.master_volume = max(0.0, config.master_volume - 0.1)
                                self.update_volumes()
                            # Volume +
                            elif pygame.Rect(320, 175, 30, 30).collidepoint(mouse_pos):
                                config.master_volume = min(1.0, config.master_volume + 0.1)
                                self.update_volumes()
                            # BGM Toggle
                            elif pygame.Rect(260, 245, 90, 40).collidepoint(mouse_pos):
                                config.bgm_enabled = not config.bgm_enabled
                                if not config.bgm_enabled: pygame.mixer.music.stop()
                                else:
                                    if not pygame.mixer.music.get_busy() and self.music_file:
                                        try:
                                            pygame.mixer.music.load(self.music_file)
                                            pygame.mixer.music.play(-1)
                                        except: pass
                                self.update_volumes()
                            # BACK
                            elif pygame.Rect(WIDTH//2 - 50, 450, 100, 40).collidepoint(mouse_pos):
                                self.state = LOBBY

                        elif self.state == SHOP:
                            # ORIGINAL Bird (Free)
                            if pygame.Rect(50, 150, 300, 40).collidepoint(mouse_pos):
                                self.stats['current_skin'] = 'default'
                                self.apply_current_skin()
                                self.save_stats()
                                self.play_sound('collect')

                            # Red Bird - 50 HS
                            elif pygame.Rect(50, 210, 300, 40).collidepoint(mouse_pos):
                                # Nếu đã unlock rồi thì chỉ Equip
                                if 'red' in self.stats['unlocked_skins']:
                                    self.stats['current_skin'] = 'red'
                                    self.apply_current_skin()
                                    self.save_stats()
                                    self.play_sound('collect')
                                # Nếu chưa unlock thì mua
                                elif self.stats['total_credits'] >= 50:
                                    self.stats['total_credits'] -= 50
                                    self.stats['current_skin'] = 'red'
                                    if 'red' not in self.stats['unlocked_skins']:
                                        self.stats['unlocked_skins'].append('red')
                                    self.apply_current_skin()
                                    self.save_stats()
                                    self.play_sound('collect')

                            # Blue Bird - 75 HS
                            elif pygame.Rect(50, 270, 300, 40).collidepoint(mouse_pos):
                                if 'blue' in self.stats['unlocked_skins']:
                                    self.stats['current_skin'] = 'blue'
                                    self.apply_current_skin()
                                    self.save_stats()
                                    self.play_sound('collect')
                                elif self.stats['total_credits'] >= 75:
                                    self.stats['total_credits'] -= 75
                                    self.stats['current_skin'] = 'blue'
                                    if 'blue' not in self.stats['unlocked_skins']:
                                        self.stats['unlocked_skins'].append('blue')
                                    self.apply_current_skin()
                                    self.save_stats()
                                    self.play_sound('collect')
                            
                            # Longer Giant - 100 HS (Cần nâng cấp logic thêm)
                            elif pygame.Rect(50, 310, 300, 40).collidepoint(mouse_pos):
                                if self.stats['total_credits'] >= 100:
                                    pass

                            # BACK
                            elif pygame.Rect(WIDTH//2 - 50, 520, 100, 40).collidepoint(mouse_pos):
                                self.state = LOBBY
                        
                        elif self.state == ACHIEVEMENTS:
                            # BACK
                            if pygame.Rect(WIDTH//2 - 50, 520, 100, 40).collidepoint(mouse_pos):
                                self.state = LOBBY
                                
                        elif self.state == GAME_OVER:
                            # RETRY (Khớp tọa độ với draw_button: +100)
                            if pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 100, 120, 50).collidepoint(mouse_pos):
                                self.reset_game()
                                self.state = PLAYING
                                self.update_volumes()
                                if self.music_file and config.bgm_enabled:
                                    try: pygame.mixer.music.play(-1)
                                    except: pass
                            # LOBBY (Khớp tọa độ với draw_button: +160)
                            elif pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 160, 120, 50).collidepoint(mouse_pos):
                                self.reset_game()
                                self.state = LOBBY

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == PLAYING:
                            self.play_sound('wing')
                            curr_jump = JUMP_STRENGTH
                            if 'SLOW' in self.active_powerups:
                                curr_jump *= 0.5
                            self.bird.jump(curr_jump)
                        
                        # Logic SPACE bị xóa khỏi LOBBY và GAME_OVER để bắt buộc dùng chuột
                    if event.key == pygame.K_f and self.state == PLAYING:
                        self.shoot_laser()

            # --- Cập nhật Logic ---
            if self.state == PLAYING:
                expired = [k for k, v in self.active_powerups.items() if v <= now]
                for k in expired:
                    del self.active_powerups[k]

                is_ghost = 'GHOST' in self.active_powerups
                is_slow = 'SLOW' in self.active_powerups
                is_giant = 'GIANT' in self.active_powerups
                is_any_warning = any((v - now) < WARNING_TIME for v in self.active_powerups.values())
                
                # Stamina warning sound (mỗi 0.5s khi sắp hết giờ GIANT)
                if is_giant and (self.active_powerups['GIANT'] - now) < WARNING_TIME:
                    if (now // 500) % 2 == 0:
                        if not hasattr(self, 'last_warning_time') or now - self.last_warning_time > 400:
                            self.play_sound('wing')
                            self.last_warning_time = now

                current_vel = self.tube_velocity
                current_gravity = GRAVITY
                
                if is_slow:
                    current_vel *= 0.5
                    current_gravity *= 0.5
                if is_giant:
                    current_vel *= 0.4
                    current_gravity *= 0.7
                
                if self.bird.update(self.state, current_gravity, is_ghost, is_any_warning, is_giant):
                    self.handle_game_over()
                
                if self.active_powerups:
                    trail = TrailEffect(self.bird.rect.centerx, self.bird.rect.centery, self.bird.image)
                    self.trails.add(trail)
                    self.all_sprites.add(trail)
                
                self.trails.update()
                self.lasers.update(self.bird.rect)
                self.floating_texts.update()
                
                # Cập nhật mây
                self.cloud_timer += dt
                if self.cloud_timer > 2000: # Cứ 2s sinh 1 đám mây
                    if len(self.clouds) < 5:
                        cloud = Cloud()
                        self.clouds.add(cloud)
                    self.cloud_timer = 0
                self.clouds.update(current_vel)

                self.tube_timer += dt
                spawn_interval = 1500 / (current_vel / INITIAL_TUBE_VELOCITY)
                if self.tube_timer > spawn_interval:
                    self.spawn_tubes()
                    self.tube_timer = 0
                
                self.tubes.update(current_vel)
                self.items.update(current_vel)
                
                # Check point & Near Miss logic
                for t in self.tubes:
                    pid = getattr(t, 'pair_id', None)
                    
                    # Point logic
                    if not hasattr(t, 'passed') and t.rect.right < self.bird.rect.left:
                        for tube_in_group in self.tubes:
                            if getattr(tube_in_group, 'pair_id', None) == pid:
                                tube_in_group.passed = True
                        self.score += 1
                        if 'GHOST' in self.active_powerups:
                            self.stats['total_ghost_passes'] += 1
                        
                        if self.score % 10 == 0:
                            self.tube_velocity += 0.5
                    
                    # Near Miss detection (Chỉ tính nếu chưa pass và chưa tính near miss cho cặp này)
                    if pid and pid not in self.near_miss_tubes and not hasattr(t, 'passed'):
                        # Kiểm tra xem chim có đang nằm trong phạm vi chiều ngang của ống không
                        if self.bird.rect.right > t.rect.left and self.bird.rect.left < t.rect.right:
                            # Khoảng cách tới cạnh ống (trên hoặc dưới)
                            dist_top = self.bird.rect.top - t.rect.bottom if t.rect.top == 0 else 999
                            dist_bottom = t.rect.top - self.bird.rect.bottom if t.rect.top > 0 else 999
                            
                            if (0 < dist_top < 10) or (0 < dist_bottom < 10):
                                self.near_miss_tubes.add(pid)
                                self.score += 2
                                ft = FloatingText(self.bird.rect.centerx, self.bird.rect.top, "+2 Near Miss", YELLOW, self.font)
                                self.floating_texts.add(ft)
                                self.all_sprites.add(ft)
                
                # Update combo timer
                if now - self.last_destruction_time > 2000:
                    self.combo_count = 0

                hit_items = pygame.sprite.spritecollide(self.bird, self.items, True)
                for item in hit_items:
                    self.handle_powerup(item.type)
                
                if not is_ghost:
                    collided_tubes = pygame.sprite.spritecollide(self.bird, self.tubes, False, pygame.sprite.collide_mask)
                    if collided_tubes:
                        if is_giant:
                            now = pygame.time.get_ticks()
                            if now - self.last_destruction_time < 2000:
                                self.combo_count += 1
                            else:
                                self.combo_count = 1
                            self.last_destruction_time = now
                            
                            for tube in collided_tubes:
                                tube.kill()
                                self.score += 1 * self.combo_count
                                self.stats['total_destroyed'] += 1
                            
                            if self.combo_count > 1:
                                ft = FloatingText(self.bird.rect.centerx, self.bird.rect.top - 40, f"COMBO X{self.combo_count}", RED, self.medium_font)
                                self.floating_texts.add(ft)
                                self.all_sprites.add(ft)

                            self.play_sound('explosion')
                            self.shake_timer = 10
                            pygame.time.delay(50) # Hit Stop
                        else:
                            self.handle_game_over()

            # --- Vẽ ---
            offset_x, offset_y = 0, 0
            if self.shake_timer > 0:
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                self.shake_timer -= 1

            self.screen.blit(self.bg_img, (offset_x, offset_y))
            
            # Vẽ mây (lớp nền)
            self.clouds.draw(self.screen)
            
            self.all_sprites.draw(self.screen)
            pygame.draw.rect(self.screen, YELLOW, (0, HEIGHT - 25, WIDTH, 25))
            self.draw_ui()
            
            if self.state == LOBBY:
                self.draw_lobby()
            
            elif self.state == SETTINGS:
                self.draw_settings()
                
            elif self.state == SHOP:
                self.draw_shop()
            
            elif self.state == ACHIEVEMENTS:
                self.draw_achievements()
                
            elif self.state == GAME_OVER:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((200, 0, 0, 80))
                self.screen.blit(overlay, (0, 0))
                msg = self.large_font.render("GAME OVER", True, WHITE)
                score_msg = self.medium_font.render(f"SCORE: {self.score}", True, WHITE)
                best_msg = self.font.render(f"BEST: {self.stats['high_score']}", True, YELLOW)
                credits_msg = self.font.render(f"TOTAL CREDITS: {self.stats['total_credits']}", True, CYAN if 'CYAN' in globals() else BLUE)
                
                self.screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
                self.screen.blit(score_msg, score_msg.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
                self.screen.blit(best_msg, best_msg.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
                self.screen.blit(credits_msg, credits_msg.get_rect(center=(WIDTH//2, HEIGHT//2 + 55)))
                
                # Nút bấm dùng chuột
                if self.draw_button("RETRY", WIDTH//2 - 60, HEIGHT//2 + 100, 120, 50, BLUE, (100, 180, 255)):
                    pass
                if self.draw_button("LOBBY", WIDTH//2 - 60, HEIGHT//2 + 160, 120, 50, GRAY, (180, 180, 180)):
                    pass

            pygame.display.flip()

        self.save_stats()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
