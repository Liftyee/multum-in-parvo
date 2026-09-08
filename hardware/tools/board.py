"""Create a KiCad 8 board from the CLI-exported schematic netlist."""
from cad import *
import pcbnew as k, collections
def mm(x):return k.FromMM(x)
def v(x,y):return k.VECTOR2I(mm(x),mm(y))
data=json.loads((ROOT/'design.json').read_text())
tree=parse((ROOT/'reports/mesh-node.net').read_text())
netpins={};netnames={};b=k.BOARD();b.SetCopperLayerCount(2)
ds=b.GetDesignSettings();ds.SetBoardThickness(mm(.8));ds.m_MinClearance=mm(.15);ds.m_CopperEdgeClearance=mm(.3);ds.m_HoleClearance=mm(.25)
for net in kids(kid(tree,'nets'),'net'):
    name=unq(kid(net,'name')[1]);ni=k.NETINFO_ITEM(b,name);b.Add(ni);netnames[name]=ni
    for n in kids(net,'node'):netpins[(unq(kid(n,'ref')[1]),unq(kid(n,'pin')[1]))]=ni
fps={};pads={}
for p in data:
    if not p['footprint']:continue
    f=k.FootprintLoad(str(LIB/'Node.pretty'),p['footprint'].split(':')[1]);assert f,p['footprint']
    f.SetReference(p['ref']);f.SetValue(p['value']);f.SetDNP(p['dnp'])
    path=k.KIID_PATH()
    for id in [uid('root'),uid(p['sheet']),p['uuid']]:path.push_back(k.KIID(id))
    f.SetPath(path);b.Add(f)
    x,y,ang=p['pcb'];f.SetPosition(v(x,y));f.SetOrientationDegrees(ang)
    for pad in f.Pads():
        n=pad.GetNumber()
        if (p['ref'],n) in netpins:pad.SetNet(netpins[p['ref'],n])
        pads.setdefault((p['ref'],n),[]).append(pad)
    f.Reference().SetTextSize(v(1,1));f.Reference().SetTextThickness(mm(.15));f.Reference().SetVisible(False)
    f.Value().SetVisible(False);fps[p['ref']]=f

# Orient the QFN RF edge toward the antenna; resolve courtyard clashes by
# searching locally around the deliberately selected functional-block positions.
fps['U101'].SetOrientationDegrees(90)
def rect(f):
    shapes=[s for s in f.GraphicalItems() if s.GetLayer()==k.F_CrtYd]
    if shapes:
        boxes=[s.GetBoundingBox() for s in shapes]
        return (min(k.ToMM(a.GetLeft()) for a in boxes),min(k.ToMM(a.GetTop()) for a in boxes),max(k.ToMM(a.GetRight()) for a in boxes),max(k.ToMM(a.GetBottom()) for a in boxes))
    a=f.GetBoundingBox(False,False);return (k.ToMM(a.GetLeft()),k.ToMM(a.GetTop()),k.ToMM(a.GetRight()),k.ToMM(a.GetBottom()))
def overlap(a,b,gap=.2):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
placed=[];moves={}
def priority(ref):return (0 if ref.startswith('U') else 1 if ref.startswith('J') else 2 if ref[1:4].startswith('6') else 3,ref)
for ref in sorted(fps,key=priority):
    f=fps[ref];pos=f.GetPosition();ox,oy=k.ToMM(pos.x),k.ToMM(pos.y)
    offsets=sorted(((x*.25,y*.25) for x in range(-40,41) for y in range(-40,41)),key=lambda z:z[0]**2+z[1]**2)
    for dx,dy in offsets:
        f.SetPosition(v(ox+dx,oy+dy));r=rect(f)
        if r[0]<6 or r[1]<14 or r[2]>97 or r[3]>67:continue
        if any(overlap(r,rr) for rr in placed):continue
        placed.append(r)
        if dx or dy:moves[ref]=[round(ox+dx,2),round(oy+dy,2)]
        break
    else:raise RuntimeError('Could not place '+ref)
(ROOT/'reports/placement-adjustments.json').write_text(json.dumps(moves,indent=2))

def segment(a,z,net,width=.2,layer=k.F_Cu,locked=True):
    t=k.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(net);t.SetLocked(locked);b.Add(t);return t
def xy(p):a=p.GetPosition();return (k.ToMM(a.x),k.ToMM(a.y))
def route(ref1,n1,ref2,n2,width=.2,via=None):
    a=pads[ref1,str(n1)][0];z=pads[ref2,str(n2)][0]
    assert a.GetNetCode()==z.GetNetCode(),(ref1,n1,ref2,n2)
    aa=xy(a);zz=xy(z);points=[aa]+(via or [])+[zz]
    for x,y in zip(points,points[1:]):segment(x,y,a.GetNet(),width)

# Board outline, assembly identification and connector polarity.
for a,z in [((5,7),(98,7)),((98,7),(98,70)),((98,70),(5,70)),((5,70),(5,7))]:
    s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*z));s.SetLayer(k.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
def text(s,x,y,size=1,layer=k.F_SilkS):
    t=k.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(mm(.15));t.SetLayer(layer);b.Add(t)
text('MULTUM IN PARVO  A-DRAFT',54,10,1.2);text('NOT FOR FABRICATION',54,12,1.0)
for s,x,y in [('BAT +   -',13,30),('SOLAR +   -',13,68),('ANT',94,17),('R303: PROTECTED PACK ONLY',52,69)]:text(s,x,y)
for p in data:
    if p['ref'].startswith('TP'):
        # Test-pad labels placed in final silk pass after routing.
        pass

# Ground planes are deliberately omitted over the cell-negative side of protector.
def zone(layer,rect,net='GND',priority=0):
    z=k.ZONE(b);z.SetLayer(layer);z.SetNet(netnames[net]);z.SetLocalClearance(mm(.2));z.SetThermalReliefGap(mm(.25));z.SetThermalReliefSpokeWidth(mm(.25));z.SetPadConnection(k.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.15));z.SetAssignedPriority(priority)
    poly=z.Outline();poly.NewOutline()
    for x,y in rect:poly.Append(mm(x),mm(y))
    b.Add(z);return z
zone(k.B_Cu,[(6,8),(97,8),(97,69),(6,69),(6,49),(21,49),(21,35),(6,35)])
zone(k.F_Cu,[(43,14),(97,14),(97,36),(43,36)])
zone(k.F_Cu,[(6,49),(42,49),(42,68),(6,68)])
zone(k.F_Cu,[(24,32),(44,32),(44,50),(24,50)])

# Ground stitching; holes outside exposed pads. Critical grounds get local vias later.
def groundvia(x,y):
    vi=k.PCB_VIA(b);vi.SetPosition(v(x,y));vi.SetWidth(mm(.6));vi.SetDrill(mm(.3));vi.SetViaType(k.VIATYPE_THROUGH);vi.SetLayerPair(k.F_Cu,k.B_Cu);vi.SetNet(netnames['GND']);b.Add(vi)
for x in range(44,98,3):
    for y in [14,36]:
        if not any(overlap((x-.4,y-.4,x+.4,y+.4),r,.2) for r in placed):groundvia(x,y)

# Export placement first; route geometry is added after clearance checks.
b.BuildListOfNets();b.GetConnectivity().Build(b)
k.SaveBoard(str(ROOT/'mesh-node.kicad_pcb'),b)
print(len(fps),'footprints',len(netnames),'nets')
