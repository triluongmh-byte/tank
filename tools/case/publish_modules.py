"""Write case/modules.json: measured device boxes (contract frame) for the board and firmware teams.

    python3 tools/case/publish_modules.py      (reads case/out/parts.json bboxes)
positionMm = min XYZ corner, sizeMm = XYZ size, contract frame (X=-Y_v1, Y=-X_v1, Z=Z_v1, ground Z=0).
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
parts = {p['name']: p for p in json.loads((ROOT / 'case/out/parts.json').read_text())['parts']}
INFO = {
 'ref_esp32_devkit': ('MCU', 'ESP32 DevKit 30-pin (GIẢ ĐỊNH 51.5 x 28.3), components up, USB end faces the tail (+Y). '
                      'PCB bottom Z=61.5 on 2 posts + foam tape. Below the PCB 18.5 mm to the floor: pins 8.5 mm, '
                      'then 90-degree dupont / soldered leads or a small carrier with female headers. Straight dupont does not fit (hull 27 mm tall).'),
 'ref_pca9685': ('PCA9685_MODULE', 'PCA9685 62.2 x 25.4, long side across the hull (X), servo headers on the tail-side long edge, '
                 'PCB bottom Z=46 on 4 peg posts. Logic end headers: 90-degree plug (straight hits the glacis). Address 0x40 unchanged.'),
 'ref_power_module_a': ('POWER_1S_BOOST_A', '1S charge/boost 5V 2A Type-C module (GIẢ ĐỊNH 26 x 21 x 7) on tray A. Type-C reachable only with the lid off.'),
 'ref_power_module_b': ('POWER_1S_BOOST_B', 'second module (separate servo / logic branch), tray B, turned 90 deg.'),
 'ref_cell_1': ('CELL_1', '18650 on the cradle (GIẢ ĐỊNH Ø18.6 x 65.2), parallel pack, leads exit at the -Y (front) end.'),
 'ref_cell_2': ('CELL_2', '18650 on the cradle.'),
 'ref_fan_3010': ('FAN_30', '30 x 30 fan (thickness GIẢ ĐỊNH 10) on the lid behind the turret, blowing into the battery window.'),
 'ref_screen_module': ('DISPLAY_ST7789_154', '1.54" ST7789 240x240 module behind the 29 mm glacis window (GIẢ ĐỊNH 32 x 38 x 4), normal (0,-0.707,0.707).'),
 'ref_servo_turret': ('SERVO_TURRET', 'SG90 180, PCA CH6, axis X=Y=0.'),
}
out = {'schema': 1, 'frame': 'contract: +X right, +Y tail, +Z up, ground Z=0 under the turret axis', 'source': 'case/out/parts.json bboxes',
       'carrier': 'Board carrier 62 x 60 x 1.6 (build/board/main-contract.step, sha in case/ref/board/SHA256SUMS). '
                  'Buildable mount = layout B: on stack_carrier_deck, board corner at contract (-31, 12.5), underside Z 77.9, '
                  'board top Z 79.5, M3 x 8 self-tap into 4 deck posts at H1..H4; next tier floor Z 109.5 (30 mm over the board top '
                  'for vertical servo plugs). Layout A (lid on) cannot hold the carrier together with the DevKit, PCA9685 and '
                  'chargers (case/DEVIATIONS.md 8); the 100 x 70 contract carrier fits nowhere.',
       'freeBoxes': [], 'modules': []}
for n, (mid, note) in INFO.items():
    if n not in parts:
        continue
    b = parts[n]['bboxMm']
    out['modules'].append({'id': mid, 'part': n, 'positionMm': b[:3], 'sizeMm': [round(b[i + 3] - b[i], 2) for i in range(3)], 'interface': note})
for s in ('front_left', 'mid_left', 'rear_left', 'front_right', 'mid_right', 'rear_right'):
    n = f'ref_servo_{s}'
    b = parts[n]['bboxMm']
    out['modules'].append({'id': f'SERVO_{s.upper()}', 'part': n, 'positionMm': b[:3], 'sizeMm': [round(b[i + 3] - b[i], 2) for i in range(3)],
                           'interface': 'SG90-360 (FS90R class) at rest on its v1 arm; moves with the suspension'})
out['freeBoxes'].append({'name': 'layout A only: under the ESP32, between its posts', 'positionMm': [11.0, -32.4, 45.0], 'sizeMm': [12.0, 37.3, 7.5],
                         'note': 'X 11..23, Y -32.4..4.9, Z 45..52.5; clear of the hull bosses, trays, the mid wire slot and ESP32 pins'})
B = {
 'ref_carrier_B': ('CARRIER', 'board 62x60 carrier on the deck (servo power switch, OE pull-up, U1, Echo shifters); servo headers J_S0..2 at X -27, J_S3..5 at X +27, J_S6 at X +21'),
 'ref_fan_B': ('FAN_30_B', '30x30 5 V fan (GIẢ ĐỊNH 10 thick) zip-tied under stack_tier_1 through its 4 zip slots, blowing down on the carrier; lead to J_FAN ~60 mm'),
 'stack_carrier_deck': ('STACK_CARRIER_DECK', 'NEW deck tier: sockets on the bridge pegs, 4 M3 posts for the carrier, 4 columns with pegs for the PCA tier'),
 'stack_bridge_plate': ('STACK_BRIDGE', 'glue-on table over the cell bay (plate + 4 legs), carries the tiers on 4 pegs'),
 'stack_tier_1': ('STACK_TIER_1', 'v5 tier 74x43, pitch 26: PCA9685 on 4 M2.5 standoffs 55.9 x 19.05; window 46 x 26 for leads'),
 'ref_pca9685_B': ('PCA9685_MODULE_B', 'PCA9685 on tier 1 (v5 model, GIẢ ĐỊNH 62.2 x 25.4); servo headers on the right (+X) long edge'),
 'stack_tier_2': ('STACK_TIER_2', 'v5 tier: ESP32 DevKit in 2 rails; pins hang down through the window'),
 'ref_esp32_B': ('MCU_B', 'ESP32 DevKit 30-pin on tier 2 (GIẢ ĐỊNH 51.5 x 28.3), USB end toward the nose (-Y)'),
 'stack_turret_mount': ('STACK_CAP', 'v5 cap: SG90 turret pocket + 45-degree face with the 29 x 29 screen window'),
 'ref_screen_stack_B': ('DISPLAY_B', '1.54" ST7789 behind the stack face window'),
 'ref_servo_turret_stack_B': ('SERVO_TURRET_B', 'SG90 180 in the cap, axis X=0, Y=42.5'),
 'ref_turret_head_B': ('TURRET_HEAD_B', 'printed v1 turret head + 2 HC-SR04P on the stack servo'),
 # DECIDED two-island power chain (engineering/POWER_SYSTEM.md, board deviation 8), hull front floor bay, lid off
 'ref_conv_a_B': ('M_SERVO_BOOST', 'Pololu U3V70F5 #1 (island A) on edge in conv_holder_a (GIẢ ĐỊNH 40.6 x 15.2 x 4.6); VIN end -Y_v1 = +X contract right side, VOUT -> J_PWR 18 AWG'),
 'ref_conv_b_B': ('M_SERVO_BOOST_B', 'Pololu U3V70F5 #2 (island B) on edge in conv_holder_b; VOUT -> F_ISLAND_B -> CH3-5 red wires; ENABLE <- ACT_EN tap, 4.7 k to GND'),
 'ref_fuse_pack_B': ('FH_PACK', 'F_PACK 0287015.U in 0FHA0002XP inline holder (GIẢ ĐỊNH 39 x 22 x 12) on edge in fuse_holder_pack, in front of the cells'),
 'ref_protector_B': ('M_PROTECT', 'PCB-Li-1S15A (GIẢ ĐỊNH <= 45 x 20 x 4.5 with pads) standing in protector_holder against the cell ends, under the bridge plate'),
 'ref_fuse_b_B': ('F_ISLAND_B', '5 A ATOF fuse 0287005.U in an inline holder (GIẢ ĐỊNH 32 x 14 x 10) in fuse_clip_b on the right 45 deg side wall'),
 # lead integration review 3: battery-fed DevKit logic 5 V (portable mode)
 'ref_logic_B': ('M_LOGIC', 'Pololu U3V16F5 (GIẢ ĐỊNH 13.2 x 8.1 x 2.5) flat in logic_holder on the hull floor left of the front window; '
                 'VIN/GND end toward the tail (+Y) <- third branch of the XT60 RUN Y harness (22 AWG); VOUT/GND end toward the nose -> '
                 'USB power-only lead into the DevKit USB port (swap with the host data cable, never both)'),
}
out['layoutB'] = {'note': 'Option (b), release note 9: lid off, v5 stack standing on stack_bridge over the cells. '
                          'BUILDABLE layout. Positions ON THE CAR (parts.json draws this group shifted +130 mm in X). Order: bridge, carrier deck (carrier), tier 1 PCA9685, tier 2 ESP32, cap. '
                          'Extra tiers add 26 mm each in Z. Power chain (pack protector, F_PACK, 2 x U3V70F5, F_ISLAND_B, XT60 RUN plug, M_LOGIC U3V16F5 for the DevKit) in the hull front bay; '
                          'M_CHARGE (Adafruit 6091) stays off the car on the bench: unplug RUN, mate the pack XT60 with the charger lead (case/DEVIATIONS.md 9).',
                  'modules': []}
for n, (mid, note) in B.items():
    if n not in parts:
        continue
    b = list(parts[n]['bboxMm']); b[0] -= 130.0; b[3] -= 130.0
    out['layoutB']['modules'].append({'id': mid, 'part': n, 'positionMm': [round(v, 2) for v in b[:3]],
                                      'sizeMm': [round(b[i + 3] - b[i], 2) for i in range(3)], 'interface': note})
out['layoutA_note'] = ('modules[] above are option (a): lid on, devices on glue-on holders inside the hull (release note 8). '
                      'NOT buildable with the board carrier (DEVIATIONS 8); kept as the record of the printed-hull fit.')
(ROOT / 'case/modules.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(len(out['modules']), 'modules')
