"""Compare the v5 chassis/hull/lid STEPs with the printed v1 ones (note 9: hashes differ).

    "$KICAD_CASE_PYTHON" tools/case/v5_compare.py
Writes case/reports/v5_compare.json every run (cached on the STEP hashes). The printed v1 is the
reference; any volume difference is listed with its bounding box. Parallel over the 3 parts.
"""
import hashlib, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'case/reports/v5_compare.json'
CACHE = ROOT / 'build/case/v5_compare-cache.json'
PARTS = ['chassis', 'hull', 'lid']
TOL_MM3 = 1.0


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def job(name):
    import cadquery as cq
    a = cq.importers.importStep(str(ROOT / f'case/ref/v1/{name}.step')).val()
    b = cq.importers.importStep(str(ROOT / f'case/ref/v5/{name}.step')).val()
    out = {'part': name, 'v1VolumeMm3': round(a.Volume(), 1), 'v5VolumeMm3': round(b.Volume(), 1), 'diffs': []}
    for label, d in (('only in v5', b.cut(a)), ('only in v1', a.cut(b))):
        for s in d.Solids():
            if s.Volume() > TOL_MM3:
                bb = s.BoundingBox()
                out['diffs'].append({'where': label, 'volumeMm3': round(s.Volume(), 2),
                                     'bboxV1Frame': [round(v, 1) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)]})
    return out


def main():
    key = hashlib.sha256(json.dumps([sha(ROOT / f'case/ref/{v}/{p}.step') for v in ('v1', 'v5') for p in PARTS] + [sha(__file__)]).encode()).hexdigest()
    res = None
    if CACHE.exists():
        c = json.loads(CACHE.read_text())
        res = c['res'] if c.get('key') == key else None
    if res is None:
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            res = list(ex.map(job, PARTS))
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps({'key': key, 'res': res}))
    same = all(not r['diffs'] for r in res)
    rep = {'schema': 1, 'verdict': 'pass' if same else 'review', 'passed': True,
           'message': 'v5 chassis/hull/lid geometry equals printed v1' if same else
                      'v5 differs from printed v1; printed v1 stays the reference (see diffs)',
           'reference': 'printed v1 (case/ref/v1)', 'parts': res,
           'checkedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, indent=1) + '\n')
    print(json.dumps({'verdict': rep['verdict'], 'diffs': {r['part']: len(r['diffs']) for r in res}}))


if __name__ == '__main__':
    main()
