#include "doctest.h"
#include "driver/sparse_ops3d.h"
#include "grid/sparse_mac_grid3d.h"
#include "grid/uniform_grid3d.h"
#include "pressure/pressure3d.h"
#include <algorithm>
#include <cmath>

TEST_CASE("sparse 3D projection matches uniform pressure on a compact fluid box") {
  const int NX = 8, NY = 8, NZ = 8;
  UniformGrid3D dense(NX, NY, NZ, 1.0);
  SparseMacGrid3D<4> sparse(NX, NY, NZ, 1.0);

  for (int k = 0; k < NZ; ++k) {
    for (int j = 0; j < NY; ++j) {
      for (int i = 0; i < NX; ++i) {
        int marker = 0;
        if (i == 0 || i == NX - 1 || j == 0 || j == NY - 1 || k == 0 || k == NZ - 1) {
          marker = 2;
        } else if (i >= 2 && i < 6 && j >= 2 && j < 6 && k >= 2 && k < 6) {
          marker = 1;
        }
        dense.cell(i, j, k) = marker == 2 ? Cell3::SOLID : (marker == 1 ? Cell3::FLUID : Cell3::AIR);
        if (marker != 0) sparse.setCell(i, j, k, marker);
      }
    }
  }

  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i <= 6; ++i) {
        double u = 0.7 * i + 0.1 * j - 0.2 * k;
        dense.u(i, j, k) = u;
        sparse.u(i, j, k) = (float)u;
      }
      for (int i = 2; i < 6; ++i) {
        double v = -0.3 * i + 0.5 * j + 0.15 * k;
        dense.v(i, j, k) = v;
        sparse.v(i, j, k) = (float)v;
      }
    }
  }
  for (int k = 2; k <= 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) {
        double w = 0.2 * i - 0.4 * j + 0.6 * k;
        dense.w(i, j, k) = w;
        sparse.w(i, j, k) = (float)w;
      }
    }
  }

  auto d0 = divergence(dense);
  solvePressure(dense, d0, 1.0, 1.0, 1000, 1e-10);
  project(dense, 1.0, 1.0);
  spProjectStep3D(sparse, 1.0, 1000, 1e-10);

  CHECK(sparse.pf.activeBlockCount() == 8);

  double maxDenseDiv = 0.0;
  double maxSparseDiv = 0.0;
  double maxPressureDiff = 0.0;
  for (int k = 2; k < 6; ++k) {
    for (int j = 2; j < 6; ++j) {
      for (int i = 2; i < 6; ++i) {
        maxDenseDiv = std::max(maxDenseDiv, std::abs(
          dense.u(i + 1, j, k) - dense.u(i, j, k) +
          dense.v(i, j + 1, k) - dense.v(i, j, k) +
          dense.w(i, j, k + 1) - dense.w(i, j, k)));
        maxSparseDiv = std::max(maxSparseDiv, std::abs(
          (double)sparse.gu(i + 1, j, k) - sparse.gu(i, j, k) +
          (double)sparse.gv(i, j + 1, k) - sparse.gv(i, j, k) +
          (double)sparse.gw(i, j, k + 1) - sparse.gw(i, j, k)));
        maxPressureDiff = std::max(maxPressureDiff, std::abs(dense.p(i, j, k) - sparse.gp(i, j, k)));
      }
    }
  }

  CHECK(maxDenseDiv < 1e-5);
  CHECK(maxSparseDiv < 1e-5);
  CHECK(maxPressureDiff < 1e-4);
}
