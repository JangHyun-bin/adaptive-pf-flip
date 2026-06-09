#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "transfer/transfer3d_tp.h"
#include "physics/phasefield.h"
TEST_CASE("3D tp p2g momentum conserved (normalized cubic)") {
  UniformGrid3D g(6,6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles3DTP ps; ps.add({3.0,2.5,2.5},{4.0,0.0,0.0},0);
  p2g_tp(g, ps, pp, Vp);
  double mom=0; for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) mom+=g.u(i,j,k)*g.mu[g.uidx(i,j,k)];
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-9));
}
TEST_CASE("3D tp p2g separates phases") {
  UniformGrid3D g(8,8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles3DTP ps;
  auto seed=[&](int i,int j,int k,unsigned char t){ for(int s=0;s<8;++s){ double x=i+0.25+0.5*(s&1), y=j+0.25+0.5*((s>>1)&1), z=k+0.25+0.5*((s>>2)&1); ps.add({x,y,z},{0,0,0},t);} };
  for(int k=1;k<7;++k)for(int j=1;j<4;++j)for(int i=1;i<7;++i) seed(i,j,k,0);
  for(int k=1;k<7;++k)for(int j=4;j<7;++j)for(int i=1;i<7;++i) seed(i,j,k,1);
  pp.rho_tilde_0 = calibrateRhoTilde0(pp, Vp);
  p2g_tp(g, ps, pp, Vp);
  double phi_liq = phiFromRawDensity(g.mu[g.uidx(4,2,3)], pp);
  double phi_gas = phiFromRawDensity(g.mu[g.uidx(4,5,3)], pp);
  CHECK(phi_liq > 0.8);
  CHECK(phi_gas < 0.2);
}
