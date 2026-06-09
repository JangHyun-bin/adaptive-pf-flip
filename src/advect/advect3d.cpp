#include "advect/advect3d.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "transfer/transfer3d.h"
#include <algorithm>
#include <vector>

static void extrapField(std::vector<double>& f, std::vector<char>& valid, int W,int H,int D,int sw,int sweeps){
  const int di[6]={1,-1,0,0,0,0},dj[6]={0,0,1,-1,0,0},dk[6]={0,0,0,0,1,-1};
  for(int s=0;s<sweeps;++s){
    std::vector<char> newly(valid.size(),0);
    for(int k=0;k<D;++k)for(int j=0;j<H;++j)for(int i=0;i<W;++i){
      int c=i+sw*(j+H*k); if(valid[c]) continue;
      double sum=0; int n=0;
      for(int t=0;t<6;++t){ int ii=i+di[t],jj=j+dj[t],kk=k+dk[t];
        if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
        int nc=ii+sw*(jj+H*kk); if(valid[nc]){ sum+=f[nc]; ++n; } }
      if(n>0){ f[c]=sum/n; newly[c]=1; }
    }
    for(size_t t=0;t<valid.size();++t) if(newly[t]) valid[t]=1;
  }
}

void extrapolateVelocity(UniformGrid3D& g, int sweeps){
  std::vector<char> vu(g.mu.size()),vv(g.mv.size()),vw(g.mw.size());
  for(size_t t=0;t<g.mu.size();++t) vu[t]=g.mu[t]>0.0;
  for(size_t t=0;t<g.mv.size();++t) vv[t]=g.mv[t]>0.0;
  for(size_t t=0;t<g.mw.size();++t) vw[t]=g.mw[t]>0.0;
  extrapField(g.ufield,vu,g.nx+1,g.ny,g.nz,g.nx+1,sweeps);
  extrapField(g.vfield,vv,g.nx,g.ny+1,g.nz,g.nx,sweeps);
  extrapField(g.wfield,vw,g.nx,g.ny,g.nz+1,g.nx,sweeps);
}

void advect(Particles3D& ps, const UniformGrid3D& g, double dt){
  double lox=g.ox+0.5*g.dx, hix=g.ox+(g.nx-0.5)*g.dx;
  double loy=g.oy+0.5*g.dx, hiy=g.oy+(g.ny-0.5)*g.dx;
  double loz=g.oz+0.5*g.dx, hiz=g.oz+(g.nz-0.5)*g.dx;
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    double u1=sampleU(g,px,py,pz),v1=sampleV(g,px,py,pz),w1=sampleW(g,px,py,pz);
    double mx=ps.pos[kpt].x+0.5*dt*u1, my=ps.pos[kpt].y+0.5*dt*v1, mz=ps.pos[kpt].z+0.5*dt*w1;
    double mpx=(mx-g.ox)/g.dx,mpy=(my-g.oy)/g.dx,mpz=(mz-g.oz)/g.dx;
    double u2=sampleU(g,mpx,mpy,mpz),v2=sampleV(g,mpx,mpy,mpz),w2=sampleW(g,mpx,mpy,mpz);
    double nx_=ps.pos[kpt].x+dt*u2, ny_=ps.pos[kpt].y+dt*v2, nz_=ps.pos[kpt].z+dt*w2;
    ps.pos[kpt].x=std::max(lox,std::min(hix,nx_));
    ps.pos[kpt].y=std::max(loy,std::min(hiy,ny_));
    ps.pos[kpt].z=std::max(loz,std::min(hiz,nz_));
  }
}
