# Soi bộ robot-tank v1 đã in (ghi chú 8)

Nguồn: bản sao có checksum ở `case/ref/v1/` (SHA256SUMS; 7 file trùng hash với
`prompts/assets/robot-tank-cadsmith-v1/SHA256SUMS`, phần còn lại chép từ
`/Users/macbookpro/cad-models/robot-tank/builds/v1/`, chỉ đọc). Số đo lấy từ STEP, không phải đo tay
trên bản in. Chưa xác minh bản in thật có khớp hash v1 không. Hệ tọa độ hợp đồng: X = −Y_v1, Y = −X_v1,
Z = Z_v1; gốc ở mặt đất dưới trục turret; mũi xe về −Y.

## Kích thước đo được
| Mục | Số đo (hệ hợp đồng) |
|---|---|
| Envelope toàn xe | X ±54,18 · Y −84,3…82,1 · Z 0…118,3 → **108,4 × 166,4 × 118,3 mm** (khớp report v1) |
| Lòng thân | sàn Z 43,0 (mặt trên chassis) → mặt dưới nắp Z 70,0: **cao 27 mm**. Rộng 64 mm (|X| ≤ 32) từ Z 43 tới 48,8, sau đó vách nghiêng 45° mở tới |X| 47 ở Z 63,8. Dài trong: Y −78 (mũi) … +80,1 (vách sau) |
| Bosses vít thân | 4 trụ r 4,5 ở X ±28, Y −20 và +40, Z 43…49, đai ốc tới Z ≈ 51,4 |
| Cửa sổ màn | **29 × 29 mm** trên mặt nghiêng 45° (pháp tuyến (0, −0,707, 0,707)), tâm mặt trong (0, −65,6, 57,6). Màn 1,54" 240×240 có vùng hiển thị ≈ 27,7 mm → dư 0,6 mm mỗi cạnh. Lòng mũi ở mép dưới màn chỉ rộng ±20,5 mm (Z 46) → module rộng tối đa ~40 mm. v1 không có chi tiết giữ màn |
| Khoang 2×18650 | Cell nằm thẳng trên sàn, Y +14,4…+79,6, |X| ≤ 19, Z 43…61,6. **v1 không có khay/đai giữ pin.** Hai rãnh dây servo sau (Y 48…56) nằm ngay dưới cell → bị cell che |
| 4 cột Nano | Ø4,4, treo 4 mm dưới nắp (Z 66…70), lỗ mồi Ø1,6, lưới 43,2 × 15,2 quanh (−19, −14). Không khớp lỗ PCA9685 (55,9 × 19,05) hay ESP32; giữ nguyên, không dùng |
| Turret | SG90 cắm thẳng qua lỗ nắp, đầu turret gắn trên horn, **không có ổ đỡ**: toàn bộ tải lệch của 2 sonar đi vào trục SG90. Quét ±90° sạch: khe nhỏ nhất 1,43 mm (đầu turret ↔ thân servo) |
| Treo | 6 đòn bẩy quay quanh M3 (khe lug 0,4 mm). Nâng bánh lên: bánh trước kẹt giá LED ở ≈ −12° (sạch tới −10° ≈ 3,1 mm hành trình đứng), bánh giữa/sau sạch tới −14° (≈ 4,4 mm). Hạ xuống do dây thun giữ, chưa đo lực thun |
| Khoảng sáng gầm | khi nghỉ: tay đòn Z 12,4 (đi theo bánh), servo 14,9, giá LED 16,0, móc thun chassis 23,5, đáy chassis 40,0 |
| Lỗ dây sẵn có | cửa sổ sàn 24×24 (Y −62…−38), 6 rãnh 8×5 cạnh mỗi servo, lỗ dây nắp Ø7 ở (14, −14), cửa pin trên nắp 52×34, 4 cửa thông gió 12×12 trên vách nghiêng (Y ±26), cửa sau 16×16 (sau cell), 2 lỗ đèn hậu 5 mm |
| USB / Type‑C | Không có lối cắm từ ngoài. USB ESP32 (quay về đuôi) chỉ cắm được khi tháo nắp; cáp host đi ra cửa thông gió sau‑phải (đầu micro‑USB lọt 12×12). Type‑C của module sạc/boost chỉ cắm được khi tháo nắp |

## Còn thiếu trong v1 → chi tiết in bổ sung (dán 502)
| Thiết bị | Chi tiết mới | Vị trí / cách giữ |
|---|---|---|
| ESP32 DevKit | `esp32_post_rear/front` (cùng 1 mẫu) | 2 cột dán sàn, gờ đỡ + chặn đầu, băng keo xốp 2 mặt; PCB ở Z 61,5. Dưới PCB còn 18,5 mm: **dupont thẳng không vừa** (cần ≈ 30 mm), dùng dupont cái bẻ 90°, hàn dây, hoặc carrier nhỏ có header cái |
| PCA9685 | `pca_post_*` ×4 (cùng 1 mẫu) | 4 cột có chốt Ø2,0 xuyên lỗ board; lấy chính board làm gá khi dán; PCB Z 46, cạnh dài ngang xe sau màn. Header logic 2 đầu: **phải dùng đầu cắm 90°** (đầu thẳng chạm mặt nghiêng) |
| Module sạc/boost 1S ×2 | `power_tray_a/b` | khay phẳng có 2 gờ, rãnh dây rút; cổng hai đầu để hở |
| 2×18650 | `cell_cradle` | 3 yên đỡ, 4 rãnh đai 15 mm; nâng cell 1,4 mm |
| Quạt 30×30 | `fan_plate` | dán trên nắp, trùm giữa cửa pin, ngay sau turret; 4 vít M3×16 + đai ốc lắp từ dưới. Cửa sau 16 mm của v1 quá nhỏ cho quạt 30 |
| Màn ST7789 1,54" | `screen_clip_left/right` | 2 kẹp dán mặt trong mặt nghiêng, mép kẹp đè lưng màn 2,5 mm |
| Carrier board | không vẽ | 100×70 không vừa. Hộp trống đo được: `case/modules.json` → `freeBoxes` |
| Thử khớp | `coupon_fit_TEST_ONLY` | in trước, thử bằng module thật |

Hộp module cho board/firmware: `case/modules.json`. Mọi kích thước module là GIẢ ĐỊNH tới khi đo
module thật; chưa coi lắp vừa là đã kiểm chứng.

## Ghi chú 9 — board stack của cadsmith v5
Nguồn: `case/ref/v5/` (SHA256SUMS; 11 file trùng hash với bản addenda, stack_tier_2 / servo / horn chép từ
`builds/v5`). Chưa rõ người dùng đã in stack hay chưa → mọi chi tiết stack để `printed: false`.

**v5 so với v1** (`case/reports/v5_compare.json`): chassis, hull, lid của v5 **trùng hình học với v1**
(thể tích bằng nhau, hiệu hình học = 0). Hash khác chỉ do nội dung file STEP. Bản v1 đã in vẫn là chuẩn.

**stack_base 92×43, M3 82×20:** không khớp lỗ nào trên phần đã in. Lỗ có sẵn: 4 lỗ vít thân 60×56, 2 lỗ giá LED
cách nhau 24. Nó cũng không đứng được trong thân: 92 mm dài hơn khoảng từ đầu cell (Y +14,4) tới mặt nghiêng.
Đặt tầng ở phía trước thì cột tầng 1 đâm vào mặt nghiêng ở độ cao Z 70. → Thay bằng **`stack_bridge_plate` + 4
`stack_leg_*`** (in mới, dán 502). Bàn kê trên khoang pin (Y +5,5…+79,5), mặt bàn Z 63,4…66,4, cách đỉnh cell 0,6 mm.
Chân dán sàn chassis cạnh cell (|X| 23…29,5) và tránh boss vít. 4 chốt Ø4,4 giống stack_base. Không khoan, không
sửa phần đã in. `stack_base` vẫn có trong parts.json, ghi DO NOT PRINT cho xe.

**Kiểm cấu hình B (bỏ lid, stack trên xe)** — `fit_checks.py`, nhóm `layoutB:*`, đều đạt:
- Bridge, 2 tầng, nắp turret, PCA, ESP32, màn, servo và đầu turret không chạm hull, chassis, cell/cradle, khay
  sạc, 6 servo bánh, tay đòn, bánh, giá LED. Tầng nằm trong miệng thân (|X| ≤ 21,5; miệng thân |X| ≤ 47).
- Envelope Z: **171,7 mm** (A: 118,3). X × Y không đổi: 108,3 × 166,4.
- Trọng tâm ước lượng (khối lượng GIẢ ĐỊNH, nhựa ~50% đặc): A Z ≈ 46 mm, góc lật ngang ≈ 44°. B Z ≈ 55 mm,
  ≈ 39°; cả xe ≈ 370 g. Turret và màn đặt cao hơn xe khoảng 50 mm.
- Dây (layout_b.json, mỗi dây 2 lối, đều mở): 6 dây servo lên qua rãnh giữa / dải cửa sổ sàn, rồi lên PCA tầng 1
  qua thân hở. PCA ↔ ESP32 đi qua cửa sổ tầng 2. ESP32 → màn đi ra mặt trước tầng, lên sau màn. Bó dây turret đi
  hai bên stack. Cáp USB DevKit (cổng hướng mũi, dưới mặt màn) đi ra bên phải hoặc xuống thân. Type‑C sạc chỉ cắm
  được ở **module B**, cắm từ phía phải, rồi ra trên miệng thân hoặc qua cửa thông gió trước‑phải. Khay A bị khay B
  và cell chắn, nên sạc pack song song qua module B (GIẢ ĐỊNH cổng nằm ở đầu ngắn).
- Muốn tháo cell thì phải nhấc tầng và bàn. Chân dán vĩnh viễn, mặt bàn chỉ dán lên chân, nên khi cần thì tách
  mặt bàn hoặc in bàn mới.

**Hai phương án turret + màn** (lead chưa chốt):
| | (a) Turret trên lid, màn sau glacis (v1) | (b) Turret + màn trên stack |
|---|---|---|
| Ưu | Thấp (118 mm), trọng tâm thấp. Không in thêm stack. Màn nằm đúng mũi ">" | Board dễ cắm, dễ sửa. Không cần đầu cắm 90°. USB, Type‑C, dây servo dễ với tới. Thêm tầng được |
| Nhược | Lòng thân chỉ cao 27 mm: dupont thẳng không vừa, cần đầu 90° hoặc hàn. Tháo lid mới cắm USB/sạc. Lid chưa có ổ đỡ | Cao 172 mm, trọng tâm cao hơn ~9 mm, góc lật nhỏ hơn ~5°. In thêm 4 chi tiết v5 + bàn + 4 chân. Cửa sổ màn trên glacis bỏ trống. Thân hở (bụi, va chạm). Turret vẫn không ổ đỡ |
| Không dùng | — | ổ turret và 4 cột Nano trên lid, kẹp màn, quạt trên lid, cột ESP32/PCA trong thân |

**Quạt 30×30 và module sạc trong B:** khe dây rút của tầng cách nhau 24 × 36. Quạt 30×30 (lỗ 24) buộc được qua
2 khe, nằm giữa 4 cột (khoảng trống |x| < 28,5). 2 module 26×21 xếp cạnh nhau (52 < 57) cũng buộc được trên
một tầng. Mỗi tầng thêm cao 26 mm. Trong bản B đã kiểm, module sạc vẫn nằm trên khay sàn; quạt chưa có chỗ
(tấm quạt chỉ dùng cho lid). Đề xuất: tầng 3 cho quạt (hoặc cho module sạc), chưa vẽ và chưa kiểm.

## Tích hợp (review của lead): carrier 62×60 của board
- Phương án A (giữ lid) **không chứa nổi** carrier cùng DevKit, PCA9685 và module sạc. Lòng thân chỉ cao
  27 mm, và chỗ carrier cần chính là chỗ đang đặt cột ESP32, cột PCA và khay sạc. → **Phương án B là phương án
  lắp được.**
- B có thêm `stack_carrier_deck`, cắm lên chốt của bàn kê. Carrier bắt 4 vít M3×8 tự ren vào 4 trụ, mặt dưới
  board ở Z 77,9. 4 cột nâng tầng PCA lên Z 109,5, chừa 30 mm cho đầu servo cắm đứng rồi bẻ dây.
- Chồng theo thứ tự: bàn kê → deck + carrier → tầng 1 PCA9685 (Z 117) → tầng 2 ESP32 (Z 135) → nắp turret
  (Z 134…170) → đầu turret tới Z 214,8. Trọng tâm ước lượng Z ≈ 65 mm, góc lật ngang ≈ 35°. Khối lượng là
  giả định.
- Dây (case/layout_b.json, mỗi dây 2 lối, đều thông):
  - 6 servo → J_S0…J_S5, servo turret → J_S6.
  - 2 sonar → J_SONAR_F/R.
  - J_CTRL → DevKit, J_PCA → PCA9685.
  - Module sạc B → J_PWR, dây 18 AWG, không mắc song song.
  - USB DevKit đi ra hai bên dưới mặt màn.
  - Type‑C sạc vẫn ở module B.
- Turret quét −70…+70° sạch ở cả hai phương án (case/reports/turret_yaw.json → case/firmware-limits.json).
  Cần chừa vòng dây dư cho sonar và servo.
- Quạt 30×30 (B): buộc dây rút dưới tầng 1 qua 4 khe sẵn có, thổi xuống carrier. Dây quạt khoảng 60 mm cắm vào
  J_FAN, có 2 lối đi đã kiểm.
- Lưu ý cho lead: chiều cao B là 214,8 mm (so với 118,3 mm của v1), cần lead duyệt. Trước khi firmware bật quét
  ±70°, quay tay turret một vòng để kiểm dây servo và dây sonar không bị kẹt.
