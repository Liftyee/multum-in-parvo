import pcbnew as k,json
from cad import ROOT
b=k.LoadBoard(str(ROOT/'mesh-node.kicad_pcb'));parts=[];tracks=[]
for f in b.GetFootprints():
 pads=[]
 for p in f.Pads():
  if not p.IsOnLayer(k.F_Cu):continue
  pads.append(dict(n=p.GetNumber(),x=k.ToMM(p.GetPosition().x),y=k.ToMM(p.GetPosition().y),w=k.ToMM(p.GetSize().x),h=k.ToMM(p.GetSize().y),rot=p.GetOrientationDegrees(),net=p.GetNetname()))
 parts.append(dict(ref=f.GetReference(),x=k.ToMM(f.GetPosition().x),y=k.ToMM(f.GetPosition().y),pads=pads))
for t in b.GetTracks():
 tracks.append(dict(via=isinstance(t,k.PCB_VIA),x=k.ToMM(t.GetStart().x),y=k.ToMM(t.GetStart().y),xx=k.ToMM(t.GetEnd().x),yy=k.ToMM(t.GetEnd().y),w=k.ToMM(t.GetWidth()),layer=t.GetLayerName(),net=t.GetNetname()))
(ROOT/'reports/plot-data.json').write_text(json.dumps(dict(parts=parts,tracks=tracks)))
