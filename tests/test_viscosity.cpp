#include "doctest.h"
#include "physics/viscosity.h"
TEST_CASE("alpha<->nu roundtrip (Eq.13)") {
  double dx=0.5, dt=0.01, alpha=0.9;
  double nu = numericalViscosity(alpha, dx, dt);
  CHECK(nu == doctest::Approx((1-alpha)*dx*dx/(6*dt)));
  CHECK(alphaForViscosity(nu, dx, dt) == doctest::Approx(alpha));
}
TEST_CASE("alphaForViscosity clamps") {
  CHECK(alphaForViscosity(1e9, 1.0, 1.0) == doctest::Approx(0.0));
  CHECK(alphaForViscosity(0.0, 1.0, 1.0) == doctest::Approx(1.0));
}
