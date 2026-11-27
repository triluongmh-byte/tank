"""Drop router stubs on EXT_5V_IN/FUSED_5V (carried by pours in finish.py; supply-input runs must be >=0.6 mm). strip.py in out"""
import pcbnew as p,sys
b=p.LoadBoard(sys.argv[1])
for t in list(b.GetTracks()):
    if t.GetNetname() in ('EXT_5V_IN','FUSED_5V'):b.Remove(t)
p.SaveBoard(sys.argv[2],b)
