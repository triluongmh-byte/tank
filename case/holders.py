"""Glue-on holders for the devices robot-tank v1 has no place for (v1 frame, mm).

Every holder has a flat glue face (502 / CA glue) and is mirror-symmetric, so the contract-frame
STL prints correctly. Device sizes are GIẢ ĐỊNH (reference datasheets / listings); the person
checks them with the TEST ONLY coupon before gluing. Positions come from free-space probes of
the printed v1 parts (case/ref/v1, tools/case/fit_checks.py re-measures them every run).
"""
import math
import cadquery as cq
from v1frame import FLOOR_Z, LID_TOP, CELL_LIFT, box, cyl_z, cyl_x, rot_z

R2 = math.sqrt(2.0)
F = FLOOR_Z

# ---------------- ESP32 DevKit 30-pin (GIẢ ĐỊNH 51.5 x 28.3 x 1.6, rows 25.4 apart) -----------
ESP_PCB = (51.5, 28.3, 1.6)
ESP_X0, ESP_Y0 = -12.0, -35.6          # PCB min corner; USB end at x = -12 (faces the tail)
ESP_CX, ESP_CY = ESP_X0 + ESP_PCB[0] / 2, ESP_Y0 + ESP_PCB[1] / 2
ESP_LEDGE_Z = 60.5                      # post ledge; 1 mm foam tape -> PCB bottom 61.5
ESP_PCB_Z = ESP_LEDGE_Z + 1.0
POST_Y = (-31.5, -24.0)                 # posts sit under the PCB, between the pin rows' ends
POST_CY = sum(POST_Y) / 2


def esp32_post_rear():
    """Post under the USB end of the DevKit: ledge + end stop; foam tape holds the PCB."""
    y0, y1 = POST_Y
    stop0 = ESP_X0 - 0.3 - 1.6
    p = box(stop0, stop0 + 6.0, y0, y1, F, ESP_LEDGE_Z)                  # post 6 x 7.5
    p = p.union(box(stop0, stop0 + 9.0, y0, y1, F, F + 2.0))             # foot: more glue area
    p = p.union(box(stop0, stop0 + 1.6, y0, y1, ESP_LEDGE_Z, ESP_LEDGE_Z + 3.5))  # end stop
    return p


def esp32_post_front():
    return rot_z(esp32_post_rear(), 180, ESP_CX, POST_CY)


def esp32_ref():
    """DevKit envelope: PCB, top parts 3.4 mm, header pins 8.5 mm below the PCB."""
    L, W, T = ESP_PCB
    z = ESP_PCB_Z
    e = box(ESP_X0, ESP_X0 + L, ESP_Y0, ESP_Y0 + W, z, z + T + 3.4)
    for dy in (-12.7, 12.7):
        e = e.union(box(ESP_CX - 19.05 - 1.3, ESP_CX + 19.05 + 1.3, ESP_CY + dy - 1.3, ESP_CY + dy + 1.3, z - 8.5, z))
    return e


# ---------------- PCA9685 16-ch (GIẢ ĐỊNH 62.2 x 25.4, holes 55.9 x 19.05; logic via 90-deg plug) -
PCA_X0 = 41.8
PCA_L, PCA_W = 25.4, 62.2              # along X, along Y (long axis across the hull)
PCA_Z = 46.0                            # PCB bottom on the pads (front edge must stay under the screen)
PCA_HOLES_X = (PCA_X0 + 3.175, PCA_X0 + 3.175 + 19.05)
PCA_HOLES_Y = (-27.95, 27.95)


def pca_post(x, y):
    """One pad under a PCA9685 hole with a 2.0 mm peg through it (4 identical posts).
    Glue them with the board fitted on the pegs (the board is the jig); a drop of glue on
    each peg head holds the board. No room for screws under the screen."""
    p = cyl_z(2.5, F, PCA_Z, x, y)
    p = p.union(cyl_z(1.0, PCA_Z, PCA_Z + 1.6 + 1.2, x, y))
    return p


def pca_posts():
    return {f'pca_post_{a}_{b}': (lambda x=x, y=y: pca_post(x, y))
            for a, x in (('rear', PCA_HOLES_X[0]), ('front', PCA_HOLES_X[1]))
            for b, y in (('left', PCA_HOLES_Y[1]), ('right', PCA_HOLES_Y[0]))}


def pca_ref():
    """PCB + 16 servo headers on the rear long edge with plugs (2.5 + 14.5 mm) + parts 10 mm."""
    z = PCA_Z
    e = box(PCA_X0, PCA_X0 + 14.0, -PCA_W / 2, PCA_W / 2, z, z + 1.6 + 10.0)     # cap, terminal block
    e = e.union(box(PCA_X0, PCA_X0 + PCA_L, -PCA_W / 2, PCA_W / 2, z, z + 1.6 + 1.5))  # chip, LEDs, resistors
    e = e.union(box(PCA_X0 + 0.8, PCA_X0 + 8.4, -22.0, 22.0, z - 2.0, z))        # header solder tails
    e = e.union(box(PCA_X0 + 0.8, PCA_X0 + 8.4, -22.0, 22.0, z, z + 1.6 + 17.0))   # servo plugs
    for sy in (1, -1):                       # 6-pin logic header, 90-degree female plug (straight: hits glacis)
        e = e.union(box(PCA_X0 + 5.1, PCA_X0 + 20.3, sy * 28.0 - 1.4, sy * 28.0 + 1.4, z, z + 1.6 + 11.5))
    return e


# ---------------- 1S charge/boost 5V 2A Type-C module (GIẢ ĐỊNH 26 x 21 x 7) --------------------
TRAY = (27.0, 23.0)                     # plate; module rests between two low lips
TRAY_A = (-13.0, 8.6)                   # min corners
TRAY_B = (15.0, -8.0)                   # turned 90 deg: 23 along X, 27 along Y (x 15..38)


def power_tray(x0=0.0, y0=0.0):
    L, W = TRAY
    t = box(0, L, 0, W, F, F + 1.6)
    for y in (0.0, W - 1.0):
        t = t.union(box(0, L, y, y + 1.0, F + 1.6, F + 3.6))              # side lips (ends open: ports)
    for x in (6.0, L - 9.0):                                              # zip-tie slots 3 x 2
        t = t.cut(box(x, x + 3.0, W / 2 - 7.0, W / 2 - 5.0, F - 1, F + 5)).cut(
            box(x, x + 3.0, W / 2 + 5.0, W / 2 + 7.0, F - 1, F + 5))
    return t.translate((x0, y0, 0))


def power_tray_a():
    return power_tray(*TRAY_A)


def power_tray_b():
    return rot_z(power_tray(), 90, 0, 0).translate((TRAY_B[0] + TRAY[1], TRAY_B[1], 0))


def power_ref(x0, y0, turned=False):
    if turned:
        return box(x0 + 1.0, x0 + 22.0, y0 + 0.5, y0 + 26.5, F + 1.6, F + 1.6 + 7.0)
    return box(x0 + 0.5, x0 + 26.5, y0 + 1.0, y0 + 22.0, F + 1.6, F + 1.6 + 7.0)


# ---------------- 30 x 30 fan plate on the lid, over the v1 battery window -----------------------
FAN_C = (-44.0, 0.0)
FAN_T = 10.0                            # GIẢ ĐỊNH 3010 fan; thickness unconfirmed (note 1)


def fan_plate():
    cx, cy = FAN_C
    p = box(cx - 18, cx + 18, cy - 21, cy + 21, LID_TOP, LID_TOP + 2.5)
    p = p.cut(cyl_z(14.25, LID_TOP - 1, LID_TOP + 4, cx, cy))
    for dx in (-12, 12):
        for dy in (-12, 12):
            p = p.cut(cyl_z(1.7, LID_TOP - 1, LID_TOP + 4, cx + dx, cy + dy))
    return p


def fan_ref():
    cx, cy = FAN_C
    z = LID_TOP + 2.5
    return box(cx - 15, cx + 15, cy - 15, cy + 15, z, z + FAN_T)


# ---------------- 1.54" ST7789 screen clips on the glacis inner face -----------------------------
# Glacis inner face: x + z = 126 - 2*sqrt(2). Screen centre / size from v1 model (GIẢ ĐỊNH 32 x 38 x 4).
G_IN = 126.0 - 2.0 * R2
SCR_C = (65.58, 0.0, 57.59)
SCR = (32.0, 38.0, 4.0)                 # along slope, across, thickness


def on_glacis(shape):
    """Local frame: X down the slope (toward the nose), Y across, Z = outward normal; origin screen centre on the inner face."""
    return shape.rotate((0, 0, 0), (0, 1, 0), 45).translate(SCR_C)


def screen_clip_local():
    """Pad glued beside the screen; its lip holds the screen's back edge (upper half of the slope)."""
    t = SCR[2] + 0.3
    y_in = SCR[1] / 2 + 0.3
    c = box(-14.0, -2.0, y_in, y_in + 4.0, -t, 0)                   # spacer pad, glue face at z=0
    c = c.union(box(-14.0, -2.0, SCR[1] / 2 - 2.5, y_in + 4.0, -t - 1.6, -t))   # lip over the screen back
    return c


def screen_clip_left():
    return on_glacis(screen_clip_local())


def screen_clip_right():
    return screen_clip_left().mirror('XZ')


def screen_ref():
    u, v, t = SCR
    return on_glacis(box(-u / 2, u / 2, -v / 2, v / 2, -t, 0))


# ---------------- 2 x 18650 cradle (cells side by side, as in v1) -------------------------------
CELL_R = 9.3
CELL_Y = 9.7                            # v1 cell centres y = +-9.7
CELL_X = (-79.6, -14.4)


def cell_cradle():
    z0 = F + 1.2
    zc = F + CELL_LIFT + CELL_R
    c = box(-78.5, -15.5, -22.0, 22.0, F, z0)
    for x in (-76.0, -49.0, -22.0):
        s = box(x, x + 4.0, -20.0, 20.0, z0, F + 7.0)
        for sy in (1, -1):
            s = s.cut(cyl_x(CELL_R + 0.25, x - 1, x + 5, sy * CELL_Y, zc))
        c = c.union(s)
    for x in (-69.0, -42.0):                                      # strap slots (15 mm strap)
        for sy in (1, -1):
            c = c.cut(box(x, x + 16.0, sy * 18.75 - 1.25, sy * 18.75 + 1.25, F - 1, z0 + 1))
    return c


# ---------------- TEST ONLY coupon: real slices of every holder fit -------------------------------
def coupon():
    """Slices of the real holders, laid out in a row beside the vehicle (never assembled)."""
    pieces = []
    e = esp32_post_rear().intersect(box(-20, 0, -40, 0, ESP_LEDGE_Z - 6, ESP_LEDGE_Z + 4))
    pieces.append(e)
    pieces.append(pca_post(PCA_HOLES_X[0], PCA_HOLES_Y[1]))
    pieces.append(power_tray_a().intersect(box(-14, 0, 0, 40, F - 1, 60)))
    pieces.append(fan_plate().intersect(box(-62.5, -25.5, 8, 21.5, 70, 80)))
    pieces.append(cell_cradle().intersect(box(-24, -16, -23, 23, F - 1, 60)))
    pieces.append(screen_clip_local())
    out, x = None, 0.0
    for p in pieces:
        bb = p.val().BoundingBox()
        q = p.translate((x - bb.xmin, 70.0 - bb.ymin, -bb.zmin))
        out = q if out is None else out.union(q)
        x += bb.xlen + 4.0
    return out
