# Pet Tank — yêu cầu hiện hành (27/11/2026)

**Case: dùng `robot-tank` của cadsmith — v1 user ĐÃ IN HẾT; bản mới nhất v5 thêm stack gắn board (đế + tầng PCA9685 + tầng ESP32 + nắp turret có mặt vát 45° gắn màn)** — không vẽ case mới ở đây. [v5 assets](assets/robot-tank-cadsmith-v5/)
Nguồn: `/Users/macbookpro/cad-models/robot-tank/builds/v1/`, bản sao kiểm hash ở [assets/robot-tank-cadsmith-v1](assets/robot-tank-cadsmith-v1/).
Bộ case đó đã có: mũi ">", glacis 45° có cửa sổ màn 1.54", treo đòn bẩy từng bánh (servo một đầu, dây thun đầu kia),
turret SG90 180° mang 2 sonar lưng nhau, cần đèn LED phía trước, khoang 2 cell 18650.

Đồ user có (27/11): ESP32 (GIẢ ĐỊNH DevKit 30 chân), màn ST7789 1.54", PCA9685 ×1, mạch sạc+boost 1S 5V 2A Type-C ×4,
2 thanh WS2812 8 bóng, 2× HC-SR04P, 6 servo 360°, SG90 turret, cell 18650, quạt 5V 30×30.

Còn lại cho team: board/đấu dây + firmware khớp với case đã in (điều khiển bằng điện thoại, 8 hướng, tốc độ,
đèn bật/tắt đổi màu, chế độ tự đi quét sonar — theo [chat cadsmith](assets/robot-tank-cadsmith-v1/firmware-chat-2026-11-25.md), chưa test).

Lịch sử: [original](original.md) · [history/](history/) — các note case trước (mũi >, bỏ ống bánh, hạ thân, bánh rộng,
treo đòn bẩy, gu xe bọc thép) đã được thay bằng case robot-tank đã in.
