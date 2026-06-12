#include "driver/sparse_ops3d.h"
#include "grid/sparse_mac_grid3d.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <vector>

namespace {

int cidx(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return i + g.nx * (j + g.ny * k);
}

std::vector<int> collectCellsWithMarker(const SparseMacGrid3D<4>& g, int marker) {
  std::vector<int> cells;
  for (int b : g.mkf.activeBlockIds()) {
    int bx, by, bz;
    g.mkf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          int i = bx * 4 + lx;
          int j = by * 4 + ly;
          int k = bz * 4 + lz;
          if (g.inBounds(i, j, k) && g.cell(i, j, k) == marker) {
            cells.push_back(cidx(g, i, j, k));
          }
        }
      }
    }
  }
  std::sort(cells.begin(), cells.end());
  return cells;
}

int findSortedIndex(const std::vector<int>& sorted, int value) {
  auto it = std::lower_bound(sorted.begin(), sorted.end(), value);
  return (it != sorted.end() && *it == value) ? (int)(it - sorted.begin()) : -1;
}

std::vector<int> collectProjectUFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int t = c / g.nx;
    int j = t % g.ny;
    int k = t / g.ny;
    if (i > 0) faces.push_back(i + (g.nx + 1) * (j + g.ny * k));
    if (i + 1 < g.nx) faces.push_back((i + 1) + (g.nx + 1) * (j + g.ny * k));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

std::vector<int> collectProjectVFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int t = c / g.nx;
    int j = t % g.ny;
    int k = t / g.ny;
    if (j > 0) faces.push_back(i + g.nx * (j + (g.ny + 1) * k));
    if (j + 1 < g.ny) faces.push_back(i + g.nx * ((j + 1) + (g.ny + 1) * k));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

std::vector<int> collectProjectWFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int t = c / g.nx;
    int j = t % g.ny;
    int k = t / g.ny;
    if (k > 0) faces.push_back(i + g.nx * (j + g.ny * k));
    if (k + 1 < g.nz) faces.push_back(i + g.nx * (j + g.ny * (k + 1)));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

bool isFluid(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return g.inBounds(i, j, k) && g.cell(i, j, k) == 1;
}

bool isSolid(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return !g.inBounds(i, j, k) || g.cell(i, j, k) == 2;
}

} // namespace

void spProjectStep3D(SparseMacGrid3D<4>& g, double dt, int cg_iters, double cg_tol) {
  g.pf.clear();
  auto cells = collectCellsWithMarker(g, 1);
  int N = (int)cells.size();
  if (N == 0) return;

  const int di[6] = {1, -1, 0, 0, 0, 0};
  const int dj[6] = {0, 0, 1, -1, 0, 0};
  const int dk[6] = {0, 0, 0, 0, 1, -1};
  double scale = dt / (g.dx * g.dx);

  std::vector<double> bvec(N), x(N, 0.0), r(N), z(N), pd(N), Ap(N);
  for (int t = 0; t < N; ++t) {
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    double d = (g.gu(i + 1, j, k) - g.gu(i, j, k) +
                g.gv(i, j + 1, k) - g.gv(i, j, k) +
                g.gw(i, j, k + 1) - g.gw(i, j, k)) / g.dx;
    bvec[t] = -d;
    r[t] = bvec[t];
  }

  std::vector<double> diag(N, 0.0);
  std::vector<std::array<int, 6>> nbr(N);
  for (int t = 0; t < N; ++t) {
    nbr[t].fill(-1);
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    for (int n = 0; n < 6; ++n) {
      int ni = i + di[n], nj = j + dj[n], nk = k + dk[n];
      if (isSolid(g, ni, nj, nk)) continue;
      diag[t] += 1.0;
      if (isFluid(g, ni, nj, nk)) {
        nbr[t][n] = findSortedIndex(cells, cidx(g, ni, nj, nk));
      }
    }
  }

  auto applyA = [&](const std::vector<double>& xx, std::vector<double>& out) {
    for (int t = 0; t < N; ++t) {
      double off = 0.0;
      for (int n = 0; n < 6; ++n) {
        if (nbr[t][n] >= 0) off += xx[nbr[t][n]];
      }
      out[t] = scale * (diag[t] * xx[t] - off);
    }
  };
  auto precond = [&](const std::vector<double>& in, std::vector<double>& out) {
    for (int t = 0; t < N; ++t) {
      double d = scale * diag[t];
      out[t] = (d > 0.0) ? in[t] / d : 0.0;
    }
  };
  auto dotp = [&](const std::vector<double>& a, const std::vector<double>& b) {
    double s = 0.0;
    for (int t = 0; t < N; ++t) s += a[t] * b[t];
    return s;
  };

  double res0 = 0.0;
  for (int t = 0; t < N; ++t) res0 = std::max(res0, std::abs(r[t]));
  if (res0 >= cg_tol) {
    precond(r, z);
    pd = z;
    double rz = dotp(r, z);
    for (int it = 0; it < cg_iters; ++it) {
      applyA(pd, Ap);
      double pAp = dotp(pd, Ap);
      if (std::abs(pAp) < 1e-30) break;
      double alpha = rz / pAp;
      for (int t = 0; t < N; ++t) {
        x[t] += alpha * pd[t];
        r[t] -= alpha * Ap[t];
      }
      double res = 0.0;
      for (int t = 0; t < N; ++t) res = std::max(res, std::abs(r[t]));
      if (res < cg_tol) break;
      precond(r, z);
      double rzn = dotp(r, z);
      double beta = rzn / rz;
      rz = rzn;
      for (int t = 0; t < N; ++t) pd[t] = z[t] + beta * pd[t];
    }
  }

  for (int t = 0; t < N; ++t) {
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    g.p(i, j, k) = (float)x[t];
  }

  double s = dt / g.dx;
  auto uFaces = collectProjectUFaces(g, cells);
  auto vFaces = collectProjectVFaces(g, cells);
  auto wFaces = collectProjectWFaces(g, cells);

  for (int fid : uFaces) {
    int i = fid % (g.nx + 1);
    int q = fid / (g.nx + 1);
    int j = q % g.ny;
    int k = q / g.ny;
    bool lf = isFluid(g, i - 1, j, k), rf = isFluid(g, i, j, k);
    if (!lf && !rf) continue;
    if (isSolid(g, i - 1, j, k) || isSolid(g, i, j, k)) {
      g.u(i, j, k) = 0.0f;
      continue;
    }
    double pl = lf ? g.gp(i - 1, j, k) : 0.0;
    double pr = rf ? g.gp(i, j, k) : 0.0;
    g.u(i, j, k) = g.gu(i, j, k) - (float)(s * (pr - pl));
  }

  for (int fid : vFaces) {
    int i = fid % g.nx;
    int q = fid / g.nx;
    int j = q % (g.ny + 1);
    int k = q / (g.ny + 1);
    bool bf = isFluid(g, i, j - 1, k), tf = isFluid(g, i, j, k);
    if (!bf && !tf) continue;
    if (isSolid(g, i, j - 1, k) || isSolid(g, i, j, k)) {
      g.v(i, j, k) = 0.0f;
      continue;
    }
    double pb = bf ? g.gp(i, j - 1, k) : 0.0;
    double pt = tf ? g.gp(i, j, k) : 0.0;
    g.v(i, j, k) = g.gv(i, j, k) - (float)(s * (pt - pb));
  }

  for (int fid : wFaces) {
    int i = fid % g.nx;
    int q = fid / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    bool df = isFluid(g, i, j, k - 1), uf = isFluid(g, i, j, k);
    if (!df && !uf) continue;
    if (isSolid(g, i, j, k - 1) || isSolid(g, i, j, k)) {
      g.w(i, j, k) = 0.0f;
      continue;
    }
    double pdn = df ? g.gp(i, j, k - 1) : 0.0;
    double pup = uf ? g.gp(i, j, k) : 0.0;
    g.w(i, j, k) = g.gw(i, j, k) - (float)(s * (pup - pdn));
  }
}
