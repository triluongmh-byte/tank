"""Release-note-8 migration (run once): J_CTRL pin12 -> STOP_N local stop button input + 10k pull-up R44."""
import json,pathlib
from kicadpy import author
p=pathlib.Path('design/spec.json');s=json.loads(p.read_text())
if not any(x['ref']=='R44' for x in s['parts']):
 s['parts'].append(dict(ref='R44',value='10k',symbol='R',footprint='Tank:R_0805_2012Metric',at=[589.28,88.9],in_bom=True))
 s['nets']['STOP_N']=[['J_CTRL','12'],['R44','1']]
 s['nets']['LOGIC_3V3'].append(['R44','2'])
 s['rev']='V0.4';p.write_text(json.dumps(s,indent=2))
print(author.write(s,pathlib.Path('design')))
q=pathlib.Path('parts.json');j=json.loads(q.read_text())
if not any('R44' in x['refdes'] for x in j['parts']):
 x=next(x.copy() for x in j['parts'] if 'R5' in x['refdes']);x.update(refdes=['R44'],value='10k');j['parts'].append(x);q.write_text(json.dumps(j,indent=2))
