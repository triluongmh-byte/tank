#!/usr/bin/env python3
"""Read-only contract/PCB/case reconciliation; reports only inside firmware/."""
import argparse,hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
FIRM=ROOT/'firmware'
SHA='a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sexpr(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text);stack=[];root=[];current=root
 for token in tokens:
  if token=='(':child=[];current.append(child);stack.append(current);current=child
  elif token==')':current=stack.pop()
  else:current.append(json.loads(token) if token.startswith('"') else token)
 if stack:raise ValueError('Unbalanced PCB expression')
 return root[0]
def tagged(node,tag):return [x for x in node if isinstance(x,list) and x and x[0]==tag]
def measure(pcb):
 root=sexpr(pcb.read_text());nets={x[1]:x[2] for x in tagged(root,'net') if len(x)>2};out={}
 for footprint in tagged(root,'footprint'):
  refs=[x[2] for x in tagged(footprint,'property') if x[1]=='Reference']+[x[2] for x in tagged(footprint,'fp_text') if x[1]=='reference']
  if not refs:continue
  ref=refs[0];pads={}
  for pad in tagged(footprint,'pad'):
   padnets=tagged(pad,'net');name='NC'
   if padnets:
    net=padnets[0]
    # KiCad 10 writes (net "name"); earlier versions use (net id "name").
    name=net[2] if len(net)>2 else nets.get(net[1],net[1])
   if pad[1] in pads and pads[pad[1]]!=name:raise ValueError('Inconsistent duplicated pad '+ref+'.'+pad[1])
   pads[pad[1]]=name
  out[ref]=pads
 return out

def compare_board(measured,pins):
 """Check connector nets plus the board's documented, noninverting U1 paths."""
 errors=[];connectors={};paths=[]
 channels=('LF','LM','LR','RF','RM','RR','TURRET')
 buffer_pins=((2,18),(4,16),(6,14),(8,12),(11,9),(13,7),(15,5))
 for pin in pins:
  ref=pin['device'];pad=pin['pin'];want=pin['net']
  if not ref.startswith('J_'):continue
  got=measured.get(ref,{}).get(pad,'MISSING');connectors.setdefault(ref,{})[pad]=got
  if ref=='J_CTRL' and pad=='12' and want=='NC' and got=='STOP_N':continue  # note 8: board assigns local stop here
  if ref=='J_CTRL' and pad=='12' and want=='NC' and got=='unconnected-(J_CTRL-Pin_12-Pad12)':
   # A named unconnected net is NC only if no second pad shares it.
   if sum(n==got for pads in measured.values() for n in pads.values())==1:continue
  if ref=='J_PCA' and pad in tuple(str(i) for i in range(6,13)) and got==want+'_RAW':
   ch=int(pad)-6;input_pin,output_pin=buffer_pins[ch];u=measured.get('U1',{})
   expected='PWM_'+channels[ch]
   ok=(want==expected and u.get(str(input_pin))==got and u.get(str(output_pin))==want
       and measured.get('J_S'+str(ch),{}).get('3')==want
       and u.get('1')==u.get('19')=='PCA_OE_N' and u.get('10')=='GND' and u.get('20')=='SERVO_3V3')
   paths.append({'channel':ch,'inputPin':input_pin,'outputPin':output_pin,'inputNet':got,'outputNet':want,'ok':ok})
   if ok:continue
   errors.append(f'{ref}.{pad}: buffered path through U1 differs')
   continue
  if got!=want:errors.append(f'{ref}.{pad}: PCB {got}, contract {want}')
 # Release notes add an always-powered 5 V fan; no GPIO or servo-enable coupling.
 for pad,want in (('1','LOAD_5V'),('2','GND')):
  got=measured.get('J_FAN',{}).get(pad,'MISSING');connectors.setdefault('J_FAN',{})[pad]=got
  if got!=want:errors.append(f'J_FAN.{pad}: PCB {got}, release notes {want}')
 return errors,connectors,paths

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--require-board',action='store_true');parser.add_argument('--require-case',action='store_true');args=parser.parse_args()
 contract=ROOT/'PILOT_CONTRACT.json';data=json.loads(contract.read_text());pins=data['interfaces']['pins']
 report={'schema':1,'contractSha256':SHA,'contractFileSha256':sha(contract),'hardwareTested':False,'mismatches':[],'board':'pending','case':'pending'}
 if sha(contract)!=SHA:report['mismatches'].append('sealed contract SHA differs')
 definitions=(FIRM/'tank/pins.h').read_text()
 constants={k:int(v) for k,v in re.findall(r'\b([A-Z][A-Z_]+)\s*=\s*(\d+)',definitions)}
 mapping={'I2C_SDA':constants['SDA_PIN'],'I2C_SCL':constants['SCL_PIN'],'PCA_OE_N':constants['OE_PIN'],'ACT_EN':constants['ACT_PIN']}
 arrays={k:[int(x) for x in v.split(',')] for k,v in re.findall(r'(TRIG_PINS|ECHO_PINS)\[2\]=\{([^}]+)\}',definitions)}
 mapping.update({'SONAR_F_TRIG_3V3':arrays['TRIG_PINS'][0],'SONAR_R_TRIG_3V3':arrays['TRIG_PINS'][1],'SONAR_F_ECHO_3V3':arrays['ECHO_PINS'][0],'SONAR_R_ECHO_3V3':arrays['ECHO_PINS'][1]})
 for pin in pins:
  pass  # sealed LILYGO GPIO names no longer bind firmware (release note 8); the board's DevKit map below does.
 pm=ROOT/'engineering/esp32-pinmap.json'
 if pm.exists():
  table=json.loads(pm.read_text());report['mcuPins']='compared with engineering/esp32-pinmap.json';report['pinmapSha256']=sha(pm)
  want={'I2C_SDA':constants['SDA_PIN'],'I2C_SCL':constants['SCL_PIN'],'PCA_OE_N':constants['OE_PIN'],'ACT_EN':constants['ACT_PIN'],'STOP_N':constants['STOP_PIN']}
  want.update({k:v for k,v in mapping.items() if k.startswith('SONAR')})
  seen=set()
  for row in table['carrierHarness']:
   net=row['net']
   if net in want:
    m=re.search(r'GPIO(\d+)',row['esp32']);seen.add(net)
    if not m or int(m[1])!=want[net]:report['mismatches'].append(f"{net}: firmware GPIO{want[net]}, board {row['esp32']}")
  for net in want:
   if net not in seen:report['mismatches'].append('board pin map lacks '+net)
  for sig,gpio in (('SCK',constants['LCD_SCK']),('MOSI',constants['LCD_MOSI']),('CS',constants['LCD_CS']),('DC',constants['LCD_DC']),('RST',constants['LCD_RST']),('BL',constants['LCD_BL'])):
   rows=[r for r in table['displayST7789_1p54_240x240_SPI_direct_wires_not_on_carrier'] if r['signal'].startswith(sig) or sig in r['signal'].split('/')]
   if not rows or not re.search(r'GPIO'+str(gpio)+r'\b',rows[0]['esp32']):report['mismatches'].append('display '+sig+' differs from board map')
 else:
  report['mcuPins']='board pin map absent';report['mismatches'].append('engineering/esp32-pinmap.json missing')
 pcb=ROOT/'design/main.kicad_pcb'
 if pcb.exists():
  measured=measure(pcb);report['board']='checked';report['boardSha256']=sha(pcb)
  errors,connectors,paths=compare_board(measured,pins)
  report['mismatches'].extend(errors);report['measuredConnectors']=connectors;report['bufferedPaths']=paths
  report['boardScope']='electrical connector pad nets only; geometry deviations remain a lead/case integration action'
 elif args.require_board:report['mismatches'].append('native PCB unavailable')
 # The case team may supply this deliberately small, hash-bound interchange file.
 # No firmware limit is silently inferred from an overview or an unchecked geometric box.
 limits=ROOT/'case/firmware-limits.json'
 if limits.exists():
  c=json.loads(limits.read_text());report['case']='checked';report['caseLimitsSha256']=sha(limits)
  lo=c.get('turretYawMinDeg');hi=c.get('turretYawMaxDeg');sources=c.get('checkedFiles',{})
  if c.get('contractSha256')!=SHA or c.get('status')!='passed' or not sources:report['mismatches'].append('case limits lack passed hash-bound contract evidence')
  for path,digest in sources.items():
   source=(ROOT/path).resolve()
   if not source.is_relative_to(ROOT/'case') or not source.is_file() or sha(source)!=digest:report['mismatches'].append('case source hash '+path)
  if not isinstance(lo,(int,float)) or not isinstance(hi,(int,float)) or not -70<=lo<=0<=hi<=70:report['mismatches'].append('case yaw interval invalid')
  header=(FIRM/'tank/mechanical_limits.h').read_text();m=re.search(r'CASE_YAW_MIN=(-?\d+), CASE_YAW_MAX=(-?\d+)',header)
  if not m or lo!=int(m[1]) or hi!=int(m[2]):report['mismatches'].append('firmware yaw limits differ; import reviewed range into mechanical_limits.h')
 elif args.require_case:report['mismatches'].append('checked case limits unavailable')
 report['status']='failed' if report['mismatches'] else 'pending-integration' if 'pending' in (report['board'],report['case']) else 'passed'
 target=FIRM/'reports';target.mkdir(exist_ok=True);(target/'integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['mismatches'])
if __name__=='__main__':sys.exit(main())
