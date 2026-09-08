from cad import ROOT,parse,dump,kids,kid,unq,q
p=ROOT/'reports/mesh-node.dsn';t=parse(p.read_text().replace('(string_quote ")','(string_quote "QUOTE")'))
network=kid(t,'network');network[:]=[n for n in network if not (isinstance(n,list) and n[0]=='net' and unq(n[1])=='GND')];names=[unq(n[1]) for n in kids(network,'net')]
network[:]=[n for n in network if not isinstance(n,list) or n[0]!='class']
wide={'RF_TX50','RF_RX50','ANT_TUNE_IN','ANT_PI','ANT','FEM_FINAL','FEM_FILTER'}
rf={'MCU_RFO_LP','MCU_RFIP','MCU_RFIN','VR_PA','PA_MATCH','PA_NOTCH','PA_DC','SW_TX','SW_RX','SW_ANT','FEM_TX','FEM_RX','FEM_ANT','FEM_PA','FEM_TXIN','OMN1','FEM_RXLOOP'}
power={'PACK_P','CELL_N','FET_MID','3V3_AON','3V3_SW'}
groups={n:[] for n in ['RF50','RF_MATCH','POWER','DEFAULT']}
for n in names:
 s=n.rsplit('/',1)[-1];g='RF50' if s in wide else 'RF_MATCH' if s in rf else 'POWER' if s in power else 'DEFAULT';groups[g].append(q(n))
for g,ns in groups.items():
 width={'RF50':750,'RF_MATCH':150,'POWER':400,'DEFAULT':150}[g]
 network.append(['class',q(g),*ns,['circuit',['use_via','"Via[0-1]_600:300_um"'],*([['use_layer','F.Cu']] if g.startswith('RF') else [])],['rule',['width',str(width)],['clearance','150']]])
struct=kid(t,'structure');rules=kid(struct,'rule')
for c in kids(rules,'clearance'):
 if len(c)==2:c[1]='150'
# Keep the underside of the RF chain free of ordinary routed copper/vias.
struct.append(['keepout','"RF_GROUND_RESERVE"',['rect','B.Cu','56000','-35500','97000','-12000']])
p.write_text(dump(t).replace('(string_quote "QUOTE")','(string_quote ")'))
print('RF top-only, 0.75mm 50-ohm corridors, 0.6mm power, .15mm clearance')
