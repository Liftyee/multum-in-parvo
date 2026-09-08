"""Grounded coplanar geometry: conformal mapping, finite copper correction.

Thickness correction follows the common quasi-static CPW approximation.
The coating is bounded with an effective upper-half-space permittivity sweep;
this is an estimate, not a field-solved/fabricator-guaranteed impedance.
"""
import math,json
from scipy.special import ellipk
from scipy.optimize import brentq
from pathlib import Path
def z0(w,g,h=.73,t=.035,er=4.5,upper=1):
    delta=t/math.pi*(1+math.log(4*math.pi*w/t))
    we=w+delta; ge=g-delta
    if ge<=0:raise ValueError('gap too small for thickness approximation')
    k=we/(we+2*ge)
    k1=math.tanh(math.pi*we/(4*h))/math.tanh(math.pi*(we+2*ge)/(4*h))
    a=ellipk(k*k)/ellipk(1-k*k);b=ellipk(k1*k1)/ellipk(1-k1*k1)
    ee=(upper*a+er*b)/(a+b)
    return 60*math.pi/((a+b)*math.sqrt(ee))
width=brentq(lambda w:z0(w,.25,upper=1.08)-50,.1,3)
report={'method':'quasi-static grounded CPW conformal approximation','finished_board_mm':.8,'core_assumption_mm':.73,'copper_mm':.035,'Er_assumed':4.5,'mask_thickness_assumed_mm':.02,'mask_Er_assumed':3.8,'gap_mm':.25,'solved_width_mm':width,'selected_width_mm':round(width,2),'nominal_ohm':z0(round(width,2),.25,upper=1.08),'limitations':'Mask effective-upper-permittivity 1.08 is a sensitivity assumption, not a solved coating correction. Obtain fab stack and measure coupon.'}
report['sensitivity']=[{'h':h,'Er':er,'upper':up,'Z':z0(round(width,2),.25,h=h,er=er,upper=up)} for h in [.65,.73,.81] for er in [4.2,4.5,4.8] for up in [1,1.16]]
Path(__file__).resolve().parents[1].joinpath('reports/impedance.json').write_text(json.dumps(report,indent=2))
print('RF width',round(width,2),'mm gap .25 mm',report['nominal_ohm'],'ohm')
