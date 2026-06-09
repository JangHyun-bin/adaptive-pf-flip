#include "driver/sim3d.h"
#include "transfer/transfer3d.h"
#include "pressure/pressure3d.h"
#include "advect/advect3d.h"
#include "physics/viscosity.h"

void Sim3D::initDamBreak(){
  int wx=grid.nx*4/10, hy=grid.ny*7/10, dz=grid.nz;
  for(int k=1;k<dz-1;++k)for(int j=1;j<hy;++j)for(int i=1;i<wx;++i)
    for(int sk=0;sk<2;++sk)for(int sj=0;sj<2;++sj)for(int si=0;si<2;++si){
      double x=grid.ox+(i+0.25+0.5*si)*grid.dx, y=grid.oy+(j+0.25+0.5*sj)*grid.dx, z=grid.oz+(k+0.25+0.5*sk)*grid.dx;
      particles.add({x,y,z},{0,0,0},0);
    }
}

static void markCells(UniformGrid3D& g, const Particles3D& ps){
  for(auto& c:g.marker) c=Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  for(size_t t=0;t<ps.size();++t){
    int i=(int)((ps.pos[t].x-g.ox)/g.dx), j=(int)((ps.pos[t].y-g.oy)/g.dx), k=(int)((ps.pos[t].z-g.oz)/g.dx);
    if(g.inBounds(i,j,k)&&g.cell(i,j,k)!=Cell3::SOLID) g.cell(i,j,k)=Cell3::FLUID;
  }
}

void Sim3D::step(){
  double alpha = alphaForViscosity(target_nu, grid.dx, dt);
  markCells(grid, particles);
  p2g(grid, particles);
  UniformGrid3D saved = grid;
  for(size_t idx=0; idx<grid.vfield.size(); ++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  // No-penetration BC at wall-interface faces (cells 0 and n-1 are SOLID)
  for(int k=0;k<grid.nz;++k)for(int j=0;j<grid.ny;++j){ grid.u(0,j,k)=0; grid.u(1,j,k)=0; grid.u(grid.nx-1,j,k)=0; grid.u(grid.nx,j,k)=0; }
  for(int k=0;k<grid.nz;++k)for(int i=0;i<grid.nx;++i){ grid.v(i,0,k)=0; grid.v(i,1,k)=0; grid.v(i,grid.ny-1,k)=0; grid.v(i,grid.ny,k)=0; }
  for(int j=0;j<grid.ny;++j)for(int i=0;i<grid.nx;++i){ grid.w(i,j,0)=0; grid.w(i,j,1)=0; grid.w(i,j,grid.nz-1)=0; grid.w(i,j,grid.nz)=0; }
  auto div = divergence(grid);
  solvePressure(grid, div, dt, rho, cg_iters, cg_tol);
  project(grid, dt, rho);
  extrapolateVelocity(grid, extrap_sweeps);
  g2p(grid, particles, saved, alpha);
  advect(particles, grid, dt);
}
