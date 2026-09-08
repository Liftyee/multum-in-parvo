"""Project-local KiCad 8 footprints; standard library land patterns copied locally."""
from cad import ROOT,LIB,parse,dump,kids,kid,unq
import pcbnew as k
FP=LIB/'Node.pretty';FP.mkdir(exist_ok=True)
def layerset(xs):
    r=k.LSET()
    for x in xs:r.AddLayer(x)
    return r
def mm(x):return k.FromMM(x)
def vec(x,y):return k.VECTOR2I(mm(x),mm(y))
def copy(name,lib,src):
    f=k.FootprintLoad('/usr/share/kicad/footprints/'+lib+'.pretty',src)
    if f is None:raise ValueError(src)
    f.SetFPID(k.LIB_ID('Node',name));f.SetValue(name)
    for p in f.Pads():p.SetLocalSolderMaskMargin(mm(.025))
    k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(FP),f)
    srcp=FP/(src+'.kicad_mod');dst=FP/(name+'.kicad_mod')
    if srcp.exists() and srcp!=dst:srcp.rename(dst)
    return f
mapping={
 'R0402':('Resistor_SMD','R_0402_1005Metric'), 'R0603':('Resistor_SMD','R_0603_1608Metric'),
 'R0805':('Resistor_SMD','R_0805_2012Metric'), 'R1206':('Resistor_SMD','R_1206_3216Metric'),
 'C0402':('Capacitor_SMD','C_0402_1005Metric'),'C0603':('Capacitor_SMD','C_0603_1608Metric'),
 'C0805':('Capacitor_SMD','C_0805_2012Metric'),'C1210':('Capacitor_SMD','C_1210_3225Metric'),
 'L0402':('Inductor_SMD','L_0402_1005Metric'),'L0201':('Inductor_SMD','L_0201_0603Metric'),
 'L0603':('Inductor_SMD','L_0603_1608Metric'),'L2520':('Inductor_SMD','L_1008_2520Metric'),
 'SOT23':('Package_TO_SOT_SMD','SOT-23'),'SC70_5':('Package_TO_SOT_SMD','SOT-353_SC-70-5'),
 'SC70_6':('Package_TO_SOT_SMD','SOT-363_SC-70-6'),
 'JST_PH_2':('Connector_JST','JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical'),
 'Header1x2':('Connector_PinHeader_2.54mm','PinHeader_1x02_P2.54mm_Vertical'),
 'Header1x6':('Connector_PinHeader_2.54mm','PinHeader_1x06_P2.54mm_Vertical'),
 'UFL':('Connector_Coaxial','U.FL_Hirose_U.FL-R-SMT-1_Vertical'),
 'ESD0402':('Diode_SMD','D_SOD-882'),
 'STM32WLE5_QFN48':('Package_DFN_QFN','QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm'),
 'TPS63900_WSON10':('Package_SON','WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm'),
 'BQ29700_WSON6':('Package_SON','WSON-6_1.5x1.5mm_P0.5mm'),
 'MAX17048_TDFN8':('Package_DFN_QFN','TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm'),
 'Crystal3225':('Crystal','Crystal_SMD_3225-4Pin_3.2x2.5mm'),
 'Crystal2012':('Crystal','Crystal_SMD_2012-2Pin_2.0x1.2mm'),
 'Crystal3215':('Crystal','Crystal_SMD_3215-2Pin_3.2x1.5mm'),
 'TestPad':('TestPoint','TestPoint_Pad_D1.5mm')}
for name,(lib,src) in mapping.items():copy(name,lib,src)
def custom(name,n,pitch,body,lead_len,lead_width,lead_center,ep):
    f=k.FOOTPRINT(None);f.SetFPID(k.LIB_ID('Node',name));f.SetReference('REF**');f.SetValue(name);f.SetAttributes(k.FP_SMD)
    f.Reference().SetPosition(vec(0,-body/2-1.4));f.Reference().SetTextSize(vec(1,1));f.Reference().SetTextThickness(mm(.15))
    def pad(num,x,y,sx,sy,layers=None):
        p=k.PAD(f);p.SetNumber(str(num));p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_ROUNDRECT);p.SetRoundRectRadiusRatio(.15);p.SetPosition(vec(x,y));p.SetSize(vec(sx,sy));p.SetLayerSet(layers or layerset([k.F_Cu,k.F_Mask,k.F_Paste]));p.SetLocalSolderMaskMargin(mm(.025));f.Add(p)
    side=n//4
    for i in range(n):
        s=i//side;j=i%side;v=(j-(side-1)/2)*pitch
        if s==0:x,y=-lead_center,v
        elif s==1:x,y=v,lead_center
        elif s==2:x,y=lead_center,-v
        else:x,y=-v,-lead_center
        pad(i+1,x,y,lead_len if s%2==0 else lead_width,lead_width if s%2==0 else lead_len)
    if ep:
        pad(n+1,0,0,ep,ep,layerset([k.F_Cu,k.F_Mask]))
        web=.14 if name.startswith('SKY') else .25
        aperture=(ep-web)/2
        for x in [-1,1]:
            for y in [-1,1]:pad('',x*(aperture+web)/2,y*(aperture+web)/2,aperture,aperture,layerset([k.F_Paste]))
    for layer,size,thick in [(k.F_CrtYd,2*lead_center+lead_len+.5,.05),(k.F_Fab,body,.1)]:
        s=k.PCB_SHAPE(f);s.SetShape(k.SHAPE_T_RECT);s.SetStart(vec(-size/2,-size/2));s.SetEnd(vec(size/2,size/2));s.SetLayer(layer);s.SetWidth(mm(thick));f.Add(s)
    mark=k.PCB_SHAPE(f);mark.SetShape(k.SHAPE_T_SEGMENT);mark.SetStart(vec(-body/2-.5,-body/2));mark.SetEnd(vec(-body/2-.5,-body/2-.6));mark.SetLayer(k.F_SilkS);mark.SetWidth(mm(.15));f.Add(mark)
    k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(FP),f)
custom('AEM10300_QFN28',28,.4,4,.8,.2,1.925,2.7)
custom('SKY66423_MCM16',16,.5,3,.5,.25,1.4,1.7)
# BGS12SN6 Infineon Rev2.3 Figure5: .25mm square copper, .4mm pitch both axes.
f=k.FOOTPRINT(None);f.SetFPID(k.LIB_ID('Node','BGS12SN6'));f.SetReference('REF**');f.SetValue('BGS12SN6');f.SetAttributes(k.FP_SMD)
for num,x,y in [(1,-.2,-.4),(2,-.2,0),(3,-.2,.4),(4,.2,.4),(5,.2,0),(6,.2,-.4)]:
    p=k.PAD(f);p.SetNumber(str(num));p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_RECT);p.SetPosition(vec(x,y));p.SetSize(vec(.25,.25));p.SetLayerSet(layerset([k.F_Cu,k.F_Mask,k.F_Paste]));p.SetLocalSolderMaskMargin(mm(.025));f.Add(p)
s=k.PCB_SHAPE(f);s.SetShape(k.SHAPE_T_RECT);s.SetStart(vec(-.65,-.85));s.SetEnd(vec(.65,.85));s.SetLayer(k.F_CrtYd);s.SetWidth(mm(.05));f.Add(s)
k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(FP),f)
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Node")(type "KiCad")(uri "${KIPRJMOD}/libraries/Node.pretty")(options "")(descr "Portable board footprints")))')
