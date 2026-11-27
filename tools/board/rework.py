"""Release-note-8 re-placement: strip copper, move footprints per tools/board/layout.json, new outline/mount keepouts.
Writes build/board/placed.kicad_pcb (input design/main.kicad_pcb). Run with KiCad's Python (pcbnew)."""
import pcbnew as p,json,math,sys
from xml.etree import ElementTree as ET
mm=p.FromMM;L=json.load(open('tools/board/layout.json'));W,H=L['outline']
b=p.LoadBoard(sys.argv[2] if len(sys.argv)>2 else "design/main.kicad_pcb")
mode=sys.argv[1]
if mode!='place':
    {'tracks':lambda:[b.Remove(t) for t in list(b.GetTracks())],'zones':lambda:[b.Remove(z) for z in list(b.Zones())],'draw':lambda:[b.Remove(d) for d in list(b.GetDrawings())]}[mode]()
    p.SaveBoard(sys.argv[2],b);sys.exit(0)
have={f.GetReference() for f in b.GetFootprints()}
root=ET.parse('build/board/main.net').getroot();comps={c.attrib['ref']:c for c in root.find('components')};pin={}
for n in root.find('nets'):
    for nd in n.findall('node'):pin[(nd.attrib['ref'],nd.attrib['pin'])]=n.attrib['name']
nets=b.GetNetsByName()
for ref in comps:
    if ref in have or ref.startswith('#'):continue
    c=comps[ref];fp=c.find('footprint').text.split(':')[-1]
    f=p.FootprintLoad('design/Tank.pretty',fp);f.SetReference(ref);f.SetValue(c.find('value').text);f.SetFPID(p.LIB_ID('Tank',fp))
    f.SetPath(p.KIID_PATH(c.find('sheetpath').attrib['tstamps'].rstrip('/')+'/'+c.find('tstamps').text.split()[0]))
    b.Add(f)
for n in {v for v in pin.values()}:
    if n not in nets:
        ni=p.NETINFO_ITEM(b,n);b.Add(ni)
nets=b.GetNetsByName()
for f in b.GetFootprints():
    r=f.GetReference()
    for pad in f.Pads():
        n=pin.get((r,pad.GetNumber()))
        if n:pad.SetNet(nets[n])
    if r in L:
        x,y,a=L[r];f.SetOrientationDegrees(a);f.SetPosition(p.VECTOR2I(mm(x),mm(y)))
    f.Value().SetVisible(False);f.Reference().SetVisible(not(r[0] in 'RCT' and r!='C1' or r[0]=='H' or r in('J_FAN','J_SONAR_R','Q2','J_PWR') or r.startswith('J_S') and r[3:] in list('0123456')));f.Reference().SetTextSize(p.VECTOR2I(mm(.8),mm(.8)));f.Reference().SetTextThickness(mm(.15))
    for it in f.GraphicalItems():
        if it.GetLayer()==p.F_SilkS and hasattr(it,'SetWidth') and hasattr(it,'GetWidth') and it.GetWidth()<mm(.15):it.SetWidth(mm(.15))
pts=[(0,0),(W,0),(W,H),(0,H)]
for a,c in zip(pts,pts[1:]+pts[:1]):
    e=p.PCB_SHAPE();e.SetShape(p.SHAPE_T_SEGMENT);e.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));e.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])));e.SetLayer(p.Edge_Cuts);e.SetWidth(mm(.05));b.Add(e)
for h in ['H1','H2','H3','H4']:
    x,y,_=L[h];z=p.ZONE(b);z.SetIsRuleArea(True);ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);po=z.Outline();po.NewOutline()
    for i in range(32):
        a=2*math.pi*i/32;po.Append(mm(x+3.6*math.cos(a)),mm(y+3.6*math.sin(a)))
    b.Add(z)
# Fixed fan feed (0.8 mm B.Cu from the LOAD_5V pour between Q1 and Q2 to J_FAN pin 1), drawn before routing.
def trk(net,pts,layer,w):
    for a,c in zip(pts,pts[1:]):
        t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])));t.SetWidth(mm(w));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(mm(29),mm(50.4)));v.SetWidth(mm(.8));v.SetDrill(mm(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets['LOAD_5V']);b.Add(v)
trk('LOAD_5V',[(29,50.4),(29,55.2),(45.5,55.2),(45.5,52)],p.B_Cu,.8)
p.SaveBoard('build/board/placed.kicad_pcb',b);print('placed',len(list(b.GetFootprints())))
