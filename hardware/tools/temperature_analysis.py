import math,itertools,json
from pathlib import Path
R25=100000;B=4200;T0=298.15
# First-order beta model; actual manufacturer R/T curve and thermal coupling need qualification.
def temp(r,r25=R25,b=B):return 1/(1/T0+math.log(r/r25)/b)-273.15
out={'model':'R25=100k +/-1%, B25/50=4200K +/-1%; resistors +/-0.1%','reference_min_V':2.164,'offset_max_mV':8,'hysteresis_mV_typ':7,'hysteresis_25C_max_mV':17,'qualification':'17mV hysteresis bound is specified at 25C, not across temperature. Input bias has no guaranteed maximum. Use manufacturer R/T curve and chamber qualification; figures below are conditional engineering bounds, not certified safety thresholds.'}
for name,upper in [('cold',357000),('hot',1980000)]:
 nominal=1e6/(1e6+upper);vals=[]
 for ur,lr,sr,nr,bb,off in itertools.product([-.001,.001],[-.001,.001],[-.001,.001],[-.01,.01],[-.01,.01],[-1,1]):
  ratio=1e6*(1+lr)/(1e6*(1+lr)+upper*(1+ur))
  # Conservative full 17mV hysteresis plus 8mV offset and 2mV extra error allowance.
  ratio+=off*.027/2.164
  r=100000*(1+sr)*ratio/(1-ratio)
  vals.append(temp(r,R25*(1+nr),B*(1+bb)))
 out[name]={'nominal_C':temp(R25*nominal/(1-nominal)),'conditional_min_C':min(vals),'conditional_max_C':max(vals),'nominal_ratio':nominal,'hysteresis_C_at_4V_typ':abs(temp(R25*(nominal+.0035/4)/(1-nominal-.0035/4))-temp(R25*(nominal-.0035/4)/(1-nominal+.0035/4)))}
out['solar_divider_uA_at_4V_25C']=4/(R25+R25)*1e6+4/(357000+1e6)*1e6+4/(1980000+1e6)*1e6
p=Path(__file__).resolve().parents[1];(p/'reports/temperature.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
