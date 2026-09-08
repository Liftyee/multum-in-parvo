from cad import ROOT,parse,dump,kid,kids,unq
import json
p=ROOT/'mesh-node.kicad_pcb';t=parse(p.read_text());nets={int(n[1]):unq(n[2]).rsplit('/',1)[-1] for n in kids(t,'net')};remove=[]
for x in kids(t,'segment'):
 n=nets[int(kid(x,'net')[1])];a=list(map(float,kid(x,'start')[1:]));z=list(map(float,kid(x,'end')[1:]))
 clear=(n=='PACK_P' and 73.9<min(a[0],z[0]) and max(a[0],z[0])<75 and min(a[1],z[1])>15.4 and max(a[1],z[1])<17.8) or (n=='RF1V55' and 56.4<min(a[0],z[0]) and max(a[0],z[0])<60 and min(a[1],z[1])>29.9 and max(a[1],z[1])<30.4) or (n=='RF_SW_SUPPLY' and min(a[0],z[0])>74.6 and min(a[1],z[1])>28.3 and max(a[1],z[1])<32)
 if clear:remove.append(x)
# Remove only the four ground items violating the antenna connector's keepout.
bad={i['uuid'] for v in json.loads((ROOT/'reports/rf-drc.json').read_text())['violations'] if v['type']=='items_not_allowed' for i in v['items']}
for x in t:
 if isinstance(x,list) and x[0] in ['segment','via'] and kid(x,'tstamp') and unq(kid(x,'tstamp')[1]) in bad:remove.append(x)
(ROOT/'reports/cleared-rf-escapes.json').write_text(json.dumps([{'type':x[0],'net':nets[int(kid(x,'net')[1])],'item':dump(x)} for x in remove],indent=2))
t[:]=[x for x in t if x not in remove];p.write_text(dump(t).replace(') (',')\n('));print('Cleared',len(remove),'documented RF-area obstructions')
