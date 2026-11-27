"""Write case/interfaces.json (contract frame) from points authored in the robot-tank v1 frame.

    python3 tools/case/make_interfaces.py

v1 -> contract: (x, y, z) -> (-y, -x, z). Joints are the printed v1 mechanisms (frozen);
travel ranges were measured on the exported parts (front arms are stopped by the v1 LED
bracket at about -12 deg wheel-up). Wires use the openings the printed chassis/lid/hull have.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def c(p):
    x, y, z = p
    return [round(-y, 2), round(-x, 2), round(z, 2)]


def route(name, pts):
    return {'name': name, 'pointsMm': [c(p) for p in pts]}


AXLE = {'front': 52.0, 'mid': 0.0, 'rear': -52.0}
PIVOT_X = {'front': 35.4, 'mid': -16.6, 'rear': -68.6}
PIVOT_Z = 28.0
SIDE = {'left': 1, 'right': -1}

joints = []
for pos in ('front', 'mid', 'rear'):
    for side, sy in SIDE.items():
        n = f'{pos}_{side}'
        clear = ['chassis', 'hull'] + [f'wheel_{p}_{side}' for p in ('front', 'mid', 'rear') if p != pos]
        if pos == 'front':
            clear += ['led_bracket', 'ref_led_bar']
        joints.append({
            'name': f'suspension_{n}', 'originMm': c((PIVOT_X[pos], 0.0, PIVOT_Z)), 'axis': [1, 0, 0],
            'rangeDeg': [-10, 25] if pos == 'front' else [-14, 25],
            'moves': [f'arm_{n}', f'wheel_{n}', f'ref_servo_{n}'], 'clearOf': clear,
            'minClearanceMm': 0.25,
            'note': 'v1 printed lever arm on an M3 pivot (lug gap 0.4 mm by design). Negative = wheel up. '
                    'Up-travel measured clear to -10 deg (front, LED bracket) / -14 deg (mid, rear); '
                    'down-travel is held by the rubber band, 25 deg sampled. Not a new part.'})
joints.append({'name': 'turret', 'originMm': [0, 0, 73.0], 'axis': [0, 0, 1], 'rangeDeg': [-90, 90],
               'moves': ['turret_head', 'ref_horn_turret', 'ref_sonar_front', 'ref_sonar_rear'],
               'clearOf': ['lid', 'fan_plate', 'ref_fan_3010', 'ref_servo_turret'],
               'allowContact': [['ref_horn_turret', 'ref_servo_turret']], 'minClearanceMm': 0.25,
               'note': 'SG90 180 deg sweep of the v1 turret head (head gap 0.3 mm over the servo by v1 design).'})

# ---- wires ------------------------------------------------------------------------------------
SLOT_R = (0.0, -8.3)          # right mid-station wire slot (chassis cut 8 x 5), left one is under tray A
STRIP_X = 39.9                # front window strip x 38..41.8 left open behind the PCA9685
CORR_Z = 34.0                 # under-chassis centre lane (servo inner faces at |y| 5.3, below z 40)
# Layout A wire set withdrawn at integration: the board's 62x60 carrier (servo power switch, Echo shifters)
# cannot fit in layout A together with the modules (case/DEVIATIONS.md 8). All wiring is layout B below.

# ---- layout B (note 9): stack on the car, lid off. Drawn beside the car at contract X +130. ----------
BX = 130.0                                   # display shift in contract X
CXS = -42.5                                  # stack centre (v1 x)
joints.append({'name': 'turret_on_stack (layout B)', 'originMm': [BX + 0.0, 42.5, 183.5], 'axis': [0, 0, 1], 'rangeDeg': [-90, 90],
               'moves': ['ref_turret_head_B', 'ref_horn_turret_stack_B', 'ref_sonar_front_B', 'ref_sonar_rear_B'],
               'clearOf': ['stack_turret_mount', 'stack_tier_2', 'ref_servo_turret_stack_B', 'ref_screen_stack_B'],
               'allowContact': [['ref_horn_turret_stack_B', 'ref_servo_turret_stack_B']], 'minClearanceMm': 0.25,
               'note': 'option (b): the printed v1 turret head on the SG90 in the v5 stack_turret_mount (on the carrier deck)'})


DZ = 2.5   # deck plate 6.5 (was 4.0): every stack height above the deck moved up 2.5 mm


def croute(name, pts):
    return {'name': name, 'pointsMm': [[round(p[0], 2), round(p[1], 2), round(p[2] + (DZ if p[2] >= 75.0 else 0.0), 2)] for p in pts]}


# Layout B (lead integration review): every lead ends at the board team's 62x60 carrier on the deck.
# Carrier corner at contract (-31, 12.5), underside Z 77.9, board top 79.5; plug tops ~Z 90.5 (DZ applied in croute).
BOARD = (-31.0, 12.5, 77.0)


def pad(bx, by, z=90.0):
    return (BOARD[0] + bx, BOARD[1] + by, z)


SERVO_HDR = {('front', 'left'): (4, 3, 'J_S0'), ('mid', 'left'): (4, 14, 'J_S1'), ('rear', 'left'): (4, 37, 'J_S2'),
             ('front', 'right'): (58, 3, 'J_S3'), ('mid', 'right'): (58, 14, 'J_S4'), ('rear', 'right'): (58, 32, 'J_S5')}
bwires = []
for pos in ('front', 'mid', 'rear'):
    for side, sy in SIDE.items():
        X = AXLE[pos]
        lane = [tuple(c(p)) for p in [(X - 6.0, sy * 2.8, 21.0), (X - 6.0, 0.0, CORR_Z)]]
        bx, by, ref = SERVO_HDR[(pos, side)]
        hx, hy, hz = pad(bx, by)
        sx = 1.0 if hx > 0 else -1.0
        tail = [(sx * 42.0, 15.0, 75.0), (sx * 42.0, hy, hz), (hx, hy, hz)]
        bwires.append({'name': f'servo {pos} {side} -> carrier {ref}', 'clearDiameterMm': 3.6,
                       'note': 'flat lead; plug threaded edge-on through the 8x5 slot / 3.8 mm strip, then up the open hull',
                       'routes': [croute('right mid slot, up the open hull', lane + [(8.3, 0.0, CORR_Z), (8.3, 0.0, 47.0), (8.3, 0.0, 65.5), (sx * 36.0, 2.0, 65.5)] + tail),
                                  croute('front window strip, up the open hull', lane + [(0.0, -39.9, CORR_Z), (0.0, -39.9, 72.0), (sx * 20.0, -10.0, 74.0)] + tail)]})
# risers kept straight up to clear the layout-B power holders in the front floor bay (case/power_b.py)
hx, hy, hz = pad(52, 3)
bwires.append({'name': 'turret SG90 -> carrier J_S6', 'clearDiameterMm': 3.6, 'note': 'slack loop for the yaw range',
               'routes': [croute('right side, outside the tiers', [(hx, hy, hz), (42.0, 15.0, 95.0), (42.0, 30.0, 160.0), (25.0, 40.0, 160.0)]),
                          croute('front, then right side', [(hx, hy, hz), (28.0, 2.0, 95.0), (28.0, 2.0, 125.0), (30.0, 2.0, 140.0), (30.0, 40.0, 160.0), (25.0, 40.0, 160.0)])]})
s_end = (-17.0, 29.0, 92.5)   # 95.0 after DZ: under the fan (bottom Z 99.5)
bwires.append({'name': 'sonars F/R -> carrier J_SONAR_F/R', 'clearDiameterMm': 4.0, 'note': '2 x 4-wire, slack loop for the yaw range',
               'routes': [croute('left side of the stack', [(-30.0, 42.5, 186.0), (-34.0, 29.0, 160.0), (-34.0, 29.0, 100.0), s_end]),
                          croute('right side, over the carrier front (clear of the fan)', [(30.0, 42.5, 186.0), (34.0, 29.0, 160.0), (34.0, 22.0, 97.0), (-20.0, 22.0, 94.5), s_end])]})
bwires.append({'name': 'carrier J_CTRL -> ESP32 DevKit (tier 3)', 'clearDiameterMm': 3.6, 'note': 'GPIO per engineering/esp32-pinmap.json',
               'routes': [croute('front of the stack, inside the posts', [(-14.6, 16.5, 92.0), (-8.0, 16.0, 95.0), (-8.0, 3.0, 100.0), (-8.0, 3.0, 130.0), (-8.0, 22.0, 130.0)]),
                          croute('left of the stack', [(-14.6, 16.5, 92.0), (-27.0, 16.5, 95.0), (-27.0, 3.0, 100.0), (-27.0, 3.0, 130.0), (-27.0, 25.0, 130.0), (-9.0, 25.0, 130.0)])]})
bwires.append({'name': 'carrier J_PCA -> PCA9685 (tier 2)', 'clearDiameterMm': 3.6,
               'routes': [croute('front, centre', [(5.0, 16.5, 92.0), (5.0, 3.0, 100.0), (5.0, 3.0, 118.0), (5.0, 9.0, 118.0)]),
                          croute('front, right of centre', [(5.0, 16.5, 92.0), (9.0, 3.0, 100.0), (9.0, 3.0, 118.0), (7.0, 9.0, 118.0)])]})
pw = pad(12.5, 47.5, 96.0)   # above the J_PWR terminal (carrier STEP tops out at Z 93.0)
# fan zip-tied under tier 1 (contract X -15..15, Y 27.5..57.5, Z 99.5..109.5) -> carrier J_FAN (board 45.5,52)
fan_pad = pad(45.5, 52.0, 93.0)   # Z 95.5: just above the J_FAN terminal (carrier STEP reaches Z 93.3 there)
bwires.append({'name': 'fan 5 V -> carrier J_FAN', 'clearDiameterMm': 3.0, 'note': '2 x 26 AWG fan lead, ~60 mm',
               'routes': [croute('straight down behind the fan', [(14.0, 59.5, 99.5), (14.5, 64.5, 94.0), fan_pad]),
                          croute('round the left of the fan', [(-14.0, 59.5, 99.5), (-5.0, 66.0, 95.0), (14.5, 66.0, 94.0), fan_pad])]})
bwires.append({'name': 'ESP32 USB host cable (tier 3, front end)', 'clearDiameterMm': 4.0,
               'routes': [croute('out to the left under the screen face', [(0.0, 15.0, 143.7), (0.0, 2.0, 143.7), (-40.0, 2.0, 143.7)]),
                          croute('out to the right under the screen face', [(0.0, 15.0, 143.7), (0.0, 2.0, 143.7), (40.0, 2.0, 143.7)])]})
bwires.append({'name': 'ESP32 (tier 3) -> screen on the stack face', 'clearDiameterMm': 3.6,
               'routes': [croute('left pin row', [(-9.0, 22.0, 130.0), (-9.0, 4.0, 131.0), (-5.0, -3.0, 139.0)]),
                          croute('right pin row', [(9.0, 22.0, 130.0), (9.0, 4.0, 131.0), (5.0, -3.0, 139.0)])]})
# ---- DECIDED two-island power chain (engineering/POWER_SYSTEM.md, board deviation 8), v1 frame ----------
# holders: case/power_b.py. Pack side (>=14 AWG, <=0.4 m round trip, XT60-class >=15 A, no Dupont).
def vroute(name, pts):
    return route(name, pts)


JPWR_L = [(-55.0, 38.0, 82.5), (-60.0, 38.0, 100.5), (-60.0, 18.5, 100.5), (-60.0, 18.5, 98.5)]    # = old J_PWR tails
JPWR_R = [(-55.0, -38.0, 82.5), (-68.0, -38.0, 97.5), (-68.0, 18.5, 97.5), (-60.0, 18.5, 98.5)]
JCTRL = (-16.5, 14.6, 94.5)          # carrier J_CTRL (pin 6 = ACT_EN), contract (-14.6, 16.5, 94.5)
SPLICE = (-30.0, -36.0, 95.0)        # red-wire splice of the J_S3..J_S5 servo plugs, beside the carrier right edge
XT60 = (44.5, -20.0, 52.0)           # RUN plug parked on the floor, right front corner (lid off)
bwires += [
    {'name': 'cell bus + -> F_PACK holder (12 AWG, pack maker)', 'clearDiameterMm': 3.6,
     'note': 'unfused length about 35 mm here (POWER_SYSTEM.md asks <=25 mm: pack maker keeps it shorter) - GIẢ ĐỊNH',
     'routes': [vroute('round the left end of the protector, high', [(-12.4, 15.0, 52.0), (-12.4, 27.5, 50.0), (3.0, 27.5, 50.0), (11.9, 23.5, 55.0)]),
                vroute('round the left end of the protector, low', [(-12.4, 15.0, 52.0), (-12.4, 27.5, 46.0), (3.0, 27.5, 46.0), (11.9, 23.5, 50.0)])]},
    {'name': 'F_PACK holder -> protector B+ (12 AWG, pack maker)', 'clearDiameterMm': 3.6,
     'routes': [vroute('round the right end of the protector', [(11.9, -23.5, 55.0), (3.0, -27.5, 50.0), (-1.2, -16.0, 52.0)]),
                vroute('right end, low', [(11.9, -23.5, 50.0), (3.0, -27.5, 46.0), (-1.2, -16.0, 47.0)])]},
    {'name': 'protector P+/P- -> XT60 RUN plug (14 AWG pair)', 'clearDiameterMm': 6.2,
     'routes': [vroute('over the converters', [(1.5, 12.0, 57.0), (2.5, 12.0, 71.0), (40.0, -20.0, 71.0), XT60]),
                vroute('over the converters, nearer the nose', [(1.5, 12.0, 57.0), (2.5, 5.0, 71.0), (30.0, -5.0, 71.0), (44.0, -14.0, 66.0), XT60])]},
    {'name': 'XT60 -> U3V70F5 A and B VIN (14 AWG Y harness, inputs in parallel)', 'clearDiameterMm': 6.2,
     'routes': [vroute('along the floor at the input ends', [XT60, (38.5, -25.0, 50.0), (25.5, -25.0, 50.0)]),
                vroute('over the input ends', [XT60, (44.5, -20.0, 64.0), (25.5, -24.0, 64.0), (25.5, -24.0, 56.0)])]},
    {'name': 'U3V70F5 A VOUT -> carrier J_PWR (18 AWG pair, island A)', 'clearDiameterMm': 4.5,
     'routes': [vroute('left side', [(25.5, 23.5, 52.0), (25.5, 23.5, 66.0), (0.0, 36.0, 72.0)] + JPWR_L),
                vroute('right side, over the carrier', [(25.5, 23.5, 52.0), (25.5, 23.5, 66.0), (10.0, 0.0, 72.0), (0.0, -36.0, 72.0)] + JPWR_R)]},
    {'name': 'U3V70F5 B VOUT -> 5 A fuse F_ISLAND_B (18 AWG, island B)', 'clearDiameterMm': 4.5,
     'routes': [vroute('across the nose', [(33.3, 23.5, 52.0), (33.3, 23.5, 66.0), (37.5, -5.0, 70.0), (37.5, -33.0, 62.0)]),
                vroute('across the nose, high', [(33.3, 23.5, 52.0), (33.3, 23.5, 72.0), (38.0, -20.0, 72.0), (37.5, -33.0, 62.0)])]},
    {'name': 'F_ISLAND_B -> red-wire splice of servos CH3-5 (18 AWG)', 'clearDiameterMm': 4.5,
     'note': 'pull the V+ pin out of the J_S3..J_S5 plug housings, join the three red wires here; carrier V+ pins stay empty',
     'routes': [vroute('up the right side wall', [(0.5, -34.0, 62.0), (-2.0, -40.0, 70.0), (-15.0, -44.0, 80.0), SPLICE]),
                vroute('up the right side, inside', [(0.5, -34.0, 62.0), (-2.0, -36.0, 72.0), (-12.0, -38.0, 84.0), SPLICE])]},
    {'name': 'ACT_EN tap J_CTRL.6 -> U3V70F5 B ENABLE (4.7 k to GND at the converter)', 'clearDiameterMm': 3.0,
     'routes': [vroute('over the right converter', [JCTRL, (-16.0, 8.0, 97.5), (-3.0, 8.0, 102.5), (10.0, 8.0, 80.0), (40.0, -12.0, 72.0), (38.5, -23.5, 60.0), (33.3, -23.5, 57.0)]),
                vroute('down the left, then across', [JCTRL, (-16.0, 8.0, 97.5), (-3.0, 8.0, 102.5), (20.0, 30.0, 72.0), (38.5, -23.5, 62.0), (33.3, -23.5, 57.0)])]},
    {'name': 'charge: XT60 pack plug lifted out to the bench charger (M_CHARGE off the car, RUN unplugged)', 'clearDiameterMm': 16.0,
     'routes': [vroute('straight up, right front corner', [XT60, (44.5, -20.0, 95.0)]),
                vroute('up over the nose', [XT60, (44.5, -6.0, 62.0), (44.5, -6.0, 95.0)])]},
]
(ROOT / 'case' / 'layout_b.json').write_text(json.dumps(
    {'schema': 1, 'note': 'Layout B = the buildable layout (lead integration review): lid off, v5 stack on the carrier deck on stack_bridge. '
                          'Contract frame, ON THE CAR. Checked by tools/case/fit_checks.py against the car + stack moved back from X +130. '
                          'case/interfaces.json carries the same routes shifted +130 mm in X (where the stack is drawn).',
     'wires': bwires}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
# interfaces.json wires: the layout-B routes at the drawn position. Layout A wiring withdrawn (DEVIATIONS 8).
wires = [{**w, 'routes': [{'name': r['name'], 'pointsMm': [[p[0] + BX, p[1], p[2]] for p in r['pointsMm']]} for r in w['routes']]}
         for w in bwires]

COUPON = 'coupon_fit_TEST_ONLY'
fits = [{'name': n, 'testPart': COUPON, 'note': note} for n, note in [
    ('ESP32 DevKit on the post ledges (foam tape) and end stops', 'coupon piece 1: post top with stop'),
    ('PCA9685 holes over the 2.0 mm pegs', 'coupon piece 2: one peg post'),
    ('power module between the tray lips + zip ties', 'coupon piece 3: tray end with lips and slots'),
    ('30 x 30 fan screws through the 24 mm hole pattern', 'coupon piece 4: plate corner with two holes'),
    ('18650 cells in the cradle saddles', 'coupon piece 5: one saddle'),
    ('screen clip lip over the screen back edge', 'coupon piece 6: one clip'),
    ('holders glued to the chassis floor / lid / glacis with 502', 'every coupon piece keeps its real glue face'),
]] + [{'name': n, 'testPart': 'coupon_stack_TEST_ONLY', 'note': note} for n, note in [
    ('stack tier 1 on the stack_bridge pegs (4.4 peg / 5.0 socket)', 'bridge peg corner + tier post socket'),
    ('tier on tier (same peg/socket)', 'same pair'),
    ('PCA9685 on the tier M2.5 standoffs, ESP32 DevKit in the tier rails', 'tier slice with one standoff and a rail end'),
    ('stack_bridge legs glued to the chassis floor beside the cells', 'flat leg feet; glue with the tiers fitted as the jig'),
]] + [{'name': n, 'testPart': 'coupon_deck_TEST_ONLY', 'note': note} for n, note in [
    ('carrier deck sockets over the bridge pegs', 'deck corner with one 5.0 socket'),
    ('carrier 62x60 on the deck M3 posts (M3x8 self-tap through H1..H4)', 'one post with its 2.6 pilot'),
    ('PCA tier (stack_tier_1) on the deck column pegs', 'column head with its 4.4 peg'),
]] + [{'name': '30x30 fan zip-tied under stack_tier_1 through its 4 zip slots', 'testPart': 'coupon_stack_TEST_ONLY',
       'note': 'the tier slice in the coupon carries one real zip slot'}] + [
    {'name': n, 'testPart': 'coupon_power_TEST_ONLY', 'note': note} for n, note in [
        ('U3V70F5 on edge in conv_holder_a/b (5.0 slot for 4.6 GIẢ ĐỊNH, foam tape)', 'coupon piece 1: converter slot end'),
        ('0FHA0002XP fuse holder on edge in fuse_holder_pack (12.4 slot)', 'coupon piece 2: pack-fuse slot end'),
        ('PCB-Li-1S15A between the protector_holder lips, foam tape on the wall', 'coupon piece 3: wall end with one lip'),
        ('5 A inline fuse holder between the fuse_clip_b lips (14.4 between lips)', 'coupon piece 4: clip slice, glue face on the bed'),
        ('power holders glued with 502: floor holders on the hull floor, fuse_clip_b flat on the 45 deg right side wall',
         'every piece keeps its real glue face')]]

SKINS = [{'part': 'stack_turret_mount', 'centerMm': [130.0 + dy, -29.9, 134.2], 'radiusMm': 9.0,
          'reason': 'v5 design: the 45-degree face panel ends in a knife edge at its lower lip (imported unchanged)'}
         for dy in (-15.0, 0.0, 15.0)]
intent = {'schema': 1, 'frame': 'contract (X=-Y_v1, Y=-X_v1, Z=Z_v1)', 'printer': {'bedMm': [256, 256, 256], 'nozzleMm': 0.4},
          'joints': joints, 'wires': wires, 'fits': fits, 'skins': SKINS}
(ROOT / 'case' / 'interfaces.json').write_text(json.dumps(intent, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(len(joints), 'joints', len(wires), 'wires', len(fits), 'fits')
