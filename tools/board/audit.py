"""Audit actual native pads, external contract and decoupling; cached by source hash."""
import json,pathlib,hashlib,math,concurrent.futures,os
from kicadpy import toolchain
R=pathlib.Path('.'); O=R/'engineering'; files=[R/'PILOT_CONTRACT.json',R/'design/main.kicad_pcb',R/'design/main.kicad_sch',R/'parts.json',pathlib.Path(__file__)]
fingerprint=hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest();path=O/'board-audit.json'
if path.exists() and json.loads(path.read_text()).get('inputSha256')==fingerprint:print('audit cached');raise SystemExit(0)
pads=toolchain.worker('pads',R/'design/main.kicad_pcb')['footprints'];by={f['ref']:f for f in pads};lookup={(f['ref'],p['number']):p for f in pads for p in f['pads']}
contract=json.load(open('PILOT_CONTRACT.json')); failures=[];rows=[]
for c in contract['interfaces']['pins']:
 if c['device'] not in by:continue
 p=lookup[(c['device'],c['pin'])];expect=c['net']
 if (c['device'],c['pin'])==('J_CTRL','12'):expect='STOP_N' # release note 8: local stop button input (DEVIATIONS.md item 6)
 if expect=='NC':ok=p['net'].startswith('unconnected-')
 else:ok=p['net']==expect or (c['device']=='J_PCA' and expect.startswith('PWM_') and p['net']==expect+'_RAW')
 if not ok:failures.append(f"{c['device']}.{c['pin']} expected {expect}, found {p['net']}")
 rows.append({**c,'actualNet':p['net'],'xMm':p['x'],'yMm':p['y'],'ok':ok})
for pin,expected in [('1','LOAD_5V'),('2','GND')]:
 actual=lookup.get(('J_FAN',pin),{}).get('net')
 if actual!=expected:failures.append(f'J_FAN.{pin} expected {expected}, found {actual}')
values={'1000u':1000,'10u':10,'1u':1,'100n':.1};totals={};caps=[]
for f in pads:
 if f['ref'].startswith('C'):
  pp=f['pads'];ns={q['net'] for q in pp}
  if 'GND' in ns:
   rail=next(q['net'] for q in pp if q['net']!='GND');u=values[f['value']];totals[rail]=totals.get(rail,0)+u
   caps.extend([(rail,f['ref'],q) for q in pp if q['net']==rail])
pins={'U1':['20'],'U2':['2','3'],'U3':['5'],'U4':['5'],'U5':['5'],'U6':['5']}
def nearest(entry):
 ref,pin=entry;p=lookup[(ref,pin)];d,cap=min((math.hypot(p['x']-q['x'],p['y']-q['y']),c) for n,c,q in caps if n==p['net'])
 return {'ref':ref,'pin':pin,'net':p['net'],'nearestCap':cap,'distanceMm':round(d,3),'ok':d<=3}
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex: distances=list(ex.map(nearest,[(r,n) for r,ns in pins.items() for n in ns]))
failures += [f"decoupling {x['ref']}.{x['pin']} {x['distanceMm']}mm" for x in distances if not x['ok']]
# Audit channel connectivity through the actual buffer pins; outputs keep contract names.
channels=[]
for i,(name,ip,op) in enumerate(zip(['LF','LM','LR','RF','RM','RR','TURRET'],[2,4,6,8,11,13,15],[18,16,14,12,9,7,5])):
 a=lookup[('U1',str(ip))]['net'];b=lookup[('U1',str(op))]['net'];ok=a=='PWM_'+name+'_RAW' and b=='PWM_'+name
 channels.append({'pcaChannel':i,'inputPin':ip,'outputPin':op,'inputNet':a,'outputNet':b,'servoRef':'J_S'+str(i),'ok':ok})
 if not ok:failures.append(f'channel {i}')
result={'schema':1,'inputSha256':fingerprint,'pcbSha256':hashlib.sha256(files[1].read_bytes()).hexdigest(),'contractSha256':'a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810','fan':{'pins':[lookup[('J_FAN',pin)] for pin in ['1','2']],'maxAllocatedA':.3,'controlGPIO':None},'pins':rows,'servoChannels':channels,'capacitanceUF':totals,'decoupling':distances,'hardwareTested':False,'failures':failures,'pass':not failures}
path.write_text(json.dumps(result,ensure_ascii=False,indent=2));(O/'native-pads.json').write_text(json.dumps(pads,indent=2));print(json.dumps({k:result[k] for k in ['pass','capacitanceUF','decoupling','failures']}))
if failures:raise SystemExit(1)
