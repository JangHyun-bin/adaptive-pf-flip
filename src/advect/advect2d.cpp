#include "advect/advect2d.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
#include <algorithm>

void advect(Particles2D& ps, const UniformGrid2D& g, double dt) {
  double lo_x = g.ox + 0.5*g.dx, hi_x = g.ox + (g.nx-0.5)*g.dx;
  double lo_y = g.oy + 0.5*g.dx, hi_y = g.oy + (g.ny-0.5)*g.dx;
  for (size_t k=0;k<ps.size();++k) {
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double u1=sampleU(g,px,py), v1=sampleV(g,px,py);
    double mx=ps.pos[k].x+0.5*dt*u1, my=ps.pos[k].y+0.5*dt*v1;
    double mpx=(mx-g.ox)/g.dx, mpy=(my-g.oy)/g.dx;
    double u2=sampleU(g,mpx,mpy), v2=sampleV(g,mpx,mpy);
    double nx_=ps.pos[k].x+dt*u2, ny_=ps.pos[k].y+dt*v2;
    ps.pos[k].x = std::max(lo_x, std::min(hi_x, nx_));
    ps.pos[k].y = std::max(lo_y, std::min(hi_y, ny_));
  }
}
