"""Print decoupling pad distances (pcbnew) for placement tuning: pad-dist.py board.kicad_pcb"""
import pcbnew as p,sys,math
b=p.LoadBoard(sys.argv[1]);pd={}
for f in b.GetFootprints():
    for q in f.Pads():pd[(f.GetReference(),q.GetNumber())]=(q.GetNetname(),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y))
caps=[(v[0],k[0],v) for k,v in pd.items() if k[0].startswith('C') and v[0]!='GND']
for ic,pin in [('U1','20'),('U2','2'),('U2','3'),('U3','5'),('U4','5'),('U5','5'),('U6','5')]:
    n,x,y=pd[(ic,pin)];d,c=min((math.hypot(x-v[1],y-v[2]),c) for nn,c,v in caps if nn==n);print(ic,pin,n,c,round(d,2))
