"""Lead integration review 3: holder for the battery-fed DevKit logic converter (layout B).

engineering/POWER_SYSTEM.md optional chain: M_LOGIC = Pololu U3V16F5 fed from the RUN harness
(after F_PACK + protector, at the XT60) -> 5 V -> USB power-only lead -> ESP32 DevKit USB port.
Portable mode: this lead is in the DevKit port. Host mode: the person unplugs it and plugs the
host data cable into the same port. Never both, no Y cable, no joined USB positives.

v1 frame (x nose, y left, z up), authored on the car, drawn beside it (stack.DISPLAY) like the rest
of layout B. Free floor measured with build/case/probe_logic.py: solid chassis floor x 44..60,
y 14..30 (left of the front floor window |y| < 12), nothing above it up to z 58.
Module size GIẢ ĐỊNH: 8.1 x 13.2 x 2.5 mm (lead review); try coupon_logic_TEST_ONLY first.
"""
from v1frame import FLOOR_Z, box

F = FLOOR_Z
BASE, WALL, LIP_H, CLR = 1.5, 1.2, 3.0, 0.2
LOGIC = (13.2, 8.1, 2.5)        # U3V16F5: length (x, pins at both x ends), width (y), height (z) GIẢ ĐỊNH
X0, Y0 = 47.0, 17.0              # holder low corner on the floor (v1)
W_Y = LOGIC[1] + 2 * CLR + 2 * WALL          # 10.9
L_X = LOGIC[0] + 2.0                          # 15.2: base 1 mm longer each end, ends open for the leads


def logic_holder():
    """Flat floor tray: base + two long side lips; both short ends open for VIN/GND and VOUT/GND leads.
    Foam tape under the module; the base is glued to the hull floor with 502."""
    p = box(X0, X0 + L_X, Y0, Y0 + W_Y, F, F + BASE)
    for ya in (Y0, Y0 + W_Y - WALL):
        p = p.union(box(X0 + 1.5, X0 + L_X - 1.5, ya, ya + WALL, F + BASE - 0.01, F + BASE + LIP_H))
    return p


def logic_ref():
    xa, ya = X0 + 1.0, Y0 + WALL + CLR
    return box(xa, xa + LOGIC[0], ya, ya + LOGIC[1], F + BASE + 0.02, F + BASE + 0.02 + LOGIC[2])


def coupon_logic():
    """TEST ONLY: the whole holder (it is only 15 x 11 x 4.5 mm), laid in the coupon row."""
    p = logic_holder()
    bb = p.val().BoundingBox()
    return p.translate((-bb.xmin - 40.0, 200.0 - bb.ymin, -bb.zmin))
