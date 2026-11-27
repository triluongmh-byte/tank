"""Lead integration review: layout-B holders for the board's DECIDED two-island power chain.

engineering/POWER_SYSTEM.md "Release note 8 - DECIDED" (board deviation 8):
  protected 1S pack (cells + F_PACK 0287015.U in FH_PACK 0FHA0002XP + PCB-Li-1S15A) -> XT60 RUN plug
  -> U3V70F5 #1 (island A) -> carrier J_PWR      and      -> U3V70F5 #2 (island B) -> 5 A fuse
  -> red wires of the CH3-5 servo plugs; island-B ENABLE <- ACT_EN tap (4.7 k to GND on the converter).
The layout-A charge/boost trays (power_tray_a/b) are not used in layout B; these holders take the
front floor bay of the open hull instead (lid off). v1 frame (x nose, y left, z up), authored on the
car, exported drawn beside the car like the rest of layout B (stack.DISPLAY).

Free space measured on the printed v1 (build/case/probe_*.py): floor z 43, inner side wall
y = +-32.25 up to z 49 then 45 deg outward (y = +-(z - 16.75)) to z 64, glacis x = 123 - z,
floor openings: mid slots x -4..4 / |y| 8..10, front window x 38..60 / |y| < 12,
hull nut bosses x 16.8..23.2 / |y| 25.3..30.8. Servo-lead risers stay open: (0, -8.3) and (39.9, 0).
All device sizes are GIẢ ĐỊNH until the real parts are measured (coupon_power_TEST_ONLY).
"""
import math
import cadquery as cq
from v1frame import FLOOR_Z, box

F = FLOOR_Z
BASE = 1.5                      # holder floor plate
WALL = 1.2
LIP_H = 6.0                     # side-wall height above the base
CLR = 0.2                       # per side around a device

# ---- device envelopes (GIẢ ĐỊNH) -------------------------------------------------------------
CONV = (4.6, 40.6, 15.2)        # Pololu U3V70F5 on edge: thickness (x), length (y), height (z)
FH = (12.0, 39.0, 22.0)         # Littelfuse 0FHA0002XP ATO inline holder with F_PACK, on edge
PROT = (4.5, 45.0, 20.0)        # PCB-Li-1S15A protector (with its pads), standing against the cells
FB = (32.0, 14.0, 10.0)         # inline ATO holder for F_ISLAND_B 0287005.U: length (x), width, thickness

# ---- positions (v1 x of each holder's low-x face) ----------------------------------------------
FH_X0 = 4.5                     # pack fuse right in front of the cell bus (x -14.4)
CONV_A_X0 = 21.8                # island A
CONV_B_X0 = 29.6                # island B (ends 37.0: riser at x 39.9 - 1.8 stays clear)
PROT_WALL = (-10.4, -7.6)       # protector back wall; 4 mm gap to the cell ends for the bus lead
FB_X0 = 1.5                     # island-B fuse clip on the right side wall (v1 y < 0)


def _edge_holder(x0, dev, half_len_extra=1.0):
    """Floor tray for a flat module standing on edge: base + two side walls, ends open for the leads."""
    t, ln, _ = dev
    w = t + 2 * CLR + 2 * WALL
    y = ln / 2 + half_len_extra
    p = box(x0, x0 + w, -y, y, F, F + BASE)
    for xa in (x0, x0 + w - WALL):
        p = p.union(box(xa, xa + WALL, -(ln / 2 - 0.1), ln / 2 - 0.1, F + BASE - 0.01, F + BASE + LIP_H))
    return p


def _edge_ref(x0, dev):
    t, ln, h = dev
    xa = x0 + WALL + CLR
    return box(xa, xa + t, -ln / 2, ln / 2, F + BASE, F + BASE + h)


def conv_holder_a():
    return _edge_holder(CONV_A_X0, CONV)


def conv_holder_b():
    return _edge_holder(CONV_B_X0, CONV)


def fuse_holder_pack():
    return _edge_holder(FH_X0, FH)


def conv_a_ref():
    return _edge_ref(CONV_A_X0, CONV)


def conv_b_ref():
    return _edge_ref(CONV_B_X0, CONV)


def fuse_pack_ref():
    return _edge_ref(FH_X0, FH)


def protector_holder():
    """Back wall standing in front of the cell ends + two end lips; the PCB stands on the floor
    between the lips (foam tape on the wall). Top stays under the stack_bridge plate (z 63.4)."""
    w0, w1 = PROT_WALL
    y = PROT[1] / 2 + CLR
    p = box(w0, w1, -(y + WALL), y + WALL, F, 62.5)
    for s in (1, -1):
        y0, y1 = sorted((s * y, s * (y + WALL)))
        p = p.union(box(w1 - 0.01, w1 + PROT[0] + CLR, y0, y1, F, F + 8.0))
    return p


def protector_ref():
    w1 = PROT_WALL[1]
    return box(w1 + 0.05, w1 + 0.05 + PROT[0], -PROT[1] / 2, PROT[1] / 2, F + 0.02, F + PROT[2])


# ---- island-B fuse clip on the 45-degree right side wall ---------------------------------------
W0 = (-33.25, 50.0)             # point on the inner wall face (y, z)
U0 = 1.0                        # clip starts 1 mm up the slope (z 50.7)
CLIP_U = FB[1] + 2 * CLR + 2 * WALL + 0.6     # 17.0 along the slope
S2 = math.sqrt(0.5)


def _on_slope(shape):
    """Local frame (x, u up-slope, -v into the wall) -> v1 right wall: u -> (0,-1,1)/sqrt2, v -> (0,1,1)/sqrt2."""
    return shape.rotate((0, 0, 0), (1, 0, 0), 135.0).translate((0, W0[0], W0[1]))


def _lbox(x0, x1, u0, u1, v0, v1):
    return box(x0, x1, u0, u1, -v1, -v0)


def fuse_clip_b():
    """Glue face (v = 0) flat on the sloped wall; lower lip carries the holder, upper lip keeps it."""
    x0, x1 = FB_X0, FB_X0 + FB[0] + 2.4
    p = _lbox(x0, x1, U0, U0 + CLIP_U, 0.05, BASE)
    for ua in (U0, U0 + CLIP_U - WALL):
        p = p.union(_lbox(x0, x1, ua, ua + WALL, BASE - 0.01, BASE + LIP_H))
    return _on_slope(p)


def fuse_b_ref():
    x0 = FB_X0 + 1.2
    ua = U0 + WALL + CLR + 0.3
    return _on_slope(_lbox(x0, x0 + FB[0], ua, ua + FB[1], BASE + 0.05, BASE + 0.05 + FB[2]))


PARTS = {'conv_holder_a': conv_holder_a, 'conv_holder_b': conv_holder_b, 'fuse_holder_pack': fuse_holder_pack,
         'protector_holder': protector_holder, 'fuse_clip_b': fuse_clip_b}
REFS = {'ref_conv_a_B': conv_a_ref, 'ref_conv_b_B': conv_b_ref, 'ref_fuse_pack_B': fuse_pack_ref,
        'ref_protector_B': protector_ref, 'ref_fuse_b_B': fuse_b_ref}
SEATS = {'ref_conv_a_B': ['conv_holder_a'], 'ref_conv_b_B': ['conv_holder_b'], 'ref_fuse_pack_B': ['fuse_holder_pack'],
         'ref_protector_B': ['protector_holder', 'chassis'], 'ref_fuse_b_B': ['fuse_clip_b']}
GLUED = {'conv_holder_a': 'chassis', 'conv_holder_b': 'chassis', 'fuse_holder_pack': 'chassis',
         'protector_holder': 'chassis', 'fuse_clip_b': 'hull'}


def coupon_power():
    """TEST ONLY: one end of each new holder with its real slot/lips and glue face, laid in a row."""
    pieces = [
        conv_holder_a().intersect(box(CONV_A_X0 - 1, CONV_A_X0 + 10, 12.0, 25.0, F - 1, F + 10)),
        fuse_holder_pack().intersect(box(FH_X0 - 1, FH_X0 + 20, 12.0, 25.0, F - 1, F + 10)),
        protector_holder().intersect(box(-11.0, 0.0, 14.0, 30.0, F - 1, F + 12.0)),
        fuse_clip_b().intersect(box(FB_X0 - 1, FB_X0 + 8, -60, 0, 0, 100)),
    ]
    out, x = None, 0.0
    for i, p in enumerate(pieces):
        if i == 3:      # lay the clip slice with its glue face on the bed
            p = p.rotate((0, 0, 0), (1, 0, 0), 45.0)
        bb = p.val().BoundingBox()
        q = p.translate((x - bb.xmin - 40.0, 160.0 - bb.ymin, -bb.zmin))
        out = q if out is None else out.union(q)
        x += bb.xlen + 4.0
    return out
