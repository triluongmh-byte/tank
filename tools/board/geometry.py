"""Export measured board interface and filled copper geometry (KiCad Python)."""
import pcbnew as p,json,pathlib,hashlib
LY=json.load(open('tools/board/layout.json'));W,H=LY['outline']
b=p.LoadBoard('design/main.kicad_pcb');O=pathlib.Path('engineering');zones=[]
for z in b.Zones():
 for layer in [p.F_Cu,p.B_Cu]:
  if not z.IsOnLayer(layer):continue
  ps=z.GetFilledPolysList(layer)
  islands=[]
  for i in range(ps.OutlineCount()):
   co=ps.Outline(i);pts=[[p.ToMM(co.CPoint(j).x),p.ToMM(co.CPoint(j).y)] for j in range(co.PointCount())];islands.append({'areaMm2':p.ToMM(p.ToMM(co.Area())),'pointsMm':pts})
  zones.append({'net':z.GetNetname(),'layer':b.GetLayerName(layer),'islands':islands})
(O/'copper-measurements.json').write_text(json.dumps(zones,indent=2))
fp=[]
for f in b.GetFootprints():
 q=f.GetPosition();box=f.GetBoundingBox(False,False);fp.append({'ref':f.GetReference(),'xMm':p.ToMM(q.x),'yMm':p.ToMM(q.y),'angleDeg':f.GetOrientationDegrees(),'models':[m.m_Filename for m in f.Models()],'bodyAndCourtyardBoxMm':[p.ToMM(box.GetX()),p.ToMM(box.GetY()),p.ToMM(box.GetRight()),p.ToMM(box.GetBottom())]})
d={'schema':1,'releaseNote':8,'contractSha256':'a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810','pcbSha256':hashlib.sha256(pathlib.Path('design/main.kicad_pcb').read_bytes()).hexdigest(),'outlineMm':[[0,0],[W,0],[W,H],[0,H],[0,0]],'caseFrame':'KiCad x = case X, KiCad y = case Y + 46 (y down = tail); board origin at case (X=-31,Y=-46); v1 model x = 46 - y, v1 y = 31 - x. Board underside Z=49 (v1 chassis boss tops) assumed.','thicknessMm':1.6,'mounts':[{'id':r,'xMm':x,'yMm':y,'holeDiameterMm':3.2} for r,x,y in [(h,LY[h][0],LY[h][1]) for h in ('H1','H2','H3','H4')]],'nativeCoordinates':'KiCad absolute x right,y down; raw STEP core Z0..1.44, copper/mask extend nominally -0.08..1.52','contractStepTransform':'mirror raw STEP Y and translate Z +0.08; exported main-contract.step already transformed, do not transform twice','footprints':fp,'hardwareTested':False}
(O/'board-geometry.json').write_text(json.dumps(d,indent=2));print('Geometry and copper measurements exported')
