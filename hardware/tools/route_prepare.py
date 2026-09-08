from pathlib import Path
import json,pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
board=ROOT/'mesh-node.kicad_pcb'
from cad import parse,dump,kid,kids
bt=parse(board.read_text())
for fp in kids(bt,'footprint'):
    if any(x[:3]==['property','"Reference"','"J601"'] for x in kids(fp,'property')):
        fp[:]=[x for x in fp if not (isinstance(x,list) and x[0].startswith('fp_') and kid(x,'layer')==['layer','"F.Mask"'])]
bt[:]=[x for x in bt if not (isinstance(x,list) and x[0] in ['zone','via','segment','arc'])]
board.write_text(dump(bt))
b=k.LoadBoard(str(board))
k.SaveBoard(str(board),b)
pro=ROOT/'mesh-node.kicad_pro';p=json.loads(pro.read_text())
cls=p['net_settings']['classes'][0];cls.update(clearance=.15,track_width=.2,via_diameter=.6,via_drill=.3)
p['board']['design_settings']['rules'].update(min_clearance=.15,min_track_width=.15,min_via_diameter=.6,min_through_hole_diameter=.3,min_copper_edge_clearance=.3,min_hole_clearance=.25)
pro.write_text(json.dumps(p,indent=2))
b=k.LoadBoard(str(board));assert k.ExportSpecctraDSN(b,str(ROOT/'reports/mesh-node.dsn'))
print('Prepared two-layer routing exchange')
