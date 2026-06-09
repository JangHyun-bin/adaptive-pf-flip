#include "driver/sim2d_tp.h"
#include "transfer/transfer2d_tp.h"
#include "pressure/pressure2d_vc.h"
#include <cmath>
#include <algorithm>

static void seedCell(Particles2DTP& ps,int i,int j,double dx,unsigned char t){
  for(int s=0;s<4;++s){ double x=(i+0.25+0.5*(s%2))*dx, y=(j+0.25+0.5*(s/2))*dx; ps.add({x,y},{0,0},t); }
}
void Sim2DTP::initTwoPhaseDamBreak(){
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int wx=grid.nx*4/10, hy=grid.ny*7/10;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    bool liquid = (i<wx && j<hy);
    seedCell(particles,i,j,grid.dx, liquid?0:1);
  }
}
void Sim2DTP::initRayleighTaylor(){
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int mid=grid.ny/2;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert = 1.0*std::cos(2*3.14159265*i/grid.nx);
    bool heavy = (double)j > (mid + pert);
    seedCell(particles,i,j,grid.dx, heavy?0:1);
  }
}
static void markCells(UniformGrid2D& g, const Particles2DTP& ps){
  for(auto& c:g.marker) c=Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(g.nx-1,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,g.ny-1)=Cell::SOLID;}
  for(size_t k=0;k<ps.size();++k){ int i=(int)((ps.pos[k].x-g.ox)/g.dx),j=(int)((ps.pos[k].y-g.oy)/g.dx);
    if(g.inBounds(i,j)&&g.cell(i,j)!=Cell::SOLID) g.cell(i,j)=Cell::FLUID; }
}
static void advect_tp(Particles2DTP& ps, UniformGrid2D& g, double dt){
  auto sU=[&](double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5);
    double fx=px-i0,fy=(py-0.5)-j0; auto gv=[&](int ii,int jj){ii=std::max(0,std::min(g.nx,ii));jj=std::max(0,std::min(g.ny-1,jj));return g.u(ii,jj);};
    return (1-fx)*(1-fy)*gv(i0,j0)+fx*(1-fy)*gv(i0+1,j0)+(1-fx)*fy*gv(i0,j0+1)+fx*fy*gv(i0+1,j0+1); };
  auto sV=[&](double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py);
    double fx=(px-0.5)-i0,fy=py-j0; auto gv=[&](int ii,int jj){ii=std::max(0,std::min(g.nx-1,ii));jj=std::max(0,std::min(g.ny,jj));return g.v(ii,jj);};
    return (1-fx)*(1-fy)*gv(i0,j0)+fx*(1-fy)*gv(i0+1,j0)+(1-fx)*fy*gv(i0,j0+1)+fx*fy*gv(i0+1,j0+1); };
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(px,py),v1=sV(px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(mx/g.dx,my/g.dx),v2=sV(mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); }
}
void Sim2DTP::step(){
  markCells(grid, particles);
  p2g_tp(grid, particles, phase, Vp);
  for(size_t idx=0; idx<grid.mu.size(); ++idx){ double phi=phiFromRawDensity(grid.mu[idx],phase); grid.bu[idx]=betaFromPhi(phi,phase); }
  for(size_t idx=0; idx<grid.mv.size(); ++idx){ double phi=phiFromRawDensity(grid.mv[idx],phase); grid.bv[idx]=betaFromPhi(phi,phase); }
  UniformGrid2D saved = grid;
  for(size_t idx=0; idx<grid.vfield.size(); ++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  for(int j=0;j<grid.ny;++j){grid.u(0,j)=0;grid.u(1,j)=0;grid.u(grid.nx-1,j)=0;grid.u(grid.nx,j)=0;}
  for(int i=0;i<grid.nx;++i){grid.v(i,0)=0;grid.v(i,1)=0;grid.v(i,grid.ny-1)=0;grid.v(i,grid.ny)=0;}
  auto div=divergenceVC(grid); solvePressureVC(grid,div,dt,cg_iters,cg_tol); projectVC(grid,dt);
  g2p_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  advect_tp(particles, grid, dt);
}
