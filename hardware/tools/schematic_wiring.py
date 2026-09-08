"""Deliberate visible wiring for the ST PA matching and balun circuits."""
def circuit_wires(pg,net,terminals,spine):
    byref={p['ref']:p for p in pg.parts}
    points=[]
    for ref,n in terminals:
        p=byref[ref];assert p['nets'][str(n)]==net,(ref,n,net)
        points.append(pg.point(p,str(n)));p.setdefault('wired',set()).add(str(n))
    # Explicit polyline skeleton, with junctions at branch intersections.
    for a,b in zip(spine,spine[1:]):pg.wire(a,b)
    for i,pt in enumerate(points):
        dst=min(spine,key=lambda a:abs(a[0]-pt[0])+abs(a[1]-pt[1]))
        if pt!=dst:
            elbow=(dst[0],pt[1]);pg.wire(pt,elbow);pg.wire(elbow,dst)
    for pt in spine:
        pg.items.append(f'(junction (at {pt[0]} {pt[1]}) (diameter 0) (color 0 0 0 0) (uuid {q(uid(pg.name+net+str(pt)))}))')
    # One net label retains cross-sheet connectivity without repeated pin labels.
    pg.label(net,spine[0])
rf=pages['06-radio']
circuit_wires(rf,'PA_MATCH',[('L601',2),('R601',2),('C603',1),('L602',1),('C604',1)],[(60.96,66.04),(60.96,91.44),(60.96,119.38),(60.96,135.89)])
circuit_wires(rf,'PA_NOTCH',[('L602',2),('C604',2),('C605',1),('C606',1)],[(106.68,91.44),(106.68,119.38),(106.68,135.89)])
circuit_wires(rf,'PA_DC',[('C606',2),('L603',1)],[(144.78,119.38)])
circuit_wires(rf,'RF_TX50',[('L603',2),('C607',1)],[(182.88,119.38),(182.88,135.89)])
# RF grounds return downward on a visible local bus.
circuit_wires(rf,'GND',[('C603',2),('C605',2),('C607',2)],[(60.96,149.86),(106.68,149.86),(182.88,149.86)])
circuit_wires(rf,'MCU_RFIP',[('L604',1),('C609',1)],[(40.64,172.72),(40.64,184.15)])
circuit_wires(rf,'MCU_RFIN',[('L604',2),('C608',1)],[(40.64,210.82)])
circuit_wires(rf,'RF_RX50',[('C609',2),('C610',1)],[(109.22,172.72),(109.22,189.23)])
