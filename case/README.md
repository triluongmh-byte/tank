# Pet Tank — case robot-tank v1 (đã in) + gá bổ sung

Điểm vào cho lắp ráp và xem 3D: **[overview.html](overview.html)** (Case → Overview; chip "Đủ bộ" rồi Bước 1…9).
Ghi chú của hệ thống cho người dùng: **[NOTES.md](NOTES.md)**. Báo cáo "soi" v1 và số đo: [INSPECTION.md](INSPECTION.md).
Sai lệch so với hợp đồng: [DEVIATIONS.md](DEVIATIONS.md). Kiểm kê bản in: [PRINTED-INVENTORY.md](PRINTED-INVENTORY.md).
Hộp module cho board/firmware: [modules.json](modules.json).

**Trạng thái trung thực:** CAD và slicer đã kiểm; **chưa in, chưa lắp thử, chưa thử phần cứng**. Mọi kích thước
module (ESP32 51,5×28,3, PCA9685 62,2×25,4, module sạc 26×21×7, quạt 30×30×10, màn 32×38×4) là **GIẢ ĐỊNH** — đo
module thật và in coupon trước.

## Cái gì đã in, cái gì cần in
- **Đã in (theo lời bạn, ghi chú 8):** chassis, hull, lid, turret_head, led_bracket, 6 tay đòn, 6 bánh Ø42 của robot-tank v1.
  Giữ nguyên, **không in lại, không khoan, không sửa**.
- **Cần in mới:** các gá dán/kẹp vào phần đã in (xem 6 plate dưới). Chưa có xác nhận in nào.
- **Phương án lắp được: B** (sau review tích hợp): lid bỏ, stack đứng trên bàn kê phía trên 2 cell, carrier 62×60 của board nằm trên `stack_carrier_deck`, rồi tầng 1 (PCA9685 + quạt), tầng 2 (ESP32), nắp stack (turret + màn). Cao 214,8 mm (v1: 118,3), **cần lead duyệt**. Phương án A (giữ lid) không chứa nổi carrier cùng module: gá A (cột ESP32/PCA, kẹp màn, tấm quạt) chỉ để ghi lại, không có trong các bước lắp. `cell_cradle` dùng cho B. Hai khay sạc "5V 2A" (`power_tray_a/b`) chỉ cho A: B dùng chuỗi nguồn hai đảo của board (deviation 8) với 5 giá mới ở plate 5.

## File in (đã slice bằng Bambu Studio CLI, chưa gửi job nào)
Cấu hình tham chiếu GIẢ ĐỊNH: Bambu A1 0,4 mm, 0.20mm Standard, PETG (Bambu PETG Basic), không support.
Thời gian và gram do slicer ước (khối lượng riêng PETG 1,27 g/cm³ GIẢ ĐỊNH).

| File | Plate (tên native trong Bambu) | Chi tiết | Ước tính |
|---|---|---|---|
| [print/production.3mf](print/production.3mf) | 1 · MỚI-SỬA — CẦN IN — Gá A — khay, quạt | cell_cradle (B), power_tray_a/b và fan_plate (chỉ A) | 43 phút · 9,1 g |
| | 2 · MỚI-SỬA — CẦN IN — Gá A — cột, kẹp | esp32_post ×2, pca_post ×4, screen_clip ×2 (chỉ A, ghi lại) | 20 phút · 2,2 g |
| | 3 · MỚI-SỬA — CẦN IN — Stack B — tầng | stack_bridge_plate, stack_tier_1, stack_tier_2 | 2 g 10 phút · 25,1 g |
| | 4 · MỚI-SỬA — CẦN IN — Stack B — deck mạch | stack_carrier_deck | 1 g 28 phút · 17,7 g |
| | 5 · MỚI-SỬA — CẦN IN — Nguồn B — giá, kẹp | conv_holder_a/b, fuse_holder_pack, protector_holder, fuse_clip_b | 40 phút · 8,1 g |
| | 6 · MỚI-SỬA — CẦN IN — Stack B — nắp, chân | stack_turret_mount, stack_leg ×4 | 1 g 11 phút · 14,4 g |
| [print/test-only.3mf](print/test-only.3mf) | 1 · TEST ONLY — thử khớp A, stack, deck, nguồn | coupon_fit, coupon_stack, coupon_deck, coupon_power | 52 phút · 8,5 g |

Không có plate "ĐÃ IN — GIỮ LẠI" vì chi tiết v1 đã in là `printable: false` (không in lại). Để làm phương án B: plate 1 (chỉ cell_cradle cần), 3, 4, 5, 6. Plate 2, fan_plate và 2 khay sạc chỉ cho A. **In TEST ONLY trước**, thử với module thật, không lắp vào xe.
Báo cáo kiểm: [print/check.json](print/check.json), [print/test-only-check.json](print/test-only-check.json)
(mỗi chi tiết nằm đúng một lần, dài nhất theo trục X, trong bàn 256 mm, tránh vùng loại trừ A1). Cảnh báo slicer thật:
không tìm thấy file preset hệ thống đầy đủ (dùng profile nhúng trong project) — không ảnh hưởng hình học.
Script: `tools/case/docs/make_plates.py`, `slice_and_verify.py`. Chưa xác minh máy in/vật liệu thật của bạn.

## Lắp ráp (phương án B, 9 bước — cùng danh sách với overview, [assembly_steps.json](assembly_steps.json))
1. Khung gầm v1 (chassis + hull) · 2. 6 servo 360° + tay đòn + bánh + giá đèn · 3. Khay đỡ 2×18650 · 4. Cụm nguồn B (bảo vệ pin, cầu chì, 2 bộ nâng áp) ·
5. Bàn đỡ + 4 chân · 6. Deck + carrier 62×60 (4 vít M3×8) · 7. Tầng 1: PCA9685 + quạt · 8. Tầng 2: ESP32 · 9. Nắp stack: turret + màn + 2 sonar.
Dây theo carrier: 6 servo → J_S0…J_S5, servo turret → J_S6, sonar → J_SONAR_F/R, DevKit → J_CTRL, PCA → J_PCA, quạt → J_FAN,
bộ nâng áp A → J_PWR; bộ nâng áp B → cầu chì 5 A → dây đỏ servo CH3–5; ACT_EN → ENABLE của B (đầu ra A và B không nối nhau). Luồn dây servo trước khi đặt pin; dùng đầu cắm 90° nếu cần.
Keo 502, dây rút và vít M3/M2.5 là phần cứng thường; số lượng đúng theo thẻ "Vít/tán bước này".

## Bản vẽ kỹ thuật (do harness vẽ từ STEP, không sửa)
Tổng thể: [assembly.svg](out/drawings/assembly.svg). Từng chi tiết trong [out/drawings/](out/drawings/index.json), ví dụ
[cell_cradle](out/drawings/cell_cradle.svg), [fan_plate](out/drawings/fan_plate.svg),
[stack_bridge_plate](out/drawings/stack_bridge_plate.svg), [stack_tier_1](out/drawings/stack_tier_1.svg),
[stack_turret_mount](out/drawings/stack_turret_mount.svg), [chassis](out/drawings/chassis.svg), [hull](out/drawings/hull.svg).
Overview cũng liệt kê danh sách bản vẽ trong phần chi tiết.

## Việc bạn có thể phải tự làm / chưa biết
- Đo module thật (ESP32, PCA9685, module nguồn (U3V70F5, bảo vệ, cầu chì), quạt, màn) rồi so với coupon; kích thước hiện là GIẢ ĐỊNH.
- Chưa có cổng USB/Type-C ra ngoài ở v1: tháo lid (A) hoặc dùng module B (B) để cắm. Sạc 2 cell song song chưa xác minh.
- Turret không có ổ đỡ (v1); bánh trước chạm giá đèn ở ≈ −12° khi nâng; lực dây thun chưa đo.
- Chiều cao B 214,8 mm cần lead duyệt; quay tay turret một vòng trước khi bật quét ±70° (`firmware-limits.json`).
- Nguồn: chuỗi hai đảo của board (pin kín + PCB-Li-1S15A + F_PACK, 2× U3V70F5, cầu chì 5 A) — linh kiện và kích thước là GIẢ ĐỊNH; board còn yêu cầu đo bench "ACT_EN thấp = 0 V ở cả hai đảo". Bộ sạc M_CHARGE không có chỗ trên xe (để ngoài, sạc rời). Dây F_PACK dài ≈35 mm, vượt 25 mm board muốn. Pin 140 g của bạn chưa xác định; tải kẹt rotor đủ cần ≈11 A.
- Firmware phải rebuild cho ESP32 + ST7789 (việc khác của đội firmware, không thuộc tài liệu này).
