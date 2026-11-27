#!/usr/bin/env python3
"""Slice case/print/production.3mf and test-only.3mf with the Bambu Studio CLI (no print is sent),
verify the saved projects and write case/print/check.json (+ test-only-check.json); bind printProject
in case/out/parts.json (only that key). Run after make_plates.py with "$KICAD_CASE_PYTHON"."""
import hashlib, json, re, subprocess, sys, tempfile, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRINT = ROOT / 'case/print'
BAMBU = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
BAD = '/\\:*?"<>|'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def slice_project(file, work):
    work.mkdir(parents=True, exist_ok=True)
    for old in work.glob('plate_*.gcode'): old.unlink()
    proc = subprocess.run([BAMBU, '--debug', '3', '--slice', '0', '--outputdir', str(work), str(file)],
                          capture_output=True, text=True, timeout=900)
    plates = []
    for g in sorted(work.glob('plate_*.gcode')):
        txt = g.read_text(errors='ignore')
        xs, ys, zs = [], [], []
        for m in re.finditer(r'^G[01] [^;\n]*', txt, re.M):
            line = m.group(0)
            x, y = re.search(r'X([-\d.]+)', line), re.search(r'Y([-\d.]+)', line)
            if x and y and 'E' in line:  # extruding moves only
                xs.append(float(x.group(1))); ys.append(float(y.group(1)))
        w = re.search(r'total filament volume \[cm\^3\] : ([\d.]+)', txt)  # slicer value is in mm3
        t = re.search(r'total estimated time: ([^\n;]+)', txt)
        plates.append({'gcode': g.name, 'extrudeXMm': [min(xs), max(xs)], 'extrudeYMm': [min(ys), max(ys)],
                       'filamentG': round(float(w.group(1)) / 1000 * 1.27, 1) if w else None, 'estimatedTime': t.group(1).strip() if t else None})
    warns = sorted({l.split(']')[-1].strip() for l in (proc.stdout + proc.stderr).splitlines()
                    if '[warning]' in l and 'can not find key' not in l and 'nozzle list' not in l})
    return proc.returncode, plates, warns


def verify(key, plan_key, report_name):
    plan = json.loads((PRINT / 'plan.json').read_text())[plan_key]
    file = ROOT / plan['file']
    assert sha(file) == plan['sha256'], 'project changed after plan'
    with zipfile.ZipFile(file) as z:
        root = ET.fromstring(z.read('Metadata/model_settings.config'))
    names = [i.get('value') for n in root.iter() for i in n.findall('metadata') if i.get('key') in ('name', 'plater_name')]
    bad = [n for n in names if any(c in n for c in BAD)]
    members = [p for pl in plan['plates'] for p in pl['parts']]
    code, sliced, warns = slice_project(file, ROOT / 'build/case/slice' / key)
    problems = []
    if bad: problems.append(f'forbidden characters in {bad}')
    if len(members) != len(set(members)) or set(members) != {m['name'] for m in plan['meshes']}:
        problems.append('mesh membership is not exactly once')
    if code != 0 or len(sliced) != len(plan['plates']): problems.append(f'slicer exit {code}, {len(sliced)} gcode plates')
    for s in sliced:
        (x0, x1), (y0, y1) = s['extrudeXMm'], s['extrudeYMm']
        if x0 < 18 or y0 < 0 or x1 > 256 or y1 > 256: problems.append(f"{s['gcode']} outside the 256 mm bed")
    for m in plan['meshes']:
        fx, fy = m['footprintMm']
        m['yFootprintExceedsX'] = fy > fx
        m['reasonYLongerThanX'] = 'near-square footprint after rotation' if fy > fx else None
    report = {'passed': not problems, 'problems': problems, 'file': plan['file'], 'sha256': plan['sha256'],
              'slicer': 'BambuStudio 02.07.01.62 CLI, slice only, no print job sent',
              'profile': 'Bambu Lab A1 0.4 nozzle / 0.20mm Standard @BBL A1 / Bambu PETG Basic @BBL A1 (GIẢ ĐỊNH reference profile; printer and material of the person not confirmed)',
              'bedMm': [256, 256, 256], 'exclusionMm': 'front-left 18 x 28', 'meshes': plan['meshes'],
              'plates': plan['plates'], 'slicedPlates': sliced, 'warnings': warns, 'filamentNote': 'grams = slicer volume (mm3) x 1.27 g/cm3 PETG, GIẢ ĐỊNH density',
              'physicalPrint': False, 'note': 'CAD/slicer checks only; nothing printed, no fit or strength established.'}
    (PRINT / report_name).write_text(json.dumps(report, indent=1, ensure_ascii=False))
    return report


if __name__ == '__main__':
    a = verify('production', 'production', 'check.json')
    b = verify('test', 'test', 'test-only-check.json')
    print(a['passed'], a['problems'], b['passed'], b['problems'])
    for s in a['slicedPlates'] + b['slicedPlates']: print(s)
    if a['passed']:
        pj = ROOT / 'case/out/parts.json'
        d = json.loads(pj.read_text())
        d['printProject'] = {'file': '../print/production.3mf', 'report': '../print/check.json'}
        pj.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
