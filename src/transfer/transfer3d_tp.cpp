#include "transfer/transfer3d_tp.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>
#include <vector>

static inline double kern(double d2_cells, double r){ double q=d2_cells/(r*r), t=1.0-q; return (t>0.0)? t*t*t : 0.0; }
static const double KR=1.5;
// normalized splat into one axis face field (sw stride x; W,H,D dims; idx=i+sw*(j+H*k))
static void splatN(std::vector<double>& field, std::vector<double>& mass, int sw,int W,int H,int D,
                   double gx,double gy,double gz, double mom,double m, double r){
  int rad=(int)std::ceil(r); int i0=(int)std::floor(gx),j0=(int)std::floor(gy),k0=(int)std::floor(gz);
  // pass 1: weight sum
  double wsum=0;
  for(int dk=-rad;dk<=rad+1;++dk)for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj,kk=k0+dk; if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double dx=gx-ii,dy=gy-jj,dz=gz-kk; wsum+=kern(dx*dx+dy*dy+dz*dz,r);
  }
  if(wsum<=0.0) return;
  // pass 2: normalized splat
  for(int dk=-rad;dk<=rad+1;++dk)for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj,kk=k0+dk; if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double dx=gx-ii,dy=gy-jj,dz=gz-kk; double w=kern(dx*dx+dy*dy+dz*dz,r)/wsum; if(w<=0.0) continue;
    int idx=ii+sw*(jj+H*kk); field[idx]+=w*mom; mass[idx]+=w*m;
  }
}
double calibrateRhoTilde0(const PhaseParams& pp, double Vp){
  UniformGrid3D g(8,8,8,1.0); double mp=pp.rho_l*Vp;
  for(int k=0;k<8;++k)for(int j=0;j<8;++j)for(int i=0;i<8;++i)for(int s=0;s<8;++s){
    double x=i+0.25+0.5*(s&1), y=j+0.25+0.5*((s>>1)&1), z=k+0.25+0.5*((s>>2)&1);
    splatN(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny,g.nz, x, y-0.5, z-0.5, 0.0, mp, KR);
  }
  double raw=g.mu[g.uidx(4,4,4)]; return (raw>0)? raw/pp.rho_l : 1.0;
}
void p2g_tp(UniformGrid3D& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0);std::fill(g.vfield.begin(),g.vfield.end(),0.0);std::fill(g.wfield.begin(),g.wfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0);std::fill(g.mv.begin(),g.mv.end(),0.0);std::fill(g.mw.begin(),g.mw.end(),0.0);
  for(size_t p=0;p<ps.size();++p){
    double rho=(ps.type[p]==0)?pp.rho_l:pp.rho_g; double mp=rho*Vp;
    double px=(ps.pos[p].x-g.ox)/g.dx,py=(ps.pos[p].y-g.oy)/g.dx,pz=(ps.pos[p].z-g.oz)/g.dx;
    splatN(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny,g.nz, px, py-0.5, pz-0.5, mp*ps.vel[p].x, mp, KR);
    splatN(g.vfield,g.mv, g.nx,  g.nx,g.ny+1,g.nz, px-0.5, py, pz-0.5, mp*ps.vel[p].y, mp, KR);
    splatN(g.wfield,g.mw, g.nx,  g.nx,g.ny,g.nz+1, px-0.5, py-0.5, pz, mp*ps.vel[p].z, mp, KR);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0) g.vfield[i]/=g.mv[i];
  for(size_t i=0;i<g.wfield.size();++i) if(g.mw[i]>0) g.wfield[i]/=g.mw[i];
}
static double tri(const std::vector<double>& f,int sw,int W,int H,int D,double gx,double gy,double gz){
  int i0=(int)std::floor(gx),j0=(int)std::floor(gy),k0=(int)std::floor(gz); double fx=gx-i0,fy=gy-j0,fz=gz-k0;
  auto get=[&](int ii,int jj,int kk){ ii=std::max(0,std::min(W-1,ii));jj=std::max(0,std::min(H-1,jj));kk=std::max(0,std::min(D-1,kk)); return f[ii+sw*(jj+H*kk)]; };
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0;
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*get(i0+di,j0+dj,k0+dk);
  return s;
}
static double sU(const UniformGrid3D& g,double px,double py,double pz){return tri(g.ufield,g.nx+1,g.nx+1,g.ny,g.nz,px,py-0.5,pz-0.5);}
static double sV(const UniformGrid3D& g,double px,double py,double pz){return tri(g.vfield,g.nx,g.nx,g.ny+1,g.nz,px-0.5,py,pz-0.5);}
static double sW(const UniformGrid3D& g,double px,double py,double pz){return tri(g.wfield,g.nx,g.nx,g.ny,g.nz+1,px-0.5,py-0.5,pz);}
void g2p_tp(const UniformGrid3D& g, Particles3DTP& ps, const UniformGrid3D& saved, double aL, double aG){
  for(size_t p=0;p<ps.size();++p){ double a=(ps.type[p]==0)?aL:aG;
    double px=(ps.pos[p].x-g.ox)/g.dx,py=(ps.pos[p].y-g.oy)/g.dx,pz=(ps.pos[p].z-g.oz)/g.dx;
    double un=sU(g,px,py,pz),vn=sV(g,px,py,pz),wn=sW(g,px,py,pz);
    double du=un-sU(saved,px,py,pz),dv=vn-sV(saved,px,py,pz),dw=wn-sW(saved,px,py,pz);
    Vec3 pic{un,vn,wn}; Vec3 flip{ps.vel[p].x+du,ps.vel[p].y+dv,ps.vel[p].z+dw};
    ps.vel[p]=flip*a+pic*(1.0-a);
  }
}
