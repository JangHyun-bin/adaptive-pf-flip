#include "driver/sparse_ops2d_tp.h"
#include "driver/sparse_ops2d_common.h"
#include "grid/block_color.h"
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <array>
#include <vector>
#include <algorithm>
#include <cmath>

// Eq.6 cubic kernel on squared distance; KR in cells (dense transfer2d_tp.cpp mirror)
static inline double kern(double d2, double r){ double q=d2/(r*r), t=1.0-q; return (t>0.0)? t*t*t : 0.0; }
static const double KR = 1.5;

static void preactivateUK(SparseMacGrid2D<8>& g,double gx,double gy){
  const int W=g.nx+1, H=g.ny;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; if(kern(dx*dx+dy*dy,KR)<=0.0) continue;
    int bx=ii/8, by=jj/8; g.uf.activateBlock(bx,by); g.muf.activateBlock(bx,by); }
}
static void preactivateVK(SparseMacGrid2D<8>& g,double gx,double gy){
  const int W=g.nx, H=g.ny+1;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; if(kern(dx*dx+dy*dy,KR)<=0.0) continue;
    int bx=ii/8, by=jj/8; g.vf.activateBlock(bx,by); g.mvf.activateBlock(bx,by); }
}
// normalized 2-pass splat (partition of unity per particle) into one color of destination blocks
static void splatUKColor(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m,int color){
  const int W=g.nx+1, H=g.ny;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    if(color4(ii/8,jj/8)!=color) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.u(ii,jj)+=(float)(w*mom); g.mu(ii,jj)+=(float)(w*m); }
}
static void splatVKColor(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m,int color){
  const int W=g.nx, H=g.ny+1;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    if(color4(ii/8,jj/8)!=color) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.v(ii,jj)+=(float)(w*mom); g.mv(ii,jj)+=(float)(w*m); }
}

void spP2G_tp(SparseMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp){
  g.uf.clear(); g.vf.clear(); g.muf.clear(); g.mvf.clear();
  for(size_t k=0;k<ps.size();++k){
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    preactivateUK(g, px, py-0.5);
    preactivateVK(g, px-0.5, py);
  }
  sparse2d::runColor4(ps.size(), [&](int color){
    for(size_t k=0;k<ps.size();++k){
      double rho=(ps.type[k]==0)? pp.rho_l : pp.rho_g; double mp=rho*Vp;
      double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
      splatUKColor(g, px, py-0.5, mp*ps.vel[k].x, mp, color);
      splatVKColor(g, px-0.5, py, mp*ps.vel[k].y, mp, color);
    }
  });
  // normalize: face velocity = momentum / raw mass, over active mass blocks only
  for(int b: g.muf.activeBlockIds()){ int bx,by; g.muf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>g.nx||j>=g.ny) continue;
      float m=g.gmu(i,j); if(m>0) g.u(i,j)=g.gu(i,j)/m; } }
  for(int b: g.mvf.activeBlockIds()){ int bx,by; g.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=g.nx||j>g.ny) continue;
      float m=g.gmv(i,j); if(m>0) g.v(i,j)=g.gv(i,j)/m; } }
}

void spG2P_tp(const SparseMacGrid2D<8>& g, Particles2DTP& ps, const SparseMacGrid2D<8>& saved, double aL, double aG){
  for(size_t k=0;k<ps.size();++k){
    double a=(ps.type[k]==0)? aL : aG;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sparse2d::sampleU(g,px,py), vn=sparse2d::sampleV(g,px,py);
    double du=un-sparse2d::sampleU(saved,px,py), dv=vn-sparse2d::sampleV(saved,px,py);
    double pic_x=un, pic_y=vn, flip_x=ps.vel[k].x+du, flip_y=ps.vel[k].y+dv;
    ps.vel[k].x=a*flip_x+(1-a)*pic_x; ps.vel[k].y=a*flip_y+(1-a)*pic_y;
  }
}
void spAdvect_tp(Particles2DTP& ps, const SparseMacGrid2D<8>& g, double dt){
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sparse2d::sampleU(g,px,py),v1=sparse2d::sampleV(g,px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sparse2d::sampleU(g,mx/g.dx,my/g.dx),v2=sparse2d::sampleV(g,mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); }
}

void spProjectStepVC(SparseMacGrid2D<8>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol){
  g.pf.clear();                                 // p-blocks track LIVE fluid (sparsity metric/viz read pf)
  auto cells = sparse2d::collectCellsWithMarker(g, 1);
  int N=(int)cells.size(); if(N==0) return;
  auto isFluid=[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==1; };
  auto isSolid=[&](int i,int j){ return !g.inBounds(i,j) || g.cell(i,j)==2; };
  auto isAir  =[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==0; };
  // face beta on the fly from raw face density (== dense per-face bu/bv computation).
  // Constants hoisted from phiFromRawDensity/betaFromPhi: std::log once per solve,
  // not per CG-iteration beta eval (8 evals/cell/iter) - numerically identical.
  const double rmin = etaPhi(pp)*pp.rho_g*pp.rho_tilde_0;
  const double invden = 1.0/(pp.alpha_phi*pp.rho_tilde_0*pp.rho_l);
  auto betaOfRaw=[&](double rt){
    double phi = (rt<rmin)? 0.0 : std::min(std::sqrt((rt-rmin)*invden), 1.0);
    return 1.0/(phi*pp.rho_l + (1.0-phi)*pp.rho_g);
  };
  auto bU=[&](int i,int j){ return betaOfRaw((double)g.gmu(i,j)); };
  auto bV=[&](int i,int j){ return betaOfRaw((double)g.gmv(i,j)); };
  // pure-Neumann pin (dense findPinCell mirror): pin first enumerated fluid cell iff no fluid cell touches AIR
  int pc=-1;
  { bool dirichlet=false; const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int t=0;t<N && !dirichlet;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
      for(int n=0;n<4;++n) if(isAir(i+di[n],j+dj[n])){ dirichlet=true; break; } }
    if(!dirichlet) pc=cells[0]; }
  double scale=dt/(g.dx*g.dx);
  // rhs = -divergence, BC-aware: solid-adjacent face velocities count as 0 (dense divergenceVC mirror)
  std::vector<double> x(N,0),r(N),z(N),pd(N),Ap(N);
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
    if(cells[t]==pc){ r[t]=0.0; continue; }
    double uR=isSolid(i+1,j)?0.0:(double)g.gu(i+1,j), uL=isSolid(i-1,j)?0.0:(double)g.gu(i,j);
    double vT=isSolid(i,j+1)?0.0:(double)g.gv(i,j+1), vB=isSolid(i,j-1)?0.0:(double)g.gv(i,j);
    r[t]=-((uR-uL)+(vT-vB))/g.dx; }
  std::vector<double> diag(N, 0.0);
  std::vector<std::array<int,4>> nbr(N);
  std::vector<std::array<double,4>> coeff(N);
  for(int t=0;t<N;++t){
    nbr[t].fill(-1);
    coeff[t].fill(0.0);
    int i=cells[t]%g.nx,j=cells[t]/g.nx;
    struct F{int ni,nj;double b;};
    F fs[4]={ {i+1,j,bU(i+1,j)},{i-1,j,bU(i,j)},{i,j+1,bV(i,j+1)},{i,j-1,bV(i,j)} };
    for(int n=0;n<4;++n){
      if(isSolid(fs[n].ni,fs[n].nj)) continue;
      diag[t]+=fs[n].b;
      coeff[t][n]=fs[n].b;
      int nc=fs[n].ni+g.nx*fs[n].nj;
      if(isFluid(fs[n].ni,fs[n].nj) && nc!=pc) nbr[t][n]=sparse2d::findSortedIndex(cells, nc);
    }
  }
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    for(int t=0;t<N;++t){
      if(cells[t]==pc){ out[t]=xx[t]; continue; }            // identity row pins pressure
      double off=0;
      for(int n=0;n<4;++n) if(nbr[t][n]>=0) off+=coeff[t][n]*xx[nbr[t][n]];
      out[t]=scale*(diag[t]*xx[t]-off); } };
  auto prec=[&](const std::vector<double>& in,std::vector<double>& o){
    for(int t=0;t<N;++t){ double d=(cells[t]==pc)?1.0:scale*diag[t]; o[t]=(d>0)?in[t]/d:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<cg_tol) return;
  prec(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<cg_iters;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<cg_tol) break;
    prec(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; g.p(i,j)=(float)x[t]; }
  // project with face beta: single-touch face sweeps (Phase A corrected pattern + dense projectVC beta)
  double s=dt/g.dx;
  auto uFaces = sparse2d::collectProjectUFaces(g, cells);
  auto vFaces = sparse2d::collectProjectVFaces(g, cells);
  for(int fid: uFaces){
    int i=fid%(g.nx+1), j=fid/(g.nx+1);
    bool lf=isFluid(i-1,j), rf=isFluid(i,j);
    if(!lf&&!rf) continue;
    if(isSolid(i-1,j)||isSolid(i,j)){ g.u(i,j)=0.0f; continue; }
    double pl=lf?(double)g.gp(i-1,j):0.0, pr=rf?(double)g.gp(i,j):0.0;
    g.u(i,j)=g.gu(i,j)-(float)(s*bU(i,j)*(pr-pl));
  }
  for(int fid: vFaces){
    int i=fid%g.nx, j=fid/g.nx;
    bool bf=isFluid(i,j-1), tf=isFluid(i,j);
    if(!bf&&!tf) continue;
    if(isSolid(i,j-1)||isSolid(i,j)){ g.v(i,j)=0.0f; continue; }
    double pb=bf?(double)g.gp(i,j-1):0.0, pt=tf?(double)g.gp(i,j):0.0;
    g.v(i,j)=g.gv(i,j)-(float)(s*bV(i,j)*(pt-pb));
  }
}
