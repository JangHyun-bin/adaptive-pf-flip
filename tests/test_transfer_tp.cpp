#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "transfer/transfer2d_tp.h"
#include "physics/phasefield.h"
TEST_CASE("tp p2g momentum conserved (cubic kernel)") {
  UniformGrid2D g(6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps; ps.add({3.0,2.5},{4.0,0.0},0);   // liquid, m_p = rho_l*Vp = 1
  p2g_tp(g, ps, pp, Vp);
  double mom=0; for(int j=0;j<g.ny;++j) for(int i=0;i<=g.nx;++i) mom += g.u(i,j)*g.mu[i+(g.nx+1)*j];
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-9));
}
TEST_CASE("tp p2g separates phases: liquid block -> phi~1, gas -> phi~0") {
  UniformGrid2D g(8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  for(int j=1;j<4;++j) for(int i=1;i<7;++i) for(int s=0;s<4;++s){ ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},0); }
  for(int j=4;j<7;++j) for(int i=1;i<7;++i) for(int s=0;s<4;++s){ ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},1); }
  pp.rho_tilde_0 = calibrateRhoTilde0_2d(pp, Vp);
  p2g_tp(g, ps, pp, Vp);
  double phi_liq = phiFromRawDensity(g.mu[4+(g.nx+1)*2], pp);
  double phi_gas = phiFromRawDensity(g.mu[4+(g.nx+1)*5], pp);
  CHECK(phi_liq > 0.8);
  CHECK(phi_gas < 0.2);
}
