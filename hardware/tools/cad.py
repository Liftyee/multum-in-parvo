"""Small deterministic KiCad 8 schematic authoring helpers. No KiCad 9 syntax."""
from pathlib import Path
import uuid, json, math, re, shutil
ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT/'libraries'
LIB.mkdir(exist_ok=True)
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL, 'multum-in-parvo/revA/'+s))
def q(s): return json.dumps(str(s))
def eff(size=1.27, extra=''): return f'(effects (font (size {size} {size})) {extra})'
def parse(s):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s)
    def rec(i):
        out=[]; i+=1
        while tokens[i]!=')':
            if tokens[i]=='(': v,i=rec(i);out.append(v)
            else: out.append(tokens[i]);i+=1
        return out,i+1
    return rec(0)[0]
def dump(x): return '('+' '.join(map(dump,x))+')' if isinstance(x,list) else x
def kids(x,n): return [a for a in x if isinstance(a,list) and a[0]==n]
def kid(x,n): return next(iter(kids(x,n)),None)
def unq(s): return json.loads(s) if s.startswith('"') else s

class Symbol:
    def __init__(self,name,body,pins): self.name,self.body,self.pins=name,body,pins
symbols={}
def standard(lib,name):
    if name in symbols:return symbols[name]
    tree=parse(Path('/usr/share/kicad/symbols',lib+'.kicad_sym').read_text())
    node=next(x for x in kids(tree,'symbol') if unq(x[1])==name)
    if kid(node,'extends'): raise ValueError('Inherited symbol: '+name)
    pins={}
    for unit in kids(node,'symbol'):
        for p in kids(unit,'pin'):
            a=kid(p,'at'); num=unq(kid(p,'number')[1])
            pins[num]=(float(a[1]),-float(a[2]),int(a[3]),unq(kid(p,'name')[1]),p[1])
    symbols[name]=Symbol(name,dump(node),pins)
    return symbols[name]
def ic(name,left,right,top=(),bottom=(),width=30.48):
    # pin tuples: number, label, electrical type; dimensions on 1.27 mm grid
    height=(max(len(left),len(right))+1)*2.54
    x=width/2;y=height/2
    b=[f'(symbol {q(name)} (pin_names (offset 0.635)) (in_bom yes) (on_board yes)',
       f'(property "Reference" "U" (at 0 {y+5.08} 0) {eff()})',
       f'(property "Value" {q(name)} (at 0 {y+2.54} 0) {eff()})',
       f'(symbol {q(name+"_0_1")} (rectangle (start {-x} {-y}) (end {x} {y}) (stroke (width 0.254) (type default)) (fill (type background))))',
       f'(symbol {q(name+"_1_1")}']
    pins={}
    for side,rows in [('L',left),('R',right),('T',top),('B',bottom)]:
        for i,(num,label,typ) in enumerate(rows):
            if side in 'LR': px=(-x-2.54 if side=='L' else x+2.54);py=y-2.54*(i+1);a=0 if side=='L' else 180
            else: px=(i-(len(rows)-1)/2)*2.54;py=y+2.54 if side=='T' else -y-2.54;a=270 if side=='T' else 90
            b.append(f'(pin {typ} line (at {px} {py} {a}) (length 2.54) (name {q(label)} {eff(1.016)}) (number {q(num)} {eff(1.016)}))')
            pins[str(num)]=(px,-py,a,label,typ)
    b.append('))')
    symbols[name]=Symbol(name,'\n'.join(b),pins)
    return symbols[name]

parts=[]
pages={}
global_nets={'GND','PACK_P','3V3_AON','3V3_SW','SOLAR_P','VINT','CHG_INHIBIT','CHG_ENABLE','AEM_STATUS','FEM_CSD','FEM_CTX','FEM_CPS','RF_TX50','RF_RX50','RF_SW','PERIPH_EN','I2C_SDA','I2C_SCL','GAUGE_ALERT','SWDIO','SWCLK','NRST','UART_TX','UART_RX'}
class Page:
    def __init__(self,name,title):
        self.name,self.title=name,title;self.id=uid(name);self.items=[];self.parts=[];self.nets={};self.wire_id=0;pages[name]=self
    def text(self,x,y,s,size=1.27): self.items.append(f'(text {q(s)} (at {x} {y} 0) {eff(size,"(justify left top)")} (uuid {q(uid(self.name+str(x)+str(y)+s))}))')
    def line(self,a,b):
        self.wire_id+=1
        self.items.append(f'(polyline (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0.254) (type default)) (uuid {q(uid(self.name+"graphic"+str(self.wire_id)))}))')
    def wire(self,a,b):
        if a==b:return
        self.wire_id+=1
        self.items.append(f'(wire (pts (xy {a[0]:.4f} {a[1]:.4f}) (xy {b[0]:.4f} {b[1]:.4f})) (stroke (width 0) (type default)) (uuid {q(uid(self.name+"wire"+str(self.wire_id)))}))')
    def label(self,net,p,ang=0):
        self.wire_id+=1
        typ='global_label' if net in global_nets else 'label'
        shape='(shape bidirectional)' if typ=='global_label' else ''
        prop=f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {p[0]} {p[1]} 0) {eff(1.016,"hide")})' if typ=='global_label' else ''
        self.items.append(f'({typ} {q(net)} {shape} (at {p[0]:.4f} {p[1]:.4f} {ang}) {eff(1.016,"(justify right bottom)" if ang==180 else "(justify left bottom)")} (uuid {q(uid(self.name+"label"+str(self.wire_id)))}) {prop})')
    def add(self,ref,sym,value,fp,x,y,nets,rot=0,dnp=False,pcb=None,group='',mpn=''):
        sym=symbols[sym];u=uid(ref)
        p={'ref':ref,'symbol':sym.name,'value':value,'footprint':fp,'nets':{str(k):v for k,v in nets.items()},'sheet':self.name,'x':x,'y':y,'rot':rot,'dnp':dnp,'pcb':pcb,'group':group,'mpn':mpn or value,'uuid':u}
        parts.append(p);self.parts.append(p)
        return p
    def point(self,p,num):
        dx,dy,a,*_=symbols[p['symbol']].pins[str(num)]
        r=math.radians(p['rot']);return (round(p['x']+dx*math.cos(r)+dy*math.sin(r),4),round(p['y']-dx*math.sin(r)+dy*math.cos(r),4))
    def connect(self,a,b,via=None):
        pa=self.point(*a);pb=self.point(*b)
        chain=[pa]+(via or ([] if pa[0]==pb[0] or pa[1]==pb[1] else [(pb[0],pa[1])]))+[pb]
        for x,y in zip(chain,chain[1:]):self.wire(x,y)
        for p,n in (a,b):p.setdefault('wired',set()).add(str(n))
    def terminal(self,p,n,net=None,length=5.08):
        num=str(n); net=net or p['nets'][num];xy=self.point(p,num)
        a=(symbols[p['symbol']].pins[num][2]+p['rot'])%360
        # from pin connection outward, opposite to the direction into symbol
        dest=(round(xy[0]-length*math.cos(math.radians(a)),4),round(xy[1]+length*math.sin(math.radians(a)),4))
        self.wire(xy,dest);self.label(net,dest,180 if a==0 else 0)
        p.setdefault('wired',set()).add(num)
    def save(self,rootid):
        body=list(self.items)
        for p in self.parts:
            sym=symbols[p['symbol']];x,y=p['x'],p['y'];ref=p['ref']
            for num,info in sym.pins.items():
                if num not in p['nets'] or p['nets'][num] is None:
                    if info[4]=='no_connect':continue
                    xy=self.point(p,num)
                    body.append(f'(no_connect (at {xy[0]} {xy[1]}) (uuid {q(uid(ref+"nc"+num))}))')
                elif num not in p.get('wired',set()):self.terminal(p,num)
            h=max([-v[1] for v in sym.pins.values()]+[3.81])
            # custom parts labels above body; passives default beside component
            py=y-h-5.08
            if sym.name in ('R','C','L','Crystal') and p['rot']==90:py=y-3.81
            b=f'(symbol (lib_id {q("Node:"+sym.name)}) (at {x} {y} {p["rot"]}) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if p["dnp"] else "no"}) (uuid {q(p["uuid"])})'
            for k,v,yy in [('Reference',ref,py),('Value',p['value'],py+2.54),('Footprint',p['footprint'],y),('MPN',p['mpn'],y),('Population',p['group'],y)]:
                hide='' if k in ('Reference','Value') else 'hide'
                xx=x
                if sym.name in ('R','C','L') and p['rot']==0 and k in ('Reference','Value'):
                    xx=x+3.81;yy=y+(-1.27 if k=='Reference' else 1.27);hide='(justify left)'
                b+=f'(property {q(k)} {q(v)} (at {xx} {yy} {p["rot"]}) {eff(1.016,hide)})'
            for num in sym.pins:b+=f'(pin {q(num)} (uuid {q(uid(ref+"pin"+num))}))'
            b+=f'(instances (project "mesh-node" (path "/{rootid}/{self.id}" (reference {q(ref)}) (unit 1)))) )'
            body.append(b)
        # terminals were appended after first copy
        body=self.items+[b for b in body if b.startswith('(symbol') or b.startswith('(no_connect')]
        lib='\n'.join(symbols[n].body.replace('(symbol '+q(n),'(symbol '+q('Node:'+n),1) for n in sorted({p['symbol'] for p in self.parts}))
        out=f'(kicad_sch (version 20231120) (generator "eeschema") (uuid {q(self.id)}) (paper "A3") (title_block (title {q(self.title)}) (rev "A-DRAFT") (company "Multum in Parvo") (comment 1 "KiCad 8 | Engineering development - release requires review")) (lib_symbols {lib})\n'+'\n'.join(body)+')\n'
        (ROOT/(self.name+'.kicad_sch')).write_text(out)

def save():
    rootid=uid('root')
    for p in pages.values():p.save(rootid)
    items=[]
    for i,p in enumerate(pages.values()):
        x=25+(i%2)*145;y=70+(i//2)*50
        items.append(f'(sheet (at {x} {y}) (size 120 30) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {q(p.id)}) (property "Sheetname" {q(p.title)} (at {x} {y-1.27} 0) {eff(1.27,"(justify left bottom)")}) (property "Sheetfile" {q(p.name+".kicad_sch")} (at {x} {y+31.27} 0) {eff(1.27,"(justify left top)")}) (instances (project "mesh-node" (path "/{rootid}" (page {q(i+2)})))))')
    txt='Solar -> AEM10300 -> PACK+ -> TPS63900 -> 3V3_AON -> STM32WLE5\nCell negative -> back-to-back MOSFETs -> system GND\nPACK+ -> optional FEM; 3V3_AON -> optional switched peripheral supply\nTwo-layer, 0.8 mm candidate stack. EU868; conducted RF verification required.'
    items.append(f'(text {q(txt)} (at 25 25 0) {eff(1.5,"(justify left top)")} (uuid {q(uid("overviewtext"))}))')
    (ROOT/'mesh-node.kicad_sch').write_text(f'(kicad_sch (version 20231120) (generator "eeschema") (uuid {q(rootid)}) (paper "A3") (title_block (title "Multum in Parvo - solar mesh node") (rev "A-DRAFT")) (lib_symbols) '+''.join(items)+f'(sheet_instances (path "/" (page "1"))))')
    (LIB/'Node.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") '+'\n'.join(s.body for s in symbols.values())+')')
    (ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Node")(type "KiCad")(uri "${KIPRJMOD}/libraries/Node.kicad_sym")(options "")(descr "Project-local verified pin maps")))')
    clean=[{k:v for k,v in p.items() if k!='wired'} for p in parts]
    (ROOT/'design.json').write_text(json.dumps(clean,indent=2))
