"""Bounding boxes of every v1 STEP (v1 frame: +X nose, +Y left, Z up, ground z=0)."""
import json, sys, glob, os
from concurrent.futures import ProcessPoolExecutor
import cadquery as cq
def bb(p):
    s = cq.importers.importStep(p).val(); b = s.BoundingBox()
    return os.path.basename(p)[:-5], [round(v,2) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)], len(s.Solids())
if __name__ == '__main__':
    files = sorted(glob.glob('case/ref/v1/*.step'))
    with ProcessPoolExecutor() as ex:
        res = list(ex.map(bb, files))
    json.dump({n: {'bbV1': b, 'solids': k} for n,b,k in res}, open('build/case/v1_bboxes.json','w'), indent=1)
    for n,b,k in res: print(f'{n:28s} x[{b[0]},{b[1]}] y[{b[2]},{b[3]}] z[{b[4]},{b[5]}] solids={k}')
