#!/usr/bin/env python3
"""Write case/assembly_steps.json (the one ordered step list shared by README, overview and guide)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
V1 = ['chassis', 'hull']
SUSP = ['arm_*', 'wheel_*', 'ref_servo_front_*', 'ref_servo_mid_*', 'ref_servo_rear_*', 'ref_horn_front_*', 'ref_horn_mid_*', 'ref_horn_rear_*']
CELLS = ['cell_cradle', 'ref_cell_*']
A_LID = ['lid']
BASE = V1 + ['led_bracket'] + SUSP + CELLS
PWR = ['conv_holder_a', 'conv_holder_b', 'fuse_holder_pack', 'protector_holder', 'fuse_clip_b', 'ref_conv_a_B', 'ref_conv_b_B', 'ref_fuse_pack_B', 'ref_protector_B', 'ref_fuse_b_B', 'logic_holder', 'ref_logic_B']
STK = ['stack_bridge_plate', 'stack_leg_*']
DECK = ['stack_carrier_deck', 'ref_carrier_B']
T1 = ['stack_tier_1', 'ref_pca9685_B', 'ref_fan_B']
T2 = ['stack_tier_2', 'ref_esp32_B']
CAP = ['stack_turret_mount', 'ref_screen_stack_B', 'ref_servo_turret_stack_B', 'ref_horn_turret_stack_B', 'ref_turret_head_B', 'ref_sonar_front_B', 'ref_sonar_rear_B']
STEPS = [
 ('Khung gầm v1 đã in: chassis + hull', V1, ['chassis', 'hull'], 'iso', [],
  'Bộ v1 đã in (chassis, hull, lid, turret_head, led_bracket, 6 tay đòn, 6 bánh): giữ nguyên, không in lại, không khoan. Chưa xác minh bản bản in thật khớp hash v1 (xem PRINTED-INVENTORY.md). Phương án B bỏ lid, turret_head v1 và lòng thân để hở.'.replace('bản bản','bản')),
 ('Treo: 6 servo 360°, tay đòn, bánh, giá đèn', V1 + ['led_bracket'] + SUSP, ['arm_*', 'wheel_*', 'led_bracket'], 'iso',
  [{'ids': ['M3-lug'], 'what': 'chốt M3 xuyên tai khung gầm và tay đòn (theo v1)', 'count': 6, 'entry': 'từ ngoài vào, v1 đã in'}],
  'Mỗi bên 3 tay đòn: servo + bánh ở một đầu, móc dây thun ở đầu kia. Dây thun lực chưa đo (GIẢ ĐỊNH). Bánh trước chạm giá đèn ở khoảng −10…−12° khi nâng. Luồn dây servo qua rãnh sàn trước khi đặt pin.'),
 ('Khay đỡ 2×18650 (cell_cradle) + 2 cell', BASE, ['cell_cradle'], 'top',
  [{'ids': ['keo-502'], 'what': 'keo 502 dán yên đỡ lên sàn chassis', 'count': 1, 'entry': 'dán từ trên xuống'},
   {'ids': ['dai-15'], 'what': 'đai/dây rút 15 mm giữ cell', 'count': 2, 'entry': 'luồn qua 4 rãnh đai'}],
  'Dán cradle vào sàn chassis trước, rồi đặt 2 cell Ø18,6 song song. Mạch bảo vệ/nối cell chưa xác minh.'),
 ('Cụm nguồn B: bảo vệ pin, cầu chì, 2 bộ nâng áp', BASE + PWR, ['conv_holder_*', 'fuse_holder_pack', 'protector_holder', 'fuse_clip_b', 'logic_holder'], 'top',
  [{'ids': ['keo-502'], 'what': 'dán 5 giá (2 bộ nâng áp, giá cầu chì pin, tường bảo vệ, giá bộ 5 V logic U3V16F5) lên sàn trước cell', 'count': 5, 'entry': 'từ trên xuống'},
   {'ids': ['keo-502'], 'what': 'dán kẹp cầu chì 5 A lên vách nghiêng 45° bên phải (mặt dán úp xuống khi in)', 'count': 1, 'entry': 'từ trong'}],
  'Theo board deviation 8: pin kín → F_PACK → PCB-Li-1S15A → XT60 → hai U3V70F5 (đầu vào song song, đầu ra KHÔNG nối nhau). A → J_PWR; B → cầu chì 5 A → chập dây đỏ servo CH3–5 (rút chân V+ khỏi J_S3…J_S5); ACT_EN (J_CTRL.6) → ENABLE của B kèm 4,7 kΩ xuống GND. Dây ≥14 AWG. Kích thước linh kiện công suất là GIẢ ĐỊNH, in coupon nguồn trước. Bộ 5 V logic U3V16F5 (logic_holder, trái cửa sổ trước): cấp DevKit chạy pin qua XT60→VIN và VOUT→USB DevKit; không cắm đồng thời cáp host (không Y-cable); tuyến theo case/layout_b.json, kích thước GIẢ ĐỊNH, in coupon logic trước. Khay sạc A/B (module "5V 2A") chỉ cho phương án A, không lắp ở B. Chưa kiểm chứng B tắt hẳn khi ACT_EN thấp.'),
 ('Bàn đỡ stack + 4 chân (bỏ lid)', BASE + PWR + STK, ['stack_bridge_plate', 'stack_leg_*'], 'iso',
  [{'ids': ['keo-502'], 'what': 'dán 4 chân lên sàn chassis cạnh cell, rồi bàn lên chân', 'count': 5, 'entry': 'từ trên'}],
  'Phương án B là phương án lắp được (carrier 62×60 không lọt phương án A). Bàn cách đỉnh cell 0,6 mm; muốn tháo cell phải tách bàn. Chưa in: in 3 coupon TEST ONLY trước.'),
 ('Deck mạch + carrier 62×60', BASE + PWR + STK + DECK, ['stack_carrier_deck', 'ref_carrier_B'], 'iso',
  [{'ids': ['M3x8'], 'what': 'vít M3×8 tự ren giữ carrier vào 4 trụ deck (H1…H4)', 'count': 4, 'entry': 'từ trên xuống qua lỗ board'}],
  'Deck cắm lên chốt của bàn. Mặt dưới board Z 77,9; tầng sau cách 30 mm để đầu servo cắm đứng. Nối: 6 servo → J_S0…J_S5, servo turret → J_S6, sonar → J_SONAR_F/R, bộ nâng áp A → J_PWR.'),
 ('Tầng 1: PCA9685 + quạt 30×30', BASE + PWR + STK + DECK + T1, ['stack_tier_1', 'ref_fan_B'], 'iso',
  [{'ids': ['M2.5'], 'what': 'vít M2.5 giữ PCA9685 (lỗ 55,9×19,05)', 'count': 4, 'entry': 'từ trên qua lỗ board'},
   {'ids': ['rut'], 'what': 'dây rút buộc quạt qua 4 khe tầng', 'count': 4, 'entry': 'qua khe 24×36'}],
  'Chốt Ø4,4 cắm lỗ 5,0. Quạt buộc dưới tầng 1, thổi xuống carrier, dây khoảng 60 mm vào J_FAN. Quạt 10 mm dày và PCA 62,2×25,4 là GIẢ ĐỊNH. Cổng J_PCA nối PCA với carrier.'),
 ('Tầng 2: ESP32 DevKit', BASE + PWR + STK + DECK + T1 + T2, ['stack_tier_2', 'ref_esp32_B'], 'iso',
  [{'ids': ['rut'], 'what': 'dây rút / 2 ray giữ DevKit', 'count': 2, 'entry': 'qua khe tầng'}],
  'DevKit 30 chân 51,5×28,3 GIẢ ĐỊNH, đo module thật. J_CTRL nối DevKit với carrier. USB ra hai bên dưới mặt màn.'),
 ('Nắp stack: turret SG90 + màn + 2 sonar HC-SR04P', BASE + PWR + STK + DECK + T1 + T2 + CAP, ['stack_turret_mount', 'ref_turret_head_B'], 'iso',
  [{'ids': ['horn-vit'], 'what': 'vít horn SG90', 'count': 1, 'entry': 'từ trên'}],
  'Mặt nghiêng 45° có cửa sổ màn 29×29. Cao toàn xe 214,8 mm (v1: 118,3), cần lead duyệt. Turret không có ổ đỡ. Chừa vòng dây dư; quay tay turret một vòng trước khi bật quét ±70°.'),
]
steps = [{'title': t, 'show': show, 'focus': focus, 'camera': cam, 'hw': hw, 'action': act} for t, show, focus, cam, hw, act in STEPS]
(ROOT / 'case/assembly_steps.json').write_text(json.dumps({'steps': steps}, indent=1, ensure_ascii=False) + '\n')
print(len(steps), 'steps')
