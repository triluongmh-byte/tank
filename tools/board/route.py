"""Router bridge on a candidate copy. usage: route.py export <in.kicad_pcb> | import <routed-out.kicad_pcb>
Net-class widths (mm) for current-carrying nets are written into the DSN; signal width 0.25."""
import pathlib, sys, re
import pcbnew as p
mode=sys.argv[1];O=pathlib.Path("build/board")
if mode=="export":
    b=p.LoadBoard(sys.argv[2]);p.SaveBoard(str(O/"route.kicad_pcb"),b);p.ExportSpecctraDSN(b,str(O/"main.dsn"))
    d=(O/"main.dsn").read_text().replace('(width 200)','(width 250)').replace('(clearance 50 (type smd_smd))','(clearance 200 (type smd_smd))').replace('(clearance 200)','(clearance %d)'%int(__import__('os').environ.get('CLR','215')))
    (O/"main.dsn").write_text(d)
elif mode=="import":
    b=p.LoadBoard(str(O/"route.kicad_pcb"));assert p.ImportSpecctraSES(b,str(O/"main.ses"));p.SaveBoard(sys.argv[2],b)
