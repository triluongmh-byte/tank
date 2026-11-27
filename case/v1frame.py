"""robot-tank v1 (printed) -> pilot contract frame, and shared primitives.

v1 frame: +X nose, +Y left, +Z up, ground z=0, turret axis x=y=0.
Contract frame (release note 8): X = -Y_v1, Y = -X_v1, Z = Z_v1  (nose -Y, +X right).
That map is the mirror across the plane through the origin with normal (1,1,0): it has
determinant -1, because the contract frame (+X right, +Y tail, +Z up) is left-handed.
Physical shape is preserved; every NEW printed part is mirror-symmetric, so its STL
prints correctly in a right-handed slicer too (see case/DEVIATIONS.md).
All new geometry is authored in the v1 frame (where the printed parts were measured).
"""
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'case' / 'ref' / 'v1'

FLOOR_Z = 43.0          # chassis plate top = hull floor (measured, chassis.step bbox z max)
LID_TOP = 73.0          # lid top face (lid.step bbox z max)
LID_UNDER = 70.0        # lid plate underside (hull_top)
CELL_LIFT = 1.4         # cells sit on the cell cradle saddles, 1.4 mm above v1 position


def to_contract(shape):
    """v1 -> contract frame: (x, y, z) -> (-y, -x, z)."""
    return shape.mirror(mirrorPlane=(1, 1, 0), basePointVector=(0, 0, 0))


def v1(name):
    """A v1 STEP as a Workplane in the v1 frame."""
    return cq.importers.importStep(str(REF / f'{name}.step'))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane('XY').circle(r).extrude(z1 - z0).translate((x, y, z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    return cq.Workplane('YZ').circle(r).extrude(x1 - x0).translate((x0, y, z))


def rot_z(shape, deg, cx, cy):
    return shape.rotate((cx, cy, 0), (cx, cy, 1), deg)
