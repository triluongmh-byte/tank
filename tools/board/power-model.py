"""Fast cached desk power/loop model; explicitly not a switching simulation or hardware validation."""
import cmath,concurrent.futures,hashlib,itertools,json,math,os,pathlib
out=pathlib.Path('engineering/power-calculations.json');key=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
if out.exists() and json.loads(out.read_text()).get('inputSha256')==key:print('power model cached');raise SystemExit()
vout=1+(59000+49.9)/14300
carrier=7*.8+.30+.030+.030
# Allow 50mV between boost terminals and J_PWR incl output breaker and wiring.
pout=(vout*carrier)+.05*carrier
eta=.8;logic=2.5/eta
budget=[dict(boostVinV=v,loadBoostInputA=pout/(v*eta),logicBoostInputA=logic/v,totalPackA=(pout/eta+logic)/v) for v in [3.3,3.7,4.2]]
def model(args):
 vin,current,cap,esr=args;load=vout/current;d=1-vin/vout;l=3.3e-6;rc=18000;cc=47e-9;cp=2.2e-9;gm=.00018;kc=20
 rhpz=load*(1-d)**2/(2*math.pi*l)
 def loop(f):
  s=2j*math.pi*f
  plant=kc*load*(1-d)/2*(1+s*cap*esr)*(1-s/(2*math.pi*rhpz))/(1+s*load*cap/2)
  z=1/(1/(rc+1/(s*cc))+s*cp)
  return plant*gm*z/vout
 # 80 points/decade is sufficient for this initial analytical sizing check.
 freqs=[10**(x/80) for x in range(80,441)];last=loop(freqs[0]);cross=None
 for a,b in zip(freqs,freqs[1:]):
  la,lb=loop(a),loop(b)
  if abs(la)>=1 and abs(lb)<1:
   cross=math.sqrt(a*b);break
 if cross is None:return {'pass':False,'args':args,'reason':'no unity crossing'}
 pm=180+math.degrees(cmath.phase(loop(cross)))
 return dict(vinV=vin,currentA=current,capF=cap,esrOhm=esr,crossoverHz=cross,phaseMarginDeg=pm,rhpZeroHz=rhpz,**{'pass':pm>=45 and cross<min(285000/10,rhpz/5)})
cases=list(itertools.product([3.3,3.7,4.2],[.5,1,3,6],[.0013,.0019,.0025],[.005,.02,.05]))
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:rows=list(pool.map(model,cases))
r=dict(inputSha256=key,model='TI TPS61287 equations 11-18, ideal averaged CCM plant, ideal gm and nominal L; no parasitic/digital/switching or fault model',hardwareTested=False,sourceVoltageV=vout,carrierPeakA=carrier,fanAllocationA=.3,logicUSBPeakA=.5,sourceOutputIncludingWiresW=pout,batteryBudget=budget,loopCases=rows,minPhaseMarginDeg=min(x['phaseMarginDeg'] for x in rows),maxCrossoverHz=max(x['crossoverHz'] for x in rows),**{'pass':all(x['pass'] for x in rows) and max(x['totalPackA'] for x in budget)<15})
out.write_text(json.dumps(r,indent=2));print({k:r[k] for k in ['sourceVoltageV','carrierPeakA','batteryBudget','minPhaseMarginDeg','maxCrossoverHz','pass']})
if not r['pass']:raise SystemExit(1)
