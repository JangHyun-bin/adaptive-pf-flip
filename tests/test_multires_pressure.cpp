#include "doctest.h"
#include "pressure/multires_pressure2d.h"
#include "grid/multires_mac_grid2d.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>
#include <vector>

namespace {

double totalConductance(const MRPressureSystem2D& sys) {
  double total = 0.0;
  for (const MREdge& e : sys.edges) {
    total += e.conductance;
  }
  return total;
}

void setMarker(MRMacGrid2D<8>& g, int i, int j, int marker) {
  g.marker.ref(g.marker.cellAtFineCell(i, j)) = static_cast<float>(marker);
}

int markerAt(const MRMacGrid2D<8>& g, int i, int j) {
  if (i < 0 || i >= g.layout.nx || j < 0 || j >= g.layout.ny) return 2;
  return static_cast<int>(g.marker.get(g.marker.cellAtFineCell(i, j)) + 0.5f);
}

double markerAwareMaxDivergence(const MRMacGrid2D<8>& g) {
  double mx = 0.0;
  for (int j = 0; j < g.layout.ny; ++j) {
    for (int i = 0; i < g.layout.nx; ++i) {
      if (markerAt(g, i, j) != 1) continue;

      bool solidLeft = markerAt(g, i - 1, j) == 2;
      bool solidRight = markerAt(g, i + 1, j) == 2;
      bool solidBottom = markerAt(g, i, j - 1) == 2;
      bool solidTop = markerAt(g, i, j + 1) == 2;

      double uR = solidRight ? 0.0 : static_cast<double>(g.gu(MRFaceKey{0, i + 1, j, 1}));
      double uL = solidLeft ? 0.0 : static_cast<double>(g.gu(MRFaceKey{0, i, j, 1}));
      double vT = solidTop ? 0.0 : static_cast<double>(g.gv(MRFaceKey{1, i, j + 1, 1}));
      double vB = solidBottom ? 0.0 : static_cast<double>(g.gv(MRFaceKey{1, i, j, 1}));

      mx = std::max(mx, std::abs(((uR - uL) + (vT - vB)) / g.layout.dx));
    }
  }
  return mx;
}

} // namespace

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

TEST_CASE("multires pressure: apply rejects mismatched vector sizes") {
  MRPressureSystem2D sys;
  sys.volumes.push_back(1.0);

  std::vector<double> out;
  std::vector<double> shortInput;
  std::vector<double> longInput{1.0, 2.0};

  CHECK_THROWS_AS(sys.apply(shortInput, out), std::invalid_argument);
  CHECK_THROWS_AS(sys.apply(longInput, out), std::invalid_argument);
}

TEST_CASE("multires pressure: build uses pressure grid layout for geometry") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D expected = buildMRPressureSystem(g, 1.0);
  g.layout.nx = 1;
  g.layout.ny = 1;
  g.layout.dx = 8.0;
  g.marker.layout.nx = 1;
  g.marker.layout.ny = 1;
  g.marker.layout.dx = 8.0;
  MRPressureSystem2D actual = buildMRPressureSystem(g, 1.0);

  CHECK(actual.cellCount() == expected.cellCount());
  CHECK(actual.edges.size() == expected.edges.size());
  CHECK(totalConductance(actual) == doctest::Approx(totalConductance(expected)).epsilon(1e-12));
}

TEST_CASE("multires pressure: same-level native conductance is exact") {
  MRLayout2D<8> layout(16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  CHECK(!sys.edges.empty());
  for (const MREdge& e : sys.edges) {
    CHECK(sys.volume(e.a) == doctest::Approx(1.0));
    CHECK(sys.volume(e.b) == doctest::Approx(1.0));
    CHECK(e.conductance == doctest::Approx(1.0).epsilon(1e-12));
  }
}

TEST_CASE("multires pressure: coarse-fine native conductance is exact") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  int mixedEdges = 0;
  for (const MREdge& e : sys.edges) {
    if (sys.volume(e.a) != doctest::Approx(sys.volume(e.b))) {
      ++mixedEdges;
      CHECK(e.conductance == doctest::Approx(2.0 / 3.0).epsilon(1e-12));
    }
  }
  CHECK(mixedEdges > 0);
}

TEST_CASE("multires pressure: phase-aware projection clears stale pressure without fluid") {
  MRLayout2D<8> layout(16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid2D<8> g(layout);
  PhaseParams pp;

  g.p.ref(g.p.cellAtFineCell(3, 3)) = 9.0f;
  setMarker(g, 3, 3, 0);
  setMarker(g, 0, 3, 2);

  projectMR(g, pp, 1.0, 20, 1e-8);

  CHECK(g.p.blocks.empty());
}

TEST_CASE("multires pressure: phase-aware projection reduces marked divergence and zeros solid faces") {
  MRLayout2D<8> layout(8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid2D<8> g(layout);
  PhaseParams pp;

  setMarker(g, 2, 3, 2);
  setMarker(g, 3, 3, 1);
  setMarker(g, 4, 3, 1);
  setMarker(g, 3, 4, 1);
  setMarker(g, 4, 4, 1);

  for (const MRFaceKey& f : g.uFaces()) {
    g.mU(f) = 1.0f;
  }
  for (const MRFaceKey& f : g.vFaces()) {
    g.mV(f) = 1.0f;
  }

  g.u(MRFaceKey{0, 3, 3, 1}) = 7.0f;
  g.u(MRFaceKey{0, 5, 3, 1}) = 4.0f;
  g.v(MRFaceKey{1, 4, 5, 1}) = -3.0f;

  double before = markerAwareMaxDivergence(g);
  projectMR(g, pp, 1.0, 80, 1e-10);
  double after = markerAwareMaxDivergence(g);

  CHECK(before > 1.0);
  CHECK(after < before * 0.5);
  CHECK(g.gu(MRFaceKey{0, 3, 3, 1}) == doctest::Approx(0.0).epsilon(1e-12));
}
