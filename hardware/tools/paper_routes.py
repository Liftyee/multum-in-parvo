"""Short orthogonal wires between nearby related parts; labels bridge crowded blocks.
Routing never crosses another net, so rearrangement cannot introduce wire junction shorts.
"""
import heapq,numpy as np
routing_summary=[]
for pg in pages.values():
 width,height=page_sizes[pg.name];pitch=1.27;nx=round(width/pitch)+1;ny=round(height/pitch)+1
 solid=np.zeros((ny,nx),bool);occ=np.zeros((ny,nx),np.int32)
 def cell(pt):return(round(pt[0]/pitch),round(pt[1]/pitch))
 def pt(c):return(round(c[0]*pitch,4),round(c[1]*pitch,4))
 def rect(x1,y1,x2,y2):
  a,b=cell((x1,y1));c,d=cell((x2,y2));solid[max(0,b):min(ny,d+1),max(0,a):min(nx,c+1)]=True
 rect(0,0,width,30.48);rect(0,height-29.21,width,height)
 terminals=collections.defaultdict(list)
 netids={n:i+1 for i,n in enumerate({n for p in pg.parts for n in p['nets'].values() if n})}
 for p in pg.parts:
  x,y=p['x'],p['y'];sym=symbols[p['symbol']];kind=p['symbol'];rot=p['rot']
  if p['ref'].startswith('#'):
   for num,net in p['nets'].items():pg.terminal(p,num)
   continue
  if kind in ['R','C','L','Crystal']:
   if rot==0:rect(x-1.9,y-2.54,x+1.9,y+2.54);rect(x+3.17,y-3.17,x+3.81+max(len(p['value']),len(p['ref']))*.6,y+3.17)
   else:rect(x-2.54,y-1.9,x+2.54,y+1.9);rect(x-max(len(p['value']),len(p['ref']))*.3,y-5.08,x+max(len(p['value']),len(p['ref']))*.3,y-1.27)
  elif kind in ['Q_NMOS_GSD','Q_PMOS_GSD']:rect(x-.635,y-3.175,x+3.175,y+3.175)
  elif kind=='TestPoint':rect(x-1.27,y-6.35,x+1.27,y-2.54)
  else:
   points=[pg.point(p,n) for n in sym.pins]
   minx=min(a[0] for a in points);maxx=max(a[0] for a in points);miny=min(a[1] for a in points);maxy=max(a[1] for a in points)
   if maxx-minx<5.08:rect(x-.635,y-2.54,x+5.08,y+5.08)
   else:rect(minx+2.0,miny+1.9,maxx-2.0,maxy-1.9)
   rect(x-max(len(p['value']),len(p['ref']))*.32,miny-7.62,x+max(len(p['value']),len(p['ref']))*.32,miny-2.54)
  for num,net in p['nets'].items():
   if net is None:continue
   a=pg.point(p,num);ang=(sym.pins[num][2]+rot)%360
   z=(round(a[0]-3.81*math.cos(math.radians(ang)),4),round(a[1]+3.81*math.sin(math.radians(ang)),4))
   start=cell(a);end=cell(z);pg.wire(a,z);p.setdefault('wired',set()).add(num)
   xx,yy=start;ex,ey=end
   while True:
    if 0<=xx<nx and 0<=yy<ny:occ[yy,xx]=netids[net]
    if (xx,yy)==end:break
    xx+=0 if xx==ex else 1 if xx<ex else -1;yy+=0 if yy==ey else 1 if yy<ey else -1
   terminals[net].append((end,p,num,180 if ang==0 else 0))
 def path(start,end,netid):
  if start==end:return[start]
  sx,sy=start;ex,ey=end
  if not(0<=sx<nx and 0<=sy<ny and 0<=ex<nx and 0<=ey<ny):return None
  direct=abs(ex-sx)+abs(ey-sy);maxcost=int(direct*1.6+24/pitch)
  if direct>150/pitch:return None
  pq=[(direct,0,sx,sy)];dist={start:0};prev={};visits=0
  while pq and visits<35000:
   _,cost,x,y=heapq.heappop(pq)
   if cost!=dist.get((x,y)):continue
   visits+=1
   if (x,y)==end:
    out=[end];c=end
    while c!=start:c=prev[c];out.append(c)
    return list(reversed(out))
   for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
    xx=x+dx;yy=y+dy;c=(xx,yy)
    if not(0<=xx<nx and 0<=yy<ny):continue
    if c not in [start,end] and (solid[yy,xx] or occ[yy,xx] not in [0,netid]):continue
    # One grid cell gap prevents accidental T-junctions to nearby other nets.
    if any(0<=xx+ddx<nx and 0<=yy+ddy<ny and occ[yy+ddy,xx+ddx] not in [0,netid] for ddx,ddy in [(1,0),(-1,0),(0,1),(0,-1)]):continue
    nc=cost+1
    if (x,y) in prev:
     px,py=prev[x,y]
     if (x-px,y-py)!=(dx,dy):nc+=3
    if nc>maxcost or nc>=dist.get(c,10**9):continue
    dist[c]=nc;prev[c]=(x,y);heapq.heappush(pq,(nc+abs(ex-xx)+abs(ey-yy),nc,xx,yy))
  return None
 wires=0;labels=0
 for net,ends in sorted(terminals.items(),key=lambda z:(z[0]=='GND',len(z[1]))):
  parent=list(range(len(ends)))
  def find(i):
   while parent[i]!=i:i=parent[i]
   return i
  pairs=sorted((abs(a[0][0]-z[0][0])+abs(a[0][1]-z[0][1]),i,j) for i,a in enumerate(ends) for j,z in enumerate(ends) if i<j)
  for length,i,j in pairs:
   if find(i)==find(j):continue
   # Keep rail buses within local functional blocks rather than crossing the sheet.
   if net in ['GND','PACK_P','3V3_AON','SOLAR_P','VINT'] and length>65/pitch:continue
   route=path(ends[i][0],ends[j][0],netids[net])
   if route is None:continue
   parent[find(j)]=find(i);wires+=1
   corners=[route[0]]
   for ii in range(1,len(route)-1):
    if (route[ii][0]-route[ii-1][0],route[ii][1]-route[ii-1][1])!=(route[ii+1][0]-route[ii][0],route[ii+1][1]-route[ii][1]):corners.append(route[ii])
   corners.append(route[-1])
   for a,z in zip(corners,corners[1:]):pg.wire(pt(a),pt(z))
   for x,y in route:occ[y,x]=netids[net]
  groups={}
  for i,end in enumerate(ends):groups.setdefault(find(i),[]).append(end)
  for group in groups.values():
   end,p,num,ang=group[0];pg.label(net,pt(end),ang);labels+=1
  # Explicit junctions at same-net branch endpoints are harmless even on a straight wire.
  if len(ends)>2:
   for end,p,num,ang in ends:
    coord=pt(end);pg.items.append(f'(junction (at {coord[0]} {coord[1]}) (diameter 0) (color 0 0 0 0) (uuid {q(uid(pg.name+net+str(coord)))}))')
 routing_summary.append(dict(page=pg.name,direct_connections=wires,net_labels=labels,connected_pins=sum(map(len,terminals.values()))))
 print(routing_summary[-1],flush=True)
(ROOT/'reports/schematic-wiring.json').write_text(json.dumps(routing_summary,indent=2))
