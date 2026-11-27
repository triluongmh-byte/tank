"""Checked turret yaw range for firmware (case/firmware-limits.json), both turret options.

    "$KICAD_CASE_PYTHON" tools/case/turret_limits.py

Sweeps the turret joints declared in case/interfaces.json ('turret' on the v1 lid, layout A, and
'turret_on_stack (layout B)') over the firmware's allowed -70..+70 deg in 5 deg steps against what
each must clear, on the exported STEPs. Writes case/reports/turret_yaw.json and
case/firmware-limits.json deterministically (no timestamps: unchanged inputs give the same bytes and
hashes, so firmware/reconcile.py can bind to them). Parallel over the poses; skips work when the
inputs are unchanged but always rewrites both files.
"""
import hashlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case' / 'out'
REPORT = ROOT / 'case' / 'reports' / 'turret_yaw.json'
LIMITS = ROOT / 'case' / 'firmware-limits.json'
CACHE = ROOT / 'build' / 'case' / 'turret-cache.json'
SHA = 'a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810'
JOINTS = ('turret', 'turret_on_stack (layout B)')
ANGLES = list(range(-70, 71, 5))
MIN_GAP = 0.25


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parts():
    return {p['name']: p for p in json.loads((OUT / 'parts.json').read_text())['parts']}


_S = {}


def shape(name):
    import cadquery as cq
    if name not in _S:
        _S[name] = cq.importers.importStep(str(OUT / parts()[name]['step'])).val()
    return _S[name]


def pose(args):
    import cadquery as cq
    joint, angle = args
    o = cq.Vector(*joint['originMm'])
    loc = cq.Location(o) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(*joint['axis']), angle) * cq.Location(o * -1)
    allowed = {frozenset(p) for p in joint.get('allowContact', [])}
    worst = None
    for m in joint['moves']:
        placed = shape(m).moved(loc)
        for f in joint['clearOf']:
            if frozenset((m, f)) in allowed:
                continue
            d = placed.distance(shape(f))
            if worst is None or d < worst[0]:
                worst = (d, m, f)
    return joint['name'], angle, round(worst[0], 3), worst[1], worst[2]


def main():
    intent_path = ROOT / 'case' / 'interfaces.json'
    intent = json.loads(intent_path.read_text())
    joints = [j for j in intent['joints'] if j['name'] in JOINTS]
    used = sorted({n for j in joints for n in j['moves'] + j['clearOf']})
    p = parts()
    inputs = {f"case/out/{p[n]['step']}": sha(OUT / p[n]['step']) for n in used}
    key = hashlib.sha256(json.dumps([inputs, joints, ANGLES, sha(__file__)], sort_keys=True).encode()).hexdigest()
    res = None
    if CACHE.exists():
        c = json.loads(CACHE.read_text())
        res = c['res'] if c.get('key') == key else None
    if res is None:
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            res = list(ex.map(pose, [(j, a) for j in joints for a in ANGLES]))
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({'key': key, 'res': res}))
    per = {}
    for name, a, gap, m, f in res:
        per.setdefault(name, []).append({'deg': a, 'gapMm': gap, 'closest': [m, f]})
    ok = {}
    for name, rows in per.items():
        clear = {r['deg'] for r in rows if r['gapMm'] >= MIN_GAP}
        lo = hi = 0
        while lo - 5 in clear:          # contiguous clear range through 0
            lo -= 5
        while hi + 5 in clear:
            hi += 5
        ok[name] = [lo, hi] if 0 in clear else [0, 0]
    lo = max(v[0] for v in ok.values())
    hi = min(v[1] for v in ok.values())
    passed = len(per) == len(JOINTS) and lo <= 0 <= hi and 0 in [r['deg'] for r in per[JOINTS[0]]]
    report = {'schema': 1, 'verdict': 'pass' if passed else 'fail', 'passed': passed,
              'contractSha256': SHA, 'minClearanceMm': MIN_GAP, 'stepDeg': 5,
              'scope': 'turret head + horn + 2 sonars swept about the SG90 axis on the v1 lid (option a) and on the '
                       'v5 stack cap (option b); solids only. The sonar/servo harness needs a slack loop for this range '
                       '(layout_b.json routes); wire wrap-up is not simulated.',
              'clearRangeDeg': ok, 'publishedRangeDeg': [lo, hi], 'inputs': inputs, 'poses': per}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    limits = {'contractSha256': SHA, 'status': 'passed' if passed else 'failed',
              'turretYawMinDeg': lo, 'turretYawMaxDeg': hi,
              'convention': 'yaw about +Z of the contract frame through the turret SG90 axis; 0 = sonar F looking -Y (nose); '
                            'same range for option (a) lid and option (b) stack',
              'checkedFiles': {'case/reports/turret_yaw.json': sha(REPORT), 'case/interfaces.json': sha(intent_path)}}
    LIMITS.write_text(json.dumps(limits, indent=1, sort_keys=True) + '\n')
    print(json.dumps({'verdict': report['verdict'], 'range': [lo, hi], 'clear': ok}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
