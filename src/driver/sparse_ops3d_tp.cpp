#include "driver/sparse_ops3d_tp.h"
#include "driver/sparse_ops3d_common.h"
#include "grid/block_color.h"
#include "grid/sparse_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <vector>

namespace {

static inline double kern(double d2, double r) {
  double q = d2 / (r * r);
  double t = 1.0 - q;
  return (t > 0.0) ? t * t * t : 0.0;
}

constexpr double KR = 1.5;

void preactivateKernel(SparseBlockGrid3D<4>& field, double gx, double gy, double gz,
                       int nx, int ny, int nz) {
  int rad = (int)std::ceil(KR);
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  for (int dk = -rad; dk <= rad + 1; ++dk) {
    for (int dj = -rad; dj <= rad + 1; ++dj) {
      for (int di = -rad; di <= rad + 1; ++di) {
        int i = i0 + di, j = j0 + dj, k = k0 + dk;
        if (i < 0 || i >= nx || j < 0 || j >= ny || k < 0 || k >= nz) continue;
        double dx = gx - i, dy = gy - j, dz = gz - k;
        if (kern(dx * dx + dy * dy + dz * dz, KR) <= 0.0) continue;
        field.activateBlock(i / 4, j / 4, k / 4);
      }
    }
  }
}

void splatKernelColor(SparseBlockGrid3D<4>& field, SparseBlockGrid3D<4>& massField,
                      double gx, double gy, double gz, double mom, double mass,
                      int nx, int ny, int nz, int color) {
  int rad = (int)std::ceil(KR);
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  double wsum = 0.0;
  for (int dk = -rad; dk <= rad + 1; ++dk) {
    for (int dj = -rad; dj <= rad + 1; ++dj) {
      for (int di = -rad; di <= rad + 1; ++di) {
        int i = i0 + di, j = j0 + dj, k = k0 + dk;
        if (i < 0 || i >= nx || j < 0 || j >= ny || k < 0 || k >= nz) continue;
        double dx = gx - i, dy = gy - j, dz = gz - k;
        wsum += kern(dx * dx + dy * dy + dz * dz, KR);
      }
    }
  }
  if (wsum <= 0.0) return;
  for (int dk = -rad; dk <= rad + 1; ++dk) {
    for (int dj = -rad; dj <= rad + 1; ++dj) {
      for (int di = -rad; di <= rad + 1; ++di) {
        int i = i0 + di, j = j0 + dj, k = k0 + dk;
        if (i < 0 || i >= nx || j < 0 || j >= ny || k < 0 || k >= nz) continue;
        if (color8(i / 4, j / 4, k / 4) != color) continue;
        double dx = gx - i, dy = gy - j, dz = gz - k;
        double w = kern(dx * dx + dy * dy + dz * dz, KR) / wsum;
        if (w <= 0.0) continue;
        field.ref(i, j, k) += (float)(w * mom);
        massField.ref(i, j, k) += (float)(w * mass);
      }
    }
  }
}

bool isFluid(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return g.inBounds(i, j, k) && g.cell(i, j, k) == 1;
}

bool isSolid(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return !g.inBounds(i, j, k) || g.cell(i, j, k) == 2;
}

bool isAir(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return g.inBounds(i, j, k) && g.cell(i, j, k) == 0;
}

double betaOfRaw(double raw, const PhaseParams& pp) {
  return betaFromPhi(phiFromRawDensity(raw, pp), pp);
}

} // namespace

void spP2G3D_tp(SparseMacGrid3D<4>& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp) {
  g.uf.clear(); g.vf.clear(); g.wf.clear();
  g.muf.clear(); g.mvf.clear(); g.mwf.clear();
  for (size_t p = 0; p < ps.size(); ++p) {
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    preactivateKernel(g.uf, px, py - 0.5, pz - 0.5, g.nx + 1, g.ny, g.nz);
    preactivateKernel(g.muf, px, py - 0.5, pz - 0.5, g.nx + 1, g.ny, g.nz);
    preactivateKernel(g.vf, px - 0.5, py, pz - 0.5, g.nx, g.ny + 1, g.nz);
    preactivateKernel(g.mvf, px - 0.5, py, pz - 0.5, g.nx, g.ny + 1, g.nz);
    preactivateKernel(g.wf, px - 0.5, py - 0.5, pz, g.nx, g.ny, g.nz + 1);
    preactivateKernel(g.mwf, px - 0.5, py - 0.5, pz, g.nx, g.ny, g.nz + 1);
  }

  sparse3d::runColor8(ps.size(), [&](int color) {
    for (size_t p = 0; p < ps.size(); ++p) {
      double rho = (ps.type[p] == 0) ? pp.rho_l : pp.rho_g;
      double mp = rho * Vp * ps.volume[p];
      double px = (ps.pos[p].x - g.ox) / g.dx;
      double py = (ps.pos[p].y - g.oy) / g.dx;
      double pz = (ps.pos[p].z - g.oz) / g.dx;
      splatKernelColor(g.uf, g.muf, px, py - 0.5, pz - 0.5, mp * ps.vel[p].x, mp,
                       g.nx + 1, g.ny, g.nz, color);
      splatKernelColor(g.vf, g.mvf, px - 0.5, py, pz - 0.5, mp * ps.vel[p].y, mp,
                       g.nx, g.ny + 1, g.nz, color);
      splatKernelColor(g.wf, g.mwf, px - 0.5, py - 0.5, pz, mp * ps.vel[p].z, mp,
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

void spG2P3D_tp(const SparseMacGrid3D<4>& g, Particles3DTP& ps, const SparseMacGrid3D<4>& saved,
                double aL, double aG) {
  for (size_t p = 0; p < ps.size(); ++p) {
    double a = (ps.type[p] == 0) ? aL : aG;
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    double un = sparse3d::sampleU(g, px, py, pz);
    double vn = sparse3d::sampleV(g, px, py, pz);
    double wn = sparse3d::sampleW(g, px, py, pz);
    double du = un - sparse3d::sampleU(saved, px, py, pz);
    double dv = vn - sparse3d::sampleV(saved, px, py, pz);
    double dw = wn - sparse3d::sampleW(saved, px, py, pz);
    Vec3 pic{un, vn, wn};
    Vec3 flip{ps.vel[p].x + du, ps.vel[p].y + dv, ps.vel[p].z + dw};
    ps.vel[p] = flip * a + pic * (1.0 - a);
  }
}

void spAdvect3D_tp(Particles3DTP& ps, const SparseMacGrid3D<4>& g, double dt,
                   ParticleEscapeStats3D* stats) {
  double lox = g.ox + 0.5 * g.dx, hix = g.ox + (g.nx - 0.5) * g.dx;
  double loy = g.oy + 0.5 * g.dx, hiy = g.oy + (g.ny - 0.5) * g.dx;
  double loz = g.oz + 0.5 * g.dx, hiz = g.oz + (g.nz - 0.5) * g.dx;
  for (size_t p = 0; p < ps.size(); ++p) {
    double px = (ps.pos[p].x - g.ox) / g.dx;
    double py = (ps.pos[p].y - g.oy) / g.dx;
    double pz = (ps.pos[p].z - g.oz) / g.dx;
    double u1 = sparse3d::sampleU(g, px, py, pz);
    double v1 = sparse3d::sampleV(g, px, py, pz);
    double w1 = sparse3d::sampleW(g, px, py, pz);
    double mx = ps.pos[p].x + 0.5 * dt * u1;
    double my = ps.pos[p].y + 0.5 * dt * v1;
    double mz = ps.pos[p].z + 0.5 * dt * w1;
    double mpx = (mx - g.ox) / g.dx;
    double mpy = (my - g.oy) / g.dx;
    double mpz = (mz - g.oz) / g.dx;
    double u2 = sparse3d::sampleU(g, mpx, mpy, mpz);
    double v2 = sparse3d::sampleV(g, mpx, mpy, mpz);
    double w2 = sparse3d::sampleW(g, mpx, mpy, mpz);
    double nx = ps.pos[p].x + dt * u2;
    double ny = ps.pos[p].y + dt * v2;
    double nz = ps.pos[p].z + dt * w2;
    const bool xLo = nx < lox;
    const bool xHi = nx > hix;
    const bool yLo = ny < loy;
    const bool yHi = ny > hiy;
    const bool zLo = nz < loz;
    const bool zHi = nz > hiz;
    if (stats) stats->recordClamp(ps.type[p], xLo, xHi, yLo, yHi, zLo, zHi);
    ps.pos[p].x = std::max(lox, std::min(hix, nx));
    ps.pos[p].y = std::max(loy, std::min(hiy, ny));
    ps.pos[p].z = std::max(loz, std::min(hiz, nz));
  }
}

void spProjectStepVC3D(SparseMacGrid3D<4>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol) {
  g.pf.clear();
  auto cells = sparse3d::collectCellsWithMarker(g, 1);
  int N = (int)cells.size();
  if (N == 0) return;

  const int di[6] = {1, -1, 0, 0, 0, 0};
  const int dj[6] = {0, 0, 1, -1, 0, 0};
  const int dk[6] = {0, 0, 0, 0, 1, -1};
  double scale = dt / (g.dx * g.dx);

  int pc = -1;
  bool touchesAir = false;
  for (int t = 0; t < N && !touchesAir; ++t) {
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    for (int n = 0; n < 6; ++n) {
      if (isAir(g, i + di[n], j + dj[n], k + dk[n])) {
        touchesAir = true;
        break;
      }
    }
  }
  if (!touchesAir) pc = cells[0];

  std::vector<double> x(N, 0.0), r(N), z(N), pd(N), Ap(N);
  for (int t = 0; t < N; ++t) {
    if (cells[t] == pc) {
      r[t] = 0.0;
      continue;
    }
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    double uR = isSolid(g, i + 1, j, k) ? 0.0 : (double)g.gu(i + 1, j, k);
    double uL = isSolid(g, i - 1, j, k) ? 0.0 : (double)g.gu(i, j, k);
    double vT = isSolid(g, i, j + 1, k) ? 0.0 : (double)g.gv(i, j + 1, k);
    double vB = isSolid(g, i, j - 1, k) ? 0.0 : (double)g.gv(i, j, k);
    double wU = isSolid(g, i, j, k + 1) ? 0.0 : (double)g.gw(i, j, k + 1);
    double wD = isSolid(g, i, j, k - 1) ? 0.0 : (double)g.gw(i, j, k);
    r[t] = -((uR - uL) + (vT - vB) + (wU - wD)) / g.dx;
  }

  std::vector<double> diag(N, 0.0);
  std::vector<std::array<int, 6>> nbr(N);
  std::vector<std::array<double, 6>> coeff(N);
  for (int t = 0; t < N; ++t) {
    nbr[t].fill(-1);
    coeff[t].fill(0.0);
    int i = cells[t] % g.nx;
    int q = cells[t] / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    struct Face { int ni, nj, nk; double beta; };
    Face faces[6] = {
      {i + 1, j, k, betaOfRaw(g.gmu(i + 1, j, k), pp)},
      {i - 1, j, k, betaOfRaw(g.gmu(i, j, k), pp)},
      {i, j + 1, k, betaOfRaw(g.gmv(i, j + 1, k), pp)},
      {i, j - 1, k, betaOfRaw(g.gmv(i, j, k), pp)},
      {i, j, k + 1, betaOfRaw(g.gmw(i, j, k + 1), pp)},
      {i, j, k - 1, betaOfRaw(g.gmw(i, j, k), pp)}
    };
    for (int n = 0; n < 6; ++n) {
      if (isSolid(g, faces[n].ni, faces[n].nj, faces[n].nk)) continue;
      diag[t] += faces[n].beta;
      coeff[t][n] = faces[n].beta;
      int nc = sparse3d::cidx(g, faces[n].ni, faces[n].nj, faces[n].nk);
      if (isFluid(g, faces[n].ni, faces[n].nj, faces[n].nk) && nc != pc) {
        nbr[t][n] = sparse3d::findSortedIndex(cells, nc);
      }
    }
  }

  auto applyA = [&](const std::vector<double>& xx, std::vector<double>& out) {
    for (int t = 0; t < N; ++t) {
      if (cells[t] == pc) {
        out[t] = xx[t];
        continue;
      }
      double off = 0.0;
      for (int n = 0; n < 6; ++n) {
        if (nbr[t][n] >= 0) off += coeff[t][n] * xx[nbr[t][n]];
      }
      out[t] = scale * (diag[t] * xx[t] - off);
    }
  };
  auto precond = [&](const std::vector<double>& in, std::vector<double>& out) {
    for (int t = 0; t < N; ++t) {
      double d = (cells[t] == pc) ? 1.0 : scale * diag[t];
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
  auto uFaces = sparse3d::collectProjectUFaces(g, cells);
  auto vFaces = sparse3d::collectProjectVFaces(g, cells);
  auto wFaces = sparse3d::collectProjectWFaces(g, cells);
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
    double pl = lf ? (double)g.gp(i - 1, j, k) : 0.0;
    double pr = rf ? (double)g.gp(i, j, k) : 0.0;
    g.u(i, j, k) = g.gu(i, j, k) - (float)(s * betaOfRaw(g.gmu(i, j, k), pp) * (pr - pl));
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
    double pb = bf ? (double)g.gp(i, j - 1, k) : 0.0;
    double pt = tf ? (double)g.gp(i, j, k) : 0.0;
    g.v(i, j, k) = g.gv(i, j, k) - (float)(s * betaOfRaw(g.gmv(i, j, k), pp) * (pt - pb));
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
    double pdn = df ? (double)g.gp(i, j, k - 1) : 0.0;
    double pup = uf ? (double)g.gp(i, j, k) : 0.0;
    g.w(i, j, k) = g.gw(i, j, k) - (float)(s * betaOfRaw(g.gmw(i, j, k), pp) * (pup - pdn));
  }
}
