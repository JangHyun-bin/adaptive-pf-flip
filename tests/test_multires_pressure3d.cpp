#include "doctest.h"
#include "pressure/multires_pressure3d.h"
#include "grid/multires_mac_grid3d.h"
#include "physics/phasefield.h"

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

void setMarker(MRMacGrid3D<4>& g, int i, int j, int k, int marker) {
  g.marker.ref(g.marker.cellAtFineCell(i, j, k)) = static_cast<float>(marker);
}

int markerAt(const MRMacGrid3D<4>& g, int i, int j, int k) {
  if (i < 0 || i >= g.layout.nx ||
      j < 0 || j >= g.layout.ny ||
      k < 0 || k >= g.layout.nz) {
    return 2;
  }
  return static_cast<int>(g.marker.get(g.marker.cellAtFineCell(i, j, k)) + 0.5f);
}

double markerAwareMaxDivergence(const MRMacGrid3D<4>& g) {
  double mx = 0.0;
  for (int k = 0; k < g.layout.nz; ++k) {
    for (int j = 0; j < g.layout.ny; ++j) {
      for (int i = 0; i < g.layout.nx; ++i) {
        if (markerAt(g, i, j, k) != 1) continue;

        bool solidLeft = markerAt(g, i - 1, j, k) == 2;
        bool solidRight = markerAt(g, i + 1, j, k) == 2;
        bool solidBottom = markerAt(g, i, j - 1, k) == 2;
        bool solidTop = markerAt(g, i, j + 1, k) == 2;
        bool solidBack = markerAt(g, i, j, k - 1) == 2;
        bool solidFront = markerAt(g, i, j, k + 1) == 2;

        double uR = solidRight ? 0.0 : static_cast<double>(g.gu(MRFaceKey3D{0, i + 1, j, k, 1, 1}));
        double uL = solidLeft ? 0.0 : static_cast<double>(g.gu(MRFaceKey3D{0, i, j, k, 1, 1}));
        double vT = solidTop ? 0.0 : static_cast<double>(g.gv(MRFaceKey3D{1, i, j + 1, k, 1, 1}));
        double vB = solidBottom ? 0.0 : static_cast<double>(g.gv(MRFaceKey3D{1, i, j, k, 1, 1}));
        double wF = solidFront ? 0.0 : static_cast<double>(g.gw(MRFaceKey3D{2, i, j, k + 1, 1, 1}));
        double wK = solidBack ? 0.0 : static_cast<double>(g.gw(MRFaceKey3D{2, i, j, k, 1, 1}));

        mx = std::max(mx, std::abs(((uR - uL) + (vT - vB) + (wF - wK)) / g.layout.dx));
      }
    }
  }
  return mx;
}

void seedMarkedDivergenceCase(MRMacGrid3D<4>& g) {
  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = 1.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = 1.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = 1.0f;

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;
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

TEST_CASE("multires 3D pressure: phase-aware projection clears stale pressure without fluid") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;

  g.p.ref(g.p.cellAtFineCell(3, 3, 3)) = 9.0f;
  setMarker(g, 3, 3, 3, 0);
  setMarker(g, 0, 3, 3, 2);

  projectMR3D(g, pp, 1.0, 20, 1e-8);

  CHECK(g.p.blocks.empty());
}

TEST_CASE("multires 3D pressure: phase-aware projection reduces marked divergence and zeros solid faces") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;

  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = 1.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = 1.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = 1.0f;

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;

  double before = markerAwareMaxDivergence(g);
  projectMR3D(g, pp, 1.0, 100, 1e-10);
  double after = markerAwareMaxDivergence(g);

  CHECK(before > 1.0);
  CHECK(after < before * 0.55);
  CHECK(g.gu(MRFaceKey3D{0, 3, 3, 3, 1, 1}) == doctest::Approx(0.0).epsilon(1e-12));
}

TEST_CASE("multires 3D pressure: solve stats track residual and iterations") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;

  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = 1.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = 1.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = 1.0f;

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, 100, 1e-10, &stats);

  CHECK(stats.active_cells == 6);
  CHECK(stats.max_iterations == 100);
  CHECK(stats.tolerance == doctest::Approx(1e-10));
  CHECK(stats.iterations > 0);
  CHECK(stats.iterations <= stats.max_iterations);
  CHECK(stats.initial_residual > 0.0);
  CHECK(stats.final_residual >= 0.0);
  CHECK(stats.final_residual <= stats.initial_residual);
  CHECK(stats.min_residual <= stats.initial_residual);
  CHECK(stats.max_residual >= stats.initial_residual);
  CHECK(stats.residual_history.empty());
  CHECK(stats.max_diag >= stats.min_positive_diag);
  CHECK(stats.min_positive_diag > 0.0);
  CHECK(!stats.used_average_projection);
}

TEST_CASE("multires 3D pressure: relative tolerance sets effective stopping threshold") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;

  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = 1.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = 1.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = 1.0f;

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;

  MRPressureSolveConfig3D config;
  config.max_iterations = 100;
  config.absolute_tolerance = 1e-12;
  config.relative_tolerance = 0.25;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, config, &stats);

  CHECK(stats.relative_tolerance == doctest::Approx(0.25));
  CHECK(stats.effective_tolerance == doctest::Approx(stats.initial_residual * 0.25));
  CHECK(stats.converged);
  CHECK(stats.final_residual <= stats.effective_tolerance);
  CHECK(stats.iterations < config.max_iterations);
}

TEST_CASE("multires 3D pressure: non-jacobi CG mode reports stats and stays finite") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;

  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = 1.0f;
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = 1.0f;
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = 1.0f;

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;

  MRPressureSolveConfig3D config;
  config.max_iterations = 100;
  config.absolute_tolerance = 1e-8;
  config.use_jacobi_preconditioner = false;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, config, &stats);

  CHECK(!stats.used_jacobi_preconditioner);
  CHECK(stats.iterations > 0);
  CHECK(stats.iterations <= config.max_iterations);
  CHECK(std::isfinite(stats.final_residual));
  CHECK(!stats.breakdown);
}

TEST_CASE("multires 3D pressure: adaptive restart reports stats and stays finite") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;
  seedMarkedDivergenceCase(g);

  MRPressureSolveConfig3D config;
  config.max_iterations = 100;
  config.absolute_tolerance = 1e-8;
  config.adaptive_restart = true;
  config.restart_growth_threshold = 1.0;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, config, &stats);

  CHECK(stats.adaptive_restart);
  CHECK(stats.restart_growth_threshold == doctest::Approx(1.0));
  CHECK(stats.restarts >= 0);
  CHECK(stats.iterations > 0);
  CHECK(stats.iterations <= config.max_iterations);
  CHECK(std::isfinite(stats.final_residual));
  CHECK(!stats.breakdown);
}

TEST_CASE("multires 3D pressure: adaptive restart can be disabled") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;
  seedMarkedDivergenceCase(g);

  MRPressureSolveConfig3D config;
  config.max_iterations = 100;
  config.absolute_tolerance = 1e-8;
  config.adaptive_restart = false;
  config.restart_growth_threshold = 1.01;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, config, &stats);

  CHECK(!stats.adaptive_restart);
  CHECK(stats.restart_growth_threshold == doctest::Approx(1.01));
  CHECK(stats.restarts == 0);
  CHECK(stats.iterations > 0);
  CHECK(stats.iterations <= config.max_iterations);
  CHECK(std::isfinite(stats.final_residual));
  CHECK(!stats.breakdown);
}

TEST_CASE("multires 3D pressure: residual history records bounded samples") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;
  seedMarkedDivergenceCase(g);

  MRPressureSolveConfig3D config;
  config.max_iterations = 100;
  config.absolute_tolerance = 1e-8;
  config.residual_history_stride = 1;
  config.residual_history_limit = 2;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, config, &stats);

  REQUIRE(!stats.residual_history.empty());
  CHECK(stats.residual_history_stride == 1);
  CHECK(stats.residual_history_limit == 2);
  CHECK(stats.residual_history.size() <= 2);
  CHECK(stats.residual_history.front() == doctest::Approx(stats.initial_residual));
  CHECK(stats.min_residual <= stats.final_residual);
  CHECK(stats.max_residual >= stats.initial_residual);
  if (stats.iterations >= 2) {
    CHECK(stats.residual_history_truncated);
  }
  CHECK(std::isfinite(stats.residual_history.back()));
  CHECK(!stats.breakdown);
}

TEST_CASE("multires 3D pressure: high density ratio stats remain finite") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);
  PhaseParams pp;
  pp.rho_l = 1000.0;
  pp.rho_g = 1.0;
  pp.rho_tilde_0 = 1.0;

  setMarker(g, 2, 3, 3, 2);
  setMarker(g, 3, 3, 3, 1);
  setMarker(g, 4, 3, 3, 1);
  setMarker(g, 3, 4, 3, 1);
  setMarker(g, 4, 4, 3, 1);
  setMarker(g, 3, 3, 4, 1);
  setMarker(g, 4, 3, 4, 1);

  for (const MRFaceKey3D& f : g.uFaces()) g.mU(f) = static_cast<float>(pp.rho_l);
  for (const MRFaceKey3D& f : g.vFaces()) g.mV(f) = static_cast<float>(pp.rho_l);
  for (const MRFaceKey3D& f : g.wFaces()) g.mW(f) = static_cast<float>(pp.rho_l);

  g.u(MRFaceKey3D{0, 3, 3, 3, 1, 1}) = 7.0f;
  g.u(MRFaceKey3D{0, 5, 3, 3, 1, 1}) = 4.0f;
  g.v(MRFaceKey3D{1, 4, 5, 3, 1, 1}) = -3.0f;
  g.w(MRFaceKey3D{2, 4, 3, 5, 1, 1}) = 2.0f;

  MRPressureSolveStats3D stats;
  projectMR3D(g, pp, 1.0, 200, 1e-8, &stats);

  CHECK(stats.active_cells == 6);
  CHECK(stats.iterations > 0);
  CHECK(stats.iterations <= stats.max_iterations);
  CHECK(std::isfinite(stats.initial_residual));
  CHECK(std::isfinite(stats.final_residual));
  CHECK(stats.final_residual <= stats.initial_residual);
  CHECK(!stats.breakdown);
}

TEST_CASE("multires 3D pressure: no-marker smoke projection reduces u spread") {
  MRLayout3D<4> layout(8, 8, 8, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid3D<4> g(layout);

  for (const MRFaceKey3D& f : g.uFaces()) {
    g.u(f) = static_cast<float>(f.fineX);
  }
  double before = maxMRDivergence3D(g);
  projectMR3D(g, 1.0, 100, 1e-8);
  double after = maxMRDivergence3D(g);

  CHECK(before > 1.0);
  CHECK(after < before * 0.1);
}
