"""Case build: robot-tank v1 (already printed, frozen) + glue-on holders for missing devices.

    "$KICAD_CASE_PYTHON" case/build.py            # rebuild only what changed
    "$KICAD_CASE_PYTHON" case/build.py --only fan_plate

Release note 8: the person printed robot-tank build v1 and adopted it as this project's case.
v1 parts are imported from case/ref/v1 (hash-checked copies of
/Users/macbookpro/cad-models/robot-tank/builds/v1) as printable:false references: never
reprinted, never edited. New parts are the glue-on holders in case/holders.py.
Everything is exported in the contract frame (v1frame.to_contract).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kicadpy.case_build import CaseBuild  # noqa: E402
import holders as H  # noqa: E402
import stack as S  # noqa: E402
import power_b as P  # noqa: E402
from v1frame import to_contract, v1, CELL_LIFT  # noqa: E402

build = CaseBuild(__file__, stl_tolerance=0.03, angular_tolerance=0.1, contract='PILOT_CONTRACT.json',
                  default_inputs=('PILOT_CONTRACT.json',),
                  manifest={'stage': 'simple', 'material': 'PETG', 'hardwareTested': False,
                            'frame': 'contract: +X right, +Y tail, +Z up, nose -Y, origin ground under turret axis; '
                                     'X=-Y_v1, Y=-X_v1, Z=Z_v1 (mirror map, see case/DEVIATIONS.md)',
                            'source': 'robot-tank cadsmith build v1 (printed by the person, 2026-11-25)',
                            'verification': {'nativePCBCheckerApplies': False,
                                             'report': '../reports/mechanical.json'},
                            'pilotContractSha256': 'a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810'})

# ---- v1 printed parts: keep using, do not reprint ---------------------------------------------
V1_PRINTED = ['chassis', 'hull', 'lid', 'turret_head', 'led_bracket'] + [
    f'{k}_{p}_{s}' for k in ('arm', 'wheel') for p in ('front', 'mid', 'rear') for s in ('left', 'right')]
# ---- bought parts placed in v1 (reference bodies) ----------------------------------------------
V1_BOUGHT = ['servo_turret', 'horn_turret', 'sonar_front', 'sonar_rear', 'led_bar'] + [
    f'{k}_{p}_{s}' for k in ('servo', 'horn') for p in ('front', 'mid', 'rear') for s in ('left', 'right')]


def ref_part(name, lift=0.0):
    def make():
        s = v1(name)
        return to_contract(s.translate((0, 0, lift)) if lift else s)
    make.__name__ = f'ref_{name}'
    return make


for n in V1_PRINTED:
    build.add(n, ref_part(n), inputs=[f'case/ref/v1/{n}.step'], role='shell' if n in ('chassis', 'hull') else 'other',
              printable=False, printed=True, group='v1',
              note='robot-tank v1, already printed by the person: keep using, do not reprint')
for n in V1_BOUGHT:
    build.add(f'ref_{n}', ref_part(n), inputs=[f'case/ref/v1/{n}.step'], printable=False, bought=True,
              group='bought', note='bought part as placed in v1 (reference body, DO NOT PRINT)')
for i in (1, 2):
    build.add(f'ref_cell_{i}', ref_part(f'cell_{i}', CELL_LIFT), inputs=[f'case/ref/v1/cell_{i}.step'],
              printable=False, bought=True, group='bought',
              note=f'18650 cell on the cradle, {CELL_LIFT} mm above its v1 position (GIẢ ĐỊNH 18.6 x 65.2)')

# ---- new glue-on holders (print these) -------------------------------------------------------
NEW = {
    'esp32_post_rear': (H.esp32_post_rear, 'ESP32 DevKit post, USB end; prints foot-down'),
    'esp32_post_front': (H.esp32_post_front, 'ESP32 DevKit post, antenna end (same design); prints foot-down'),
    'power_tray_a': (H.power_tray_a, '1S charge/boost module tray A; prints flat'),
    'power_tray_b': (H.power_tray_b, '1S charge/boost module tray B (same design, turned 90 deg); prints flat'),
    'cell_cradle': (H.cell_cradle, '2 x 18650 cradle with strap slots; prints flat'),
    'fan_plate': (H.fan_plate, '30 x 30 fan plate glued on the lid over the battery window; prints flat'),
    'screen_clip_left': (H.screen_clip_left, 'screen clip on the glacis inner face; prints glue face down'),
    'screen_clip_right': (H.screen_clip_right, 'screen clip, mirror copy (same design); prints glue face down'),
}
for n, fn in H.pca_posts().items():
    NEW[n] = (fn, 'PCA9685 peg post (4 identical); glue with the board on the pegs as the jig; prints peg up')
for n, (fn, note) in NEW.items():
    build.add(n, (lambda f=fn: to_contract(f())), inputs=['case/holders.py', 'case/v1frame.py'],
              role='bracket', glueOn=True, group='new', note=note + '; glue with 502 (CA)',
              printRotateDeg=[-45, 0, 0] if n.startswith('screen_clip') else [0, 0, 0])
build.add('coupon_fit_TEST_ONLY', lambda: to_contract(H.coupon()), inputs=['case/holders.py', 'case/v1frame.py'],
          role='coupon', group='test', note='TEST ONLY: slices of the ESP32 post, PCA post, power tray, fan holes and '
                                             'cell saddle; print first and try the real modules')

# ---- release note 9: v5 board stack, layout B (lid off), drawn beside the car ---------------------
S_IN = ['case/stack.py', 'case/v1frame.py']
build.add('stack_bridge_plate', lambda: to_contract(S.stack_bridge_plate()), inputs=S_IN, role='bracket', glueOn=True,
          group='stack', layout='B', printed=False,
          note='NEW: plate over the 2x18650 bay carrying the v5 tiers on its 4 pegs (stack_base does not fit in the hull); '
               'glued with 502 onto the 4 stack legs; prints flat, pegs up')
for k in S.LEG_KEYS:
    build.add(f'stack_leg_{k}', (lambda k=k: to_contract(S.stack_leg(k))), inputs=S_IN, role='bracket', glueOn=True,
              group='stack', layout='B', printed=False,
              note='NEW: stack leg (4 identical 10 x 6.5 x 20.4 blocks), glued with 502 to the chassis floor beside the '
                   'cells and under the bridge plate; glue with the plate and tier 1 fitted as the jig; prints on end')
for n in ('stack_tier_1', 'stack_tier_2', 'stack_turret_mount'):
    build.add(n, (lambda n=n: to_contract(S.v5_on_car_display(n))), inputs=S_IN + [f'case/ref/v5/{n}.step'],
              role='bracket', group='stack', layout='B', printed=False,
              printRotateDeg=[180, 0, 0] if n == 'stack_turret_mount' else [0, 0, 0],
              imported='v5', note='cadsmith v5 part imported unchanged (not printed yet); plugs onto the pegs below')
build.add('stack_base', lambda: to_contract(S.display(S.on_car_v5('stack_base').translate((0, -60.0, -S.ON_CAR[2])))),
          inputs=S_IN + ['case/ref/v5/stack_base.step'], printable=False, group='stack', layout='standalone',
          note='v5 stack_base (92x43, M3 82x20): only for a stand-alone stack; no matching holes and no room in the '
               'printed hull, replaced on the car by stack_bridge. DO NOT PRINT for the car')
build.add('coupon_stack_TEST_ONLY', lambda: to_contract(S.coupon_stack()), inputs=S_IN + ['case/ref/v5/stack_tier_1.step'],
          role='coupon', group='test', note='TEST ONLY: bridge peg corner + tier-1 post socket; print first')
build.add('stack_carrier_deck', lambda: to_contract(S.carrier_deck()), inputs=S_IN, role='bracket', group='stack',
          layout='B', printed=False,
          note='NEW (integration): deck tier for the board 62x60 carrier: sockets onto the bridge pegs, 4 M3 posts '
               '(M3x8 self-tap through H1..H4), 4 columns with v5 pegs carrying the PCA tier 40.6 mm higher so vertical '
               'servo plugs have >= 30 mm; prints plate-down, columns up')
build.add('coupon_deck_TEST_ONLY', lambda: to_contract(S.coupon_deck()), inputs=S_IN, role='coupon', group='test',
          note='TEST ONLY: deck socket over a bridge peg, carrier M3 post, column head with peg into a tier socket')
build.add('ref_fan_B', S.fan_b and (lambda: to_contract(S.fan_b())), inputs=S_IN, printable=False, bought=True,
          group='stack', layout='B', note='30x30 5 V fan (GIẢ ĐỊNH 10 mm thick) zip-tied under stack_tier_1 through its 4 zip slots, DO NOT PRINT')
build.add('ref_carrier_B', S.carrier_ref_contract, inputs=S_IN + ['case/ref/board/main-contract.step'],
          printable=False, bought=True, group='stack', layout='B',
          note='board team carrier 62x60 (build/board/main-contract.step, sha in case/ref/board/SHA256SUMS) on the deck, DO NOT PRINT')
for n in ('pca9685', 'esp32', 'screen_stack', 'servo_turret_stack', 'horn_turret_stack'):
    build.add(f'ref_{n}_B', (lambda n=n: to_contract(S.v5_on_car_display(n))), inputs=S_IN + [f'case/ref/v5/{n}.step'],
              printable=False, bought=True, group='stack', layout='B', note='v5 reference body on the stack, DO NOT PRINT')
for n in ('turret_head', 'sonar_front', 'sonar_rear'):
    build.add(f'ref_{n}_B', (lambda n=n: to_contract(S.turret_on_stack_display(n))), inputs=S_IN + [f'case/ref/v1/{n}.step'],
              printable=False, group='stack', layout='B',
              note='the printed v1 turret head / sonars moved onto the stack servo (same physical part), DO NOT PRINT')

# ---- lead integration review 2: DECIDED two-island power chain, layout B front floor bay -----------
P_IN = ['case/power_b.py', 'case/v1frame.py', 'case/stack.py']
P_NOTE = {'conv_holder_a': 'NEW: Pololu U3V70F5 #1 (island A -> carrier J_PWR) on edge between two walls, foam tape; glued to the hull floor; prints flat',
          'conv_holder_b': 'NEW: Pololu U3V70F5 #2 (island B -> 5 A fuse -> CH3-5 red wires), same design as A; prints flat',
          'fuse_holder_pack': 'NEW: F_PACK 0287015.U in its 0FHA0002XP inline holder, on edge, right in front of the cells; prints flat',
          'protector_holder': 'NEW: back wall + end lips for the PCB-Li-1S15A pack protector standing in front of the cell ends; prints flat',
          'fuse_clip_b': 'NEW: clip for the 5 A island-B inline fuse holder, glued flat on the 45 deg right side wall; prints glue face down'}
for n, fn in P.PARTS.items():
    build.add(n, (lambda f=fn: to_contract(S.display(f()))), inputs=P_IN, role='bracket', glueOn=True, group='power',
              layout='B', printed=False, note=P_NOTE[n] + '; glue with 502 (CA)',
              printRotateDeg=[0, 45, 0] if n == 'fuse_clip_b' else [0, 0, 0])
for n, fn in P.REFS.items():
    build.add(n, (lambda f=fn: to_contract(S.display(f()))), inputs=P_IN, printable=False, bought=True, group='power',
              layout='B', note='power-chain device envelope GIẢ ĐỊNH (engineering/POWER_SYSTEM.md DECIDED), DO NOT PRINT')
build.add('coupon_power_TEST_ONLY', lambda: to_contract(P.coupon_power()), inputs=P_IN, role='coupon', group='test',
          note='TEST ONLY: converter slot, pack-fuse slot, protector wall end and the 45 deg fuse clip; try the real parts first')

# ---- lead integration review 3: battery-fed DevKit logic branch (M_LOGIC U3V16F5), layout B -------
import logic_b as L  # noqa: E402
L_IN = ['case/logic_b.py', 'case/v1frame.py', 'case/stack.py']
build.add('logic_holder', lambda: to_contract(S.display(L.logic_holder())), inputs=L_IN, role='bracket', glueOn=True,
          group='power', layout='B', printed=False,
          note='NEW: flat tray for the M_LOGIC U3V16F5 (DevKit 5 V on battery), foam tape, ends open for the leads; '
               'glued with 502 to the hull floor left of the front window; prints flat')
build.add('ref_logic_B', lambda: to_contract(S.display(L.logic_ref())), inputs=L_IN, printable=False, bought=True,
          group='power', layout='B', note='U3V16F5 envelope 13.2 x 8.1 x 2.5 GIẢ ĐỊNH, DO NOT PRINT')
build.add('coupon_logic_TEST_ONLY', lambda: to_contract(L.coupon_logic()), inputs=L_IN, role='coupon', group='test',
          note='TEST ONLY: the logic holder itself; try the real U3V16F5 first')

# ---- device envelopes (GIẢ ĐỊNH, never printed) -------------------------------------------------
DEV = {
    'ref_esp32_devkit': H.esp32_ref,
    'ref_pca9685': H.pca_ref,
    'ref_power_module_a': lambda: H.power_ref(*H.TRAY_A),
    'ref_power_module_b': lambda: H.power_ref(*H.TRAY_B, turned=True),
    'ref_fan_3010': H.fan_ref,
    'ref_screen_module': H.screen_ref,
}
for n, fn in DEV.items():
    build.add(n, (lambda f=fn: to_contract(f())), inputs=['case/holders.py', 'case/v1frame.py'],
              printable=False, bought=True, group='device', note='device envelope GIẢ ĐỊNH, DO NOT PRINT')

if __name__ == '__main__':
    build.main()
