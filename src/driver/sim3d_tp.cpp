#include "driver/sim3d_tp.h"
#include "transfer/transfer3d_tp.h"
#include "pressure/pressure3d_vc.h"
#include <cmath>
#include <algorithm>
static void seed(Particles3DTP& ps,int i,int j,int k,double dx,unsigned char t){
  for(int s=0;s<8;++s){ double x=(i+0.25+0.5*(s&1))*dx,y=(j+0.25+0.5*((s>>1)&1))*dx,z=(k+0.25+0.5*((s>>2)&1))*dx; ps.add({x,y,z},{0,0,0},t);} }
void Sim3DTP::initTwoPhaseDamBreak(){
  phase.rho_tilde_0=calibrateRhoTilde0(phase,Vp);
  int wx=grid.nx*4/10,hy=grid.ny*7/10;
  for(int k=1;k<grid.nz-1;++k)for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){ bool liq=(i<wx&&j<hy); seed(particles,i,j,k,grid.dx,liq?0:1); }
}
void Sim3DTP::initRayleighTaylor(){
  phase.rho_tilde_0=calibrateRhoTilde0(phase,Vp); int mid=grid.ny/2;
  for(int k=1;k<grid.nz-1;++k)for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert=1.0*std::cos(2*3.14159265*i/grid.nx)*std::cos(2*3.14159265*k/grid.nz);
    bool heavy=(double)j>(mid+pert); seed(particles,i,j,k,grid.dx,heavy?0:1); }
}
static void markCells(UniformGrid3D& g,const Particles3DTP& ps){
  for(auto& c:g.marker) c=Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  for(size_t p=0;p<ps.size();++p){ int i=(int)((ps.pos[p].x-g.ox)/g.dx),j=(int)((ps.pos[p].y-g.oy)/g.dx),k=(int)((ps.pos[p].z-g.oz)/g.dx);
    if(g.inBounds(i,j,k)&&g.cell(i,j,k)!=Cell3::SOLID) g.cell(i,j,k)=Cell3::FLUID; }
}
static double sUg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5),k0=(int)std::floor(pz-0.5);
  double fx=px-i0,fy=(py-0.5)-j0,fz=(pz-0.5)-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx,i));j=std::max(0,std::min(g.ny-1,j));k=std::max(0,std::min(g.nz-1,k));return g.u(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static double sVg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py),k0=(int)std::floor(pz-0.5);
  double fx=(px-0.5)-i0,fy=py-j0,fz=(pz-0.5)-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx-1,i));j=std::max(0,std::min(g.ny,j));k=std::max(0,std::min(g.nz-1,k));return g.v(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static double sWg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py-0.5),k0=(int)std::floor(pz);
  double fx=(px-0.5)-i0,fy=(py-0.5)-j0,fz=pz-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx-1,i));j=std::max(0,std::min(g.ny-1,j));k=std::max(0,std::min(g.nz,k));return g.w(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static void advect_tp(Particles3DTP& ps,UniformGrid3D& g,double dt){
  double lo=0.5*g.dx,hix=(g.nx-0.5)*g.dx,hiy=(g.ny-0.5)*g.dx,hiz=(g.nz-0.5)*g.dx;
  for(size_t p=0;p<ps.size();++p){ double px=ps.pos[p].x/g.dx,py=ps.pos[p].y/g.dx,pz=ps.pos[p].z/g.dx;
    double u1=sUg(g,px,py,pz),v1=sVg(g,px,py,pz),w1=sWg(g,px,py,pz);
    double mx=ps.pos[p].x+0.5*dt*u1,my=ps.pos[p].y+0.5*dt*v1,mz=ps.pos[p].z+0.5*dt*w1;
    double u2=sUg(g,mx/g.dx,my/g.dx,mz/g.dx),v2=sVg(g,mx/g.dx,my/g.dx,mz/g.dx),w2=sWg(g,mx/g.dx,my/g.dx,mz/g.dx);
    ps.pos[p].x=std::max(lo,std::min(hix,ps.pos[p].x+dt*u2));
    ps.pos[p].y=std::max(lo,std::min(hiy,ps.pos[p].y+dt*v2));
    ps.pos[p].z=std::max(lo,std::min(hiz,ps.pos[p].z+dt*w2)); }
}
void Sim3DTP::step(){
  markCells(grid,particles); p2g_tp(grid,particles,phase,Vp);
  for(size_t idx=0;idx<grid.mu.size();++idx) grid.bu[idx]=betaFromPhi(phiFromRawDensity(grid.mu[idx],phase),phase);
  for(size_t idx=0;idx<grid.mv.size();++idx) grid.bv[idx]=betaFromPhi(phiFromRawDensity(grid.mv[idx],phase),phase);
  for(size_t idx=0;idx<grid.mw.size();++idx) grid.bw[idx]=betaFromPhi(phiFromRawDensity(grid.mw[idx],phase),phase);
  UniformGrid3D saved=grid;
  for(size_t idx=0;idx<grid.vfield.size();++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  for(int k=0;k<grid.nz;++k)for(int j=0;j<grid.ny;++j){grid.u(0,j,k)=0;grid.u(1,j,k)=0;grid.u(grid.nx-1,j,k)=0;grid.u(grid.nx,j,k)=0;}
  for(int k=0;k<grid.nz;++k)for(int i=0;i<grid.nx;++i){grid.v(i,0,k)=0;grid.v(i,1,k)=0;grid.v(i,grid.ny-1,k)=0;grid.v(i,grid.ny,k)=0;}
  for(int j=0;j<grid.ny;++j)for(int i=0;i<grid.nx;++i){grid.w(i,j,0)=0;grid.w(i,j,1)=0;grid.w(i,j,grid.nz-1)=0;grid.w(i,j,grid.nz)=0;}
  auto div=divergenceVC(grid); solvePressureVC(grid,div,dt,cg_iters,cg_tol); projectVC(grid,dt);
  g2p_tp(grid,particles,saved,alpha_liquid,alpha_gas); advect_tp(particles,grid,dt);
}
