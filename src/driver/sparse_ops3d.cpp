#include "driver/sparse_ops3d.h"
#include "grid/block_color.h"
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <future>
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

template<typename Fn>
void runColor8(size_t workItems, Fn&& fn) {
  if (workItems < 2048) {
    for (int color = 0; color < 8; ++color) fn(color);
    return;
  }
  std::array<std::future<void>, 8> jobs;
  for (int color = 0; color < 8; ++color) {
    jobs[(size_t)color] = std::async(std::launch::async, [&, color]() { fn(color); });
  }
  for (auto& job : jobs) job.get();
}

void preactivateField(SparseBlockGrid3D<4>& f, double gx, double gy, double gz,
                      int nx, int ny, int nz) {
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  for (int dk = 0; dk < 2; ++dk) {
    for (int dj = 0; dj < 2; ++dj) {
      for (int di = 0; di < 2; ++di) {
        int i = i0 + di;
        int j = j0 + dj;
        int k = k0 + dk;
        if (i < 0 || i >= nx || j < 0 || j >= ny || k < 0 || k >= nz) continue;
        f.activateBlock(i / 4, j / 4, k / 4);
      }
    }
  }
}

void splatFieldColor(SparseBlockGrid3D<4>& f, SparseBlockGrid3D<4>& mfield,
                     double gx, double gy, double gz, double mom, double mass,
                     int nx, int ny, int nz, int color) {
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  double fx = gx - i0, fy = gy - j0, fz = gz - k0;
  double wx[2] = {1.0 - fx, fx};
  double wy[2] = {1.0 - fy, fy};
  double wz[2] = {1.0 - fz, fz};
  for (int dk = 0; dk < 2; ++dk) {
    for (int dj = 0; dj < 2; ++dj) {
      for (int di = 0; di < 2; ++di) {
        int i = i0 + di;
        int j = j0 + dj;
        int k = k0 + dk;
        if (i < 0 || i >= nx || j < 0 || j >= ny || k < 0 || k >= nz) continue;
        if (color8(i / 4, j / 4, k / 4) != color) continue;
        float w = (float)(wx[di] * wy[dj] * wz[dk]);
        f.ref(i, j, k) += (float)(w * mom);
        mfield.ref(i, j, k) += (float)(w * mass);
      }
    }
  }
}

float sampleField(const SparseBlockGrid3D<4>& f, int nx, int ny, int nz,
                  double gx, double gy, double gz) {
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  double fx = gx - i0, fy = gy - j0, fz = gz - k0;
  double wx[2] = {1.0 - fx, fx};
  double wy[2] = {1.0 - fy, fy};
  double wz[2] = {1.0 - fz, fz};
  double s = 0.0;
  for (int dk = 0; dk < 2; ++dk) {
    for (int dj = 0; dj < 2; ++dj) {
      for (int di = 0; di < 2; ++di) {
        int i = std::max(0, std::min(nx - 1, i0 + di));
        int j = std::max(0, std::min(ny - 1, j0 + dj));
        int k = std::max(0, std::min(nz - 1, k0 + dk));
        s += wx[di] * wy[dj] * wz[dk] * f.get(i, j, k);
      }
    }
  }
  return (float)s;
}

float sampleU(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.uf, g.nx + 1, g.ny, g.nz, px, py - 0.5, pz - 0.5);
}

float sampleV(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.vf, g.nx, g.ny + 1, g.nz, px - 0.5, py, pz - 0.5);
}

float sampleW(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.wf, g.nx, g.ny, g.nz + 1, px - 0.5, py - 0.5, pz);
}

} // namespace

void spP2G3D(SparseMacGrid3D<4>& g, const Particles3D& ps) {
  g.uf.clear(); g.vf.clear(); g.wf.clear();
  g.muf.clear(); g.mvf.clear(); g.mwf.clear();
  const double mp = 1.0;
  for (size_t p = 0; p < ps.size(); ++p) {
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    preactivateField(g.uf, px, py - 0.5, pz - 0.5, g.nx + 1, g.ny, g.nz);
    preactivateField(g.muf, px, py - 0.5, pz - 0.5, g.nx + 1, g.ny, g.nz);
    preactivateField(g.vf, px - 0.5, py, pz - 0.5, g.nx, g.ny + 1, g.nz);
    preactivateField(g.mvf, px - 0.5, py, pz - 0.5, g.nx, g.ny + 1, g.nz);
    preactivateField(g.wf, px - 0.5, py - 0.5, pz, g.nx, g.ny, g.nz + 1);
    preactivateField(g.mwf, px - 0.5, py - 0.5, pz, g.nx, g.ny, g.nz + 1);
  }

  runColor8(ps.size(), [&](int color) {
    for (size_t p = 0; p < ps.size(); ++p) {
      double px = (ps.pos[p].x - g.ox) / g.dx;
      double py = (ps.pos[p].y - g.oy) / g.dx;
      double pz = (ps.pos[p].z - g.oz) / g.dx;
      splatFieldColor(g.uf, g.muf, px, py - 0.5, pz - 0.5, mp * ps.vel[p].x, mp,
                      g.nx + 1, g.ny, g.nz, color);
      splatFieldColor(g.vf, g.mvf, px - 0.5, py, pz - 0.5, mp * ps.vel[p].y, mp,
                      g.nx, g.ny + 1, g.nz, color);
      splatFieldColor(g.wf, g.mwf, px - 0.5, py - 0.5, pz, mp * ps.vel[p].z, mp,
                      g.nx, g.ny, g.nz + 1, color);
    }
  });

  for (int b : g.muf.activeBlockIds()) {
    int bx, by, bz; g.muf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) for (int ly = 0; ly < 4; ++ly) for (int lx = 0; lx < 4; ++lx) {
      int i = bx * 4 + lx, j = by * 4 + ly, k = bz * 4 + lz;
      if (i > g.nx || j >= g.ny || k >= g.nz) continue;
      float m = g.gmu(i, j, k);
      if (m > 0.0f) g.u(i, j, k) = g.gu(i, j, k) / m;
    }
  }
  for (int b : g.mvf.activeBlockIds()) {
    int bx, by, bz; g.mvf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) for (int ly = 0; ly < 4; ++ly) for (int lx = 0; lx < 4; ++lx) {
      int i = bx * 4 + lx, j = by * 4 + ly, k = bz * 4 + lz;
      if (i >= g.nx || j > g.ny || k >= g.nz) continue;
      float m = g.gmv(i, j, k);
      if (m > 0.0f) g.v(i, j, k) = g.gv(i, j, k) / m;
    }
  }
  for (int b : g.mwf.activeBlockIds()) {
    int bx, by, bz; g.mwf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) for (int ly = 0; ly < 4; ++ly) for (int lx = 0; lx < 4; ++lx) {
      int i = bx * 4 + lx, j = by * 4 + ly, k = bz * 4 + lz;
      if (i >= g.nx || j >= g.ny || k > g.nz) continue;
      float m = g.gmw(i, j, k);
      if (m > 0.0f) g.w(i, j, k) = g.gw(i, j, k) / m;
    }
  }
}

void spG2P3D(const SparseMacGrid3D<4>& g, Particles3D& ps, const SparseMacGrid3D<4>& saved, double alpha) {
  for (size_t p = 0; p < ps.size(); ++p) {
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    double un = sampleU(g, px, py, pz);
    double vn = sampleV(g, px, py, pz);
    double wn = sampleW(g, px, py, pz);
    double du = un - sampleU(saved, px, py, pz);
    double dv = vn - sampleV(saved, px, py, pz);
    double dw = wn - sampleW(saved, px, py, pz);
    Vec3 pic{un, vn, wn};
    Vec3 flip{ps.vel[p].x + du, ps.vel[p].y + dv, ps.vel[p].z + dw};
    ps.vel[p] = flip * alpha + pic * (1.0 - alpha);
  }
}

void spAdvect3D(Particles3D& ps, const SparseMacGrid3D<4>& g, double dt) {
  double lox = g.ox + 0.5 * g.dx, hix = g.ox + (g.nx - 0.5) * g.dx;
  double loy = g.oy + 0.5 * g.dx, hiy = g.oy + (g.ny - 0.5) * g.dx;
  double loz = g.oz + 0.5 * g.dx, hiz = g.oz + (g.nz - 0.5) * g.dx;
  for (size_t p = 0; p < ps.size(); ++p) {
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    double u1 = sampleU(g, px, py, pz);
    double v1 = sampleV(g, px, py, pz);
    double w1 = sampleW(g, px, py, pz);
    double mx = ps.pos[p].x + 0.5 * dt * u1;
    double my = ps.pos[p].y + 0.5 * dt * v1;
    double mz = ps.pos[p].z + 0.5 * dt * w1;
    double mpx = (mx - g.ox) / g.dx;
    double mpy = (my - g.oy) / g.dx;
    double mpz = (mz - g.oz) / g.dx;
    double u2 = sampleU(g, mpx, mpy, mpz);
    double v2 = sampleV(g, mpx, mpy, mpz);
    double w2 = sampleW(g, mpx, mpy, mpz);
    ps.pos[p].x = std::max(lox, std::min(hix, ps.pos[p].x + dt * u2));
    ps.pos[p].y = std::max(loy, std::min(hiy, ps.pos[p].y + dt * v2));
    ps.pos[p].z = std::max(loz, std::min(hiz, ps.pos[p].z + dt * w2));
  }
}

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
