#!/usr/bin/env python3
"""Arrange the case's printable parts on native Bambu plates and write case/print/*.3mf + check.json.

Run with "$KICAD_CASE_PYTHON". Reads case/out/parts.json (read-only) and the exported STL files.
Plates: all parts are new (nothing of this set is recorded as printed), PETG, A1 256x256 reference bed.
Rotation: printRotateDeg (x,y,z in order) then a Z-only turn so the longest footprint runs along X.
"""
import hashlib, json, math, sys, zipfile
from pathlib import Path
import numpy as np
from kicadpy import case_measure as cm

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'case/out'
PRINT = ROOT / 'case/print'
BED, MARGIN, GAP = 256.0, 8.0, 6.0
X0, Y0 = 26.0, 34.0  # keep clear of the A1 front-left exclusion (18 x 28 mm)

PROD = {  # plate name -> parts (names <= 40 chars, no / \ : * ? " < > |)
    'MỚI-SỬA — CẦN IN — Gá A — khay, quạt': ['cell_cradle', 'power_tray_a', 'power_tray_b', 'fan_plate'],
    'MỚI-SỬA — CẦN IN — Gá A — cột, kẹp': ['esp32_post_rear', 'esp32_post_front', 'pca_post_rear_left',
        'pca_post_rear_right', 'pca_post_front_left', 'pca_post_front_right', 'screen_clip_left', 'screen_clip_right'],
    'MỚI-SỬA — CẦN IN — Stack B — tầng': ['stack_bridge_plate', 'stack_tier_1', 'stack_tier_2'],
    'MỚI-SỬA — CẦN IN — Stack B — deck mạch': ['stack_carrier_deck'],
    'MỚI-SỬA — CẦN IN — Nguồn B — giá, kẹp': ['conv_holder_a', 'conv_holder_b', 'fuse_holder_pack',
        'protector_holder', 'fuse_clip_b', 'logic_holder'],
    'MỚI-SỬA — CẦN IN — Stack B — nắp, chân': ['stack_turret_mount', 'stack_leg_rear_left', 'stack_leg_rear_right',
        'stack_leg_front_left', 'stack_leg_front_right'],
}
TEST = {'TEST ONLY — thử khớp A, stack, deck, nguồn, logic': ['coupon_fit_TEST_ONLY', 'coupon_stack_TEST_ONLY', 'coupon_deck_TEST_ONLY', 'coupon_power_TEST_ONLY', 'coupon_logic_TEST_ONLY']}


def rot(deg):
    m = np.eye(3)
    for axis, d in enumerate(deg):
        a = math.radians(d); c, s = math.cos(a), math.sin(a)
        i, j = [(1, 2), (2, 0), (0, 1)][axis]
        r = np.eye(3); r[i, i] = c; r[i, j] = -s; r[j, i] = s; r[j, j] = c
        m = r @ m
    return m


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name, entry):
    tris = cm.stl_triangles(OUT / entry['stl']).reshape(-1, 3)
    R = rot(entry.get('printRotateDeg') or [0, 0, 0])
    p = tris @ R.T
    sz = p.max(0) - p.min(0)
    if sz[1] > sz[0]:
        R = rot([0, 0, 90]) @ R
        p = tris @ R.T
        sz = p.max(0) - p.min(0)
    return tris, R, p.min(0), sz


def layout(names, entries):
    items, x, y, rowh = [], X0, Y0, 0.0
    for n in sorted(names, key=lambda n: -load(n, entries[n])[3][1]):
        tris, R, lo, sz = load(n, entries[n])
        if x + sz[0] > BED - MARGIN:
            x, y, rowh = X0, y + rowh + GAP, 0.0
        if x + sz[0] > BED - MARGIN or y + sz[1] > BED - MARGIN:
            raise SystemExit(f'{n} does not fit the plate')
        items.append((n, tris, R, lo, sz, (x, y)))
        x += sz[0] + GAP; rowh = max(rowh, sz[1])
    return items


def write(path, plates, entries, title):
    objs, build, plate_xml, oid = [], [], [], 0
    cols = math.ceil(math.sqrt(len(plates)))
    meshes = []
    for pi, (pname, names) in enumerate(plates.items(), 1):
        ox, oy = ((pi - 1) % cols) * BED * 1.2, -((pi - 1) // cols) * BED * 1.2
        inst = []
        for n, tris, R, lo, sz, (x, y) in layout(names, entries):
            oid += 1
            uniq, inv = np.unique(np.round(tris, 5), axis=0, return_inverse=True)
            faces = inv.reshape(-1, 3)
            v = ''.join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in uniq)
            f = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces)
            objs.append(f'<object id="{oid}" name="{n}" type="model"><mesh><vertices>{v}</vertices><triangles>{f}</triangles></mesh></object>')
            pm = (uniq @ R.T).min(0)
            t = np.array([ox + x, oy + y, 0.0]) - pm
            tf = ' '.join(f'{v:.6f}' for v in [*R.T.flatten(), *t])
            build.append(f'<item objectid="{oid}" transform="{tf}" printable="1"/>')
            inst.append((oid, n))
            meshes.append({'name': entries[n]['stl'], 'plate': pi, 'footprintMm': [round(sz[0], 1), round(sz[1], 1)],
                           'heightMm': round(float(sz[2]), 1), 'canonicalSTLSha256': sha(OUT / entries[n]['stl']),
                           'printRotateDeg': entries[n].get('printRotateDeg') or [0, 0, 0]})
        plate_xml.append((pi, pname, inst))
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<metadata name="Application">BambuStudio-02.07.01.62</metadata><metadata name="BambuStudio:3mfVersion">1</metadata><metadata name="Title">{title}</metadata><resources>{"".join(objs)}</resources><build>{"".join(build)}</build></model>')
    cfg = ['<?xml version="1.0" encoding="UTF-8"?><config>']
    for i, n in [(i, n) for _, _, ins in plate_xml for i, n in ins]:
        cfg.append(f'<object id="{i}"><metadata key="name" value="{n}"/></object>')
    for pi, pname, ins in plate_xml:
        cfg.append(f'<plate><metadata key="plater_id" value="{pi}"/><metadata key="plater_name" value="{pname}"/>'
                   '<metadata key="locked" value="false"/>')
        for i, _ in ins:
            cfg.append(f'<model_instance><metadata key="object_id" value="{i}"/><metadata key="instance_id" value="0"/></model_instance>')
        cfg.append('</plate>')
    cfg.append('</config>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', model); z.writestr('Metadata/project_settings.config', (Path(__file__).parent / 'profile/project_settings.config').read_text()); z.writestr('Metadata/model_settings.config', '\n'.join(cfg))
    return meshes, [{'index': pi, 'name': pn, 'filament': 'PETG', 'parts': [entries[n]['stl'] for _, n in ins]} for pi, pn, ins in plate_xml]


def main():
    parts = {p['name']: p for p in json.loads((OUT / 'parts.json').read_text())['parts']}
    printable = {n for n, p in parts.items() if p.get('printable', True) is not False and p['role'] != 'coupon'}
    planned = {n for ns in PROD.values() for n in ns}
    if planned != printable:
        raise SystemExit(f'plan differs from manifest: missing {printable-planned}, extra {planned-printable}')
    PRINT.mkdir(exist_ok=True)
    res = {}
    for key, plan, file in (('production', PROD, 'production.3mf'), ('test', TEST, 'test-only.3mf')):
        meshes, plates = write(PRINT / file, plan, parts, 'Pet Tank ' + key)
        res[key] = {'file': f'case/print/{file}', 'sha256': sha(PRINT / file), 'meshes': meshes, 'plates': plates}
    (PRINT / 'plan.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print({k: [(p['index'], p['name'], len(p['parts'])) for p in v['plates']] for k, v in res.items()})


if __name__ == '__main__':
    main()
