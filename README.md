# 🚀 Action Bird - Premium Arcade Edition

**Action Bird** là một phiên bản nâng cấp mạnh mẽ từ trò chơi Flappy Bird cổ điển, kết hợp với các yếu tố hành động kịch tính, hệ thống Boss Fight và trải nghiệm hình ảnh Arcade chuyên nghiệp.

![Action Bird](https://github.com/TwinMindWeekly/06_04_2026_Action_Bird/raw/main/assets/images/banner.png)

## ✨ Tính năng nổi bật

- **👾 Boss Fight Hệ thống:**
  - Mỗi 50 điểm, một thực thể Boss (UFO/Mecha) sẽ xuất hiện cản đường.
  - Người chơi sẽ được cấp **Laser vô hạn** trong giai đoạn này để bắn hạ Boss.
- **🚀 Cảnh báo Tên lửa (Missile System):**
  - Hệ thống tên lửa tầm nhiệt sẽ tấn công bất ngờ.
  - Có biển báo **Cảnh báo (!)** nhấp nháy 1.5 giây trước khi tên lửa lao tới để người chơi chủ động né tránh.
- **💎 Hiệu ứng Arcade Cao cấp (UX Upgrade):**
  - **Screen Shake:** Màn hình rung chuyển mạnh mẽ khi nổ ống nước hoặc va chạm.
  - **Scene Transitions:** Hiệu ứng mờ dần (Fade in/out) mượt mà khi chuyển cảnh.
  - **Premium UI:** Giao diện nút bấm 3D và các bảng thông báo phong cách **Glassmorphism**.
- **🔥 Kỹ năng & Aura:**
  - **Fire Aura:** Mua tại shop để chim tỏa ra tia lửa khi bay.
  - **Giant Mode:** Biến khổng lồ, húc đổ mọi vật cản và tạo combo điểm.
  - **Laser Shot (F):** Phá hủy ống nước từ xa.

## 🛠️ Hướng dẫn cài đặt

### Yêu cầu hệ thống
- Python 3.8 trở lên.
- Thư viện Pygame.

### Các bước cài đặt
1. Tải toàn bộ mã nguồn về máy hoặc dùng lệnh:
   ```bash
   git clone https://github.com/TwinMindWeekly/06_04_2026_Action_Bird.git
   ```
2. Cài đặt thư viện:
   ```bash
   pip install pygame
   ```
3. Chạy trò chơi:
   ```bash
   python main.py
   ```

## 🎮 Cách chơi

- **Chuột (Mouse):** Điều hướng chính trong Menu, Shop và Settings.
- **SPACE:** Nhảy (Flap).
- **F:** Bắn Laser (khi có Powerup Laser).
- **Trạng thái Boss:** Tập trung bắn Laser liên tục vào Boss để nhận thưởng lớn.

## 📂 Cấu trúc dự án

- `main.py`: File khởi chạy game.
- `game.py`: Logic cốt lõi, xử lý va chạm và vòng lặp game.
- `entities.py`: Định nghĩa Chim, Boss, Tên lửa, Vật phẩm...
- `ui.py`: Xử lý giao diện đồ họa cao cấp.
- `asset_manager.py`: Quản lý tài nguyên hình ảnh, âm thanh và lưu trữ stats.
- `config.py`: Các thông số cài đặt mặc định.

---
© 2026 **Action Bird Team** - Một dự án thuộc [TwinMindWeekly](https://github.com/TwinMindWeekly).
