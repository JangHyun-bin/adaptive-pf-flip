#include "pressure/pressure3d_vc.h"
#include "grid/uniform_grid3d.h"
#include <cmath>
#include <algorithm>
namespace {
inline bool isFluid(const UniformGrid3D& g,int i,int j,int k){ return g.inBounds(i,j,k)&&g.cell(i,j,k)==Cell3::FLUID; }
inline bool isSolid(const UniformGrid3D& g,int i,int j,int k){ return !g.inBounds(i,j,k)||g.cell(i,j,k)==Cell3::SOLID; }
inline double bU(const UniformGrid3D& g,int i,int j,int k){ return g.bu[g.uidx(i,j,k)]; }
inline double bV(const UniformGrid3D& g,int i,int j,int k){ return g.bv[g.vidx(i,j,k)]; }
inline double bW(const UniformGrid3D& g,int i,int j,int k){ return g.bw[g.widx(i,j,k)]; }
// returns true if pure-Neumann (no fluid cell touches AIR)
bool pureNeumann(const UniformGrid3D& g){
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(isFluid(g,i,j,k)){
    const int di[6]={1,-1,0,0,0,0},dj[6]={0,0,1,-1,0,0},dk[6]={0,0,0,0,1,-1};
    for(int n=0;n<6;++n){ int ni=i+di[n],nj=j+dj[n],nk=k+dk[n];
      if(g.inBounds(ni,nj,nk)&&g.cell(ni,nj,nk)==Cell3::AIR) return false; } }
  return true;
}
int firstFluid(const UniformGrid3D& g){ for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(isFluid(g,i,j,k)) return g.cidx(i,j,k); return -1; }
struct Face{int ni,nj,nk; double b;};
void faces(const UniformGrid3D& g,int i,int j,int k,Face f[6]){
  f[0]={i+1,j,k,bU(g,i+1,j,k)}; f[1]={i-1,j,k,bU(g,i,j,k)};
  f[2]={i,j+1,k,bV(g,i,j+1,k)}; f[3]={i,j-1,k,bV(g,i,j,k)};
  f[4]={i,j,k+1,bW(g,i,j,k+1)}; f[5]={i,j,k-1,bW(g,i,j,k)};
}
}
std::vector<double> divergenceVC(const UniformGrid3D& g){
  std::vector<double> d(g.nx*g.ny*g.nz,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    // BC-aware: solid-adjacent faces count as 0 velocity (consistent with projection)
    double up = isSolid(g,i,j,k)||isSolid(g,i+1,j,k)? 0.0 : g.u(i+1,j,k);
    double um = isSolid(g,i,j,k)||isSolid(g,i-1,j,k)? 0.0 : g.u(i,j,k);
    double vp = isSolid(g,i,j,k)||isSolid(g,i,j+1,k)? 0.0 : g.v(i,j+1,k);
    double vm = isSolid(g,i,j,k)||isSolid(g,i,j-1,k)? 0.0 : g.v(i,j,k);
    double wp = isSolid(g,i,j,k)||isSolid(g,i,j,k+1)? 0.0 : g.w(i,j,k+1);
    double wm = isSolid(g,i,j,k)||isSolid(g,i,j,k-1)? 0.0 : g.w(i,j,k);
    d[g.cidx(i,j,k)]=((up-um)+(vp-vm)+(wp-wm))/g.dx;
  }
  return d;
}
double solvePressureVC(UniformGrid3D& g,const std::vector<double>& div,double dt,int max_iter,double tol){
  int N=g.nx*g.ny*g.nz; double scale=dt/(g.dx*g.dx);
  bool pin = pureNeumann(g); int pc = pin? firstFluid(g) : -1;
  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pd(N,0.0),Ap(N,0.0);
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k); out[c]=0.0;
      if(!isFluid(g,i,j,k)) continue;
      if(c==pc){ out[c]=xx[c]; continue; }                  // identity row pins pressure
      Face f[6]; faces(g,i,j,k,f); double diag=0,off=0;
      for(int n=0;n<6;++n){ if(isSolid(g,f[n].ni,f[n].nj,f[n].nk)) continue; diag+=f[n].b;
        if(isFluid(g,f[n].ni,f[n].nj,f[n].nk) && g.cidx(f[n].ni,f[n].nj,f[n].nk)!=pc) off+=f[n].b*xx[g.cidx(f[n].ni,f[n].nj,f[n].nk)]; }
      out[c]=scale*(diag*xx[c]-off);
    } };
  auto diagOf=[&](int i,int j,int k){ Face f[6]; faces(g,i,j,k,f); double d=0; for(int n=0;n<6;++n) if(!isSolid(g,f[n].ni,f[n].nj,f[n].nk)) d+=f[n].b; return scale*d; };
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k); r[c]= isFluid(g,i,j,k)? (c==pc?0.0:-div[c]) : 0.0; }
  auto precond=[&](const std::vector<double>& in,std::vector<double>& o){ for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k);
    double dd = isFluid(g,i,j,k)? (c==pc?1.0:diagOf(i,j,k)) : 0.0; o[c]=(dd>0)?in[c]/dd:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<tol){g.pfield=x;return res0;}
  precond(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<max_iter;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<tol) break;
    precond(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  g.pfield=x; return res;
}
void projectVC(UniformGrid3D& g,double dt){
  double s=dt/g.dx;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){ if(isSolid(g,i-1,j,k)||isSolid(g,i,j,k)){g.u(i,j,k)=0;continue;}
    bool a=isFluid(g,i-1,j,k),b=isFluid(g,i,j,k); if(a||b){ double pl=a?g.p(i-1,j,k):0.0,pr=b?g.p(i,j,k):0.0; g.u(i,j,k)-=s*bU(g,i,j,k)*(pr-pl);} }
  for(int k=0;k<g.nz;++k)for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){ if(isSolid(g,i,j-1,k)||isSolid(g,i,j,k)){g.v(i,j,k)=0;continue;}
    bool a=isFluid(g,i,j-1,k),b=isFluid(g,i,j,k); if(a||b){ double pb=a?g.p(i,j-1,k):0.0,pt=b?g.p(i,j,k):0.0; g.v(i,j,k)-=s*bV(g,i,j,k)*(pt-pb);} }
  for(int k=1;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ if(isSolid(g,i,j,k-1)||isSolid(g,i,j,k)){g.w(i,j,k)=0;continue;}
    bool a=isFluid(g,i,j,k-1),b=isFluid(g,i,j,k); if(a||b){ double pd=a?g.p(i,j,k-1):0.0,pu=b?g.p(i,j,k):0.0; g.w(i,j,k)-=s*bW(g,i,j,k)*(pu-pd);} }
}
