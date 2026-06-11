#include "doctest.h"
#include "pressure/multires_pressure2d.h"
#include "grid/multires_mac_grid2d.h"

#include <algorithm>
#include <cmath>
#include <set>
#include <vector>

// Task 5 is smoke-only; native finite-volume coarse-fine coupling is Task 6.
TEST_CASE("multires pressure: smoke mean operator annihilates constant pressure") {
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

TEST_CASE("multires pressure: smoke u-face averaging reduces spread") {
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

TEST_CASE("multires pressure: constant pressure has zero native operator") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> p(sys.cellCount(), 7.0);
  std::vector<double> Ap;
  sys.apply(p, Ap);

  double mx = 0.0;
  for (double v : Ap) {
    mx = std::max(mx, std::abs(v));
  }
  CHECK(mx < 1e-10);
}

TEST_CASE("multires pressure: weighted dot symmetry") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> x(sys.cellCount());
  std::vector<double> y(sys.cellCount());
  std::vector<double> Ax;
  std::vector<double> Ay;
  for (int i = 0; i < sys.cellCount(); ++i) {
    x[i] = 0.25 + 0.1 * i;
    y[i] = 1.0 - 0.03 * i;
  }
  sys.apply(x, Ax);
  sys.apply(y, Ay);

  double lhs = 0.0;
  double rhs = 0.0;
  for (int i = 0; i < sys.cellCount(); ++i) {
    lhs += sys.volume(i) * x[i] * Ay[i];
    rhs += sys.volume(i) * y[i] * Ax[i];
  }
  CHECK(lhs == doctest::Approx(rhs).epsilon(1e-9));
}

TEST_CASE("multires pressure: native edges include mixed-level coupling") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  bool sawMixedVolumeEdge = false;
  std::set<std::pair<int, int>> edgePairs;
  for (const MREdge& e : sys.edges) {
    CHECK(e.a >= 0);
    CHECK(e.b >= 0);
    CHECK(e.a < sys.cellCount());
    CHECK(e.b < sys.cellCount());
    CHECK(e.a != e.b);
    CHECK(e.conductance > 0.0);
    CHECK(edgePairs.insert({std::min(e.a, e.b), std::max(e.a, e.b)}).second);
    sawMixedVolumeEdge = sawMixedVolumeEdge || sys.volume(e.a) != doctest::Approx(sys.volume(e.b));
  }

  CHECK(!sys.edges.empty());
  CHECK(sawMixedVolumeEdge);
}
