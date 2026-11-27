"""Regenerate engineering/pinout.md from engineering/board-audit.json (run after audit.py). Pure text, instant."""
import json,pathlib
a=json.load(open('engineering/board-audit.json'));L=json.load(open('tools/board/layout.json'))
o=['# Measured carrier pin map (release note 8, 62x60 carrier)','',
'Generated from actual native PCB pad nets by tools/board/pinout-doc.py. Board frame: x right, y down from the front-left corner; case X = x-31, case Y = y-46 (nose is -Y). RAW = module-side PWM copper behind the SN74LVC244A isolation buffer (DEVIATIONS.md item 1). J_CTRL.12 is STOP_N (item 6). ESP32 GPIO assignment: esp32-pinmap.json.','',
'|Connector|Pin|Function net|Actual copper net|X mm|Y mm|','|---|---:|---|---|---:|---:|']
rows=list(a['pins'])+[{'device':'J_FAN','pin':str(i),'net':n,'actualNet':n,'xMm':p['x'],'yMm':p['y']} for i,(n,p) in enumerate(zip(['LOAD_5V','GND'],a['fan']['pins']),1)]
for r in rows:o.append(f"|{r['device']}|{r['pin']}|{'STOP_N' if (r['device'],r['pin'])==('J_CTRL','12') else r['net']}|{r['actualNet']}|{r['xMm']:.3f}|{r['yMm']:.3f}|")
o+=['','Mount holes (3.2 mm, copper keep-out R3.6): '+', '.join(f"{h} ({L[h][0]},{L[h][1]})" for h in ('H1','H2','H3','H4')),'']
pathlib.Path('engineering/pinout.md').write_text('\n'.join(o));print('pinout.md',len(rows),'rows')
