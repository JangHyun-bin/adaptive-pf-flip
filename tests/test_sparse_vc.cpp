#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d_tp.h"
#include "physics/phasefield.h"
#include <cmath>
TEST_CASE("sparse VC projection removes divergence (uniform liquid beta, Dirichlet air)") {
  SparseMacGrid2D<8> g(32,32,1.0); PhaseParams pp;
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=(i==0||i==g.nx-1||j==0||j==g.ny-1)?2 : ((i>=10&&i<20&&j>=10&&j<20)?1:0);
    if(c!=0) g.setCell(i,j,c);
  }
  // packed-liquid raw density (=rho_l*rho_tilde_0=1) on blob faces -> beta ~ 1/rho_l
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.mu(i,j)=1.0f;
  for(int j=10;j<=20;++j)for(int i=10;i<20;++i) g.mv(i,j)=1.0f;
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.u(i,j)=(float)i;   // divergent
  spProjectStepVC(g, pp, 1.0, 500, 1e-9);
  double mx=0; for(int j=10;j<20;++j)for(int i=10;i<20;++i){
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j)); mx=std::max(mx,std::abs(d)); }
  CHECK(mx < 1e-4);
  CHECK(g.pf.activeBlockCount() == 4);   // blob [10,20)^2 -> p-blocks {1,2}x{1,2} only
}
TEST_CASE("sparse VC hydrostatic two-phase column, pure Neumann (pin engaged): residual |v| bounded") {
  SparseMacGrid2D<8> g(6,16,1.0); PhaseParams pp;
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=(i==0||i==g.nx-1||j==0||j==g.ny-1)?2:1;     // ALL interior FLUID -> no AIR anywhere
    g.setCell(i,j,c);
  }
  // face raw densities: heavy (packed liquid, raw=1 -> beta~1) below j=8, light (gas, raw=0.01 -> beta=100) above
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.mu(i,j)=(j<8)?1.0f:0.01f;
  for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i) g.mv(i,j)=(j<8)?1.0f:0.01f;
  double dt=0.1, gc=-9.81;
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.v(i,j)=g.gv(i,j)+(float)(dt*gc);
  spProjectStepVC(g, pp, dt, 1000, 1e-10);
  double mv=0; for(int j=2;j<g.ny-1;++j)for(int i=1;i<g.nx-1;++i) mv=std::max(mv,std::abs((double)g.gv(i,j)));
  CHECK(mv < 0.5);   // hydrostatic balance held (free-fall would be ~0.981)
}
