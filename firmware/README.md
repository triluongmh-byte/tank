# Pet Tank V0 — firmware chưa nạp

**[Hướng dẫn nối dây](WIRING.md)** · [Giao thức host](PROTOCOL.md) · [Tích hợp board/case](INTEGRATION.md).

Bản này giữ mặt pet, trạng thái phiên Claude, TITLE/ACTION, danh sách phiên, usage, mood và hoạt ảnh từ repo được người dùng chỉ định. Màn ST7789 1,54" 240×240 SPI (release note 8; trước đó LILYGO T-Display-S3) **không cảm ứng** được điều khiển bằng SPI 240×240 (mặt pet vẽ gốc 240×240, vẽ hai nửa 240×120 để vừa RAM). Liên kết host là UART0 qua cầu USB-UART của DevKit (mở cổng có thể kích reset qua DTR/RTS; xe khởi động ở trạng thái dừng), không dùng Wi-Fi/Bluetooth.

PCA9685 0x40 cấp xung danh nghĩa 50 Hz: CH0–2 bánh trái trước/giữa/sau, CH3–5 bánh phải trước/giữa/sau, CH6 turret; CH7–15 tắt. Có hiệu chuẩn từng bánh, kiểm tra một bánh có thời hạn, CUE/DRIVE, turret và chế độ dò đường tiến–dừng bảo thủ. Không có SLAM, chống rơi mép bàn hoặc bảo đảm tránh va chạm bên hông.

Khởi động luôn dừng, ACT_EN thấp/OE cao. Không tự chạy sau kết nối, reset, nhả nút hay lưu hiệu chuẩn. Mọi lệnh chạy cần ARM mới, liên kết còn sống và hiệu chuẩn phù hợp. Nút GPIO27 hoặc giữ nút BOOT/GPIO0 cắt nguồn servo, có latch cần ARM mới; giữ BOOT lúc reset có thể vào bootloader. STOP, ask/cancelled, sleep, lỗi parser/I2C, mất USB, hết heartbeat hoặc deadline đều dừng. Timer kiểm tra vòng điều khiển độc lập và task watchdog hỗ trợ dừng khi treo; trạng thái reset/blank flash vẫn phải được mạch carrier bảo đảm.

## Tình trạng 2026-11-20

Đã biên dịch cho ESP32 (không phải S3, release note 8) bằng core Arduino ESP32 **2.0.14** sẵn trong cache chung. Bộ test chạy trên host với mock và ASan/UBSan; không phải phép đo phần cứng. `flash.json` trỏ tới binary thực. Không flash, mở cổng USB, chạy servo hoặc đọc phần cứng trong công việc này.

Đã đối chiếu GPIO, chân connector và bảy kênh qua buffer U1 với PCB KiCad thực trong worktree; không thấy sai lệch điện ở các giao diện này. [Báo cáo đối chiếu](reports/integration.json) vẫn pending vì chưa có giới hạn case đã kiểm tra. Board ghi nhận thay đổi vị trí/hình dạng đầu cắm trong [DEVIATIONS.md](../engineering/DEVIATIONS.md), mục 3; lead/case còn phải đối chiếu cơ khí. Firmware đang giữ turret ở tâm, `AUTO SCAN` bị chặn đến khi nhập phạm vi case đã kiểm tra. Bản compile thành công không đồng nghĩa toàn sản phẩm sẵn sàng.

Đã áp dụng release note 1–2: sonar tham chiếu HC-SR04P ×2, quạt 5 V luôn cấp từ LOAD_5V, pin 18650 song song 1S qua bộ nguồn bảo vệ/nâng áp đã xác minh. [WIRING.md](WIRING.md) ghi chi tiết và các phần chưa xác minh của pin 140 g. GPIO và hành vi không đổi nên giữ nguyên binary, không biên dịch lại.

## Build và kiểm tra

Từ root workspace, giữ nguyên `ARDUINO_DIRECTORIES_DATA`, `PLATFORMIO_CORE_DIR`, `PIP_CACHE_DIR` mà Harness cấp; không cài SDK/toolchain vào worktree. Không cần thư viện tải thêm: dùng Wire, Preferences và esp_lcd của core đã ghim.

```sh
python3 firmware/check.py
python3 firmware/build.py
```

Build dùng mọi CPU, output `build/firmware/esp32/tank.ino.bin`, `.elf`, bootloader và partitions. Fingerprint input giúp bỏ qua compile nếu nguồn không đổi. Test cũng tái sử dụng executable/kết quả khi input không đổi. Có thể chạy nhanh từng nhóm: `python3 firmware/check.py core`, `guard`, `pet`, `scan`, `host` hoặc `interfaces`. Bài test scan dùng fixture **mock** ±30°, không mở khóa bản firmware sản phẩm.

FQBN trong [flash.json](flash.json): `esp32:esp32:esp32` (ESP32 DevKit cổ điển, flash 4 MB, partition default); liên kết host qua cầu USB-UART của DevKit (UART0, 115200). Cần đối chiếu module thực. Màn ST7789 1,54" 240×240 SPI phát từng dải 20 hàng mỗi vòng lặp; framebuffer tĩnh 57,6 KB (nửa khung, vẽ hai lượt cửa sổ hàng; không cần khối heap lớn). Nếu màn không có chân CS có thể cần SPI_MODE3 trong display.h.

Chỉ khi có yêu cầu flash riêng: nút Flash của pane đọc recipe, hiện đúng cầu USB-UART (VID trong flash.json) rồi mới ghi. Phải giữ bản khôi phục trước khi ghi. Cách tương đương trong terminal sau khi được phép và đã xác định đúng port:

```sh
arduino-cli upload --fqbn 'esp32:esp32:esp32:PartitionScheme=default' --port '<cổng-đã-xác-minh>' --input-dir build/firmware/esp32 firmware/tank
```

Không chạy lệnh upload trong nhiệm vụ thiết kế này. Flash không cho phép tự chạy động cơ.

## GPIO và nguồn

| GPIO (ESP32 DevKit) | Net / chức năng |
|---|---|
| 21 / 22 | I2C_SDA / I2C_SCL |
| 25 | PCA_OE_N; HIGH tắt output |
| 26 | ACT_EN; LOW tắt nguồn servo |
| 32 / 34 | Front sonar Trig / Echo phía 3V3 (34 chỉ vào) |
| 33 / 35 | Rear sonar Trig / Echo phía 3V3 (35 chỉ vào) |
| 27 / 0 | Nút STOP cục bộ / nút BOOT của DevKit + duyệt phiên |
| 1 / 3 | TX0 / RX0 tới cầu USB-UART: liên kết host, không dùng làm GPIO |
| 18 / 23 / 16 / 17 | ST7789 SCK / MOSI / CS / DC (SPI VSPI, chỉ ghi) |
| 4 / 13 | ST7789 RST / backlight |

Bảng theo [pins.h](tank/pins.h) khớp bảng board công bố `engineering/esp32-pinmap.json` (release note 8); `reconcile.py` so sánh tự động. Loại DevKit 30 chân là GIẢ ĐỊNH. Carrier lấy 3V3 từ LDO của DevKit. Nguồn tải DC 5 V đã điều chỉnh qua J_PWR, mass chung; không nối pin 1S trực tiếp vào đó hoặc nối EXT_5V_IN với USB VBUS. Không cấp servo qua PCA V+, LILYGO hoặc USB host. Quạt không có GPIO và không tắt bằng MOTOR STOP. Hướng dẫn đầy đủ ở [WIRING.md](WIRING.md).

## Hiệu chuẩn và sử dụng sau khi được phép thử thực

Mặc định sáu bánh chưa calibrated; DRIVE/CUE/AUTO bị từ chối. Kê bánh khỏi mặt bàn và chỉ nối một servo bánh trong lần xác định đầu tiên. `MOTOR ARM`, rồi `MOTOR TEST <0..5> 0` kiểm tra trung tính trong 100 ms; `+`/`-` thử chiều. Chỉ đích được phát xung trong TEST; các kênh còn lại full-off. Có biến thể `2000ms`, vẫn cần heartbeat mỗi 200 ms, không dùng để thử mù.

`CAL SET <kênh> <neutral_us> <direction> <span_us>` đặt riêng từng bánh. Neutral chấp nhận 1300–1700 µs, direction ±1, span 10–200 µs. Đây là giới hạn cấu hình, không phải thông số đã đo; phải tìm trung tính thật và kiểm tra lệnh dương làm bánh đi tiến theo xe. `CAL TURRET <center_us> <us_per_deg>` đặt tâm (1400–1600 µs) và độ dốc (4–8 µs/độ). Tháo horn trước khi tìm tâm, chưa chạy góc ngoài phạm vi case. `CAL SAVE` lưu NVS có phiên bản/CRC, `CAL GET` xem hiệu chuẩn. Mọi sửa/lưu hiệu chuẩn đều disarm, không tự bật tải.

Sau ARM, DRIVE/CUE cần hai echo hợp lệ liên tiếp của hướng chạy. Khi bật tải, bánh ở trung tính trong lúc turret ổn định 300 ms rồi nhận echo mới; dữ liệu trước lần bật không được dùng để bắt đầu chạy. Hết lệnh có 40 ms trung tính rồi OE cao/ACT_EN thấp; dừng lỗi cắt ngay. Các thời gian/ngưỡng là mục tiêu chưa thử thực, xem [DEVIATIONS.md](DEVIATIONS.md).

`AUTO ON` là tiến chậm, dừng và cắt nguồn khi đường bị chắn hoặc không rõ, tối đa 9 giây; không tự quay tránh chướng ngại hay tự khởi động lại. `AUTO SCAN` chỉ xoay turret khi bánh đứng yên, trái–tâm–phải–tâm trong phạm vi case đã kiểm tra, rồi tắt tải; phạm vi hiện là −70…+70° nhập từ case/firmware-limits.json; góc thực chưa kiểm trên phần cứng. Mỗi lệnh cần ARM mới. Không dùng sonar ngang làm chống rơi bàn.

Host cũ hard-code MAC và GPIO của pet cũ nên không được dùng receipt cũ. [tank_transport.py](host/tank_transport.py) cung cấp adapter cho API `send/lines` và `MotionForwarder` của bridge tham chiếu; xác minh receipt riêng và MAC tank trước khi cho phép motion. Nó không mở serial hay thay daemon. Các message mặt pet có thể dùng lại theo [PROTOCOL.md](PROTOCOL.md).

Các giả định phần cứng, reset-state, neutral, chiều quay, xung/tần số thật, độ tin cậy sonar, khoảng dừng, nguồn tải, nhiệt và fit đều chưa thử thực. [SOURCES.md](SOURCES.md) ghi nguồn đối chiếu, [HANDOFF.md](HANDOFF.md) ghi điểm vào cho người sửa tiếp.
