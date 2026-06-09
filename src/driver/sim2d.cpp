#include "driver/sim2d.h"
#include "transfer/transfer2d.h"
#include "pressure/pressure2d.h"
#include "advect/advect2d.h"

void Sim2D::initDamBreak() {
  int wcols = grid.nx*4/10, hrows = grid.ny*7/10;
  for (int j=1;j<hrows;++j) for (int i=1;i<wcols;++i)
    for (int sj=0;sj<2;++sj) for (int si=0;si<2;++si) {
      double x = grid.ox + (i + 0.25 + 0.5*si)*grid.dx;
      double y = grid.oy + (j + 0.25 + 0.5*sj)*grid.dx;
      particles.add({x,y}, {0.0,0.0});
    }
}

static void markCells(UniformGrid2D& g, const Particles2D& ps) {
  for (auto& c : g.marker) c = Cell::AIR;
  for (int j=0;j<g.ny;++j){ g.cell(0,j)=Cell::SOLID; g.cell(g.nx-1,j)=Cell::SOLID; }
  for (int i=0;i<g.nx;++i){ g.cell(i,0)=Cell::SOLID; g.cell(i,g.ny-1)=Cell::SOLID; }
  for (size_t k=0;k<ps.size();++k) {
    int i=(int)((ps.pos[k].x-g.ox)/g.dx), j=(int)((ps.pos[k].y-g.oy)/g.dx);
    if (g.inBounds(i,j) && g.cell(i,j)!=Cell::SOLID) g.cell(i,j)=Cell::FLUID;
  }
}

void Sim2D::step() {
  markCells(grid, particles);
  p2g(grid, particles);
  UniformGrid2D saved = grid;                 // velocity snapshot before pressure
  for (size_t idx=0; idx<grid.vfield.size(); ++idx)
    if (grid.mv[idx] > 0.0) grid.vfield[idx] += dt*gravity;
  for (int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for (int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  auto div = divergence(grid);
  solvePressure(grid, div, dt, rho, cg_iters, cg_tol);
  project(grid, dt, rho);
  g2p(grid, particles, saved, alpha);
  advect(particles, grid, dt);
}
