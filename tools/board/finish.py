"""Release-note-8 finish: widen router stubs, add pours (GND bottom, SERVO_5V top, local 6A pours), fill. usage: finish.py in out
Current path is a pour chain: J_PWR.1 -> F1 -> Q1 drains (FUSED) ; Q1 sources -> Q2 sources (LOAD) ; Q2 drains -> SERVO_5V plane."""
import pcbnew as p,sys
b=p.LoadBoard(sys.argv[1]);mm=p.FromMM;nets=b.GetNetsByName();W,H=62,60
for t in b.GetTracks():
    if not isinstance(t,p.PCB_VIA) and t.GetWidth()<mm(.25):t.SetWidth(mm(.25))
def pads(ref,nums):
    f=next(x for x in b.GetFootprints() if x.GetReference()==ref);return [pd for pd in f.Pads() if pd.GetNumber() in nums]
def bbox(items,m):
    xs=[];ys=[]
    for ref,nums in items:
        for pd in pads(ref,nums):
            bb=pd.GetBoundingBox();xs+= [p.ToMM(bb.GetLeft()),p.ToMM(bb.GetRight())];ys+=[p.ToMM(bb.GetTop()),p.ToMM(bb.GetBottom())]
    return min(xs)-m,min(ys)-m,max(xs)+m,max(ys)+m
def zone(net,layer,pts,prio,rel=False):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(nets[net].GetNetCode());z.SetAssignedPriority(prio);z.SetLocalClearance(mm(.25));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2));z.SetThermalReliefGap(mm(.3));z.SetThermalReliefSpokeWidth(mm(.5));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    po=z.Outline();po.NewOutline()
    for x,y in pts:po.Append(mm(x),mm(y))
    b.Add(z)
def rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
zone('GND',p.B_Cu,rect(.5,.5,W-.5,H-.5),0)
zone('SERVO_5V',p.F_Cu,rect(.5,.5,W-.5,H-.5),0)
x0,y0,x1,y1=bbox([('J_PWR',['1']),('F1',['1'])],.6);zone('EXT_5V_IN',p.F_Cu,rect(x0,y0,x1,y1),40)
x0,y0,x1,y1=bbox([('F1',['2']),('Q1',['5','6','7','8'])],.6);zone('FUSED_5V',p.F_Cu,rect(x0,y0,x1,y1),30)
x0,y0,x1,y1=bbox([('Q1',['1','2','3']),('Q2',['1','2','3'])],.6);zone('LOAD_5V',p.F_Cu,rect(x0,y0,x1,y1),20)
def text(t,x,y,size=.8):
    o=p.PCB_TEXT(b);o.SetText(t);o.SetPosition(p.VECTOR2I(mm(x),mm(y)));o.SetLayer(p.F_SilkS);o.SetTextSize(p.VECTOR2I(mm(size),mm(size)));o.SetTextThickness(mm(.15));b.Add(o)
for ref,(x,y,n) in {'J_S0':(4,3,'LF'),'J_S1':(4,14,'LM'),'J_S2':(4,37,'LR'),'J_S3':(58,3,'RF'),'J_S4':(58,14,'RM'),'J_S5':(58,32,'RR'),'J_S6':(52,3,'TUR')}.items():text(n,x,y+8.6)
text('5V IN',10.5,41.2);text('GND',16.2,41.2);text('NOSE=TOP',6,57.6);text('V0.4 ESP32',46,58.9)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(sys.argv[2],b);print('finished')
