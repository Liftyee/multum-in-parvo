"""Complete only RF signal nets, preserving all other routing."""
import sys,math,heapq,json
sys.path.insert(0,'/tmp/multum-cad-deps')
import numpy as np,pcbnew as k,shapely
from shapely.geometry import Point,box,LineString
from shapely.affinity import rotate,translate
from shapely.ops import unary_union,nearest_points
from cad import ROOT,parse,dump,kid,kids,unq
path=ROOT/'mesh-node.kicad_pcb'
# Work on selected signal nets. No other net is ripped up or routed.
selected={'SW_TX','SW_RX','SW_ANT','FEM_PA','MCU_RFIP'}
t=parse(path.read_text());netnames={int(n[1]):unq(n[2]) for n in kids(t,'net')}
ripcodes=set()
t[:]=[x for x in t if not(isinstance(x,list) and x[0] in ['segment','arc','via'] and int(kid(x,'net')[1]) in ripcodes)]
path.write_text(dump(t).replace(') (',')\n('));b=k.LoadBoard(str(path))
def xy(p):return(k.ToMM(p.x),k.ToMM(p.y))
def vec(p):return k.VECTOR2I(k.FromMM(p[0]),k.FromMM(p[1]))
def objects(layer=k.F_Cu):
 out=[]
 for f in b.GetFootprints():
  for p in f.Pads():
   if not p.IsOnLayer(layer):continue
   x,y=xy(p.GetPosition());w,h=xy(p.GetSize());sh=translate(rotate(box(-w/2,-h/2,w/2,h/2),-p.GetOrientationDegrees(),origin=(0,0)),x,y)
   out.append((p.GetNetCode(),sh))
 for tr in b.GetTracks():
  if isinstance(tr,k.PCB_VIA):sh=Point(xy(tr.GetPosition())).buffer(k.ToMM(tr.GetWidth())/2)
  elif tr.GetLayer()==layer:sh=LineString([xy(tr.GetStart()),xy(tr.GetEnd())]).buffer(k.ToMM(tr.GetWidth())/2)
  else:continue
  out.append((tr.GetNetCode(),sh))
 return out
step=.025;x0=44.;y0=12.;x1=97.;y1=38.
xs=np.arange(x0,x1+step/2,step);ys=np.arange(y0,y1+step/2,step);nx=len(xs);ny=len(ys)
X,Y=np.meshgrid(xs,ys)
def grid(p):return (min(nx-1,max(0,round((p.x-x0)/step))),min(ny-1,max(0,round((p.y-y0)/step))))
def physical(p):return (x0+p[0]*step,y0+p[1]*step)
def astar(blocked,start,end):
 sx,sy=start;ex,ey=end;blocked[sy,sx]=False;blocked[ey,ex]=False
 pq=[(0,0,sx,sy)];cost={start:0};prev={};moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414214),(1,-1,1.414214),(-1,1,1.414214),(-1,-1,1.414214)]
 while pq:
  _,d,x,y=heapq.heappop(pq)
  if d!=cost.get((x,y)):continue
  if (x,y)==end:
   p=end;route=[p]
   while p!=start:p=prev[p];route.append(p)
   return list(reversed(route))
  for dx,dy,dd in moves:
   xx=x+dx;yy=y+dy
   if not(0<=xx<nx and 0<=yy<ny) or blocked[yy,xx]:continue
   if dx and dy and (blocked[y,xx] or blocked[yy,x]):continue
   nd=d+dd
   if nd>=cost.get((xx,yy),float('inf')):continue
   cost[xx,yy]=nd;prev[xx,yy]=(x,y)
   h=max(abs(ex-xx),abs(ey-yy))+.414214*min(abs(ex-xx),abs(ey-yy))
   heapq.heappush(pq,(nd+h,nd,xx,yy))
 return None
def crossover(blockedF,start,end,code):
 back=objects(k.B_Cu)
 backobs=unary_union([s for n,s in back if n!=code]).buffer(.233)
 blockedB=shapely.contains_xy(backobs,X,Y)
 # RF transitions are confined to the MCU matching/switch area, away from antenna CPWG.
 allowed=(X>54.9)&(X<75.6)&(Y>25)&(Y<33.7)
 blockedB|=~allowed
 allobs=unary_union([s for n,s in objects()+back if n!=code]).buffer(.46)
 viaok=~shapely.contains_xy(allobs,X,Y)&allowed
 for f in b.GetFootprints():
  for p in f.Pads():
   if p.IsOnLayer(k.F_Cu):
    x,y=xy(p.GetPosition());w,h=xy(p.GetSize())
    sh=translate(rotate(box(-w/2,-h/2,w/2,h/2),-p.GetOrientationDegrees(),origin=(0,0)),x,y).buffer(.18)
    viaok&=~shapely.contains_xy(sh,X,Y)
 sx,sy=start;ex,ey=end;blockedF[sy,sx]=False;blockedF[ey,ex]=False
 first=(sx,sy,0);last=(ex,ey,0);pq=[(0,0,first)];cost={first:0};prev={};blocked=[blockedF,blockedB]
 moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414214),(1,-1,1.414214),(-1,1,1.414214),(-1,-1,1.414214)]
 while pq:
  _,d,p=heapq.heappop(pq);x,y,l=p
  if d!=cost.get(p):continue
  if p==last:
   out=[p]
   while p!=first:p=prev[p];out.append(p)
   return list(reversed(out))
  nxt=[]
  for dx,dy,dd in moves:
   xx=x+dx;yy=y+dy
   if not(0<=xx<nx and 0<=yy<ny) or blocked[l][yy,xx]:continue
   if dx and dy and (blocked[l][y,xx] or blocked[l][yy,x]):continue
   nxt.append(((xx,yy,l),dd*(1 if l==0 else 3)))
  if viaok[y,x] and not blocked[1-l][y,x]:nxt.append(((x,y,1-l),300))
  for z,dd in nxt:
   nd=d+dd
   if nd>=cost.get(z,1e30):continue
   cost[z]=nd;prev[z]=p;xx,yy,ll=z
   h=max(abs(ex-xx),abs(ey-yy))+.414214*min(abs(ex-xx),abs(ey-yy))
   heapq.heappush(pq,(nd+h,nd,z))
 return None
results=[]
for name in ['MCU_RFIN','SW_RX']:
 net=next(n for n in b.GetNetInfo().NetsByNetcode().values() if n.GetNetname().rsplit('/',1)[-1]==name)
 code=net.GetNetCode();width=.15
 for attempt in range(12):
  obs=objects();copper=unary_union([s.buffer(.001) for n,s in obs+objects(k.B_Cu) if n==code]);components=list(copper.geoms) if copper.geom_type=='MultiPolygon' else [copper]
  if len(components)<2:results.append({'net':name,'complete':True});break
  pairs=sorted((a.distance(z),i,j) for i,a in enumerate(components) for j,z in enumerate(components) if i<j)
  obstacles=unary_union([s for n,s in obs if n!=code]).buffer(.15+width/2+.008)
  blocked=shapely.contains_xy(obstacles,X,Y)
  found=False
  for _,i,j in pairs:
   a=components[i].representative_point();z=components[j].representative_point();start=grid(a);end=grid(z)
   route=astar(blocked.copy(),start,end)
   if route is None:
    cross=crossover(blocked.copy(),start,end,code)
    if cross is None:continue
    # Compress collinear segments on each layer.
    cp=[cross[0]]
    for ix in range(1,len(cross)-1):
     d1=tuple(cross[ix][j]-cross[ix-1][j] for j in range(3));d2=tuple(cross[ix+1][j]-cross[ix][j] for j in range(3))
     if d1!=d2:cp.append(cross[ix])
    cp.append(cross[-1])
    for aa,zz in zip(cp,cp[1:]):
     if aa[2]!=zz[2]:
      tr=k.PCB_VIA(b);tr.SetPosition(vec(physical(aa)));tr.SetWidth(k.FromMM(.6));tr.SetDrill(k.FromMM(.3));tr.SetViaType(k.VIATYPE_THROUGH);tr.SetLayerPair(k.F_Cu,k.B_Cu)
     else:
      tr=k.PCB_TRACK(b);tr.SetStart(vec(physical(aa)));tr.SetEnd(vec(physical(zz)));tr.SetWidth(k.FromMM(width));tr.SetLayer(k.F_Cu if aa[2]==0 else k.B_Cu)
     tr.SetNet(net);tr.SetLocked(True);b.Add(tr)
    for aa,zz in [((a.x,a.y),physical(start)),(physical(end),(z.x,z.y))]:
     if math.dist(aa,zz)>.00001:
      tr=k.PCB_TRACK(b);tr.SetStart(vec(aa));tr.SetEnd(vec(zz));tr.SetWidth(k.FromMM(width));tr.SetLayer(k.F_Cu);tr.SetNet(net);tr.SetLocked(True);b.Add(tr)
    print(name,'local crossover',sum(a[2]!=z[2] for a,z in zip(cp,cp[1:])),'vias',flush=True);found=True;break
   pts=[physical(route[0])]
   for ix in range(1,len(route)-1):
    if (route[ix][0]-route[ix-1][0],route[ix][1]-route[ix-1][1])!=(route[ix+1][0]-route[ix][0],route[ix+1][1]-route[ix][1]):pts.append(physical(route[ix]))
   pts.append(physical(route[-1]));pts=[(a.x,a.y)]+pts+[(z.x,z.y)]
   for aa,zz in zip(pts,pts[1:]):
    if math.dist(aa,zz)<.00001:continue
    tr=k.PCB_TRACK(b);tr.SetStart(vec(aa));tr.SetEnd(vec(zz));tr.SetWidth(k.FromMM(width));tr.SetLayer(k.F_Cu);tr.SetNet(net);tr.SetLocked(True);b.Add(tr)
   print(name,'joined',len(components),'components, length',sum(math.dist(a,z) for a,z in zip(pts,pts[1:])),flush=True);found=True;break
  if not found:results.append({'net':name,'complete':False,'islands':len(components)});print('No route',name,flush=True);break
b.GetConnectivity().Build(b);k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(path),b)
(ROOT/'reports/rf-route.json').write_text(json.dumps(results,indent=2));print(results)
