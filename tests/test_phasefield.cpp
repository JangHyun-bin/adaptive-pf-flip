#include "doctest.h"
#include "physics/phasefield.h"
#include <cmath>
TEST_CASE("Eq.7 phase field curve (Fig.7)") {
  PhaseParams pp;
  CHECK(phiFromRawDensity(pp.rho_g, pp) == doctest::Approx(0.0));
  CHECK(phiFromRawDensity(pp.rho_l, pp) == doctest::Approx(1.0).epsilon(0.02));
  double prev=-1;
  for(double rt=0; rt<=1.0; rt+=0.05){ double f=phiFromRawDensity(rt,pp); CHECK(f>=prev-1e-12); CHECK(f>=0.0); CHECK(f<=1.0); prev=f; }
  double rmin = std::log(pp.rho_l/pp.rho_g)*pp.rho_g*pp.rho_tilde_0;
  CHECK(phiFromRawDensity(rmin*0.99, pp) == doctest::Approx(0.0));
  CHECK(phiFromRawDensity(rmin*1.01 + 0.05, pp) > 0.0);
}
