import os

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
CYAN = (0, 255, 255)

# Trạng thái Game
LOBBY = "LOBBY"
PLAYING = "PLAYING"
GAME_OVER = "GAME_OVER"
SETTINGS = "SETTINGS"
SHOP = "SHOP"
ACHIEVEMENTS = "ACHIEVEMENTS"
PAUSED = "PAUSED"

class Config:
    def __init__(self):
        self.master_volume = 1.0  # 0% - 100% (0.0 - 1.0)
        self.bgm_enabled = True

config = Config()
