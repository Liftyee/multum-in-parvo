"""Circuit definition. All pin numbers refer to manufacturer top views."""
from cad import *
for lib,name in [('Device','R'),('Device','C'),('Device','L'),('Device','Crystal'),('Device','Crystal_GND24'),('Device','Q_NMOS_GSD'),('Device','Q_PMOS_GSD'),('Connector_Generic','Conn_01x02'),('Connector_Generic','Conn_01x06'),('Connector','TestPoint'),('MCU_ST_STM32WL','STM32WLE5CCUx')]:standard(lib,name)
P='power_in';I='input';O='output';B='bidirectional';A='passive';NC='no_connect'
ic('AEM10300',[(2,'SRC',P),(28,'CS_IN',A),(4,'BUFSRC',A),(5,'LIN',A),(6,'LOUT',A),(1,'ZMPP',A),(8,'R_MPP2',I),(9,'R_MPP1',I),(11,'R_MPP0',I),(22,'T_MPP1',I),(20,'T_MPP0',I)],[(14,'STO',A),(10,'VINT','power_out'),(12,'EN_STO_CH',I),(26,'ST_STO',O),(21,'EN_STO_FT',I),(19,'EN_HP',I),(18,'STO_CFG3',I),(25,'STO_CFG2',I),(24,'STO_CFG1',I),(23,'STO_CFG0',I),(17,'STO_OVCH',I),(16,'STO_RDY',I),(15,'STO_OVDIS',I),(13,'BAL',A)],bottom=[(3,'GND',P),(7,'GND',P),(27,'GND',P),(29,'EP',P)],width=35.56)
ic('BQ29700',[(5,'BAT',P),(6,'V-',I),(1,'NC',NC)],[(3,'DOUT',O),(2,'COUT',O)],bottom=[(4,'VSS_CELL',P)],width=20.32)
ic('TPS63900',[(10,'VIN',P),(1,'EN',I),(2,'SEL',I),(3,'CFG1',I),(4,'CFG2',I),(5,'CFG3',I)],[(6,'VOUT','power_out'),(9,'LX1',A),(7,'LX2',A)],bottom=[(8,'GND',P),(11,'EP',P)],width=25.4)
ic('MAX17048',[(3,'VDD',P),(2,'CELL',I),(6,'QSTRT',I)],[(7,'SCL',I),(8,'SDA','open_collector'),(5,'ALRT','open_collector')],bottom=[(1,'CTG',P),(4,'GND',P),(9,'EP',P)],width=25.4)
ic('TLV3691DCK',[(1,'IN+',I),(3,'IN-',I)],[(4,'OUT',O)],top=[(5,'VCC',P)],bottom=[(2,'GND',P)],width=17.78)
ic('TPS22919',[(1,'IN',P),(3,'ON',I),(4,'NC',NC)],[(6,'OUT','power_out'),(5,'QOD',A)],bottom=[(2,'GND',P)],width=20.32)
ic('SKY66423-11',[(1,'TX',I),(2,'RX',O),(3,'TX_ALT',I),(4,'CSD',I),(5,'CPS',I),(6,'CTX',I)],[(13,'PA_OUT',A),(11,'TX_IN',I),(9,'ANT',B),(7,'LNA_IN',I),(8,'RX_FLT',O),(14,'NC',NC)],top=[(15,'VCC0',P),(16,'VCC1',P)],bottom=[(10,'GND',P),(12,'GND',P),(17,'EP',P)],width=30.48)
ic('BGS12SN6',[(3,'RF1',A),(1,'RF2',A),(6,'CTRL',I)],[(5,'RFIN',A)],top=[(4,'VDD',P)],bottom=[(2,'GND',P)],width=17.78)
ic('UFL',[(1,'RF',A)],[],bottom=[(2,'GND',A)],width=10.16)
RFP='Node:R0402';CFP='Node:C0402';R6='Node:R0603';C6='Node:C0603';C8='Node:C0805';C12='Node:C1210';LFP='Node:L0402'
def comp(pg,ref,val,a,b,x,y,pcb,rot=90,dnp=False,group='',fp=None,mpn=''):
    sym={'R':'R','C':'C','L':'L','Y':'Crystal'}[ref[0]]
    fp=fp or {'R':R6,'C':C6,'L':LFP,'Y':'Node:Crystal2012'}[ref[0]]
    return pg.add(ref,sym,val,fp,x,y,{1:a,2:b},rot,dnp,pcb,group,mpn)
def tp(pg,ref,net,x,y,pcb):return pg.add(ref,'TestPoint',net,'Node:TestPad',x,y,{1:net},pcb=pcb)
def box(pg,x,y,title,lines):
    pg.text(x,y,title,2.0);pg.text(x,y+6,lines,1.27)

# 1. MCU, clocks and local supplies.
m=Page('01-mcu','MCU, clocks and debug')
u=m.add('U101','STM32WLE5CCUx','STM32WLE5CCU6','Node:STM32WLE5_QFN48',100.33,101.6,
 {11:'3V3_AON',44:'3V3_AON',37:'3V3_AON',41:'VDDA',49:'GND',46:'3V3_AON',47:'MCU_LX',45:'RF1V55',48:'GND',29:'RF1V55',25:'RF1V55',28:'3V3_AON',24:'VR_PA',23:None,22:'MCU_RFO_LP',20:'MCU_RFIP',21:'MCU_RFIN',26:'HSE_IN',27:'HSE_OUT',30:None,39:'LSE_IN',40:'LSE_OUT',18:'NRST',19:'BOOT0',42:'SWDIO',43:'SWCLK',4:'UART_TX',5:'UART_RX',7:'CHG_INHIBIT',8:'FEM_CSD',9:'FEM_CTX',10:'FEM_CPS',12:'PERIPH_EN',13:'GAUGE_ALERT',15:'I2C_SCL',16:'I2C_SDA',38:'RF_SW',34:'RF_SW_SUPPLY'},pcb=[51,29,180])
global_nets.update(['MCU_RFO_LP','MCU_RFIP','MCU_RFIN','VR_PA','RF_SW_SUPPLY'])
box(m,20,18,'STM32WLE5 / QFN48 / 256 KB','ST MB1720 HighBand LowPower A-01 pin map and RF circuit.\nRFO_HP (pin 23) intentionally unused. Normal variant uses +14 dBm LP PA.\nFirmware port and timing/power validation are required for Meshtastic.')
for i,(ref,val,net,xy) in enumerate([('C101','100nF','3V3_AON',[48,33,0]),('C102','100nF','3V3_AON',[54,25,0]),('C103','100nF','3V3_AON',[49,24,0]),('C104','4.7uF','3V3_AON',[48,35,0]),('C105','100nF','VDDA',[55,25,0]),('C106','4.7uF','VDDA',[56,23,0]),('C107','100nF','3V3_AON',[55,32,0]),('C108','4.7uF','3V3_AON',[56,34,0])]):
    c=comp(m,ref,val,net,'GND',190.5+(i%4)*30.48,55.88+(i//4)*35.56,xy,rot=0)
fb=comp(m,'L101','600R@100MHz','3V3_AON','VDDA',243.84,129.54,[55,27,0],fp='Node:L0603',mpn='BLM18AG601SN1D')
sl=comp(m,'L102','15uH','MCU_LX','RF1V55',213.36,165.1,[54.5,33,90],fp='Node:L2520',mpn='LQM2MPN150MEHL')
comp(m,'C109','470nF','RF1V55','GND',243.84,175.26,[56.5,31.5,90],rot=0)
comp(m,'C110','100nF','RF1V55','GND',269.24,175.26,[54.5,30.8,90],rot=0)
for i,net in enumerate(['3V3_AON','RF1V55']):comp(m,'C'+str(111+i),'33pF',net,'GND',299.72+i*25.4,175.26,[54.5+i*1.6,29.8,90],rot=0,fp=CFP)
comp(m,'R101','100k','BOOT0','GND',45.72,165.1,[47,28,90],rot=0)
comp(m,'C113','100nF','NRST','GND',45.72,203.2,[48,25,90],rot=0)
y=m.add('Y101','Crystal_GND24','32MHz CL=10pF','Node:Crystal3225',203.2,228.6,{1:'HSE_IN',3:'HSE_OUT',2:'GND',4:'GND'},pcb=[57,28,90],mpn='ABM8-32.000MHZ-10-D1G-T')
comp(m,'C114','6.8pF','HSE_IN','GND',172.72,233.68,[55.5,27.2,90],rot=0,fp=CFP)
comp(m,'C115','6.8pF','HSE_OUT','GND',233.68,233.68,[55.5,28.8,90],rot=0,fp=CFP)
comp(m,'Y102','32.768kHz CL=7pF','LSE_IN','LSE_OUT',294.64,228.6,[45.5,25,90],rot=0,fp='Node:Crystal3215',mpn='ABS07-32.768KHZ-7-T')
comp(m,'C116','6.8pF','LSE_IN','GND',269.24,233.68,[46.8,23.5,90],rot=0,fp=CFP)
comp(m,'C117','6.8pF','LSE_OUT','GND',320.04,233.68,[46.8,25.2,90],rot=0,fp=CFP)
m.add('J101','Conn_01x06','SWD / UART','Node:Header1x6',353.06,78.74,{1:'3V3_AON',2:'GND',3:'SWDIO',4:'SWCLK',5:'NRST',6:'UART_TX'},pcb=[44,43,90])
for i,n in enumerate(['SWDIO','SWCLK','NRST','UART_TX','UART_RX']):tp(m,'TP'+str(101+i),n,350.52,119.38+i*15.24,[47+i*3,40,0])
box(m,20,247,'Clock configuration','LSE: 6.8pF/2 + estimated 3.6pF parasitic = 7pF. Validate oscillator margin.\nHSE: 6.8pF external values follow MB1720; internal trim must be calibrated\nfor the selected crystal CL. Keep all oscillator nets away from switch nodes.')

# 2. Harvester.
s=Page('02-solar','Solar MPPT and storage bus')
box(s,20,18,'AEM10300 / photovoltaic / 4.05 V long-life charge','Panel maximum cold Voc <= 4.3 V; SRC operating limit is 4.5 V.\nNo nominal 6 V panels. EN_STO_FT is strapped LOW.\n4.05 V preset avoids continuous custom-divider loss; do not use 4.35 V preset.')
s.add('J201','Conn_01x02','SOLAR + / -','Node:JST_PH_2',35.56,78.74,{1:'SOLAR_P',2:'GND'},pcb=[10,60,180],mpn='B2B-PH-K-S(LF)(SN)')
a=s.add('U201','AEM10300','AEM10300','Node:AEM10300_QFN28',152.4,116.84,{2:'SOLAR_P',28:None,4:'AEM_BUF',5:'AEM_LIN',6:'AEM_LOUT',1:None,8:'VINT',9:'GND',11:'GND',22:'GND',20:'VINT',14:'PACK_P',10:'VINT',12:'CHG_ENABLE',26:'AEM_STATUS',21:'GND',19:'VINT',18:'GND',25:'GND',24:'GND',23:'GND',17:None,16:None,15:None,13:'GND',3:'GND',7:'GND',27:'GND',29:'GND'},pcb=[20,53,0])
comp(s,'L201','10uH','AEM_LIN','AEM_LOUT',71.12,132.08,[16,53.5,90],fp='Node:L2520',mpn='DFE252010F-100M')
comp(s,'C201','22uF 10V','AEM_BUF','GND',71.12,106.68,[16.8,50.3,90],rot=0,fp=C8,mpn='GRM21BR61A226ME44L')
comp(s,'C202','10uF 6.3V','VINT','GND',223.52,96.52,[20.5,56.5,0],rot=0,fp=C8)
for i in range(4):comp(s,'C'+str(203+i),'100uF 10V','PACK_P','GND',264.16+i*30.48,86.36,[26+i*4,49,90],rot=0,fp=C12,mpn='GRM32ER61A107ME20L')
box(s,231,117,'Storage capacitance','4 x 100uF / 10V / 1210 X5R.\nRequire >=100uF EFFECTIVE at 4.05 V\nincluding DC bias, tolerance and temperature.\nBattery supplies TX pulses directly from PACK+.')
box(s,30,188,'Strap choices from AEM10300 v1.5','STO_CFG[3:0] = 0000: 4.05 V charge, 3.50 V ready, 3.00 V low status.\nR_MPP[2:0] = 100: 80% Voc. T_MPP[1:0] = 01: 4.5 s / 70.8 ms.\nEN_HP=1; high-power harvest mode. CS_IN, ZMPP and custom sense pins open.\nST_STO can rise to PACK voltage. Test pad only; no direct 3.3 V MCU connection.\nAll grounds on this page are protected PACK- / system GND.')
for i,n in enumerate(['SOLAR_P','PACK_P','VINT','CHG_ENABLE','AEM_STATUS']):tp(s,'TP'+str(201+i),n,40.64+i*60.96,246.38,[12+i*4,66,0])

# 3. Cell protector. Common drain, source at cell-/pack- respectively.
b=Page('03-battery','Raw cell protection and bypass variant')
box(b,20,18,'BQ29700 / common-drain back-to-back N-MOSFETs','Cell + is PACK+ electrically; protection interrupts the negative conductor.\nNo system copper, test equipment ground, charger or load may connect to CELL_N.\nDefault raw-cell build: U301, Q301, Q302 populated; R303 OPEN / DNP.')
b.add('J301','Conn_01x02','BAT + / CELL-','Node:JST_PH_2',40.64,81.28,{1:'PACK_P',2:'CELL_N'},pcb=[10,39,180],mpn='B2B-PH-K-S(LF)(SN)')
b.add('U301','BQ29700','BQ29700DSET','Node:BQ29700_WSON6',147.32,101.6,{5:'BMS_BAT',6:'BMS_VM',3:'DSG_GATE',2:'CHG_GATE',4:'CELL_N'},pcb=[17,40,0],group='PROTECT')
comp(b,'R301','330R','PACK_P','BMS_BAT',93.98,71.12,[16,37,0],group='PROTECT')
comp(b,'C301','100nF','BMS_BAT','CELL_N',119.38,78.74,[18,38,0],rot=0,group='PROTECT')
comp(b,'R302','2.2k','BMS_VM','GND',99.06,111.76,[19,42,0],group='PROTECT')
b.add('Q301','Q_NMOS_GSD','AO3400A / DSG','Node:SOT23',177.8,160.02,{1:'DSG_GATE',2:'CELL_N',3:'FET_MID'},pcb=[14.5,43.5,0],group='PROTECT',mpn='AO3400A')
b.add('Q302','Q_NMOS_GSD','AO3400A / CHG','Node:SOT23',228.6,160.02,{1:'CHG_GATE',2:'GND',3:'FET_MID'},pcb=[18,45.5,180],group='PROTECT',mpn='AO3400A')
comp(b,'R303','0R BYPASS - DNP','CELL_N','GND',203.2,205.74,[12,47.5,0],dnp=True,fp='Node:R1206',group='PROTECTED_PACK_ONLY')
box(b,260,72,'Population interlock','RAW CELL: populate PROTECT group; R303 DNP.\nPROTECTED PACK: R303=0R; PROTECT group DNP.\nNever use R303 with an unprotected cell.\nThe only bypass connects CELL- to PACK-.\nIt cannot short PACK+ to PACK-.')
box(b,260,132,'MOSFET selection change','AO3400A replaces CSD16301Q2.\nSpecified Rds(on) <=48mOhm at Vgs=2.5V.\nCSD16301Q2 only specifies on-resistance\nat 4.5V; low-cell operation needs margin.\n2 FETs: <=96mOhm at 25C; 300mA ->\n28.8mV and 8.64mW total (excludes traces).')
box(b,25,228,'Independent hardware protection','BQ29700: OVP 4.275 V; UVP 2.800 V; overcurrent +/-100mV nominal.\nKelvin-route VSS and V- to cell-side / pack-side source pads.\nSystem operating floor 3.0 V; reserve headroom for burst droop and protection tolerance.\nBring-up: verify body-diode orientation and protection release before attaching a cell.')
tp(b,'TP301','PACK_P',45.72,152.4,[10,34,0]);tp(b,'TP302','GND',71.12,152.4,[22,39,0])

# 4. 3V3 conversion and optional loads.
p=Page('04-rails','Regulator, optional gauge and switched peripherals')
box(p,20,18,'TPS63900 / 3V3_AON','SEL=0; CFG3=16.2k selects 3.3 V. CFG1=36.5k and CFG2=0 selects\n3.3 V / unlimited input-current setting for the alternate state too.\n1% configuration resistors; sampled at startup, no continuous divider load.')
p.add('U501','TPS63900','TPS63900DSKR','Node:TPS63900_WSON10',101.6,91.44,{10:'PACK_P',1:'PACK_P',2:'GND',3:'CFG1',4:'CFG2',5:'CFG3',6:'3V3_AON',9:'TPS_LX1',7:'TPS_LX2',8:'GND',11:'GND'},pcb=[32,37,0])
comp(p,'L501','2.2uH','TPS_LX1','TPS_LX2',162.56,101.6,[35.3,37,90],fp='Node:L2520',mpn='DFE252012F-2R2M')
for ref,val,net,xy,px in [('C501','22uF 10V','PACK_P',[32,33.5,0],40.64),('C502','22uF 10V','3V3_AON',[32,40.5,0],208.28),('C503','22uF 10V','3V3_AON',[35,40.5,0],238.76)]:comp(p,ref,val,net,'GND',px,78.74,xy,rot=0,fp=C8)
for i,val in enumerate(['36.5k 1%','0R','16.2k 1%']):comp(p,'R'+str(501+i),val,'CFG'+str(i+1),'GND',40.64+i*25.4,142.24,[29,35+i*2,90],rot=0)
p.add('U502','MAX17048','MAX17048G+ OPTIONAL','Node:MAX17048_TDFN8',101.6,208.28,{3:'PACK_P',2:'PACK_P',6:'GND',7:'I2C_SCL',8:'I2C_SDA',5:'GAUGE_ALERT',1:'GND',4:'GND',9:'GND'},dnp=True,pcb=[29,45,0],group='GAUGE',mpn='MAX17048G+')
comp(p,'C504','100nF','PACK_P','GND',50.8,203.2,[29,42.5,0],rot=0,dnp=True,group='GAUGE')
for i,net in enumerate(['I2C_SCL','I2C_SDA','GAUGE_ALERT']):comp(p,'R'+str(504+i),'10k' if i<2 else '100k','3V3_AON',net,157.48+i*25.4,203.2,[32+i*2,45,90],rot=0,dnp=True,group='GAUGE')
box(p,25,246,'OPTIONAL / DNP FOR MINIMUM QUIESCENT CURRENT','MAX17048 group is DNP by default; enable hibernate in firmware if fitted.\n10k pullups with <=100pF bus: estimated rise time 0.847us at 100kHz.\nThis I2C bus stays on board; switched peripheral connector carries power only.')
p.add('U503','TPS22919','TPS22919DCKR','Node:SC70_6',304.8,106.68,{1:'3V3_AON',3:'PERIPH_EN',6:'3V3_SW',5:'3V3_SW',2:'GND'},pcb=[40,46,0],group='PERIPH')
comp(p,'R507','1M','PERIPH_EN','GND',269.24,137.16,[37.5,46,90],rot=0,group='PERIPH')
comp(p,'C505','1uF','3V3_AON','GND',271.78,81.28,[40,43.5,0],rot=0,group='PERIPH')
comp(p,'C506','1uF','3V3_SW','GND',353.06,96.52,[40,48.5,0],rot=0,group='PERIPH')
p.add('J501','Conn_01x02','3V3_SW / GND','Node:Header1x2',365.76,144.78,{1:'3V3_SW',2:'GND'},pcb=[44,48,0],group='PERIPH')
box(p,259,174,'Expansion power','TPS22919 defaults off; QOD discharges output.\nDo not externally power 3V3_SW.\nNo GPIO connections avoids phantom power.\nPeripheral budget <=100mA during MCU TX.\nFEM is supplied directly from PACK+, not 3V3.')
tp(p,'TP501','3V3_AON',294.64,238.76,[37,33,0]);tp(p,'TP502','3V3_SW',337.82,238.76,[43,50,0])

# Temperature and RF added by modules to keep definitions reviewable.
exec((ROOT/'tools/temperature.py').read_text())
exec((ROOT/'tools/radio.py').read_text())
# Correct generic library electrical direction on two internal-regulator outputs.
st=symbols['STM32WLE5CCUx'];tree=parse(st.body)
for unit in kids(tree,'symbol'):
    for pin in kids(unit,'pin'):
        n=unq(kid(pin,'number')[1])
        if n in ['24','47','34']:
            pin[1]='power_out';old=st.pins[n];st.pins[n]=old[:4]+('power_out',)
st.body=dump(tree)
# Supply flags document external sources and nodes beyond passive filters.
standard('power','PWR_FLAG')
for pg,nets in [(m,['VDDA','RF1V55']),(s,['SOLAR_P','PACK_P','GND']),(pages['03-battery'],['CELL_N','BMS_BAT']),(f,['FEM_VCC0','FEM_VCC1'])]:
    for j,net in enumerate(nets):
        pg.add('#FLG'+str(len(parts)),'PWR_FLAG','PWR_FLAG','',355.6+j*12.7,55.88,{1:net})
exec((ROOT/'tools/schematic_wiring.py').read_text())
# Wire aligned local nodes instead of repeating labels on each part in a chain.
for pg in pages.values():
    if pg.name=='06-radio':continue
    points={}
    for part in pg.parts:
        for num,net in part['nets'].items():
            if net is not None:points.setdefault(net,[]).append((part,num,pg.point(part,num)))
    for net,pins in points.items():
        if net in global_nets and net not in ['GND','3V3_AON','PACK_P']:continue
        for i,(aa,an,ap) in enumerate(pins):
            for bb,bn,bp in pins[i+1:]:
                if aa is bb:continue
                if ap[0]!=bp[0] and ap[1]!=bp[1]:continue
                dist=abs(ap[0]-bp[0])+abs(ap[1]-bp[1])
                if not 3<dist<45:continue
                # restrict to two-terminal passives to keep wires out of IC bodies
                if aa['symbol'] not in ['R','C','L'] or bb['symbol'] not in ['R','C','L']:continue
                if (ap[0]==bp[0] and aa['rot']==0) or (ap[1]==bp[1] and aa['rot']==90):continue
                pg.connect((aa,an),(bb,bn))
                # Label one endpoint to retain connections to non-aligned members.
                pg.label(net,ap)
save()
