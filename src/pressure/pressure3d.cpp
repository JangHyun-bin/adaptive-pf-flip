#include "pressure/pressure3d.h"
#include "grid/uniform_grid3d.h"
#include <cmath>
#include <algorithm>

std::vector<double> divergence(const UniformGrid3D& g){
  std::vector<double> d(g.nx*g.ny*g.nz,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    double du=g.u(i+1,j,k)-g.u(i,j,k), dv=g.v(i,j+1,k)-g.v(i,j,k), dw=g.w(i,j,k+1)-g.w(i,j,k);
    d[g.cidx(i,j,k)]=(du+dv+dw)/g.dx;
  }
  return d;
}

namespace {
inline bool isFluid(UniformGrid3D& g,int i,int j,int k){ return g.inBounds(i,j,k)&&g.cell(i,j,k)==Cell3::FLUID; }
inline bool isSolid(UniformGrid3D& g,int i,int j,int k){ return !g.inBounds(i,j,k)||g.cell(i,j,k)==Cell3::SOLID; }
const int DI[6]={1,-1,0,0,0,0}, DJ[6]={0,0,1,-1,0,0}, DK[6]={0,0,0,0,1,-1};

void applyA(UniformGrid3D& g,double scale,const std::vector<double>& x,std::vector<double>& out){
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=g.cidx(i,j,k); out[c]=0.0;
    if(!isFluid(g,i,j,k)) continue;
    double diag=0,off=0;
    for(int n=0;n<6;++n){ int ni=i+DI[n],nj=j+DJ[n],nk=k+DK[n];
      if(isSolid(g,ni,nj,nk)) continue; diag+=1.0; if(isFluid(g,ni,nj,nk)) off+=x[g.cidx(ni,nj,nk)]; }
    out[c]=scale*(diag*x[c]-off);
  }
}

double diagOf(UniformGrid3D& g,double scale,int i,int j,int k){
  double d=0; for(int n=0;n<6;++n) if(!isSolid(g,i+DI[n],j+DJ[n],k+DK[n])) d+=1.0; return scale*d;
}
} // namespace

double solvePressure(UniformGrid3D& g,const std::vector<double>& div,double dt,double rho,int max_iter,double tol){
  int N=g.nx*g.ny*g.nz; double scale=dt/(rho*g.dx*g.dx);
  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pdir(N,0.0),Ap(N,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=g.cidx(i,j,k); r[c]=isFluid(g,i,j,k)?-div[c]:0.0;
  }
  auto precond=[&](const std::vector<double>& in,std::vector<double>& outv){
    for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
      int c=g.cidx(i,j,k);
      double d=isFluid(g,i,j,k)?diagOf(g,scale,i,j,k):0.0; outv[c]=(d>0.0)?in[c]/d:0.0;
    }
  };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){
    double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s;
  };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t]));
  if(res0<tol){ g.pfield=x; return res0; }
  precond(r,z); pdir=z; double rz=dotp(r,z), res=res0;
  for(int it=0;it<max_iter;++it){
    applyA(g,scale,pdir,Ap); double pAp=dotp(pdir,Ap); if(std::abs(pAp)<1e-30) break;
    double alpha=rz/pAp; for(int t=0;t<N;++t){ x[t]+=alpha*pdir[t]; r[t]-=alpha*Ap[t]; }
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<tol) break;
    precond(r,z); double rzn=dotp(r,z), beta=rzn/rz; rz=rzn;
    for(int t=0;t<N;++t) pdir[t]=z[t]+beta*pdir[t];
  }
  g.pfield=x; return res;
}

void project(UniformGrid3D& g,double dt,double rho){
  double scale=dt/(rho*g.dx);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){
    if(isSolid(g,i-1,j,k)||isSolid(g,i,j,k)){ g.u(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i-1,j,k),b=isFluid(g,i,j,k); if(a||b){ double pl=a?g.p(i-1,j,k):0.0, pr=b?g.p(i,j,k):0.0; g.u(i,j,k)-=scale*(pr-pl); }
  }
  for(int k=0;k<g.nz;++k)for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(isSolid(g,i,j-1,k)||isSolid(g,i,j,k)){ g.v(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i,j-1,k),b=isFluid(g,i,j,k); if(a||b){ double pb=a?g.p(i,j-1,k):0.0, pt=b?g.p(i,j,k):0.0; g.v(i,j,k)-=scale*(pt-pb); }
  }
  for(int k=1;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(isSolid(g,i,j,k-1)||isSolid(g,i,j,k)){ g.w(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i,j,k-1),b=isFluid(g,i,j,k); if(a||b){ double pd=a?g.p(i,j,k-1):0.0, pu=b?g.p(i,j,k):0.0; g.w(i,j,k)-=scale*(pu-pd); }
  }
}
