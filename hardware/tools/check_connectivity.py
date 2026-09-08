from cad import ROOT,parse,kid,kids,unq
import json

def sets(path):
 out={}
 for net in kids(kid(parse(path.read_text()),'nets'),'net'):
  pins=frozenset((unq(kid(n,'ref')[1]),unq(kid(n,'pin')[1])) for n in kids(net,'node') if not unq(kid(n,'ref')[1]).startswith('#'))
  if pins:out[pins]=unq(kid(net,'name')[1])
 return out
before=sets(ROOT/'reports/netlist-before-rearrange.net');after=sets(ROOT/'reports/four-page.net')
missing=[{'name':before[s],'pins':sorted(s)} for s in before.keys()-after.keys()];extra=[{'name':after[s],'pins':sorted(s)} for s in after.keys()-before.keys()]
r={'identical_pin_connectivity':not missing and not extra,'nets_before':len(before),'nets_after':len(after),'missing':missing,'extra':extra}
(ROOT/'reports/connectivity-comparison.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['identical_pin_connectivity']
