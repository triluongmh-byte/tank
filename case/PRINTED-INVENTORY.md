# Kiểm kê bản in thật (case-docs, r005)

Nguồn bằng chứng: lời người dùng trong ghi chú 8 ("Tao in hết rồi", build v1 của cadsmith robot-tank, check pass
2026-11-25) và ghi chú 9 (không nói đã in stack v5). Không có `print/events.jsonl` (không có xác nhận hay lỗi in từ
máy in). Một job in "complete" không bao giờ được coi là đã in. Chưa có ảnh nào xác định bản in.
Độ tin cậy: **thấp-trung bình** — lời kể, chưa có ảnh/hash. Chưa xác minh máy in, vật liệu, ngày in, và file in
có trùng hash v1 hay không. Chưa có báo cáo vừa/hỏng/chỉnh sửa → trạng thái "vừa/chạy" **chưa biết**.

## Đã in (theo lời người dùng) — GIỮ LẠI, không in lại
| ID | SL | Revision | Bằng chứng | Trạng thái |
|---|---|---|---|---|
| chassis | 1 | cadsmith v1 | ghi chú 8 | đã in; vừa/chạy chưa biết |
| hull | 1 | v1 | ghi chú 8 | như trên |
| lid | 1 | v1 | ghi chú 8 | như trên |
| turret_head | 1 | v1 | ghi chú 8 | như trên |
| led_bracket | 1 | v1 | ghi chú 8 | như trên |
| arm_front/mid/rear_left/right | 6 | v1 | ghi chú 8 | như trên |
| wheel_front/mid/rear_left/right (Ø42×18,7) | 6 | v1 | ghi chú 8 | như trên |

Hình học: v5 chassis/hull/lid trùng v1 (`case/reports/v5_compare.json`); bản v1 đã in là chuẩn.
Bốn bánh claude-pet Ø54 (ghi chú 3) bị thay bằng bánh v1 ở ghi chú 8: không còn theo dõi 2 bánh cần in thêm.
Các bánh/ chi tiết **không** nằm trong production 3MF vì `printable: false` trong `parts.json` (không in lại; nếu
hỏng thì in lại từ STEP v1 gốc ở `case/ref/v1/`).

## Chưa in — cần in mới (nằm trên 6 plate production)
| ID | SL | Phương án | Trạng thái |
|---|---|---|---|
| cell_cradle (cũng dùng cho B), power_tray_a, power_tray_b, fan_plate | 1 mỗi loại | A | chưa in |
| esp32_post_rear/front, pca_post ×4, screen_clip_left/right | 2 + 4 + 2 | A | chưa in |
| stack_bridge_plate, stack_tier_1, stack_tier_2 | 1 mỗi loại | B | chưa in (chưa rõ người dùng đã in stack v5 chưa → không tính là đã in) |
| stack_carrier_deck (mới, tích hợp: đỡ carrier 62×60) | 1 | B | chưa in |
| stack_turret_mount, stack_leg ×4 | 1 + 4 | B | chưa in |
| conv_holder_a/b, fuse_holder_pack, protector_holder, fuse_clip_b (mới: chuỗi nguồn hai đảo) | 5 | B | chưa in |
| coupon_fit_TEST_ONLY, coupon_stack_TEST_ONLY, coupon_deck_TEST_ONLY, coupon_power_TEST_ONLY | 1 + 1 + 1 + 1 | thử | TEST ONLY, in trước, không lắp vào xe |
| stack_base (v5 92×43) | — | — | KHÔNG in: lỗ M3 82×20 không khớp phần đã in, thay bằng bridge + 4 chân |

Đối chiếu: 17 chi tiết v1 đã in + 26 chi tiết mới (12 gá A + 9 stack B + 5 nguồn B) = 43 chi tiết hiện hành; thêm 4 coupon TEST ONLY riêng. Production 3MF chứa 26 chi tiết mới.
Phương án B là phương án lắp được (carrier 62×60 không lọt phương án A, xem INSPECTION.md); nhóm gá A chỉ còn để ghi lại / phần cell_cradle và dùng chung với B (khay sạc chỉ A). Cả hai nhóm vẫn nằm trong 3MF.

Cập nhật file này khi người dùng báo đã in, hỏng, chỉnh hoặc gửi ảnh. Chưa có print/events.jsonl.
