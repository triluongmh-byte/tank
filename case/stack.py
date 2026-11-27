"""Release note 9: the cadsmith v5 board stack on the printed v1 car (layout B: lid off).

v1 frame (x nose, y left, z up). The v5 stack_base (92 x 43, M3 82 x 20) cannot stand in the hull:
92 mm does not fit between the cells (x -14.4) and the glacis, and tier posts placed in front of the
cells would hit the glacis at hull height. So the tiers stand on `stack_bridge`, a glue-on table
over the 2 x 18650 bay: 4 legs glued to the chassis floor beside the cells, a plate with the same
4 pegs as stack_base. Layout B is drawn beside the car (DISPLAY offset) so it does not overlap
layout A (lid on, in-hull holders); tools/case/fit_checks.py checks it on the car (ON_CAR pose).
"""
import cadquery as cq
from v1frame import FLOOR_Z, REF, box, cyl_z, v1

F = FLOOR_Z
CX = -42.5                      # stack centre over the cell bay
PL_Z0, PL_T = 63.4, 3.0         # plate 0.6 mm above the cells on the cradle (top 62.8)
TIER_Z = PL_Z0 + PL_T           # tier 1 bottom
POST = (32.5, 17.0)             # v5 stack_post
PEG_D, PEG_H = 4.4, 3.0         # v5 peg into the 5.0 tier socket
WIN = (46.0, 26.0)              # v5 tier window
V5_TIER1_Z = 3.0                # tier 1 bottom in the v5 file
# ---- integration (lead review): carrier deck between the bridge and the PCA tier ------------------
DECK_Z0, DECK_T = TIER_Z, 6.5   # deck plate (socket 3.4 + 45-deg roof 2.5 inside it) sits on the bridge pegs (sockets 5.0 x 3.4 in its underside)
CARRIER_Z = DECK_Z0 + DECK_T + 5.0          # carrier underside on 5 mm M3 posts (tails <= 1.9 mm)
CARRIER_TOP = CARRIER_Z + 1.6
T2_Z = CARRIER_TOP + 30.0                   # >= 30 mm over the board top for vertical servo plugs + bend
CARRIER_HOLES = ((-38.5, 28.0), (-38.5, -28.0), (-64.5, 28.0), (-64.5, -28.0))   # v1 frame (board H1..H4)
COL_X = (30.2, 35.0)            # deck columns along x from CX (carrier spans CX +-30, 0.2 mm gap)
COL_Y = (13.0, 21.0)
ON_BRIDGE = (CX, 112.0, TIER_Z - V5_TIER1_Z)        # pose the coupon slice was cut at (unchanged)
ON_CAR = (CX, 112.0, T2_Z - V5_TIER1_Z)             # v5 stack file -> on the car, above the deck
V5_SERVO_TOP, V1_SERVO_TOP = 77.0, 87.0                # turret SG90 top face in v5 stack file / v1 lid
TURRET_ON_STACK = (CX, 0.0, V5_SERVO_TOP + ON_CAR[2] - V1_SERVO_TOP)  # v1 turret head + sonars -> stack servo
DISPLAY = (0.0, -130.0, 0.0)    # layout B drawn beside the car (v1 y -130 = contract X +130)
LEGS_X = ((-78.5, -68.5), (-28.0, -18.0))
LEGS_Y = (23.0, 29.5)


def stack_bridge_on_car():
    """Plate + legs as assembled (used for checks and the coupon)."""
    p = bridge_plate_on_car()
    for key in LEG_KEYS:
        p = p.union(bridge_leg_on_car(key))
    return p


def bridge_plate_on_car():
    """Flat plate over the cell bay with the 4 v5 pegs on top; prints flat, pegs up."""
    p = box(CX - 37.0, CX + 37.0, -29.5, 29.5, PL_Z0, TIER_Z)
    p = p.cut(box(CX - WIN[0] / 2, CX + WIN[0] / 2, -WIN[1] / 2, WIN[1] / 2, PL_Z0 - 1, TIER_Z + 1))
    for sx in (1, -1):
        for sy in (1, -1):
            p = p.union(cyl_z(PEG_D / 2, TIER_Z, TIER_Z + PEG_H, CX + sx * POST[0], sy * POST[1]))
    return p


LEG_KEYS = {'rear_left': (0, 1), 'rear_right': (0, -1), 'front_left': (1, 1), 'front_right': (1, -1)}


def bridge_leg_on_car(key):
    """One of 4 identical legs: glued to the chassis floor and under the plate (502)."""
    i, sy = LEG_KEYS[key]
    x0, x1 = LEGS_X[i]
    y0, y1 = sorted((sy * LEGS_Y[0], sy * LEGS_Y[1]))
    return box(x0, x1, y0, y1, F, PL_Z0)


def on_car_v5(name):
    return v1_like(name).translate(ON_CAR)


def carrier_deck_on_car():
    """Deck tier for the board's 62 x 60 carrier: plate on the bridge pegs, 4 M3 posts at the carrier
    holes, 4 columns beside the carrier carrying the v5 pegs for the PCA tier 40.6 mm higher.
    Prints plate-down, columns up, no overhang."""
    z0, z1 = DECK_Z0, DECK_Z0 + DECK_T
    p = box(CX - 37.0, CX + 37.0, -32.0, 32.0, z0, z1)
    p = p.cut(box(CX - 20.0, CX + 20.0, -13.0, 13.0, z0 - 1, z1 + 1))          # wire window
    for sx in (1, -1):
        for sy in (1, -1):
            x0, x1 = sorted((CX + sx * COL_X[0], CX + sx * COL_X[1]))
            y0, y1 = sorted((sy * COL_Y[0], sy * COL_Y[1]))
            p = p.union(box(x0, x1, y0, y1, z1 - 0.01, T2_Z))
            px, py = CX + sx * POST[0], sy * POST[1]
            p = p.union(cyl_z(PEG_D / 2, T2_Z - 0.01, T2_Z + PEG_H, px, py))
            p = p.cut(cyl_z(2.5, z0 - 1, z0 + PEG_H + 0.4, px, py))                # socket for the bridge peg
            p = p.cut(cq.Workplane('XY').circle(2.5).workplane(offset=2.5).circle(0.05).loft()
                      .translate((px, py, z0 + PEG_H + 0.4)))                         # 45-deg roof: prints without a ceiling
    for x, y in CARRIER_HOLES:
        p = p.union(cyl_z(3.0, z1 - 0.01, CARRIER_Z, x, y))
        p = p.cut(cyl_z(1.3, z0 + 1.0, CARRIER_Z + 0.1, x, y))                     # M3 self-tap pilot
    return p


FAN_T = 10.0                    # GIẢ ĐỊNH 30 x 30 x 10 fan


def fan_b_on_car():
    """30x30 fan zip-tied under the PCA tier plate through its 4 zip slots, blowing down on the carrier."""
    return box(CX - 15.0, CX + 15.0, -15.0, 15.0, T2_Z - FAN_T, T2_Z - 0.01)


def fan_b():
    return display(fan_b_on_car())


def carrier_deck():
    return display(carrier_deck_on_car())


def coupon_deck():
    """TEST ONLY: deck corner with one bridge-peg socket, one column + peg and one carrier post."""
    c = carrier_deck_on_car().intersect(box(-79.5, -58.0, 10.0, 32.0, DECK_Z0, T2_Z + PEG_H + 1))
    bb = c.val().BoundingBox()
    lo = c.intersect(box(-80, 0, -40, 40, DECK_Z0 - 1, CARRIER_Z + 2))          # plate + post + column foot
    top = c.intersect(box(-80, 0, -40, 40, T2_Z - 6.0, T2_Z + PEG_H + 1))       # column head + peg
    tb = top.val().BoundingBox()
    out = lo.translate((-bb.xmin - 160.0, 130.0 - bb.ymin, -DECK_Z0))
    return out.union(top.translate((-tb.xmin - 160.0 + bb.xlen + 4.0, 130.0 - tb.ymin, -tb.zmin)))


def carrier_ref_contract():
    """Board's populated carrier STEP (contract frame, origin board corner) on the deck, layout B, displayed."""
    s = cq.importers.importStep(str(REF.parent / 'board' / 'main-contract.step'))
    return s.translate((-31.0 - DISPLAY[1], 12.5, CARRIER_Z))


def v1_like(name):
    return cq.importers.importStep(str(REF.parent / 'v5' / f'{name}.step'))


def display(shape):
    return shape.translate(DISPLAY)


def stack_bridge_plate():
    return display(bridge_plate_on_car())


def stack_leg(key):
    return display(bridge_leg_on_car(key))


def v5_on_car_display(name):
    return display(on_car_v5(name))


def turret_on_stack_display(name):
    return display(v1(name).translate(TURRET_ON_STACK))


def coupon_stack():
    """TEST ONLY: one bridge peg corner and the matching tier-1 post socket, side by side."""
    a = bridge_plate_on_car().intersect(box(CX + 24.0, CX + 37.0, 10.0, 29.5, PL_Z0, TIER_Z + PEG_H + 1))
    t = v1_like('stack_tier_1').translate(ON_BRIDGE).intersect(box(CX + 14.0, CX + 37.0, 5.0, 21.5, TIER_Z, TIER_Z + 9.0))
    out, x = None, 0.0
    for p in (a, t):
        bb = p.val().BoundingBox()
        q = p.translate((x - bb.xmin - 40.0, 100.0 - bb.ymin, -bb.zmin))
        out = q if out is None else out.union(q)
        x += bb.xlen + 4.0
    return out
