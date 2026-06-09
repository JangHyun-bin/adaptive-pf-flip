#include "transfer/transfer3d.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include <vector>
#include <algorithm>
#include <cmath>

static void splat3(std::vector<double>& field, std::vector<double>& mass,
                   int sw, int W,int H,int D, double gx,double gy,double gz, double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy), k0=(int)std::floor(gz);
  double fx=gx-i0, fy=gy-j0, fz=gz-k0;
  double wx[2]={1-fx,fx}, wy[2]={1-fy,fy}, wz[2]={1-fz,fz};
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){
    int ii=i0+di, jj=j0+dj, kk=k0+dk;
    if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double wgt=wx[di]*wy[dj]*wz[dk];
    int idx=ii + sw*(jj + H*kk);
    field[idx]+=wgt*mom; mass[idx]+=wgt*m;
  }
}

void p2g(UniformGrid3D& g, const Particles3D& ps){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0); std::fill(g.vfield.begin(),g.vfield.end(),0.0);
  std::fill(g.wfield.begin(),g.wfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0); std::fill(g.mv.begin(),g.mv.end(),0.0); std::fill(g.mw.begin(),g.mw.end(),0.0);
  const double m_p=1.0;
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    splat3(g.ufield,g.mu, g.nx+1, g.nx+1,g.ny,g.nz, px, py-0.5, pz-0.5, m_p*ps.vel[kpt].x, m_p);
    splat3(g.vfield,g.mv, g.nx,   g.nx,g.ny+1,g.nz, px-0.5, py, pz-0.5, m_p*ps.vel[kpt].y, m_p);
    splat3(g.wfield,g.mw, g.nx,   g.nx,g.ny,g.nz+1, px-0.5, py-0.5, pz, m_p*ps.vel[kpt].z, m_p);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0.0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0.0) g.vfield[i]/=g.mv[i];
  for(size_t i=0;i<g.wfield.size();++i) if(g.mw[i]>0.0) g.wfield[i]/=g.mw[i];
}

static double tri(const std::vector<double>& f,int sw,int W,int H,int D,double gx,double gy,double gz){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy), k0=(int)std::floor(gz);
  double fx=gx-i0, fy=gy-j0, fz=gz-k0;
  auto get=[&](int ii,int jj,int kk)->double{
    ii=std::max(0,std::min(W-1,ii)); jj=std::max(0,std::min(H-1,jj)); kk=std::max(0,std::min(D-1,kk));
    return f[ii+sw*(jj+H*kk)]; };
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0;
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di)
    s+=wx[di]*wy[dj]*wz[dk]*get(i0+di,j0+dj,k0+dk);
  return s;
}

double sampleU(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.ufield,g.nx+1,g.nx+1,g.ny,g.nz,px,py-0.5,pz-0.5); }
double sampleV(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.vfield,g.nx,g.nx,g.ny+1,g.nz,px-0.5,py,pz-0.5); }
double sampleW(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.wfield,g.nx,g.nx,g.ny,g.nz+1,px-0.5,py-0.5,pz); }

void g2p(const UniformGrid3D& g, Particles3D& ps, const UniformGrid3D& saved, double alpha){
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    double un=sampleU(g,px,py,pz), vn=sampleV(g,px,py,pz), wn=sampleW(g,px,py,pz);
    double du=un-sampleU(saved,px,py,pz), dv=vn-sampleV(saved,px,py,pz), dw=wn-sampleW(saved,px,py,pz);
    Vec3 pic{un,vn,wn}; Vec3 flip{ps.vel[kpt].x+du, ps.vel[kpt].y+dv, ps.vel[kpt].z+dw};
    ps.vel[kpt] = flip*alpha + pic*(1.0-alpha);
  }
}
