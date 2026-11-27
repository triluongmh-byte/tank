#!/usr/bin/env python3
"""Regenerate build/firmware/esp32/build-proof.json and firmware/reports/validation.json from current files.
Run after `python3 firmware/build.py` and `python3 firmware/check.py` have passed."""
import datetime,hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
tank=sorted(p for p in (ROOT/'firmware/tank').iterdir() if p.is_file())
binary=ROOT/'build/firmware/esp32/tank.ino.bin'
evidence=json.loads((ROOT/'build/firmware/esp32/build-evidence.json').read_text())
srcs={str(p.relative_to(ROOT)):sha(p) for p in tank}
fp=hashlib.sha256()
for p in tank:fp.update(p.name.encode());fp.update(p.read_bytes())
if evidence.get('inputSha256') is None or sha(binary)!=evidence['binarySha256']:sys.exit('binary does not match build-evidence; run build.py')
(ROOT/'build/firmware/esp32/build-proof.json').write_text(json.dumps({'binary':sha(binary),'sources':srcs,'fqbn':json.loads((ROOT/'firmware/flash.json').read_text())['fqbn']},indent=1)+'\n')
rep=json.loads((ROOT/'firmware/reports/integration.json').read_text())
if rep.get('status')!='passed':sys.exit('integration report not passed; run reconcile.py')
suites={}
for n in ('core','guard','pet','scan'):
    f=ROOT/f'build/firmware/tests/{n}_test'
    if not (ROOT/f'build/firmware/tests/{n}_test.passed').exists():sys.exit('suite not passed: '+n)
    suites[n]={'status':'passed','executableSha256':sha(f),'inputSha256':(ROOT/f'build/firmware/tests/{n}_test.passed').read_text(),'sanitizers':['address','undefined']}
out={'schema':1,'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'contractSha256':rep['contractSha256'],'stage':'firmware','status':'local-checks-passed','hardwareTested':False,
 'releaseNotes':'1,2,8 (chain tip 26b0ea5e…)','target':'esp32:esp32:esp32 core 2.0.14','binarySha256':sha(binary),'pinsHSha256':srcs['firmware/tank/pins.h'],'mechanicalLimitsHSha256':srcs['firmware/tank/mechanical_limits.h'],
 'cppSuites':suites,'integrationReportSha256':sha(ROOT/'firmware/reports/integration.json'),'integrationStatus':rep['status'],'board':rep['board'],'case':rep['case'],
 'caseYawDeg':[-70,70],'note':'Host mocks only; no device, flash or physical test.'}
(ROOT/'firmware/reports/validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('published proofs')
