#include "doctest.h"
#include "driver/sparse_ops3d_tp.h"
#include "grid/sparse_mac_grid3d.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>

TEST_CASE("sparse 3D VC projection removes divergence with liquid beta") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  PhaseParams pp;
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      for (int i = 0; i < g.nx; ++i) {
        int marker = 0;
        if (i == 0 || i == g.nx - 1 || j == 0 || j == g.ny - 1 || k == 0 || k == g.nz - 1) marker = 2;
        else if (i >= 2 && i < 6 && j >= 2 && j < 6 && k >= 2 && k < 6) marker = 1;
        if (marker != 0) g.setCell(i, j, k, marker);
      }
    }
  }
  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i <= 6; ++i) {
        g.mu(i, j, k) = 1.0f;
        g.u(i, j, k) = (float)i;
      }
      for (int i = 2; i < 6; ++i) {
        g.mv(i, j, k) = 1.0f;
        g.mw(i, j, k) = 1.0f;
      }
    }
  }
  for (int k = 2; k <= 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) g.mw(i, j, k) = 1.0f;
    }
  }

  spProjectStepVC3D(g, pp, 1.0, 1000, 1e-9);

  double maxDiv = 0.0;
  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) {
        double d = g.gu(i + 1, j, k) - g.gu(i, j, k) +
                   g.gv(i, j + 1, k) - g.gv(i, j, k) +
                   g.gw(i, j, k + 1) - g.gw(i, j, k);
        maxDiv = std::max(maxDiv, std::abs(d));
      }
    }
  }
  CHECK(maxDiv < 1e-4);
  CHECK(g.pf.activeBlockCount() == 8);
}

TEST_CASE("sparse 3D VC projection can preserve a target c_div") {
  SparseMacGrid3D<4> g(8, 8, 8, 1.0);
  PhaseParams pp;
  for (int k = 0; k < g.nz; ++k) {
    for (int j = 0; j < g.ny; ++j) {
      for (int i = 0; i < g.nx; ++i) {
        int marker = 0;
        if (i == 0 || i == g.nx - 1 || j == 0 || j == g.ny - 1 || k == 0 || k == g.nz - 1) marker = 2;
        else if (i >= 2 && i < 6 && j >= 2 && j < 6 && k >= 2 && k < 6) marker = 1;
        if (marker != 0) g.setCell(i, j, k, marker);
      }
    }
  }
  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i <= 6; ++i) g.mu(i, j, k) = 1.0f;
      for (int i = 2; i < 6; ++i) {
        g.mv(i, j, k) = 1.0f;
        g.mw(i, j, k) = 1.0f;
      }
    }
  }
  for (int k = 2; k <= 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) g.mw(i, j, k) = 1.0f;
    }
  }

  spProjectStepVC3D(g, pp, 1.0, 1000, 1e-9, 0.125);

  double sumDiv = 0.0;
  int cells = 0;
  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) {
        double d = g.gu(i + 1, j, k) - g.gu(i, j, k) +
                   g.gv(i, j + 1, k) - g.gv(i, j, k) +
                   g.gw(i, j, k + 1) - g.gw(i, j, k);
        sumDiv += d;
        ++cells;
      }
    }
  }
  CHECK(sumDiv / static_cast<double>(cells) == doctest::Approx(0.125).epsilon(1e-4));
}
