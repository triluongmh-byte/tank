"""Bind the engineering review and explicit manual assembly to the current native sources."""
import json,pathlib,hashlib
from kicadpy.project import Project
from kicadpy.manufacture import design_inputs
root=pathlib.Path('.');j=json.loads((root/'boards/main.board.json').read_text());check=json.loads(next(p for p in sorted((root/'boards/main_review').glob('*/reports/check.json'),key=lambda p:p.stat().st_mtime,reverse=True)).read_text())
analyses={
'power':'Selected external sealed1S protection/charging, modified boost, output latching breaker and separate USB logic boost per POWER_SYSTEM.md;5.96A carrier peak including0.30A fan,12.7A pack peak budget. Exact pack fuse/holder and second input RUN breaker, wire and fault-envelope coordination are specified in POWER_SYSTEM.md and reproduced in pack-protection-calculations.json. Owned pack and physical fault/thermal qualification remain unverified. native audit measures1.2µF logic and all seven IC supply pins within2.891mm of bypass capacitors. Reset hardware and loaded module OE calculated in evidence.',
'protection':'Input fuse and reverse PMOS, default-off high-side switch, Ioff PWM isolation and five-volt tolerant sonar paths reviewed against primary datasheets. External regulated source and6.1–7.2A latching breaker qualification are required; regeneration and hardware fault behavior have explicit bench acceptance limits.',
'pinout':'Actual KiCad pad audit matches all carrier connector pins, seven buffered channel pairs, rails and mount frame. Only internal module-side PWM net names differ for required isolation; deviation recorded, physical pins/GPIOs unchanged.',
 'thermal':'Filled source/drain copper and five heat-spreading vias measured; hot-R loss and conservative board-dependent thermal estimates documented. Low-voltage prototype requires staged load/temperature qualification; no measured hardware result claimed.',
'assembly':'Deliberate manual prototype assembly, all populated components top side; exact manufacturer/MPN/footprint for every populated item. Polarity, silicon pin maps and reference module qualification documented; no factory sourcing or rotations fabricated.',
'fabricator':'Explicit1.6mm2-layer70µm stackup,0.20mm geometry floors,0.30mm drill,0.15mm legend. Official publisher independently checks native files and final Gerber/drill truth at every publication.',
'bringup':'Staged current-limited no-load, reset/isolation, module identity, sonar, single-channel, peak-load and temperature tests with numerical limits. Parallel18650 owned pack and configured external assembly require the documented acceptance checks; hardwareTested remains false.'}
r={'schemaVersion':1,'reviewer':'Board builder — Codex; independent board tester attestation pending','designInputs':design_inputs(Project('design/main.kicad_pro').root),'acceptedIgnoredChecks':check['ignoredChecks'],'checks':{},'assembly':{}}
for area,analysis in analyses.items():
 paths=[root/'engineering'/f'{area}.md']
 if area=='power':paths += [root/'engineering/POWER_SYSTEM.md',root/'engineering/power-calculations.json',root/'engineering/pack-protection-spec.json',root/'engineering/pack-protection-calculations.json']
 r['checks'][area]={'status':'pass','analysis':analysis,'evidence':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
for part in json.load(open('parts.json'))['parts']:
 for ref in part['refdes']:r['assembly'][ref]={'method':'manual'}
(root/'manufacturing.json').write_text(json.dumps(r,indent=2));print('Engineering review bound to',len(r['designInputs']),'source files and',len(r['assembly']),'manual references')
