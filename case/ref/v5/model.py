"""
Robot tank 6 banh (6WD rover) - mui nhon ">" kieu xe tang, co turret radar.

Plan
- Envelope ~162 x 99 x ~110 mm (co cai touchpad MacBook ~160 x 100).
- Nose points +X, ground at z=0. +Y side = left.
- Parts (printed): chassis (khung gam phang + 6 tai treo), hull (vo than doc 45 do,
  mo tren + duoi), lid (nap co cua so pin, o servo turret, cot de Nano),
  turret_head (gia ">" cho 2 sonar), 6 suspension arms, 6 wheels co gai chevron ">".
- Suspension: moi arm la 1 don bay quay quanh 1 vit M3 xuyen tai treo cua chassis.
  Dau sau gan servo SG90 (360 do, quay lien tuc) + banh xe tren horn; dau truoc
  (duoi nho) co lo de moc day thun (thun buoc toc / loom band) di len qua 2 khe tren
  chassis, vong qua thanh ngang giua 2 khe. Banh bi day len -> thun cang -> phuoc nhun.
- Turret: 1 SG90 (180 do) o giua nap; turret_head mang 2 HC-SR04 dau lung nhau
  (1 nhin truoc, 1 nhin sau) -> servo quet 180 do = phu 360 do.
- Mat robot: mui xe co tam glacis vat 45 do tu tren xuong, cua so cho man 1.54"
  (module gia dinh 38 x 32 x 4, vung hien thi 28 x 28) gan tu ben trong.
- Den pha: thanh LED 8 bong (WS2812 stick 51 x 10.2) tren can truoc led_bracket treo
  duoi mui chassis (2 vit M3 tu duoi len + dai oc), che 2 servo banh truoc; can nam
  trong khoang |y| < 28 nen khong vuong banh (mat trong banh o |y| = 35.5). Nano doi sang ben trai duoi nap.
- Joints: pivot = vit M3x10 + dai oc M3 (6 cai). Hull <-> chassis = 4 vit M3x12 tu
  duoi len + dai oc tren bosses. Lid ngam lip vao hull (friction).
- Bought: 6 SG90 360 (FS90R), 1 SG90 turret, 7 horns, 2 HC-SR04, 2 cell 18650,
  1 Arduino Nano (envelope 45x18x8), vit/dai oc M3.
- Assumptions: kich thuoc SG90/HC-SR04/Nano la danh nghia -> do lai truoc khi in.
  Can 1 board driver servo / nguon 5V (BEC) - de trong hull canh Nano.
- Board stack (module roi, KHONG sua xe): stack_base (tam de 4 lo M3 de bat vao dau
  cung duoc) + stack_tier giong het nhau, chong len nhau bang chot 4.4 / lo 5.0 o 4 cot
  goc, buoc tang 26 mm. Moi tang: khung 74 x 42 co cua so giua (cho chan header ESP32
  thong xuong), 4 tru M2.5 theo lo PCA9685 (55.9 x 19.05), 2 ray do mep ESP32 DevKit,
  4 khe day rut cho board khong co lo (mach sac...). Hien thi: tang 1 PCA9685, tang 2 ESP32.
  Gia dinh: PCA9685 62.2 x 25.4, ESP32 DevKit 30 chan 51.5 x 28.3 -> do lai truoc khi in.
"""
import math

import cadquery as cq
from cadsmith import Fit
from cadsmith.cadlib.components import (
    servo, servo_horn, servo_cutout, screw, nut, cell_18650,
)
from cadsmith.cadlib.styling import soften_edges, break_edges


class Params:
    servo_kind = "SG90"
    # wheels
    wheel_w = 14.0 * 4 / 3     # widened by 1/3 for a wider, more stable stance
    half_width = 35.5 + wheel_w   # outer face of wheels; inner face stays at ~35.5
    tire_r = 19.5
    lug_h = 1.5                # chevron tread height
    wheel_gap = 0.3            # servo shaft top -> wheel inner face
    wheel_chamfer = 1.0
    n_lugs = 16
    horn_arm = 14.0
    axle_x = (52.0, 0.0, -52.0)   # front, mid, rear
    # suspension arm (servo-local frame)
    arm_t = 3.0
    arm_margin = 2.5
    pivot_dx = 6.0             # pivot beyond flange end
    pivot_dz = 7.0             # pivot above axle
    pivot_r = 4.5
    tail_dx = 6.5              # band tab beyond pivot
    tail_dz = 11.0
    tail_r = 3.0
    band_hole = 3.0
    pin_hole_arm = 3.6         # rotating on M3
    pin_hole_lug = 3.4
    lug_t = 4.0
    lug_gap = 0.4
    band_slot_x = 2.5
    band_slot_y = 3.0
    hook_stem = (12.0, 9.0)    # stem x span behind the lug centre (rear, front)
    hook_tip = 6.5             # tooth tip behind the lug centre (lug rear face at 4.5)
    hook_z = (31.0, 0.0)       # tooth bottom
    hook_web_z = 37.5          # web joining hook to lug from here up to the plate
    band_bar = 3.5
    # chassis / hull
    chassis_z0 = 40.0
    chassis_t = 3.0
    tub_half = 34.0            # lower hull / chassis half width
    hull_half = 49.0
    slope_z0 = 48.0
    hull_top = 70.0
    wall = 2.0
    front_straight_x = 54.0
    nose_x = 80.0
    nose_half = 20.0
    glacis_z0 = 46.0          # glacis starts at the nose tip at this height, rises at 45 deg
    # 1.54" display module (assumed envelope)
    screen = (32.0, 38.0, 4.0)     # along slope, across (Y), thickness
    screen_win = 29.0
    # LED stick headlight
    led = (51.0, 10.2, 1.6)
    # front bumper under the nose (carries the LED bar, shields the front servos)
    bumper_gap = 2.5           # ahead of the front arm/servo, room for suspension travel
    bumper_min_x = 74.0
    bumper_t = 2.5
    bumper_half = 28.0
    bumper_z0 = 16.0
    bumper_led_z = 27.0
    bumper_pad_x0 = 62.0
    bumper_pad_half = 18.0
    bumper_screw_x = 68.0
    bumper_screw_y = 12.0
    rear_min = -80.0
    boss_x = (-40.0, 20.0)
    boss_y = 28.0
    boss_r = 4.5
    boss_h = 6.0
    m3_clear = 3.4
    vent_x = (-26.0, 26.0)
    vent_len = 12.0
    rear_window = 16.0             # square window in the rear wall
    tail_led = (34.5, 64.3, 5.2)   # y, z, hole dia for a 5 mm LED (press-fit, glue)
    # lid
    lid_t = 3.0
    lip_h = 3.0
    lip_clear = 0.3
    lip_w = 2.0
    window = (-70.0, -18.0, 17.0)   # x0, x1, half y
    wire_hole = (14.0, -14.0, 3.5)
    # electronics
    nano = (45.0, 18.0, 8.0)
    nano_x = 14.0
    nano_y = 19.0
    nano_standoff = 4.0
    nano_holes = (21.6, 7.6)
    # turret
    turret_x = 0.0
    head_r = 15.0
    head_t = 7.0               # thick enough to cover the horn hub with a solid skin
    head_gap = 0.3
    sonar_zc = 19.0            # sonar centre above head base
    plate_h = 31.0
    plate_t = 3.0              # one plate, a sonar on each face
    plate_half = 23.5
    # board stack (stand-alone module next to the car)
    stack_xy = (0.0, -112.0)
    stack_L = 74.0
    stack_W = 43.0
    stack_t = 2.5
    stack_r = 4.5                # corner fillet centred on the post, 0.5 outside it
    stack_pitch = 26.0           # tier to tier: room for PCA9685 + plugged servo leads
    stack_post = (32.5, 17.0)
    stack_post_d = 8.0
    stack_peg_d = 4.4
    stack_peg_h = 3.0
    stack_sock_d = 5.0           # 0.3 clearance per side on the peg
    stack_win = (46.0, 26.0)
    stack_so_h = 5.0             # board standoff / rail height
    stack_so_d = 5.0
    stack_so_hole = 2.2          # M2.5 self-tap
    pca = (62.2, 25.4, 1.6)
    pca_holes = (55.9, 19.05)
    esp = (51.5, 28.3, 1.6)
    stack_rail = (13.0, 15.0, 22.0)   # y0, y1, half length
    stack_zip = (12.0, 18.0, 4.0, 2.0)  # x, y, slot x, slot y
    base_t = 3.0
    base_L = 92.0
    base_holes = (41.0, 10.0)
    # 1.54" screen face on the stack's turret cap (45 deg, facing forward-up)
    stack_face_t = 2.5
    stack_face_len = 50.0        # along the slope
    stack_face_half = 43.0       # full width across Y
    stack_face_s = 25.0          # screen centre, measured down the slope from the top edge


P = Params

# ---------- derived from the servo model ----------
_bb = servo(P.servo_kind).val().BoundingBox()
LONG_NEG = abs(_bb.xmin) >= abs(_bb.xmax)


def orient_wheel(s):
    """Long side of the servo body to local -X (becomes world +X at a station)."""
    return s if LONG_NEG else s.rotate((0, 0, 0), (0, 0, 1), 180)


def orient_turret(s):
    """Long side of the servo body to world +X."""
    return s.rotate((0, 0, 0), (0, 0, 1), 180) if LONG_NEG else s


_ob = orient_wheel(servo(P.servo_kind)).val().BoundingBox()
FX0, FX1 = _ob.xmin, _ob.xmax
HY = max(-_ob.ymin, _ob.ymax)
ZMIN, ZMAX = _ob.zmin, _ob.zmax

AXLE_Z = P.tire_r + P.lug_h
Y_FLANGE = P.half_width - P.wheel_w - P.wheel_gap - ZMAX
PX_L = FX1 + P.pivot_dx
PZ_L = P.pivot_dz
TX_L = PX_L + P.tail_dx
TZ_L = P.tail_dz
PZ = AXLE_Z + PZ_L
BUMPER_X = max(P.bumper_min_x, max(P.axle_x) - FX0 + P.arm_margin + P.bumper_gap)
X_REAR = min(P.rear_min, min(P.axle_x) - TX_L - P.tail_r - 4.0)
CH_TOP = P.chassis_z0 + P.chassis_t
LID_TOP = P.hull_top + P.lid_t
HEAD_Z = LID_TOP + _bb.zmax + P.head_gap
LUG_Y1 = Y_FLANGE - P.arm_t - P.lug_gap
LUG_Y0 = LUG_Y1 - P.lug_t
NAMES = {52.0: "front", 0.0: "mid", -52.0: "rear"}


# ---------- primitives ----------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return (cq.Workplane("XY").circle(r).extrude(y1 - y0)
            .rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y0, z)))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    return (cq.Workplane("XY").circle(r).extrude(x1 - x0)
            .rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, y, z)))


def _gable(a0, a1, z0, zw):
    """Pentagon in (a, z): wall from z0 to zw, 45-degree roof to apex. Extruded 120 along local Z."""
    ha = (a1 - a0) / 2
    pts = [(a0, z0), (a1, z0), (a1, zw), ((a0 + a1) / 2, zw + ha), (a0, zw)]
    return cq.Workplane("XY").polyline(pts).close().extrude(120).translate((0, 0, -60))


def gable_x(x0, x1, z0, zw):
    """Gable cutter, outline in XZ, running through along Y."""
    return _gable(x0, x1, z0, zw).rotate((0, 0, 0), (1, 0, 0), 90)


def gable_y(y0, y1, z0, zw):
    """Gable cutter, outline in YZ, running along X over a short length (4 mm)."""
    g = _gable(y0, y1, z0, zw).rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 90)
    return g.intersect(box(-2.5, 2.5, -100, 100, -100, 100))


R2 = math.sqrt(2.0)


def glacis_keep(d=0.0):
    """Half-space behind the 45-degree front glacis, moved back by d (perpendicular)."""
    return (box(-400, 0, -200, 200, -200, 200).rotate((0, 0, 0), (0, 1, 0), -45)
            .translate((P.nose_x - d / R2, 0, P.glacis_z0 - d / R2)))


def on_glacis(shape):
    """Local frame on the glacis inner face: local Z = outward normal, centred on the slope."""
    w, g0 = P.wall, P.glacis_z0
    z_lo = g0 + w - w * R2            # inner face meets the inner front wall
    zc = (z_lo + P.hull_top) / 2
    xc = P.nose_x + g0 - w * R2 - zc
    return shape.rotate((0, 0, 0), (0, 1, 0), 45).translate((xc, 0, zc))


def plan_pts():
    H, fs, nx, nh = P.hull_half, P.front_straight_x, P.nose_x, P.nose_half
    return [(X_REAR, -H), (fs, -H), (nx, -nh), (nx, nh), (fs, H), (X_REAR, H)]


def prism(z0, z1, off=0.0):
    wp = cq.Workplane("XY").workplane(offset=z0).polyline(plan_pts()).close()
    if off:
        wp = wp.offset2D(off, "intersection")
    return wp.extrude(z1 - z0)


def xsec(pts_yz, x0, x1):
    return cq.Workplane("YZ").workplane(offset=x0).polyline(pts_yz).close().extrude(x1 - x0)


def station(shape, X, side):
    """Servo-local (oriented) frame -> world at wheel station X; side +1 = left (+Y)."""
    s = (shape.rotate((0, 0, 0), (0, 0, 1), 180)
         .rotate((0, 0, 0), (1, 0, 0), -90)
         .translate((X, Y_FLANGE, AXLE_Z)))
    return s if side > 0 else s.mirror("XZ")


def mirror_side(shape, side):
    return shape if side > 0 else shape.mirror("XZ")


def try_soften(part, radius, selector):
    try:
        return soften_edges(part, radius=radius, selector=selector)
    except Exception:
        return part


# ---------- wheel station pieces (servo-local frame) ----------
def servo_o():
    return orient_wheel(servo(P.servo_kind))


def horn_o():
    return orient_wheel(servo_horn(P.servo_kind, arm=P.horn_arm)).translate((0, 0, ZMAX))


def wheel_local():
    R, W = P.tire_r, P.wheel_w
    w = cq.Workplane("XY").circle(R).extrude(W).edges("%CIRCLE").chamfer(P.wheel_chamfer)
    for k in range(5):
        a = math.radians(36 + 72 * k)
        w = w.cut(cyl_z(3.5, -1, W + 1, 11.5 * math.cos(a), 11.5 * math.sin(a)))
    w = w.cut(cyl_z(2.75, -1, W + 1))
    for hx in (8.0, 12.0):
        w = w.cut(cyl_z(0.8, -1, W + 1, hx, 0))
    # chevron ">" tread lug
    # lugs run the full width so their ends sit on the bed instead of overhanging the chamfer
    pts = [(0, 0), (2, 0), (5, W / 2), (2, W), (0, W), (3, W / 2)]
    pts = [(u - 2.5, v) for u, v in pts]
    lug = (cq.Workplane("XY").polyline(pts).close().extrude(P.lug_h + 0.5)
           .rotate((0, 0, 0), (1, 0, 0), 90).translate((0, -(R - 0.5), 0)))
    for k in range(P.n_lugs):
        w = w.union(lug.rotate((0, 0, 0), (0, 0, 1), k * 360.0 / P.n_lugs))
    w = w.translate((0, 0, ZMAX + P.wheel_gap))
    return w.cut(horn_o())


def arm_local():
    t, m, r, tr = P.arm_t, P.arm_margin, P.pivot_r, P.tail_r
    hy = HY + m
    a = box(FX0 - m, FX1 + m, -hy, hy, -t, 0)
    a = a.union(box(FX1, PX_L, PZ_L - r, PZ_L + r, -t, 0))
    a = a.union(cyl_z(r, -t, 0, PX_L, PZ_L))
    link = (cq.Workplane("XY").workplane(offset=-t)
            .polyline([(PX_L, PZ_L - r), (TX_L, TZ_L - tr), (TX_L, TZ_L + tr), (PX_L, PZ_L + r)])
            .close().extrude(t))
    a = a.union(link).union(cyl_z(tr, -t, 0, TX_L, TZ_L))
    a = try_soften(a, 1.0, "|Z")
    a = a.cut(cyl_z(P.pin_hole_arm / 2, -t - 1, 1, PX_L, PZ_L))
    a = a.cut(cyl_z(P.band_hole / 2, -t - 1, 1, TX_L, TZ_L))
    a = a.cut(orient_wheel(servo_cutout(P.servo_kind, screw_hole=2.0)))
    return a


# ---------- chassis ----------
def chassis():
    z0, z1 = P.chassis_z0, CH_TOP
    plate = prism(z0, z1).intersect(box(X_REAR - 1, P.nose_x + 1, -P.tub_half, P.tub_half, z0 - 1, z1 + 1))
    plate = try_soften(plate, 2.0, "|Z")
    r = P.pivot_r
    for side in (1, -1):
        for X in P.axle_x:
            xc = X - PX_L
            lug = box(xc - r, xc + r, LUG_Y0, LUG_Y1, PZ, z0 + 0.5).union(
                cyl_y(r, LUG_Y0, LUG_Y1, xc, PZ))
            rh = P.pin_hole_lug / 2
            lug = lug.cut(cyl_y(rh, LUG_Y0 - 1, LUG_Y1 + 1, xc, PZ))
            # teardrop tip toward -Z: chassis prints top-down, so -Z is "up" on the bed
            tip = (cq.Workplane("XY").box(2 * rh, LUG_Y1 - LUG_Y0 + 2, 2 * rh)
                   .rotate((0, 0, 0), (0, 1, 0), 45)
                   .translate((xc, (LUG_Y0 + LUG_Y1) / 2, PZ))
                   .intersect(box(xc - 5, xc + 5, LUG_Y0 - 2, LUG_Y1 + 2, PZ - 5, PZ)))
            lug = lug.cut(tip)
            # band hook: ear behind the lug with a rear-opening notch; the band runs
            # from the arm's tail hole up into the notch and is held by the lower jaw
            # J-hook hanging behind the lug, its tooth pointing forward: the throat
            # between tooth and lug opens to the front, the tail pulls the band down
            # onto the tooth. Tooth top is 45 deg so it prints (chassis prints top-down).
            # One hook behind and a mirrored one in front, each joined to the lug by a top web.
            tz0 = P.hook_z[0]
            a0, a1, at = P.hook_stem[0], P.hook_stem[1], P.hook_tip
            for sg in (1, -1):                     # +1 = behind the lug, -1 = in front
                def X(o):
                    return xc - sg * o
                pts = [(X(a0), tz0), (X(at), tz0), (X(at), tz0 + 1.5),
                       (X(a1), tz0 + 1.5 + (a1 - at)), (X(a1), P.hook_web_z),
                       (X(r - 0.5), P.hook_web_z), (X(r - 0.5), z0 + 0.5), (X(a0), z0 + 0.5)]
                if sg < 0:
                    pts = pts[::-1]
                hook = (cq.Workplane("XY").polyline(pts).close().extrude(LUG_Y1 - LUG_Y0)
                        .rotate((0, 0, 0), (1, 0, 0), 90).translate((0, LUG_Y1, 0)))
                lug = lug.union(hook)
            plate = plate.union(mirror_side(lug, side))
    cuts = []
    for side in (1, -1):
        for X in P.axle_x:
            tx = X - TX_L
            yc = Y_FLANGE - P.arm_t / 2
            for dx in (-1, 1):
                sx = tx + dx * (P.band_bar + P.band_slot_x) / 2
                cuts.append(mirror_side(box(sx - P.band_slot_x / 2, sx + P.band_slot_x / 2,
                                            yc - P.band_slot_y / 2, yc + P.band_slot_y / 2,
                                            z0 - 1, z1 + 1), side))
            wy = max(8.0, Y_FLANGE + ZMIN + 3.0)
            cuts.append(mirror_side(box(X - 4, X + 4, wy - 2.5, wy + 2.5, z0 - 1, z1 + 1), side))
    for bx in P.boss_x:
        for sy in (1, -1):
            cuts.append(cyl_z(P.m3_clear / 2, z0 - 1, z1 + 1, bx, sy * P.boss_y))
    for sy in (1, -1):
        cuts.append(cyl_z(P.m3_clear / 2, z0 - 1, z1 + 1, P.bumper_screw_x, sy * P.bumper_screw_y))
    win = (cq.Workplane("XY").rect(24, 24).extrude(z1 - z0 + 2).edges("|Z").fillet(4)
           .translate((50, 0, z0 - 1)))
    cuts.append(win)
    for c in cuts:
        plate = plate.cut(c)
    return plate


# ---------- hull ----------
def hull():
    tub, H, w = P.tub_half, P.hull_half, P.wall
    zb, s0, top = CH_TOP, P.slope_z0, P.hull_top
    s1 = s0 + (H - tub)
    k = w * math.sqrt(2) - w
    outer = [(-tub, zb), (tub, zb), (tub, s0), (H, s1), (H, top), (-H, top), (-H, s1), (-tub, s0)]
    inner = [(-(tub - w), zb - 1), (tub - w, zb - 1), (tub - w, s0 + k), (H - w, s1 + k),
             (H - w, top + 1), (-(H - w), top + 1), (-(H - w), s1 + k), (-(tub - w), s0 + k)]
    x0, x1 = X_REAR - 1, P.nose_x + 1
    shell = xsec(outer, x0, x1).intersect(prism(zb, top)).intersect(glacis_keep(0.0))
    cavity = (xsec(inner, x0, x1).intersect(prism(zb - 1, top + 1, off=-w))
              .intersect(glacis_keep(w)))
    h = shell.cut(cavity)
    # screen window in the glacis (the robot's face)
    sw = P.screen_win / 2
    h = h.cut(on_glacis(box(-sw, sw, -sw, sw, -1, w + 2)))
    for bx in P.boss_x:
        for sy in (1, -1):
            b = cyl_z(P.boss_r, zb, zb + P.boss_h, bx, P.boss_y).union(
                box(bx - P.boss_r, bx + P.boss_r, P.boss_y, tub - w + 0.8, zb, zb + P.boss_h))
            b = b.cut(cyl_z(P.m3_clear / 2, zb - 1, zb + P.boss_h + 1, bx, P.boss_y))
            h = h.union(mirror_side(b, sy))
    # square side windows: vent_len x vent_len measured on the 45-degree slope
    hv = P.vent_len / 2
    dz = P.vent_len / math.sqrt(2)
    for vx in P.vent_x:
        for sy in (1, -1):
            v = box(vx - hv, vx + hv, 30, 47, 50, 50 + dz)
            h = h.cut(mirror_side(v, sy))
    rw = P.rear_window
    h = h.cut(box(X_REAR - 1, X_REAR + w + 1, -rw / 2, rw / 2, 49.0, 49.0 + rw))
    # tail lights: two 5 mm LED holes in the rear wall
    ly, lz, ld = P.tail_led
    for sy in (1, -1):
        h = h.cut(cyl_x(ld / 2, X_REAR - 1, X_REAR + w + 1, sy * ly, lz))
    return h


# ---------- lid ----------
def turret_servo():
    return orient_turret(servo(P.servo_kind)).translate((P.turret_x, 0, LID_TOP))


def turret_horn():
    return orient_turret(servo_horn(P.servo_kind, arm=P.horn_arm)).translate(
        (P.turret_x, 0, LID_TOP + _bb.zmax))


def lid():
    top, w = P.hull_top, P.wall
    l = prism(top, LID_TOP)
    try:  # chamfer, not fillet: the lid prints top-down
        l = break_edges(l, size=1.0, selector=">Z")
    except Exception:
        pass
    l = l.intersect(glacis_keep(0.0))
    lip = prism(top - P.lip_h, top + 0.5, off=-(w + P.lip_clear)).cut(
        prism(top - P.lip_h - 1, top + 1, off=-(w + P.lip_clear + P.lip_w)))
    lip = lip.intersect(glacis_keep(w + 0.6))
    l = l.union(lip)
    hx, hy = P.nano_holes
    for dx in (-hx, hx):
        for dy in (-hy, hy):
            px, py = P.nano_x + dx, P.nano_y + dy
            s = cyl_z(2.2, top - P.nano_standoff, top + 0.5, px, py).cut(
                cyl_z(0.8, top - P.nano_standoff - 1, top, px, py))
            l = l.union(s)
    l = l.cut(orient_turret(servo_cutout(P.servo_kind, screw_hole=2.0)).translate(
        (P.turret_x, 0, LID_TOP)))
    x0, x1, wy = P.window
    win = (cq.Workplane("XY").rect(x1 - x0, 2 * wy).extrude(P.lid_t + 2).edges("|Z").fillet(5)
           .translate(((x0 + x1) / 2, 0, top - 1)))
    l = l.cut(win)
    wx, wy, wr = P.wire_hole
    l = l.cut(cyl_z(wr, top - 1, LID_TOP + 1, wx, wy))
    return l


def nano():
    L, W, Hn = P.nano
    z1 = P.hull_top - P.nano_standoff
    return box(P.nano_x - L / 2, P.nano_x + L / 2, P.nano_y - W / 2, P.nano_y + W / 2, z1 - Hn, z1)


# ---------- face screen + headlight ----------
def screen():
    u, v, t = P.screen
    return on_glacis(box(-u / 2, u / 2, -v / 2, v / 2, -t, 0))


def led_bracket():
    """Front bumper hanging under the chassis nose: shields the front servos, carries the LED bar."""
    xb, ut, hb = BUMPER_X, P.bumper_t, P.bumper_half
    z1 = P.chassis_z0
    pt = 3.0
    b = box(P.bumper_pad_x0, xb + 0.5, -P.bumper_pad_half, P.bumper_pad_half, z1 - pt, z1)
    b = b.union(box(xb, xb + ut, -hb, hb, P.bumper_z0, z1))
    # 45-degree gussets between pad and plate
    for y in (-24.0, 0.0, 24.0):
        g = (cq.Workplane("XY")
             .polyline([(xb - 8.0, z1), (xb + 0.5, z1), (xb + 0.5, z1 - 8.5)])
             .close().extrude(1.6).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, y + 0.8, 0)))
        b = b.union(g)
    for sy in (1, -1):
        b = b.cut(cyl_z(P.m3_clear / 2, z1 - pt - 1, z1 + 1, P.bumper_screw_x, sy * P.bumper_screw_y))
    return b


def led_bar():
    L, H, t = P.led
    x1 = BUMPER_X + P.bumper_t
    zc = P.bumper_led_z
    b = box(x1, x1 + t, -L / 2, L / 2, zc - H / 2, zc + H / 2)
    for k in range(8):
        y = (k - 3.5) * 6.3
        b = b.union(box(x1 + t, x1 + t + 1.6, y - 2.5, y + 2.5, zc - 2.5, zc + 2.5))
    return b


# ---------- turret ----------
def sonar_local():
    """HC-SR04 facing +X, its back 1.5 mm in front of the centre plate face."""
    zc, x0 = P.sonar_zc, P.plate_t / 2 + 3.0
    s = box(x0, x0 + 1.6, -22.5, 22.5, zc - 10.0, zc + 10.0)
    for dy in (-13.0, 13.0):
        s = s.union(cyl_x(8.0, x0 + 1.6, x0 + 13.6, dy, zc))
    return s


def turret_place(shape, facing):
    """facing +1 = forward (+X), -1 = backward: the two sonars sit back to back."""
    s = shape if facing > 0 else shape.rotate((0, 0, 0), (0, 0, 1), 180)
    return s.translate((P.turret_x, 0, HEAD_Z))


def turret_head():
    ph, pt, hw = P.plate_h, P.plate_t, P.plate_half
    h = cyl_z(P.head_r, 0, P.head_t)
    h = h.union(box(-pt / 2, pt / 2, -hw, hw, 0, ph))          # shared back plate
    h = h.union(box(-6.0, 6.0, -hw, hw, 0, 3.0))               # foot along the plate
    for sy in (1, -1):                                         # end ribs
        h = h.union(box(-4.0, 4.0, sy * hw - 1.0 - 0.8, sy * hw - 1.0 + 0.8, 0, ph * 0.5))
    for dy in (-18.0, 18.0):                                   # standoffs, both faces
        for dz in (-8.5, 8.5):
            h = h.union(cyl_x(1.6, -pt / 2 - 3.0, pt / 2 + 3.0, dy, P.sonar_zc + dz))
    h = h.translate((P.turret_x, 0, HEAD_Z)).cut(turret_horn())
    # the horn pocket can leave a loose sliver (e.g. inside the horn's arm holes); keep the main body
    solids = h.solids().vals()
    main = max(solids, key=lambda s: s.Volume())
    return cq.Workplane("XY").newObject([main])


# ---------- board stack ----------
def _rplate(L, W, t, r):
    return cq.Workplane("XY").rect(L, W).extrude(t).edges("|Z").fillet(r)


def _stack_window(t):
    wx, wy = P.stack_win
    return cq.Workplane("XY").rect(wx, wy).extrude(t + 2).edges("|Z").fillet(3.0).translate((0, 0, -1))


def _post_pts():
    px, py = P.stack_post
    return [(sx * px, sy * py) for sx in (1, -1) for sy in (1, -1)]


def _peg(x, y, z0):
    return (cq.Workplane("XY").circle(P.stack_peg_d / 2).extrude(P.stack_peg_h + 0.5)
            .faces(">Z").chamfer(0.4).translate((x, y, z0 - 0.5)))


def stack_tier():
    """One stackable tier, origin at its bottom face centre."""
    t, so = P.stack_t, P.stack_so_h
    p = _rplate(P.stack_L, P.stack_W, t, P.stack_r).cut(_stack_window(t))
    for x, y in _post_pts():
        p = p.union(cyl_z(P.stack_post_d / 2, 0, P.stack_pitch, x, y))
        p = p.union(_peg(x, y, P.stack_pitch))
    hx, hy = P.pca_holes[0] / 2, P.pca_holes[1] / 2
    so_pts = [(sx * hx, sy * hy) for sx in (1, -1) for sy in (1, -1)]
    for x, y in so_pts:
        p = p.union(cyl_z(P.stack_so_d / 2, t - 0.5, t + so, x, y))
    y0, y1, rl = P.stack_rail
    p = p.union(box(-rl, rl, y0, y1, t - 0.5, t + so)).union(box(-rl, rl, -y1, -y0, t - 0.5, t + so))
    for x, y in so_pts:
        p = p.cut(cyl_z(P.stack_so_hole / 2, -1, t + so + 1, x, y))
    for x, y in _post_pts():
        p = p.cut(cyl_z(P.stack_sock_d / 2, -1, P.stack_peg_h + 0.4, x, y))
    zx, zy, sx_, sy_ = P.stack_zip
    for sx in (1, -1):
        for sy in (1, -1):
            p = p.cut(box(sx * zx - sx_ / 2, sx * zx + sx_ / 2, sy * zy - sy_ / 2, sy * zy + sy_ / 2, -1, t + 1))
    return p


def stack_base():
    t = P.base_t
    p = _rplate(P.base_L, P.stack_W, t, P.stack_r).cut(_stack_window(t))
    for x, y in _post_pts():
        p = p.union(_peg(x, y, t))
    hx, hy = P.base_holes
    for sx in (1, -1):
        for sy in (1, -1):
            p = p.cut(cyl_z(P.m3_clear / 2, -1, t + 1, sx * hx, sy * hy))
    return p


def stack_turret_mount():
    """Cap that plugs onto the top tier's pegs and seats the turret SG90 (option 2 turret spot)."""
    t, h = 3.0, 8.0
    p = _rplate(P.stack_L, P.stack_W, t, P.stack_r).translate((0, 0, h - t))
    for x, y in _post_pts():
        p = p.union(cyl_z(P.stack_post_d / 2, 0, h - t + 0.5, x, y))
        p = p.cut(cyl_z(P.stack_sock_d / 2, -1, P.stack_peg_h + 0.4, x, y))
    p = p.cut(orient_turret(servo_cutout(P.servo_kind, screw_hole=2.0)).translate((0, 0, h)))
    # 45-degree face panel hanging from the front edge (same look as the car's glacis)
    x0, pt, S, hw = P.stack_L / 2, P.stack_face_t, P.stack_face_len, P.stack_face_half
    run = S / R2
    k = x0 + h                      # outer plane x + z = k
    ki = k - pt * R2                # inner plane
    zb = h - run
    panel = (cq.Workplane("XZ")
             .polyline([(x0 - 1, h), (x0, h), (x0 + run, zb), (ki - zb, zb),
                        (ki - (h - t), h - t), (x0 - 1, h - t)]).close()
             .extrude(hw).translate((0, hw / 2, 0)))
    p = p.union(panel)
    for sy in (1, -1):              # side cheeks bracing the panel
        y0 = hw / 2 - 2.0
        cheek = (cq.Workplane("XZ")
                 .polyline([(x0, -12.0), (ki + 0.5 + 12.0, -12.0), (x0, ki + 0.5 - x0)])
                 .close().extrude(2.0).translate((0, y0 + 2.0, 0)))
        p = p.union(cheek if sy > 0 else cheek.mirror("XZ"))
    sw = P.screen_win / 2
    p = p.cut(stack_face_frame(box(-sw, sw, -sw, sw, -1, pt + 1)))
    return p


def stack_face_frame(shape):
    """Local frame on the stack face panel inner side: local Z = outward normal, local X down the slope."""
    x0, h, pt = P.stack_L / 2, 8.0, P.stack_face_t
    s = P.stack_face_s
    xo, zo = x0 + s / R2, h - s / R2
    return shape.rotate((0, 0, 0), (0, 1, 0), 45).translate((xo - pt / R2, 0, zo - pt / R2))


def stack_screen():
    u, v, t = P.screen
    return stack_face_frame(box(-u / 2, u / 2, -v / 2, v / 2, -t, 0))


STACK_CAP_H = 8.0


def pca_board(z):
    L, W, t = P.pca
    b = box(-L / 2, L / 2, -W / 2, W / 2, z, z + t)
    return b.union(box(-20.3, 20.3, -W / 2 + 0.6, -W / 2 + 8.2, z + t - 0.1, z + t + 8.5))


def esp_board(z):
    L, W, t = P.esp
    b = box(-L / 2, L / 2, -W / 2, W / 2, z, z + t)
    b = b.union(box(L / 2 - 25.5, L / 2, -9.0, 9.0, z + t - 0.1, z + t + 3.2))
    for sy in (1, -1):   # header pins hanging down through the tier window
        b = b.union(box(-19.0, 19.0, sy * 11.43 - 1.25, sy * 11.43 + 1.25, z - 8.0, z + 0.1))
    return b


def stack_parts():
    sx, sy = P.stack_xy
    z1 = P.base_t
    z2 = z1 + P.stack_pitch
    board_dz = P.stack_t + P.stack_so_h
    z3 = z2 + P.stack_pitch
    top = z3 + STACK_CAP_H
    return {
        "stack_turret_mount": stack_turret_mount().translate((sx, sy, z3)),
        "screen_stack": stack_screen().translate((sx, sy, z3)),
        "servo_turret_stack": orient_turret(servo(P.servo_kind)).translate((sx, sy, top)),
        "horn_turret_stack": orient_turret(servo_horn(P.servo_kind, arm=P.horn_arm)).translate(
            (sx, sy, top + _bb.zmax)),
        "stack_base": stack_base().translate((sx, sy, 0)),
        "stack_tier_1": stack_tier().translate((sx, sy, z1)),
        "stack_tier_2": stack_tier().translate((sx, sy, z2)),
        "pca9685": pca_board(z1 + board_dz).translate((sx, sy, 0)),
        "esp32": esp_board(z2 + board_dz).translate((sx, sy, 0)),
    }


# ---------- assembly ----------
def parts():
    out = {
        "chassis": chassis(),
        "hull": hull(),
        "lid": lid(),
        "turret_head": turret_head(),
        "servo_turret": turret_servo(),
        "horn_turret": turret_horn(),
        "sonar_front": turret_place(sonar_local(), 1),
        "sonar_rear": turret_place(sonar_local(), -1),
        "nano": nano(),
        "screen": screen(),
        "led_bracket": led_bracket(),
        "led_bar": led_bar(),
    }
    for j, sy in enumerate((1, -1)):
        out[f"screw_led_{j + 1}"] = screw("M3", 10.0).rotate((0, 0, 0), (1, 0, 0), 180).translate(
            (P.bumper_screw_x, sy * P.bumper_screw_y, P.chassis_z0 - 3.0))
        out[f"nut_led_{j + 1}"] = nut("M3").translate(
            (P.bumper_screw_x, sy * P.bumper_screw_y, CH_TOP))
    arm = arm_local()
    wheel = wheel_local()
    sv, hn = servo_o(), horn_o()
    for side, sname in ((1, "left"), (-1, "right")):
        for X in P.axle_x:
            n = f"{NAMES[X]}_{sname}"
            out[f"arm_{n}"] = station(arm, X, side)
            out[f"wheel_{n}"] = station(wheel, X, side)
            out[f"servo_{n}"] = station(sv, X, side)
            out[f"horn_{n}"] = station(hn, X, side)
            xc = X - PX_L
            out[f"screw_pivot_{n}"] = mirror_side(
                screw("M3", 10.0).rotate((0, 0, 0), (1, 0, 0), -90).translate((xc, Y_FLANGE, PZ)), side)
            out[f"nut_pivot_{n}"] = mirror_side(
                nut("M3").rotate((0, 0, 0), (1, 0, 0), 90).translate((xc, LUG_Y0, PZ)), side)
    i = 0
    for bx in P.boss_x:
        for sy in (1, -1):
            i += 1
            out[f"screw_hull_{i}"] = screw("M3", 12.0).rotate((0, 0, 0), (1, 0, 0), 180).translate(
                (bx, sy * P.boss_y, P.chassis_z0))
            out[f"nut_hull_{i}"] = nut("M3").translate((bx, sy * P.boss_y, CH_TOP + P.boss_h))
    cb = cell_18650().val().BoundingBox()
    cx = X_REAR + P.wall + 0.5 + cb.xlen / 2
    for j, sy in enumerate((1, -1)):
        out[f"cell_{j + 1}"] = cell_18650().translate(
            (cx - (cb.xmin + cb.xmax) / 2, sy * (cb.ylen / 2 + 0.4) - (cb.ymin + cb.ymax) / 2,
             CH_TOP - cb.zmin))
    out.update(stack_parts())
    return out


_side_names = [f"{a}_{s}" for a in ("front", "mid", "rear") for s in ("left", "right")]

BOUGHT = {"servo_turret", "horn_turret", "sonar_front", "sonar_rear", "nano", "cell_1", "cell_2",
          "screen", "led_bar", "screw_led_1", "screw_led_2", "nut_led_1", "nut_led_2",
          "pca9685", "esp32", "servo_turret_stack", "horn_turret_stack",
          "screen_stack"}
BOUGHT |= {f"{p}_{n}" for p in ("servo", "horn", "screw_pivot", "nut_pivot") for n in _side_names}
BOUGHT |= {f"{p}_{i}" for p in ("screw_hull", "nut_hull") for i in range(1, 5)}

FITS = [
    Fit("hull", "chassis", seat="z"),
    Fit("lid", "hull", seat="z"),
    Fit("led_bracket", "chassis", seat="z"),
    Fit("stack_base", "stack_tier_1", seat="z"),
    Fit("stack_tier_1", "stack_tier_2", seat="z"),
    Fit("stack_tier_2", "stack_turret_mount", seat="z"),
]

ORIENT = {"chassis": "+Z", "hull": "-Z", "lid": "+Z", "turret_head": "-Z", "led_bracket": "+Z",
          "stack_base": "-Z", "stack_tier_1": "-Z", "stack_tier_2": "-Z",
          "stack_turret_mount": "+Z"}
for _n in _side_names:
    _o = "+Y" if _n.endswith("left") else "-Y"
    ORIENT[f"wheel_{_n}"] = _o
    ORIENT[f"arm_{_n}"] = _o
