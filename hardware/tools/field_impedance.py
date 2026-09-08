"""2-D finite-volume electrostatic GCPW cross section, SI capacitance per metre.
Solve div(epsilon grad V)=0 twice, with dielectric and vacuum. Z0=1/(c sqrt(C C0)).
Finite boundaries are grounded; widths and material tolerances remain fab assumptions.
"""
import numpy as np,json,time
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from pathlib import Path
EPS0=8.8541878128e-12;LIGHT=299792458.
def solve(w=.75,g=.25,h=.73,t=.035,mask=.02,er=4.5,erm=3.8,step=.02,extent=3):
 x=np.unique(np.round(np.r_[np.arange(-extent,extent+step/2,step),-w/2,w/2,-w/2-g,w/2+g],9))
 y=np.unique(np.round(np.r_[np.arange(-h,0,step),0,t,t+mask,np.arange(step,extent,step)],9))
 X,Y=np.meshgrid(x,y);ny,nx=X.shape
 signal=(abs(X)<=w/2+1e-8)&(Y>=0)&(Y<=t+1e-8)
 coplane=(abs(X)>=w/2+g-1e-8)&(Y>=0)&(Y<=t+1e-8)
 fixed=signal|coplane;fixed[0,:]=True;fixed[-1,:]=True;fixed[:,0]=True;fixed[:,-1]=True
 ids=np.full((ny,nx),-1);ids[~fixed]=np.arange((~fixed).sum());N=(~fixed).sum()
 dx=np.diff(x);dy=np.diff(y);cx=np.r_[dx[0]/2,(dx[:-1]+dx[1:])/2,dx[-1]/2];cy=np.r_[dy[0]/2,(dy[:-1]+dy[1:])/2,dy[-1]/2]
 eps=np.where(Y<0,er,1.)
 coating=((Y>=0)&(Y<=mask))|((Y>0)&(Y<=t+mask)&((abs(X)<=w/2+mask)|(abs(X)>=w/2+g-mask)))
 eps[coating]=erm
 def capacitance(vac):
  e=np.ones_like(eps) if vac else eps
  # Mid-face dielectric evaluation keeps the substrate/air interface exact.
  ey=2*e[:-1,:]*e[1:,:]/(e[:-1,:]+e[1:,:]); ex=2*e[:,:-1]*e[:,1:]/(e[:,:-1]+e[:,1:])
  metal=signal|coplane
  ex=np.where(metal[:,:-1],e[:,1:],np.where(metal[:,1:],e[:,:-1],ex))
  ey=np.where(metal[:-1,:],e[1:,:],np.where(metal[1:,:],e[:-1,:],ey))
  gy=ey*cx[None,:]/dy[:,None];gx=ex*cy[:,None]/dx[None,:]
  rows=[];cols=[];vals=[];diag=np.zeros(N);rhs=np.zeros(N)
  for a,b,gg in [(ids[:,:-1],ids[:,1:],gx),(ids[:-1,:],ids[1:,:],gy)]:
   for aa,bb in [(a,b),(b,a)]:
    valid=aa>=0;np.add.at(diag,aa[valid],gg[valid]);both=valid&(bb>=0)
    rows.extend(aa[both]);cols.extend(bb[both]);vals.extend(-gg[both])
  for a,b,gg,sa,sb in [(ids[:,:-1],ids[:,1:],gx,signal[:,:-1],signal[:,1:]),(ids[:-1,:],ids[1:,:],gy,signal[:-1,:],signal[1:,:])]:
   for aa,ss in [(a,sb),(b,sa)]:
    z=(aa>=0)&ss;np.add.at(rhs,aa[z],gg[z])
  rows.extend(np.arange(N));cols.extend(np.arange(N));vals.extend(diag)
  V=np.zeros((ny,nx));V[signal]=1;V[~fixed]=spsolve(coo_matrix((vals,(rows,cols)),shape=(N,N)).tocsr(),rhs)
  charge=0
  for a,b,gg,sa,sb in [(V[:,:-1],V[:,1:],gx,signal[:,:-1],signal[:,1:]),(V[:-1,:],V[1:,:],gy,signal[:-1,:],signal[1:,:])]:
   charge+=np.sum(gg[sa&~sb]*(a-b)[sa&~sb])+np.sum(gg[sb&~sa]*(b-a)[sb&~sa])
  return charge*EPS0
 C=capacitance(False);C0=capacitance(True)
 return dict(width_mm=w,gap_mm=g,step_mm=step,extent_mm=extent,capacitance_pF_per_m=C*1e12,vacuum_pF_per_m=C0*1e12,Z_ohm=1/(LIGHT*np.sqrt(C*C0)),effective_Er=C/C0)
if __name__=='__main__':
 results=[]
 for w in [.75,.85,1.0]:
  r=solve(w=w);results.append(r);print(r,flush=True)
 best=min(results,key=lambda r:abs(r['Z_ohm']-50));results.append(solve(w=best['width_mm'],step=.01));print(results[-1],flush=True)
 out=dict(method='2D finite-volume electrostatic / quasi-TEM',board_mm=.8,substrate_mm=.73,copper_mm=.035,mask_mm=.02,Er=4.5,mask_Er=3.8,results=results,limitations='Assumed FR4 and conformal mask; not a fabricator guarantee. Finite box boundaries and grid convergence reported. Pad launches and lumped matching require VNA tuning.')
 Path(__file__).resolve().parents[1].joinpath('reports/field-impedance.json').write_text(json.dumps(out,indent=2))
