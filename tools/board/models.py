"""Reference component envelopes from primary dimensions; run with case Python."""
import cadquery as cq, pathlib
D=pathlib.Path('design/Tank.3dshapes');D.mkdir(exist_ok=True)
fuse=cq.Workplane('XY').box(6.1,2.69,2.69,centered=(True,True,False)).translate((0,0,.1))
cq.exporters.export(fuse,str(D/'Fuse_451.step'))
cap=cq.Workplane('XY').center(2.5,0).circle(5).extrude(16)
for x in (0,5):cap=cap.union(cq.Workplane('XY').center(x,0).circle(.3).extrude(-3.5))
cq.exporters.export(cap,str(D/'EEU_FR1A102.step'))
for file in [pathlib.Path('design/main.kicad_pcb'),pathlib.Path('design/Tank.pretty/Fuse_2512_6332Metric.kicad_mod'),pathlib.Path('design/Tank.pretty/CP_Radial_D10.0mm_P5.00mm.kicad_mod')]:
 s=file.read_text().replace('${KICAD10_3DMODEL_DIR}/Fuse.3dshapes/Fuse_2512_6332Metric.step','${KIPRJMOD}/Tank.3dshapes/Fuse_451.step').replace('${KICAD10_3DMODEL_DIR}/Capacitor_THT.3dshapes/CP_Radial_D10.0mm_P5.00mm.step','${KIPRJMOD}/Tank.3dshapes/EEU_FR1A102.step');file.write_text(s)
print('Exact nominal fuse/cap reference envelopes generated')
