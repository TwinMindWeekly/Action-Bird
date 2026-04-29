import os
import pygame
import json
import base64
import hashlib
from config import *

class AssetManager:
    def __init__(self):
        self.stats = {
            'high_score': 0,
            'total_credits': 0,
            'total_destroyed': 0,
            'total_ghost_passes': 0,
            'total_giant_uses': 0,
            'current_skin': 'default',
            'unlocked_skins': ['default'],
            'unlocked_upgrades': [],
            'master_volume': 1.0,
            'bgm_enabled': True
        }
        self.sounds = {}
        self.bg_img = None
        self.bird_img = None
        self.music_file = None
        self.skin_cache = {}
        
        self.load_stats()

    def load_assets(self):
        self.bg_img = self.load_image("BG2.png", (WIDTH, HEIGHT))
        self.bird_img = self.load_image("FB2.png", (35, 35))

        self.sounds['wing'] = self.load_sound('wing.wav')
        self.sounds['laser'] = self.load_sound('laser_shot.wav')
        self.sounds['collect'] = self.load_sound('powerup_collect.wav')
        self.sounds['explosion'] = self.load_sound('explosion.wav')
        self.sounds['game_over'] = self.load_sound('game_over.wav')
        
        music_paths = [os.path.join(SND_DIR, 'music.mp3'), 'music.mp3']
        self.music_file = next((p for p in music_paths if os.path.exists(p)), None)
        
        self.pre_render_skins()

    def load_image(self, filename, scale=None):
        paths = [os.path.join(IMG_DIR, filename), filename]
        for p in paths:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    if scale:
                        img = pygame.transform.scale(img, scale)
                    return img
                except: pass
        fallback = pygame.Surface(scale if scale else (35, 35))
        fallback.fill(RED)
        return fallback

    def load_sound(self, filename):
        paths = [os.path.join(SND_DIR, filename), filename]
        for p in paths:
            if os.path.exists(p):
                try:
                    return pygame.mixer.Sound(p)
                except: pass
        return None

    def play_sound(self, key, combo_count=0):
        if key in self.sounds and self.sounds[key]:
            vol_mult = 1.0
            if combo_count > 3: vol_mult = 1.2
            self.sounds[key].set_volume(config.master_volume * vol_mult)
            self.sounds[key].play()

    def update_volumes(self, is_powerup_active=False):
        base_vol = 0.5 if not is_powerup_active else 0.6
        if config.bgm_enabled:
            pygame.mixer.music.set_volume(base_vol * config.master_volume)
        else:
            pygame.mixer.music.set_volume(0)

    def get_save_hash(self, data_str):
        # Sử dụng một "muối" (salt) ẩn để chống lại việc giả mạo hash
        salt = "ActionBird_Hardcore_Secret_Key_2026"
        return hashlib.sha256((data_str + salt).encode('utf-8')).hexdigest()

    def load_stats(self):
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    raw_data = f.read()
                
                # Kiểm tra xem file là JSON định dạng cũ hay Anti-Cheat mới
                try:
                    parsed = json.loads(raw_data)
                    if "payload" in parsed and "hash" in parsed:
                        # File đã được mã hóa
                        payload = parsed["payload"]
                        expected_hash = self.get_save_hash(payload)
                        if expected_hash == parsed["hash"]:
                            # Hash khớp -> file an toàn
                            decoded_str = base64.b64decode(payload).decode('utf-8')
                            data = json.loads(decoded_str)
                            self.stats.update(data)
                        else:
                            print("[Anti-Cheat] Cảnh báo: File save đã bị chỉnh sửa trái phép!")
                    else:
                        # Hỗ trợ tương thích ngược: Load file JSON cũ
                        self.stats.update(parsed)
                except json.JSONDecodeError:
                    print("Lỗi đọc JSON từ file save.")
                    
                config.master_volume = self.stats.get('master_volume', 1.0)
                config.bgm_enabled = self.stats.get('bgm_enabled', True)
            except Exception as e:
                print(f"Lỗi truy cập file save: {e}")

    def save_stats(self):
        try:
            self.stats['master_volume'] = config.master_volume
            self.stats['bgm_enabled'] = config.bgm_enabled
            
            # Chuyển dữ liệu thành chuỗi JSON
            json_str = json.dumps(self.stats)
            
            # Mã hóa Base64 và tạo chữ ký số (Hash)
            encoded_payload = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            save_hash = self.get_save_hash(encoded_payload)
            
            save_data = {
                "_warning": "DO NOT EDIT THIS FILE. TAMPERING WILL CORRUPT YOUR SAVE.",
                "payload": encoded_payload,
                "hash": save_hash
            }
            
            with open('settings.json', 'w') as f:
                json.dump(save_data, f, indent=4)
        except Exception as e:
            print(f"Lỗi ghi file save: {e}")

    def pre_render_skins(self):
        self.skin_cache['default'] = self.bird_img
        
        # Pre-render Red and Blue skins
        for skin_key, target_color in [('red', (255, 50, 50)), ('blue', (50, 150, 255))]:
            filename = f"FB_{skin_key}.png"
            paths = [os.path.join(IMG_DIR, filename), filename]
            current_path = next((p for p in paths if os.path.exists(p)), None)
            
            if current_path:
                try:
                    img = pygame.image.load(current_path).convert_alpha()
                    self.skin_cache[skin_key] = pygame.transform.scale(img, (35, 35))
                    continue
                except: pass
            
            # Palette Swap fallback
            if self.bird_img:
                new_surf = self.bird_img.copy()
                pixels = pygame.PixelArray(new_surf)
                for x in range(new_surf.get_width()):
                    for y in range(new_surf.get_height()):
                        curr_color = new_surf.unmap_rgb(pixels[x, y])
                        if curr_color.r > 120 and curr_color.g > 80 and curr_color.b < 100:
                            factor = curr_color.r / 255
                            pixels[x, y] = (int(target_color[0] * factor), 
                                            int(target_color[1] * factor), 
                                            int(target_color[2] * factor))
                del pixels
                self.skin_cache[skin_key] = new_surf

    def get_skin_image(self, skin_key):
        return self.skin_cache.get(skin_key, self.bird_img)
