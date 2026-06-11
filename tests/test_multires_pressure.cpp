#include "doctest.h"
#include "pressure/multires_pressure2d.h"
#include "grid/multires_mac_grid2d.h"

#include <cmath>
#include <vector>

// Task 5 is smoke-only; native finite-volume coarse-fine coupling is Task 6.
TEST_CASE("multires pressure smoke: mean operator annihilates constant pressure") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> p(sys.cellCount(), 1.0);
  std::vector<double> Ap(sys.cellCount(), 0.0);
  sys.apply(p, Ap);

  double weightedSum = 0.0;
  for (int i = 0; i < sys.cellCount(); ++i) {
    weightedSum += sys.volume(i) * Ap[i];
  }
  CHECK(std::abs(weightedSum) < 1e-9);
}

TEST_CASE("multires pressure smoke: u-face averaging reduces spread") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  for (const MRFaceKey& f : g.uFaces()) {
    g.u(f) = static_cast<float>(f.fineX);
  }
  double before = maxMRDivergence(g);
  projectMR(g, 1.0, 300, 1e-8);
  double after = maxMRDivergence(g);

  CHECK(before > 1.0);
  CHECK(after < before * 0.1);
}

TEST_CASE("multires pressure: system volumes include mixed leaf levels") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  bool sawFineVolume = false;
  bool sawCoarseVolume = false;
  for (int i = 0; i < sys.cellCount(); ++i) {
    sawFineVolume = sawFineVolume || sys.volume(i) == doctest::Approx(1.0);
    sawCoarseVolume = sawCoarseVolume || sys.volume(i) == doctest::Approx(4.0);
    CHECK(sys.volume(i) > 0.0);
  }

  CHECK(sawFineVolume);
  CHECK(sawCoarseVolume);
}
