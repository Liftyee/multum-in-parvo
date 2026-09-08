"""Add ground planes and clearance-screened return vias to the routed draft."""
import sys,math,json
sys.path.insert(0,'/tmp/multum-cad-deps')
import pcbnew as k
from shapely.geometry import Point,box,LineString
from shapely.affinity import rotate,translate
from shapely.strtree import STRtree
from cad import ROOT,parse,dump,kid,kids
path=ROOT/'mesh-node.kicad_pcb';b=k.LoadBoard(str(path));gnd=b.FindNet('GND')
def xy(p):return(k.ToMM(p.x),k.ToMM(p.y))
def vv(p):return k.VECTOR2I(k.FromMM(p[0]),k.FromMM(p[1]))
objects=[];nets=[];padobjs=[];groundpads=[];vias=[]
for f in b.GetFootprints():
 for p in f.Pads():
  if not(p.IsOnLayer(k.F_Cu) or p.IsOnLayer(k.B_Cu)):continue
  x,y=xy(p.GetPosition());w,h=xy(p.GetSize())
  shape=translate(rotate(box(-w/2,-h/2,w/2,h/2),-p.GetOrientationDegrees(),origin=(0,0)),x,y)
  objects.append(shape);nets.append(p.GetNetname());padobjs.append(len(objects)-1)
  if p.GetNetname()=='GND':groundpads.append((f.GetReference(),p,shape))
for t in b.GetTracks():
 if isinstance(t,k.PCB_VIA):
  sh=Point(xy(t.GetPosition())).buffer(k.ToMM(t.GetWidth())/2)
  if t.GetNetname()=='GND':vias.append(xy(t.GetPosition()))
 else:sh=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(k.ToMM(t.GetWidth())/2)
 objects.append(sh);nets.append(t.GetNetname())
tree=STRtree(objects);padset=set(padobjs)
def clear(pt):
 P=Point(pt)
 if not(5.8<pt[0]<97.2 and 7.8<pt[1]<69.2):return False
 if any(math.dist(pt,v)<.8 for v in vias):return False
 for i in tree.query(P.buffer(.46)):
  d=objects[i].distance(P)
  if nets[i]!='GND' and d<.46:return False
  if i in padset and d<.18:return False # keep drill outside SMD copper
 return True
def add(pt):
 v=k.PCB_VIA(b);v.SetPosition(vv(pt));v.SetWidth(k.FromMM(.6));v.SetDrill(k.FromMM(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(gnd);b.Add(v);vias.append(pt)
def link(a,z):
 sh=LineString([a,z]).buffer(.10+.151)
 if any(nets[i]!='GND' and objects[i].intersects(sh) for i in tree.query(sh)):return False
 t=k.PCB_TRACK(b);t.SetStart(vv(a));t.SetEnd(vv(z));t.SetWidth(k.FromMM(.2));t.SetLayer(k.F_Cu);t.SetNet(gnd);b.Add(t);return True
miss=[]
for ref,p,shape in groundpads:
 a=xy(p.GetPosition())
 if any(math.dist(a,v)<1.3 for v in vias):continue
 candidates=[]
 for r in [.75,1.,1.25,1.5,2.]:
  for deg in range(0,360,45):candidates.append((round(a[0]+r*math.cos(math.radians(deg)),4),round(a[1]+r*math.sin(math.radians(deg)),4)))
 for pt in candidates:
  if clear(pt) and link(a,pt):add(pt);break
 else:miss.append((ref,p.GetNumber()))
# Fence actual wide RF routes, at about 2mm intervals and 1.0mm centre offset.
for t in list(b.GetTracks()):
 if isinstance(t,k.PCB_VIA) or t.GetLayer()!=k.F_Cu or k.ToMM(t.GetWidth())<.7:continue
 a=xy(t.GetStart());z=xy(t.GetEnd());length=math.dist(a,z)
 if a[0]<56 or a[1]>36 or length<.4:continue
 for j in range(max(1,math.ceil(length/2))):
  f=(j+.5)/max(1,math.ceil(length/2));x=a[0]+f*(z[0]-a[0]);y=a[1]+f*(z[1]-a[1])
  for sign in [-1,1]:
   pt=(x-sign*(z[1]-a[1])/length,y+sign*(z[0]-a[0])/length)
   if clear(pt):add(pt)
for layer in [k.F_Cu,k.B_Cu]:
 zone=k.ZONE(b);zone.SetLayer(layer);zone.SetNet(gnd);zone.SetLocalClearance(k.FromMM(.25 if layer==k.F_Cu else .2));zone.SetThermalReliefGap(k.FromMM(.25));zone.SetThermalReliefSpokeWidth(k.FromMM(.3));zone.SetPadConnection(k.ZONE_CONNECTION_FULL);zone.SetMinThickness(k.FromMM(.15))
 poly=zone.Outline();poly.NewOutline()
 for p in [(5.5,7.5),(97.5,7.5),(97.5,69.5),(5.5,69.5)]:poly.Append(vv(p).x,vv(p).y)
 b.Add(zone)
b.BuildListOfNets();b.GetConnectivity().Build(b);k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(path),b)
(ROOT/'reports/ground-review.json').write_text(json.dumps({'via_count':len(vias),'ground_pads_without_direct_local_via':miss},indent=2));print('Ground vias',len(vias),'Review pads',miss)
