#!/bin/bash
# usage: quickdrc.sh candidate.kicad_pcb  -> build/board/cand/drc.json + cand/pcb.png (staged with project libraries)
C=build/board/cand;mkdir -p $C;rm -rf $C/Tank.pretty;cp -R design/Tank.pretty design/Tank.3dshapes design/fp-lib-table design/main.kicad_pro $C/ ;cp $1 $C/main.kicad_pcb
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb drc --severity-all --format json -o $C/drc.json $C/main.kicad_pcb >/dev/null 2>&1
python3 - <<'P'
import json,collections
d=json.load(open('build/board/cand/drc.json'));c=collections.Counter(v['type'] for v in d['violations']+d.get('unconnected_items',[]));print(dict(c))
for v in d['violations'][:int(__import__('os').environ.get('N','25'))]:print(v['type'],[ (i['description'][:40],round(i['pos']['x'],1),round(i['pos']['y'],1)) for i in v['items']])
P
