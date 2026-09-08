"""Four-sheet presentation rebuilt from the frozen, user-approved connectivity."""
from cad import *
import collections
baseline=json.loads((ROOT/'reports/design-before-rearrange.json').read_text())
lib=parse((LIB/'Node.kicad_sym').read_text())
for node in kids(lib,'symbol'):
 name=unq(node[1]);pins={}
 for unit in kids(node,'symbol'):
  for pin in kids(unit,'pin'):
   a=kid(pin,'at');n=unq(kid(pin,'number')[1]);pins[n]=(float(a[1]),-float(a[2]),int(a[3]),unq(kid(pin,'name')[1]),pin[1])
 symbols[name]=Symbol(name,dump(node),pins)
root=Page('mesh-node','MCU, clocks and debug');root.id=uid('root')
power=Page('power','Solar harvesting and regulated power')
battery=Page('battery','Battery protection, temperature and optional gauge')
radio=Page('radio','EU868 radio matching, RF variants and antenna')
page_sizes={'mesh-node':(420,297),'power':(420,297),'battery':(594,420),'radio':(594,420)}
byref={}
for p in baseline:
 old=p['sheet'];pg=root if old=='01-mcu' else power if old=='02-solar' or (old=='04-rails' and p['group']!='GAUGE') else battery if old in ['03-battery','05-temperature'] or p['group']=='GAUGE' else radio
 pp=pg.add(p['ref'],p['symbol'],p['value'],p['footprint'],p['x'],p['y'],p['nets'],p['rot'],p['dnp'],p['pcb'],p['group'],p['mpn']);byref[p['ref']]=pp
# Derive actual cross-sheet nets; internal RF labels are local, not global.
netpages=collections.defaultdict(set)
for pg in pages.values():
 for p in pg.parts:
  if p['ref'].startswith('#'):continue
  for net in p['nets'].values():
   if net:netpages[net].add(pg.name)
global_nets.clear();global_nets.update(n for n,pgs in netpages.items() if len(pgs)>1);global_nets.update(['GND','PACK_P','3V3_AON','SOLAR_P','VINT'])
def move(ref,x,y,rot=None):
 p=byref[ref];p['x']=round(x/1.27)*1.27;p['y']=round(y/1.27)*1.27
 if rot is not None:p['rot']=rot
# Keep the MCU pin map recognisable and move clocks directly below it.
move('Y101',203.2,213.36);move('C114',172.72,218.44);move('C115',233.68,218.44)
move('Y102',294.64,213.36);move('C116',269.24,218.44);move('C117',320.04,218.44)
# Solar / PMIC page, two adjacent power blocks.
for ref,x,y in [('J201',40.64,71.12),('U201',101.6,99.06),('L201',48.26,109.22),('C201',48.26,76.2),('C202',165.1,121.92)]:move(ref,x,y)
for i,ref in enumerate(['C203','C204','C205','C206']):move(ref,165.1+i*22.86,71.12)
for i,ref in enumerate(['TP201','TP202','TP203','TP204','TP205']):move(ref,25.4+i*43.18,190.5)
for ref,x,y in [('U501',307.34,88.9),('L501',355.6,99.06),('C501',256.54,76.2),('C502',365.76,63.5),('C503',391.16,63.5),('R501',274.32,139.7),('R502',302.26,139.7),('R503',330.2,139.7),('U503',307.34,213.36),('R507',266.7,238.76),('C505',264.16,193.04),('C506',360.68,195.58),('J501',375.92,228.6),('TP501',350.52,162.56),('TP502',386.08,162.56)]:move(ref,x,y)
# Cell protection, compact common-drain FET arrangement; gauge below it.
for ref,x,y in [('J301',40.64,76.2),('U301',96.52,86.36),('R301',53.34,60.96),('C301',66.04,91.44),('R302',55.88,121.92),('Q301',96.52,149.86),('Q302',147.32,149.86),('R303',121.92,195.58),('TP301',25.4,154.94),('TP302',50.8,175.26),('U502',96.52,271.78),('C504',48.26,271.78),('R504',149.86,259.08),('R505',175.26,259.08),('R506',200.66,259.08)]:move(ref,x,y)
# Independent temperature sensing and its gating stage in the right column.
for ref,x,y in [('R401',259.08,71.12),('J401',259.08,119.38),('C401',287.02,114.3),('R402',322.58,66.04),('R403',322.58,104.14),('R404',360.68,66.04),('R405',360.68,104.14),('U401',421.64,71.12),('U402',421.64,124.46),('C402',464.82,66.04),('C403',464.82,124.46),('U403',525.78,71.12),('C404',566.42,71.12),('R412',535.94,121.92),('Q401',294.64,228.6),('Q402',342.9,228.6),('Q405',393.7,228.6),('R406',269.24,259.08),('R407',342.9,259.08),('Q403',457.2,228.6),('R408',434.34,193.04),('R409',508,218.44),('R410',513.08,259.08),('Q404',558.8,228.6),('R411',568.96,266.7)]:move(ref,x,y)
# RF signal flow: normal path across top, FEM in middle, control level shifts below.
for ref,x,y in [('L601',48.26,55.88),('C601',25.4,76.2),('C602',48.26,81.28),('R601',48.26,106.68),('C603',76.2,132.08),('L602',106.68,106.68),('C604',106.68,81.28),('C605',132.08,132.08),('C606',157.48,106.68),('L603',182.88,106.68),('C607',203.2,132.08),('L604',48.26,177.8),('C608',48.26,215.9),('C609',83.82,162.56),('C610',116.84,187.96),('R602',248.92,76.2),('R603',248.92,116.84),('U601',304.8,101.6),('R604',264.16,147.32),('C611',304.8,160.02),('C612',342.9,63.5),('R623',368.3,63.5),('R605',365.76,99.06),('R606',218.44,218.44),('R607',218.44,243.84),('U602',284.48,243.84),('R608',254,187.96),('L605',284.48,187.96),('L606',335.28,187.96),('L607',353.06,220.98),('C621',368.3,243.84),('C622',391.16,243.84),('L608',421.64,220.98),('C623',447.04,243.84),('L609',353.06,276.86),('C624',353.06,259.08),('C625',388.62,299.72),('L610',419.1,276.86),('C626',449.58,299.72),('R609',487.68,276.86),('C627',505.46,99.06),('C628',513.08,137.16),('R610',539.75,99.06),('J601',570.23,99.06),('D601',560.07,137.16)]:move(ref,x,y)
for i,ref in enumerate(['C613','C614','C615','C616','C617','C618','C619','C620']):move(ref,229.87+i*24.13,172.72)
for i in range(3):
 x=63.5+i*172.72
 for ref,xx,yy in [('Q'+str(601+i*2),x,342.9),('Q'+str(602+i*2),x+55.88,368.3),('R'+str(611+i*4),x-27.94,365.76),('R'+str(612+i*4),x+27.94,327.66),('R'+str(613+i*4),x+76.2,335.28),('R'+str(614+i*4),x+91.44,368.3),('TP'+str(601+i),x+116.84,350.52)]:move(ref,xx,yy)
# Preserve power-source ERC flags, in a clearly separated strip.
for pg in pages.values():
 flag=[p for p in pg.parts if p['ref'].startswith('#')]
 for i,p in enumerate(flag):move(p['ref'],25.4+i*38.1,243.84 if pg is root else page_sizes[pg.name][1]-35.56)
for pg in pages.values():pg.text(15.24,12.7,pg.title,2.0)
root.text(20.32,20.32,'STM32WLE5CCU6 | LP PA pin 22; HP PA pin 23 unused | SWD/UART | 32 MHz + RTC',1.27)
power.text(15.24,20.32,'SOLAR cold Voc <=4.3V | AEM: 80% Voc MPPT, 4.05V charge | Battery supplies RF pulses directly.',1.27)
battery.text(15.24,20.32,'CELL_N is cell-side only. All chargers, loads and debug grounds connect to PACK- / GND.',1.27)
radio.text(15.24,20.32,'EU868 ST LP matching / optional SKY66423 EK3 network. Fit only NORMAL or FEM selectors. +27dBm requires regional limits.',1.27)
exec((ROOT/'tools/paper_routes.py').read_text())
# Direct local supply/input wires kept explicit for reader-friendly power flow.
power.connect((byref['U501'],'6'),(byref['C502'],'1'),via=[(345.44,83.82),(345.44,55.88),(365.76,55.88)])
power.connect((byref['J201'],'1'),(byref['U201'],'2'),via=[(30.48,71.12),(30.48,50.8),(76.2,50.8),(76.2,82.55)])
radio.connect((byref['R609'],'2'),(byref['C627'],'1'),via=[(495.3,276.86),(495.3,99.06)])
radio.connect((byref['C609'],'2'),(byref['R603'],'1'),via=[(198.12,162.56),(198.12,116.84)])
radio.connect((byref['C609'],'2'),(byref['R607'],'1'),via=[(198.12,162.56),(198.12,243.84)])
for x,y in [(495.3,99.06),(198.12,162.56)]:radio.items.append(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {q(uid("manualRF"+str(x)+str(y)))}))')
radio.text(365.76,40.64,'NORMAL: R602/R603/R605 fitted; FEM selectors open.\nFEM: R606/R607/R609 fitted; normal selectors open.\nCTRL 0=TX, 1=RX. PA11 powers the normal switch.\nBefore sleep: CTRL low, then PA11 low; wake settling >=20us.',1.27)
battery.text(25.4,218.44,'RAW CELL: PROTECT group fitted, R303 open.\nPROTECTED PACK: R303 fitted, PROTECT group omitted.',1.27)
battery.text(254,299.72,'Hardware window: nominal 4.7...40.2 C; NTC at the cell.\nTLV7031S pinout is required. Solar-valid threshold ~2.63 V.\nTemperature networks are solar-fed; MCU inhibit cannot override them.',1.27)
power.text(25.4,218.44,'AEM STO_CFG=0000: 4.05 V charge / 3.5 V ready / 3.0 V low.\nR_MPP=100: 80% Voc. T_MPP=01: 4.5 s / 70.8 ms. EN_HP=1.\nTPS63900 SEL=0, CFG3=16.2k: 3.3 V; alternate state also 3.3 V.\nNo peripheral GPIO on J501: switched power only.',1.27)
# Save exactly four sheets; MCU is the root instead of a fifth overview page.
for pg in pages.values():
 pg.save(root.id)
 fp=ROOT/(pg.name+'.kicad_sch');txt=fp.read_text()
 if page_sizes[pg.name][0]>420:txt=txt.replace('(paper "A3")','(paper "A2")')
 if pg is root:
  txt=txt.replace('/'+root.id+'/'+root.id,'/'+root.id)
  extra=[]
  for i,ch in enumerate([power,battery,radio]):
   x=20.32+i*129.54;y=266.7
   extra.append(f'(sheet (at {x} {y}) (size 116.84 12.7) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {q(ch.id)}) (property "Sheetname" {q(ch.title)} (at {x} {y-1.27} 0) {eff(1.016,"(justify left bottom)")}) (property "Sheetfile" {q(ch.name+".kicad_sch")} (at {x} {y+13.97} 0) {eff(1.016,"(justify left top)")}) (instances (project "mesh-node" (path "/{root.id}" (page {q(i+2)})))))')
  txt=txt.rstrip()[:-1]+''.join(extra)+f'(sheet_instances (path "/" (page "1"))))'
 fp.write_text(txt)
clean=[{k:v for k,v in p.items() if k!='wired'} for p in parts]
(ROOT/'design.json').write_text(json.dumps(clean,indent=2))
print('Four sheets:',[(p.name,len(p.parts)) for p in pages.values()])
