"""Cached external pack sizing/coordination, never a hardware qualification claim."""
import concurrent.futures, hashlib, json, os, pathlib

ROOT = pathlib.Path('.')
OUT = ROOT / 'engineering/pack-protection-calculations.json'
INPUTS = [pathlib.Path(__file__), ROOT / 'engineering/pack-protection-spec.json',
          ROOT / 'engineering/power-calculations.json', ROOT / 'parts.json', ROOT / 'product.json']
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
    hashes = list(pool.map(lambda p: hashlib.sha256(p.read_bytes()).hexdigest(), INPUTS))
key = hashlib.sha256('\n'.join(hashes).encode()).hexdigest()
if OUT.exists() and json.loads(OUT.read_text()).get('inputSha256') == key:
    print('Pack coordination inputs unchanged; reusing sizing report.')
    raise SystemExit()
s = json.loads(INPUTS[1].read_text())
power = json.loads(INPUTS[2].read_text())
parts = json.loads(INPUTS[3].read_text())
product = json.loads(INPUTS[4].read_text())
f, h, b, w, p = (s[k] for k in ['fuse', 'holder', 'runBreaker', 'wiring', 'pack'])
peak = product['power'].get('referenceChain',product['power'])['packPeakEstimateA']
area = w['minAreaMm2'] * 1e-6
wire_r = w['copperResistivityOhmM20C'] * w['maxRoundTripM'] / area
heat_factor = w['copperResistivityOhmM20C'] / (w['copperDensityKgM3'] * w['copperHeatCapacityJkgK'] * area**2)
points = f['openingPoints']

def interval(i):
    point = points[i]
    low = point['multiple'] * f['ratedA']
    high = min(points[i + 1]['multiple'] * f['ratedA'], p['prospectiveFaultMaxARequired']) if i + 1 < len(points) else p['prospectiveFaultMaxARequired']
    t = point['maxSeconds']
    return {'fromA': low, 'toA': high, 'upperTimeS': t,
            'rectangularI2tA2s': high**2*t,
            'adiabaticCopperRiseEstimateC': high**2*t*heat_factor if t <= 5 else None,
            'qualificationRequired': 'Pack maker must substantiate safe assembly withstand or earlier safe opening; not measured.'}

with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
    rows = list(pool.map(interval, range(len(points))))
by_id = {part['id']: part for part in parts['externalParts']}
assert all(by_id[x['id']]['mpn'] == x['mpn'] for x in [f, h, b])
assert max(x['totalPackA'] for x in power['batteryBudget']) < peak < b['qualifiedTripMinA']
assert b['qualifiedTripMaxA'] < p['assemblyContinuousA'] <= f['ratedA']
assert f['ratedA'] <= h['ratedA'] <= w['qualifiedContinuousA']
assert p['cellAndInterconnectContinuousARequired'] >= 2*f['ratedA']
assert p['maxV'] < min(f['ratedVDC'], h['ratedVDC'])
assert p['prospectiveFaultMaxARequired'] < f['interruptA']
assert b['maxProgrammedBlankingSeconds'] == 0
assert all(r['adiabaticCopperRiseEstimateC'] < 10 for r in rows if r['upperTimeS'] <= 5)
drop = peak * (wire_r + w['maxFuseHolderPlusContactsOhmRequired'] + b['qualifiedOnResistanceMaxOhm'] + .020)
result = {'inputSha256': key, 'specificationArithmeticPass': True, 'hardwareTested': False,
          'qualificationStatus': 'REQUIRED: unknown owned pack, modified modules, fault/thermal/threshold acceptance remain unverified',
          'boostInputPeakEstimateA': max(x['totalPackA'] for x in power['batteryBudget']),
          'packPeakBudgetA': peak, 'runTripNominalA': 1460/b['r9Ohm']+.11,
          'runTripQualifiedRangeA': [b['qualifiedTripMinA'], b['qualifiedTripMaxA']],
          'runUVLONominalV': {'rising': 1.2*(1+b['r1Ohm']/b['r2Ohm']), 'falling': 1.1*(1+b['r1Ohm']/b['r2Ohm'])},
          'fuseBackupEnvelope': rows, 'maxShortPulseCopperRiseEstimateC': max(r['adiabaticCopperRiseEstimateC'] or 0 for r in rows),
          'wireResistance20COhm': wire_r, 'peakPackToBoostDropEstimateV': drop,
          'packVNeededFor3V3BoostAtPeakEstimate': 3.3+drop,
          'fuseColdLossTypicalW': peak**2*f['coldResistanceOhmTypical'],
          'holderFuseContactsLossAtAcceptanceLimitW': peak**2*w['maxFuseHolderPlusContactsOhmRequired'],
          'runBreakerLossAtAcceptanceLimitW': peak**2*b['qualifiedOnResistanceMaxOhm'],
          'limitations': 'Copper estimate excludes contacts/cells and cooling. No interpolation of fuse typical curve or use of typical pre-arcing I2t as guaranteed total clearing. No selective-trip or safety certification claimed.'}
OUT.write_text(json.dumps(result, indent=2)+'\n')
print({k: result[k] for k in ['specificationArithmeticPass', 'hardwareTested', 'runTripNominalA', 'peakPackToBoostDropEstimateV', 'maxShortPulseCopperRiseEstimateC']})
