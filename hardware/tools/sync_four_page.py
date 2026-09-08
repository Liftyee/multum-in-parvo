"""Update PCB net names and symbol paths after connectivity-preserving sheet moves."""
from cad import *
import json
p=ROOT/'mesh-node.kicad_pcb';t=parse(p.read_text());net=parse((ROOT/'reports/four-page.net').read_text())
node_net={};namecode={unq(n[2]):int(n[1]) for n in kids(t,'net')}
for n in kids(kid(net,'nets'),'net'):
 for node in kids(n,'node'):node_net[unq(kid(node,'ref')[1]),unq(kid(node,'pin')[1])]=unq(kid(n,'name')[1])
# Identify each net by its component pins, rather than hierarchy-dependent names.
rename={};changes=[]
for f in kids(t,'footprint'):
 ref=next(unq(q[2]) for q in kids(f,'property') if unq(q[1])=='Reference')
 for pad in kids(f,'pad'):
  old=kid(pad,'net');new=node_net.get((ref,unq(pad[1])))
  if old and new and not(ref in ['R401','R402','R404'] and unq(old[2])=='SOLAR_P'):
   rename[int(old[1])]=new
for n in kids(t,'net'):
 if int(n[1]) in rename:n[2]=json.dumps(rename[int(n[1])])
namecode={unq(n[2]):int(n[1]) for n in kids(t,'net')}
comps={unq(kid(c,'ref')[1]):c for c in kids(kid(net,'components'),'comp')}
for f in kids(t,'footprint'):
 ref=next(unq(q[2]) for q in kids(f,'property') if unq(q[1])=='Reference');c=comps[ref]
 path=unq(kid(kid(c,'sheetpath'),'tstamps')[1])+unq(kid(c,'tstamps')[1])
 old=kid(f,'path')
 if old:old[1]=json.dumps(path)
 else:f.append(['path',json.dumps(path)])
 for pad in kids(f,'pad'):
  old=kid(pad,'net');new=node_net.get((ref,unq(pad[1])))
  if old and new:
   if int(old[1])!=namecode[new]:changes.append({'ref':ref,'pad':unq(pad[1]),'old':unq(old[2]),'new':new})
   old[1:]=[str(namecode[new]),json.dumps(new)]
p.write_text(dump(t).replace(') (',')\n('));(ROOT/'reports/pcb-net-sync.json').write_text(json.dumps(changes,indent=2));print(changes)
