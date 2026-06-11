#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d_tp.h"
#include "transfer/transfer2d_tp.h"   // calibrateRhoTilde0_2d
#include "physics/phasefield.h"
#include "particles/particles2d_tp.h"
TEST_CASE("sparse tp p2g: momentum conserved (normalized cubic)") {
  SparseMacGrid2D<8> g(6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps; ps.add({3.0,2.5},{4.0,3.0},0);   // liquid, m_p=rho_l*Vp=1
  spP2G_tp(g, ps, pp, Vp);
  double mom=0; for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) mom += g.gu(i,j)*g.gmu(i,j);
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-6));
  double momv=0; for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i) momv += g.gv(i,j)*g.gmv(i,j);
  CHECK(momv == doctest::Approx(3.0).epsilon(1e-6));
}
TEST_CASE("sparse tp p2g: phase separation phi_liq~1 / phi_gas~0") {
  SparseMacGrid2D<8> g(8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  for(int j=1;j<4;++j)for(int i=1;i<7;++i)for(int s=0;s<4;++s) ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},0);
  for(int j=4;j<7;++j)for(int i=1;i<7;++i)for(int s=0;s<4;++s) ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},1);
  pp.rho_tilde_0 = calibrateRhoTilde0_2d(pp, Vp);
  spP2G_tp(g, ps, pp, Vp);
  CHECK(phiFromRawDensity(g.gmu(4,2), pp) > 0.8);
  CHECK(phiFromRawDensity(g.gmu(4,5), pp) < 0.2);
}
TEST_CASE("sparse tp p2g: splat activates only touched blocks") {
  SparseMacGrid2D<8> g(64,64,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  for(int s=0;s<32;++s) ps.add({16.0+0.2*(s%8), 16.0+0.2*(s/8)},{1.0,0.0},0);  // confined near (16,16)
  spP2G_tp(g, ps, pp, Vp);
  CHECK(g.muf.activeBlockCount() > 0);
  CHECK(g.muf.activeBlockCount() < g.muf.totalBlocks());
}
TEST_CASE("sparse tp g2p: typed alpha blend (FLIP vs PIC per phase)") {
  SparseMacGrid2D<8> g(4,4,1.0), saved(4,4,1.0);
  for(int j=0;j<4;++j)for(int i=0;i<=4;++i){ g.u(i,j)=5.0f; saved.u(i,j)=2.0f; }
  Particles2DTP ps; ps.add({2.0,2.0},{10.0,0.0},0); ps.add({2.0,2.0},{10.0,0.0},1);
  spG2P_tp(g, ps, saved, 1.0, 0.0);   // liquid pure FLIP, gas pure PIC
  CHECK(ps.vel[0].x == doctest::Approx(13.0));  // 10 + (5-2)
  CHECK(ps.vel[1].x == doctest::Approx(5.0));   // grid velocity
}
