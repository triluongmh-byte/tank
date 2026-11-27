"""Simple-stage mechanical check for the glue-on holders on the printed robot-tank v1.

    "$KICAD_CASE_PYTHON" tools/case/fit_checks.py [--force]

Measures the exported files in case/out (never the build code):
  print:     every printable part is one valid solid, fits the A1 bed in its print orientation,
             walls >= 0.75 mm (kicadpy.case_measure), overhang past 45 deg in print orientation
  collide:   every new holder against every v1 printed part, bought reference and other holder
             (a glue face may touch: overlap <= 0.5 mm3); every device envelope against all bodies
             except the holder it rests on
  wires:     every route in case/interfaces.json against ALL bodies, printed or reference
             (the harness's own wire check only sees printable parts)
Writes case/reports/mechanical.json (verdict, passed, scope, partShas) on every run; reuses the
previous measurements when no input changed. Uses every CPU core.
"""
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case' / 'out'
REPORT = ROOT / 'case' / 'reports' / 'mechanical.json'
CACHE = ROOT / 'build' / 'case' / 'mechanical-cache.json'
BED = (256.0, 256.0, 256.0)
OVERLAP_MM3 = 0.5
OVERHANG_REVIEW_MM2 = 20.0
# device envelope -> the holders it may rest on
SEATS = {'ref_esp32_devkit': ['esp32_post_rear', 'esp32_post_front'],
         'ref_pca9685': ['pca_post_rear_left', 'pca_post_rear_right', 'pca_post_front_left', 'pca_post_front_right'],
         'ref_power_module_a': ['power_tray_a'], 'ref_power_module_b': ['power_tray_b'],
         'ref_fan_3010': ['fan_plate'], 'ref_screen_module': ['screen_clip_left', 'screen_clip_right', 'hull'],
         'ref_cell_1': ['cell_cradle', 'ref_cell_2'], 'ref_cell_2': ['cell_cradle', 'ref_cell_1'],
         'ref_pca9685_B': ['stack_tier_1'], 'ref_esp32_B': ['stack_tier_2'], 'ref_fan_B': ['stack_tier_1'],
         'ref_screen_stack_B': ['stack_turret_mount'],
         'ref_servo_turret_stack_B': ['stack_turret_mount', 'ref_horn_turret_stack_B'],
         'ref_horn_turret_stack_B': ['ref_servo_turret_stack_B', 'ref_turret_head_B'],
         'ref_turret_head_B': ['ref_horn_turret_stack_B', 'ref_sonar_front_B', 'ref_sonar_rear_B'],
         'ref_sonar_front_B': ['ref_turret_head_B'], 'ref_sonar_rear_B': ['ref_turret_head_B'],
         # layout B power chain (case/power_b.py, lead integration review 2)
         'ref_conv_a_B': ['conv_holder_a'], 'ref_conv_b_B': ['conv_holder_b'], 'ref_fuse_pack_B': ['fuse_holder_pack'],
         'ref_protector_B': ['protector_holder', 'chassis'], 'ref_fuse_b_B': ['fuse_clip_b'],
         'ref_logic_B': ['logic_holder']}
POWER_B = ['conv_holder_a', 'conv_holder_b', 'fuse_holder_pack', 'protector_holder', 'fuse_clip_b',
           'ref_conv_a_B', 'ref_conv_b_B', 'ref_fuse_pack_B', 'ref_protector_B', 'ref_fuse_b_B',
           'logic_holder', 'ref_logic_B']   # lead review 3: M_LOGIC U3V16F5 (case/logic_b.py)
# ---- layout B (note 9): stack drawn beside the car at contract X +130; checked here on the car -----
B_SHIFT = (-130.0, 0.0, 0.0)
B_MOVE = ['stack_carrier_deck', 'ref_carrier_B', 'ref_fan_B', 'stack_bridge_plate', 'stack_leg_rear_left', 'stack_leg_rear_right', 'stack_leg_front_left', 'stack_leg_front_right', 'stack_tier_1', 'stack_tier_2', 'stack_turret_mount', 'ref_pca9685_B', 'ref_esp32_B',
          'ref_screen_stack_B', 'ref_servo_turret_stack_B', 'ref_horn_turret_stack_B', 'ref_turret_head_B',
          'ref_sonar_front_B', 'ref_sonar_rear_B'] + POWER_B
# layout B: the layout-A charge/boost trays are not fitted (their bay holds the DECIDED power chain)
B_CAR = ['chassis', 'hull', 'led_bracket', 'ref_led_bar', 'cell_cradle', 'ref_cell_1', 'ref_cell_2'] + [
    f'{k}_{p}_{s}' for k in ('arm', 'wheel', 'ref_servo', 'ref_horn') for p in ('front', 'mid', 'rear') for s in ('left', 'right')]
LEGS = ['stack_leg_rear_left', 'stack_leg_rear_right', 'stack_leg_front_left', 'stack_leg_front_right']
B_ALLOW = {'stack_bridge_plate': ['stack_carrier_deck'] + LEGS, **{l: ['chassis', 'stack_bridge_plate'] for l in LEGS},
           'stack_carrier_deck': ['stack_bridge_plate', 'stack_tier_1', 'ref_carrier_B'],
           'ref_carrier_B': ['stack_carrier_deck'],
           'stack_tier_1': ['stack_carrier_deck', 'stack_tier_2', 'ref_pca9685_B'],
           'stack_tier_2': ['stack_tier_1', 'stack_turret_mount', 'ref_esp32_B', 'ref_servo_turret_stack_B'],
           'stack_turret_mount': ['stack_tier_2', 'ref_screen_stack_B', 'ref_servo_turret_stack_B'],
           **{n: ['chassis'] for n in ('conv_holder_a', 'conv_holder_b', 'fuse_holder_pack', 'protector_holder')},
           'fuse_clip_b': ['hull'], 'logic_holder': ['chassis']}
B_LAYOUT = ROOT / 'case' / 'layout_b.json'
MASS_G = {'ref_carrier': 30.0, 'ref_fan': 10.0, 'ref_servo': 9.0, 'ref_cell': 47.0, 'ref_sonar': 9.0, 'ref_pca9685': 9.0, 'ref_esp32': 10.0, 'ref_screen': 6.0,
          'ref_power_module': 5.0, 'ref_servo_turret': 9.0,
          'ref_conv': 7.0, 'ref_logic': 2.0, 'ref_fuse_pack': 12.0, 'ref_fuse_b': 8.0, 'ref_protector': 8.0}
PETG_G_MM3 = 1.27e-3 * 0.5     # GIẢ ĐỊNH: printed at about half solid density
# a holder's glue face and the printed part it is glued to
GLUED = {'esp32_post_rear': 'chassis', 'esp32_post_front': 'chassis', 'pca_post_rear_left': 'chassis', 'pca_post_rear_right': 'chassis',
         'pca_post_front_left': 'chassis', 'pca_post_front_right': 'chassis', 'power_tray_a': 'chassis', 'power_tray_b': 'chassis',
         'cell_cradle': 'chassis', 'fan_plate': 'lid', 'screen_clip_left': 'hull', 'screen_clip_right': 'hull'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    import cadquery as cq
    parts = {p['name']: p for p in json.loads((OUT / 'parts.json').read_text())['parts']}
    return cq.importers.importStep(str(OUT / parts[name]['step'])).val()


_SHAPES = {}


def shape(name):
    if name not in _SHAPES:
        if name.endswith('@car'):
            import cadquery as cq
            _SHAPES[name] = load(name[:-4]).moved(cq.Location(cq.Vector(*B_SHIFT)))
        else:
            _SHAPES[name] = load(name)
    return _SHAPES[name]


def b_name(n):
    return n + '@car' if n in B_MOVE else n


def b_collide_job(name):
    others = [b_name(o) for o in B_MOVE + B_CAR if o != name]
    allowed = [b_name(o) for o in B_ALLOW.get(name, []) + SEATS.get(name, [])]
    hits = []
    for o in others:
        v = overlap(b_name(name), o)
        if isinstance(v, str):
            hits.append({'with': o, 'level': 'unverified', 'message': v})
        elif v > OVERLAP_MM3 and o not in allowed:
            hits.append({'with': o, 'level': 'fail', 'overlapMm3': round(v, 2)})
    return name, hits


def b_mass_props():
    """Envelope and a rough centre of gravity, layout A (lid on) and B (stack on the car)."""
    import numpy as np
    def mass(n):
        for k, g in MASS_G.items():
            if n.startswith(k):
                return g
        return shape(n).Volume() * PETG_G_MM3
    a_names = [n for n in json_parts() if not n.startswith('coupon') and n not in B_MOVE and n != 'stack_base']
    out = {}
    for label, names in (('A_lid_on', a_names), ('B_stack_on_car', [b_name(n) for n in B_MOVE] + B_CAR + ['ref_esp32_devkit_skip'])):
        names = [n for n in names if not n.endswith('_skip')]
        if label.startswith('B'):
            names = [n for n in names if n.replace('@car', '') != 'ref_esp32_devkit']
        m, c, lo, hi = 0.0, np.zeros(3), np.full(3, 1e9), np.full(3, -1e9)
        for n in names:
            sh = shape(n); bb = sh.BoundingBox()
            g = mass(n.replace('@car', '')); cm = sh.Center()
            m += g; c += g * np.array([cm.x, cm.y, cm.z])
            lo = np.minimum(lo, [bb.xmin, bb.ymin, bb.zmin]); hi = np.maximum(hi, [bb.xmax, bb.ymax, bb.zmax])
        cg = c / m
        out[label] = {'massG': round(m), 'cgMm': [round(v, 1) for v in cg], 'envelopeMm': [round(v, 1) for v in (hi - lo)],
                      'boxMm': [[round(v, 1) for v in lo], [round(v, 1) for v in hi]],
                      'sideTipDeg': round(float(np.degrees(np.arctan2(45.0, cg[2]))), 1)}
    return out


def json_parts():
    return [p['name'] for p in json.loads((OUT / 'parts.json').read_text())['parts']]


def overlap(a, b):
    sa, sb = shape(a), shape(b)
    ba, bb = sa.BoundingBox(), sb.BoundingBox()
    if (ba.xmin > bb.xmax or bb.xmin > ba.xmax or ba.ymin > bb.ymax or bb.ymin > ba.ymax
            or ba.zmin > bb.zmax or bb.zmin > ba.zmax):
        return 0.0
    try:
        return sum(s.Volume() for s in sa.intersect(sb).Solids())
    except Exception as exc:  # noqa: BLE001
        return f'kernel: {exc}'


def collide_job(args):
    name, others, allowed = args
    hits, worst_gap = [], None
    for other in others:
        v = overlap(name, other)
        if isinstance(v, str):
            hits.append({'with': other, 'level': 'unverified', 'message': v})
        elif v > OVERLAP_MM3 and other not in allowed:
            hits.append({'with': other, 'level': 'fail', 'overlapMm3': round(v, 2)})
        elif v > 20.0 and other in allowed:
            hits.append({'with': other, 'level': 'fail', 'overlapMm3': round(v, 2),
                         'message': 'resting/glue contact overlaps more than a touch'})
    return name, hits


def rotate_tris(tris, deg):
    import numpy as np
    out = tris.copy()
    for axis, d in zip(range(3), deg):
        if not d:
            continue
        a = math.radians(d)
        c, s = math.cos(a), math.sin(a)
        i, j = [(1, 2), (2, 0), (0, 1)][axis]
        x, y = out[..., i].copy(), out[..., j].copy()
        out[..., i], out[..., j] = c * x - s * y, s * x + c * y
    return out


def print_job(entry):
    """Printability of one part in its print orientation."""
    import numpy as np
    sys.path.insert(0, '')
    from kicadpy import case_measure as cm
    name = entry['name']
    res = {'part': name, 'items': []}
    s = shape(name)
    solids = s.Solids()
    if not s.isValid():
        res['items'].append({'level': 'fail', 'message': f'{name}: STEP solid is not valid'})
    if name.startswith('coupon'):
        pass
    elif len(solids) != 1:
        res['items'].append({'level': 'fail', 'message': f'{name}: {len(solids)} solids, expected one piece'})
    tris = cm.stl_triangles(OUT / entry['stl'])
    t = rotate_tris(tris, entry.get('printRotateDeg') or [0, 0, 0])
    lo, hi = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    size = hi - lo
    if sorted(size[:2])[1] > BED[1] or sorted(size[:2])[0] > BED[0] or size[2] > BED[2]:
        res['items'].append({'level': 'fail', 'message': f'{name}: {size.round(1).tolist()} does not fit the bed'})
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
    zmin = t[:, :, 2].min(1)
    down = (nz < -math.cos(math.radians(45))) & (zmin > lo[2] + 0.2)
    over = float(area[down].sum())
    res['overhangMm2'] = round(over, 1)
    res['printSizeMm'] = [round(float(v), 1) for v in size]
    if entry.get('imported'):
        res['note'] = 'imported unchanged from cadsmith v5 (its own report passed); overhang recorded, not reworked'
    elif over > OVERHANG_REVIEW_MM2:
        res['items'].append({'level': 'review', 'message': f'{name}: {over:.0f} mm2 faces down past 45 deg in print orientation'})
    ip = ROOT / 'case' / 'interfaces.json'
    skins = (json.loads(ip.read_text()).get('skins') or []) if ip.exists() else []
    w = cm.check_walls(name, OUT / entry['stl'], 0.4, skins)
    res['walls'] = {k: w.get(k) for k in ('level', 'message', 'minMm', 'p05Mm')}
    if w['level'] != 'pass':
        res['items'].append({'level': w['level'], 'message': w['message']})
    return res


def wire_job(args):
    import cadquery as cq
    wire, route, names = args
    d = float(wire.get('clearDiameterMm', 8.5))
    pts = route['pointsMm']
    blocked = {}
    for a, b in zip(pts, pts[1:]):
        va, vb = cq.Vector(*a), cq.Vector(*b)
        tube = cq.Solid.makeCylinder(d / 2, (vb - va).Length, va, vb - va)
        tb = tube.BoundingBox()
        for n in names:
            sb = shape(n).BoundingBox()
            if tb.xmin > sb.xmax or sb.xmin > tb.xmax or tb.ymin > sb.ymax or sb.ymin > tb.ymax or tb.zmin > sb.zmax or sb.zmin > tb.zmax:
                continue
            v = sum(s.Volume() for s in tube.intersect(shape(n)).Solids())
            if v > 0.5:
                blocked[n] = round(blocked.get(n, 0) + v, 1)
    return wire['name'], route['name'], blocked


def main(force=False):
    manifest = json.loads((OUT / 'parts.json').read_text())
    entries = manifest['parts']
    intent_path = ROOT / 'case' / 'interfaces.json'
    intent = json.loads(intent_path.read_text()) if intent_path.exists() else {}
    part_shas = {'parts.json': sha(OUT / 'parts.json')}
    for e in entries:
        for k in ('step', 'stl'):
            part_shas[e[k]] = sha(OUT / e[k])
    blayout = json.loads(B_LAYOUT.read_text()) if B_LAYOUT.exists() else {'wires': []}
    key = hashlib.sha256(json.dumps([part_shas, sha(intent_path) if intent_path.exists() else None,
                                     sha(B_LAYOUT) if B_LAYOUT.exists() else None,
                                     sha(__file__)], sort_keys=True).encode()).hexdigest()
    cached = None
    if not force and CACHE.exists():
        c = json.loads(CACHE.read_text())
        if c.get('key') == key:
            cached = c['result']
    started = time.time()
    if cached is None:
        names = [e['name'] for e in entries if not e['name'].startswith('coupon')]
        new = [e['name'] for e in entries if e.get('printable') is not False and not e['name'].startswith('coupon')]
        devices = [n for n in SEATS]
        jobs = []
        for n in new:
            seated = [d for d, holders in SEATS.items() if n in holders]
            jobs.append((n, [o for o in names if o != n], [GLUED.get(n)] + seated))
        for dname in devices:
            if dname in names:
                jobs.append((dname, [o for o in names if o != dname], SEATS[dname]))
        printable = [e for e in entries if e.get('printable') is not False]
        wires = [(w, r, names) for w in intent.get('wires', []) for r in w.get('routes', [])]
        bwires = [(w, r, [b_name(n) for n in B_MOVE + B_CAR]) for w in blayout.get('wires', []) for r in w.get('routes', [])]
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            col = list(ex.map(collide_job, jobs))
            prn = list(ex.map(print_job, printable))
            wr = list(ex.map(wire_job, wires))
            bcol = list(ex.map(b_collide_job, [n for n in B_MOVE if n in names]))
            bwr = list(ex.map(wire_job, bwires))
            bmass = ex.submit(b_mass_props).result()
        routes, broutes = {}, {}
        for wname, rname, blocked in wr:
            routes.setdefault(wname, {})[rname] = blocked
        for wname, rname, blocked in bwr:
            broutes.setdefault(wname, {})[rname] = blocked
        cached = {'collisions': {n: h for n, h in col}, 'print': prn, 'wires': routes,
                  'bCollisions': {n: h for n, h in bcol}, 'bWires': broutes, 'mass': bmass}
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({'key': key, 'result': cached}))
    items = []
    for n, hits in cached['collisions'].items():
        for h in hits:
            items.append({'check': f'collide:{n}', 'level': h['level'],
                          'message': f"{n} vs {h['with']}: " + (h.get('message') or f"{h.get('overlapMm3')} mm3 overlap")})
        if not hits:
            items.append({'check': f'collide:{n}', 'level': 'pass', 'message': f'{n}: clear of every other body'})
    for p in cached['print']:
        lv = [i['level'] for i in p['items']]
        if not lv:
            items.append({'check': f"print:{p['part']}", 'level': 'pass',
                          'message': f"{p['part']}: one solid, fits the bed, walls ok, {p['overhangMm2']} mm2 overhang" + (f" ({p['note']})" if p.get('note') else '')})
        for i in p['items']:
            items.append({'check': f"print:{p['part']}", **i})
    for w in intent.get('wires', []):
        rs = cached['wires'].get(w['name'], {})
        clear = [r for r, b in rs.items() if not b]
        lvl = 'pass' if len(clear) >= 2 else ('review' if clear else 'fail')
        items.append({'check': f"wire:{w['name']}", 'level': lvl,
                      'message': f"{w['name']}: {len(clear)} open route(s) of {len(rs)} for {w.get('clearDiameterMm', 8.5)} mm "
                                 f"(against every body incl. v1 and bought parts)",
                      'blocked': {r: b for r, b in rs.items() if b}})
    for n, hits in cached.get('bCollisions', {}).items():
        for h in hits:
            items.append({'check': f'layoutB:{n}', 'level': h['level'],
                          'message': f"layout B on the car: {n} vs {h['with']}: " + (h.get('message') or f"{h.get('overlapMm3')} mm3 overlap")})
        if not hits:
            items.append({'check': f'layoutB:{n}', 'level': 'pass', 'message': f'layout B on the car: {n} clear of the printed car, cells, trays and stack'})
    for w in blayout.get('wires', []):
        rs = cached.get('bWires', {}).get(w['name'], {})
        clear = [r for r, b in rs.items() if not b]
        lvl = 'pass' if len(clear) >= 2 else ('review' if clear else 'fail')
        items.append({'check': f"layoutB-wire:{w['name']}", 'level': lvl, 'blocked': {r: b for r, b in rs.items() if b},
                      'message': f"layout B: {w['name']}: {len(clear)} open route(s) of {len(rs)} for {w.get('clearDiameterMm')} mm"})
    levels = {i['level'] for i in items}
    verdict = next((l for l in ('fail', 'unverified', 'review') if l in levels), 'pass')
    errors = [i for i in items if i['level'] == 'fail']
    report = {'schema': 1, 'verdict': verdict, 'passed': verdict in ('pass', 'review'),
              'scope': 'simple stage: glue-on holders, v5 stack (layout B, checked on the car), coupons on printed robot-tank v1; v1 refs printable:false',
              'checks': items, 'errors': [e['message'] for e in errors], 'partShas': part_shas,
              'massAndEnvelope': cached.get('mass'),
              'parts': [e['name'] for e in entries], 'reusedMeasurements': cached is not None and time.time() - started < 1,
              'hardwareTested': False, 'checkedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=1) + '\n')
    for i in items:
        if i['level'] != 'pass':
            print(f"{i['level']:10} {i['message']}")
    print(json.dumps({'verdict': verdict, 'checks': len(items), 'report': str(REPORT.relative_to(ROOT))}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main('--force' in sys.argv))
