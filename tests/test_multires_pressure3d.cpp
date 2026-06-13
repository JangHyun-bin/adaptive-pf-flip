#include "doctest.h"
#include "pressure/multires_pressure3d.h"
#include "grid/multires_mac_grid3d.h"

#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>
#include <vector>

namespace {

double totalConductance(const MRPressureSystem3D& sys) {
  double total = 0.0;
  for (const MREdge3D& e : sys.edges) {
    total += e.conductance;
  }
  return total;
}

} // namespace

TEST_CASE("multires 3D pressure: constant pressure has zero native operator") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D sys = buildMRPressureSystem3D(g, 1.0);
  std::vector<double> p(sys.cellCount(), 7.0);
  std::vector<double> Ap;
  sys.apply(p, Ap);

  double mx = 0.0;
  for (double v : Ap) {
    mx = std::max(mx, std::abs(v));
  }
  CHECK(mx < 1e-10);
}

TEST_CASE("multires 3D pressure: weighted dot symmetry") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D sys = buildMRPressureSystem3D(g, 1.0);
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

TEST_CASE("multires 3D pressure: volumes and mixed-level edges are present") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D sys = buildMRPressureSystem3D(g, 1.0);
  bool sawFineVolume = false;
  bool sawCoarseVolume = false;
  bool sawMixedVolumeEdge = false;
  std::set<std::pair<int, int>> edgePairs;
  for (int i = 0; i < sys.cellCount(); ++i) {
    sawFineVolume = sawFineVolume || sys.volume(i) == doctest::Approx(1.0);
    sawCoarseVolume = sawCoarseVolume || sys.volume(i) == doctest::Approx(8.0);
    CHECK(sys.volume(i) > 0.0);
  }
  for (const MREdge3D& e : sys.edges) {
    CHECK(e.a >= 0);
    CHECK(e.b >= 0);
    CHECK(e.a < sys.cellCount());
    CHECK(e.b < sys.cellCount());
    CHECK(e.a != e.b);
    CHECK(e.conductance > 0.0);
    CHECK(edgePairs.insert({std::min(e.a, e.b), std::max(e.a, e.b)}).second);
    sawMixedVolumeEdge = sawMixedVolumeEdge || sys.volume(e.a) != doctest::Approx(sys.volume(e.b));
  }

  CHECK(sawFineVolume);
  CHECK(sawCoarseVolume);
  CHECK(!sys.edges.empty());
  CHECK(sawMixedVolumeEdge);
}

TEST_CASE("multires 3D pressure: apply rejects mismatched vector sizes") {
  MRPressureSystem3D sys;
  sys.volumes.push_back(1.0);

  std::vector<double> out;
  std::vector<double> shortInput;
  std::vector<double> longInput{1.0, 2.0};

  CHECK_THROWS_AS(sys.apply(shortInput, out), std::invalid_argument);
  CHECK_THROWS_AS(sys.apply(longInput, out), std::invalid_argument);
}

TEST_CASE("multires 3D pressure: build uses pressure grid layout for geometry") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D expected = buildMRPressureSystem3D(g, 1.0);
  g.layout.nx = 1;
  g.layout.ny = 1;
  g.layout.nz = 1;
  g.layout.dx = 8.0;
  g.marker.layout.nx = 1;
  g.marker.layout.ny = 1;
  g.marker.layout.nz = 1;
  g.marker.layout.dx = 8.0;
  MRPressureSystem3D actual = buildMRPressureSystem3D(g, 1.0);

  CHECK(actual.cellCount() == expected.cellCount());
  CHECK(actual.edges.size() == expected.edges.size());
  CHECK(totalConductance(actual) == doctest::Approx(totalConductance(expected)).epsilon(1e-12));
}

TEST_CASE("multires 3D pressure: same-level native conductance is exact") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D sys = buildMRPressureSystem3D(g, 1.0);
  CHECK(!sys.edges.empty());
  for (const MREdge3D& e : sys.edges) {
    CHECK(sys.volume(e.a) == doctest::Approx(1.0));
    CHECK(sys.volume(e.b) == doctest::Approx(1.0));
    CHECK(e.conductance == doctest::Approx(1.0).epsilon(1e-12));
  }
}

TEST_CASE("multires 3D pressure: coarse-fine native conductance is exact") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();
  MRMacGrid3D<4> g(layout);

  MRPressureSystem3D sys = buildMRPressureSystem3D(g, 1.0);
  int mixedEdges = 0;
  for (const MREdge3D& e : sys.edges) {
    if (sys.volume(e.a) != doctest::Approx(sys.volume(e.b))) {
      ++mixedEdges;
      CHECK(e.conductance == doctest::Approx(2.0 / 3.0).epsilon(1e-12));
    }
  }
  CHECK(mixedEdges > 0);
}
