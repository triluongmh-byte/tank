# Pet Tank 🛞🤖

[English](README.md) · **Tiếng Việt**

Xe tăng 6 bánh kiểu thiết giáp, nhân bản từ con **claude-pet**: trên mặt nghiêng có cái màn hiển thị mặt pet và trạng thái phiên Claude Code. Turret gắn 2 sonar quay lưng vào nhau để dò đường.

- **Thân xe:** case `robot-tank` v1 do cadsmith vẽ, người dùng đã in xong. Thêm cụm stack v5 và các gá dán/kẹp.
- **Mạch:** carrier 62×60 mm, 2 lớp.
- **Bộ điều khiển:** ESP32 DevKit + PCA9685 điều 7 servo: 6 servo 360° kéo bánh, 1 SG90 xoay turret.
- **Pin:** 2 cell 18650 mắc song song (1S), qua bộ bảo vệ pin và 2 module nâng áp 5 V.

> **Trạng thái:** thiết kế đã qua kiểm tra của team (board, firmware, case, tích hợp). **Chưa thử phần cứng.** Chưa flash firmware. Chưa in các gá mới. Chưa đặt mạch. Kích thước module ghi trong tài liệu là **GIẢ ĐỊNH**: đo module thật trước khi in hoặc hàn.

## Có gì trong repo

| Thư mục | Nội dung |
|---|---|
| `design/` | Dự án KiCad: schematic, PCB, thư viện, model 3D linh kiện |
| `engineering/` | Nguồn ([POWER_SYSTEM.md](engineering/POWER_SYSTEM.md)), nối dây stack ([STACK_WIRING.md](engineering/STACK_WIRING.md)), lắp ráp, bring-up, pinout, các phép tính |
| `parts.json`, `product.json`, `manufacturing.json` | BOM (mã LCSC), mô tả board, cấu hình gia công |
| `case/` | Script CadQuery cho các gá ([build.py](case/build.py), `holders.py`, `stack.py`, `power_b.py`). `case/ref/v1`, `case/ref/v5` là STEP gốc của robot-tank đã in, giữ nguyên |
| `firmware/` | Firmware ESP32 (`firmware/tank/`), [hướng dẫn nối dây](firmware/WIRING.md), [giao thức host](firmware/PROTOCOL.md), test chạy trên máy (`firmware/tests/`), host bridge (`firmware/host/`) |
| `tools/` | Script kiểm/xuất của từng team (board, case, firmware) |
| `contract/` | Hợp đồng team đã niêm phong và release notes (lời người dùng giữ nguyên văn + cách lead diễn giải) |
| `prompts/`, `references/` | Yêu cầu gốc, lịch sử yêu cầu, ảnh tham khảo. STEP/STL trong `prompts/assets` không commit: hash nằm trong các file `SHA256SUMS` |

Những thứ không commit, vì `./build.sh` sinh lại được: STL/STEP/3MF, gerber, zip, ảnh render, `build/`, `boards/`, `case/out/`, `case/print/`, binary firmware. Datasheet không commit: link nằm ở `engineering/sources/manifest.json`.

## Build

```sh
./build.sh              # board -> case -> firmware
./build.sh firmware     # chỉ một stage
./build.sh board case
```

Yêu cầu, không tự cài gì qua mạng:

- `KICAD_HARNESS_PYTHON` (Python có `kicadpy`) và `KICAD_CASE_PYTHON` (Python có CadQuery + `kicadpy`). Harness cấp sẵn cả hai.
- KiCad 9 `kicad-cli`. Script tự tìm ở `/Applications/KiCad/KiCad.app`, hoặc set `KICAD_CLI`.
- Bambu Studio ở `/Applications/BambuStudio.app`, dùng để slice `case/print/*.3mf`. Không job in nào được gửi.
- `arduino-cli` với core `esp32:esp32@2.0.14` đã cài sẵn. Nếu core nằm ngoài thư mục mặc định thì set `ARDUINO_DIRECTORIES_DATA` trỏ tới đó (Harness để ở `~/.cache/autonomous-circuit/firmware/arduino`).

Build sinh lại vài file đang commit: hash STEP của board trong `case/ref/board/SHA256SUMS`, `engineering/step-handoff.json` và `case/firmware-limits.json`. Thấy chúng đổi sau khi build là bình thường.

Từng stage sinh ra:

- **board:** chạy kiểm tra chính thức của board (ERC/DRC, netlist, gate) và sinh gói gia công vào `boards/`. Xuất STEP mạch có linh kiện ra `build/board/main-contract.step`, rồi giao cho case (`case/ref/board/`, hash được tính lại).
- **case:** chạy `case/build.py` xuất STEP/STL vào `case/out/`. Chạy 3 bài kiểm của case: in được và va chạm, v5 so với v1, góc xoay turret. Sau đó sinh plate in `case/print/production.3mf` + `test-only.3mf`, file `case/overview.html`, và chạy `kicadpy.case check-print` (kiểm in: bề mặt in được, vừa bàn in).
- **firmware:** chạy test host, gồm mock và ASan/UBSan, rồi compile ESP32 ra `build/firmware/esp32/tank.ino.bin`. **Không flash.**

Stage nào đọc output của stage trước thì `build.sh` tự chạy luôn stage đó nếu output còn thiếu. Case cần STEP của board. Firmware cần `case/reports/turret_yaw.json` để biết góc xoay turret.

## Firmware làm được gì

- Giữ mặt pet và trạng thái phiên Claude Code của claude-pet, giờ trên màn ST7789 1.54" 240×240.
- Nói chuyện với máy tính qua USB (UART0 115200).
- **Điều khiển bằng điện thoại**, làm theo UI của con cua crab-robot-v17g:
  - Xe tự phát WiFi mở tên `XeTang-XXXX`. Trên màn hiện tên mạng, địa chỉ và mã QR.
  - Vào WiFi đó rồi mở `http://192.168.4.1/`. Nhiều máy tự bật trang lên luôn.
  - Trang **Lái**: pad 8 hướng, giữ nút để chạy, thả là dừng. Có 3 mức tốc độ 0.4 / 0.65 / 1. Xe không cho tiến/lùi khi sonar hướng đó báo vật cản gần hơn 350 mm, hoặc chưa có số đo mới (cũ hơn 250 ms). Nút đèn hiện "chưa nối" vì đèn chưa có chân điều khiển.
  - Trang **Ráp**: chỉnh tâm, biên và chiều quay cho từng bánh, chỉnh tâm turret (giới hạn ±70°), rồi Lưu. Chưa hiệu chuẩn xong thì xe không cho lái.
  - Trang **Wi-Fi** (tuỳ chọn): nối vào WiFi nhà, mật khẩu lưu trong NVS.
  - Cái gì đòi dừng thì dừng: thả nút, quá 500 ms không có lệnh, mất kết nối phone, nút STOP, lỗi I2C, watchdog.
  - Mấy hằng số (500 ms, 5 s, 60 % xung ở tốc độ 1) **chưa thử** trên xe và phone thật.
- Board có thêm module nâng áp logic `M_LOGIC` (Pololu U3V16F5) cấp USB cho DevKit từ pin. Nhờ vậy xe chạy được mà không cần cắm máy tính.
- Điều khiển 6 bánh (PCA CH0–5) với hiệu chuẩn từng bánh, và turret (CH6).
- Chế độ dò đường kiểu chạy–dừng bằng 2 sonar HC-SR04P. `AUTO SCAN` đang bị khoá cho đến khi đo góc turret thật trên xe.
- Bật lên luôn ở trạng thái dừng. Mất link, hết heartbeat hoặc bấm nút STOP (GPIO27) là cắt servo.

Chân GPIO: xem [firmware/README.md](firmware/README.md) và [engineering/esp32-pinmap.json](engineering/esp32-pinmap.json).

## Case: in gì, lắp ra sao

Đọc [case/README.md](case/README.md). Tóm tắt:

- **Không in lại** phần robot-tank v1 đã in: chassis, hull, lid, turret, giá đèn, 6 tay đòn, 6 bánh.
- In mới các gá dán/kẹp và cụm **stack v5**: đế, tầng PCA9685 + quạt, tầng ESP32, nắp có ô servo turret và mặt vát 45° cho màn.
- **Phương án B** là phương án đang chọn: bỏ lid, stack đứng trên bàn kê phía trên 2 cell. Tổng cao **214,8 mm**, so với 118,3 mm của v1. Chỉ có B chứa vừa carrier 62×60 cùng các module.
- In plate **TEST ONLY** trước, thử với module thật, rồi mới in bản chính.

## Những chỗ có thể phải tự sửa tay

Các tester ghi lại những điểm dưới đây. Mục 1–8 có từ lần chạy `r006`, có thể đã được sửa một phần. Mục 9–11 có từ lần chạy mới nhất `r007`. Cả 2 lần chạy đều không có `lead-document-findings.json`. Chưa điểm nào được đo trên phần cứng.

1. **Bộ nâng áp servo sát giới hạn.** Dòng đỉnh ước tính khi lấy từ pin là ~8,9 A, cao hơn mức 8 A điển hình của Pololu U3V70F5. Đo dòng thật khi 6 bánh cùng kẹt hoặc khởi động, cân nhắc giới hạn tốc độ hoặc tách tải.
2. **Tài liệu nguồn còn sót bản cũ.** Vài dòng trong `product.json`, `engineering/POWER_SYSTEM.md`, `parts.json` vẫn mô tả chuỗi nguồn cũ (TPS61287, LILYGO, carrier 100×70, dây 12 AWG / 30 A). Bản đang dùng là: 2 module Pololu U3V70F5, ESP32 DevKit, carrier 62×60. Dây pin chính cần đầu nối chịu ≥15 A, khớp với cầu chì `F_PACK`.
3. **ACT_EN lúc ESP32 khởi động.** Chân ENABLE của bộ nâng áp thứ hai nối vào ACT_EN qua dây Dupont, có kéo lên VIN (≤4,2 V) qua 100 kΩ. Đo kiểm trên bàn rằng ACT_EN ở mức thấp trong lúc ESP32 boot và reset, để servo không giật.
4. **Chiều header 2×6 trong `firmware/WIRING.md`** chưa khớp layout 62×60 mới. Lấy [engineering/pinout.md](engineering/pinout.md) làm chuẩn khi bấm dây `J_CTRL` / `J_PCA`.
5. **Dây pin chưa qua cầu chì dài ~35 mm**, vượt giới hạn ≤25 mm. Dời giá `fuse_holder_pack` lại gần pin, hoặc gắn `F_PACK` ngay trong cụm pin.
6. **Không có chỗ cho mạch sạc trên xe.** Muốn sạc thì rút phích RUN ra, sạc trên bàn.
7. **Kích thước module là giả định:** ESP32 51,5×28,3, PCA9685 62,2×25,4, quạt 30×30×10, màn 32×38×4. Đo đồ thật và in coupon TEST ONLY trước.
8. **Phương án B làm xe cao gần gấp đôi** và phải bỏ lid. Nếu muốn giữ lid như v1 thì phải nhờ team thiết kế lại.
9. **Sơ đồ nguồn chưa cập nhật `M_LOGIC`.** Vài chỗ trong `engineering/POWER_SYSTEM.md` vẫn ghi DevKit lấy 5 V từ USB riêng, có dòng còn nhắc LILYGO. `case/logic_b.py` và `firmware/reports/integration.json` cũng còn nhắc "chuỗi optional" cũ. Thứ tự cấp nguồn bring-up trong `firmware/WIRING.md` (cấp logic trước, rồi mới cấp 2 đảo A/B) không khớp sơ đồ, vì trên sơ đồ cả 3 module nâng áp nối song song ngay ở dây RUN.
10. **Chỗ đặt DevKit:** đường dây `M_LOGIC` ghi DevKit nằm ở "tier 3", trong khi `STACK_WIRING.md` và `parts.json` ghi tier 2. Lấy tier 2.
11. **Cấp nguồn DevKit qua cổng USB thôi**, đừng nối thêm vào chân VIN song song với USB.

## An toàn

Pin Li-ion 1S cho dòng lớn. Phải có bộ bảo vệ và cầu chì như trong [engineering/POWER_SYSTEM.md](engineering/POWER_SYSTEM.md). Không nối song song đầu ra hai bộ nâng áp. Không cấp servo qua chân 5V của DevKit hay qua USB máy tính.
