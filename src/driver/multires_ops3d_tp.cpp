#include "driver/multires_ops3d_tp.h"

#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <vector>

namespace {

constexpr double KR = 1.5;

struct WeightedFace {
  MRFaceKey3D face;
  double weight = 0.0;
};

double kernel(double d2, double r) {
  double q = d2 / (r * r);
  double t = 1.0 - q;
  return t > 0.0 ? t * t * t : 0.0;
}

double trilerp(double fx, double fy, double fz, const double v[2][2][2]) {
  double s = 0.0;
  for (int dz = 0; dz < 2; ++dz) {
    double wz = dz == 0 ? 1.0 - fz : fz;
    for (int dy = 0; dy < 2; ++dy) {
      double wy = dy == 0 ? 1.0 - fy : fy;
      for (int dx = 0; dx < 2; ++dx) {
        double wx = dx == 0 ? 1.0 - fx : fx;
        s += wx * wy * wz * v[dx][dy][dz];
      }
    }
  }
  return s;
}

int loRange(double c, double r, int lo, int hi) {
  return std::max(lo, std::min(hi, static_cast<int>(std::floor(c - r))));
}

int hiRange(double c, double r, int lo, int hi) {
  return std::max(lo, std::min(hi, static_cast<int>(std::ceil(c + r))));
}

void pushWeightedFace(const std::vector<MRFaceKey3D>& validFaces,
                      const MRFaceKey3D& face,
                      double dx,
                      double dy,
                      double dz,
                      std::vector<WeightedFace>& out,
                      double& sum) {
  double w = kernel(dx * dx + dy * dy + dz * dz, KR);
  if (w <= 0.0) return;
  if (!std::binary_search(validFaces.begin(), validFaces.end(), face)) return;
  out.push_back(WeightedFace{face, w});
  sum += w;
}

double collectWeightedFaces(const MRMacGrid3D<4>& g,
                            const std::vector<MRFaceKey3D>& validFaces,
                            int axis,
                            double px,
                            double py,
                            double pz,
                            std::vector<WeightedFace>& out) {
  out.clear();
  double sum = 0.0;

  if (axis == 0) {
    int ix0 = loRange(px, KR, 0, g.layout.nx);
    int ix1 = hiRange(px, KR, 0, g.layout.nx);
    int iy0 = loRange(py - 0.5, KR, 0, g.layout.ny - 1);
    int iy1 = hiRange(py - 0.5, KR, 0, g.layout.ny - 1);
    int iz0 = loRange(pz - 0.5, KR, 0, g.layout.nz - 1);
    int iz1 = hiRange(pz - 0.5, KR, 0, g.layout.nz - 1);
    for (int k = iz0; k <= iz1; ++k) {
      for (int j = iy0; j <= iy1; ++j) {
        for (int i = ix0; i <= ix1; ++i) {
          pushWeightedFace(validFaces, MRFaceKey3D{0, i, j, k, 1, 1},
                           px - static_cast<double>(i),
                           py - (static_cast<double>(j) + 0.5),
                           pz - (static_cast<double>(k) + 0.5),
                           out, sum);
        }
      }
    }
  } else if (axis == 1) {
    int ix0 = loRange(px - 0.5, KR, 0, g.layout.nx - 1);
    int ix1 = hiRange(px - 0.5, KR, 0, g.layout.nx - 1);
    int iy0 = loRange(py, KR, 0, g.layout.ny);
    int iy1 = hiRange(py, KR, 0, g.layout.ny);
    int iz0 = loRange(pz - 0.5, KR, 0, g.layout.nz - 1);
    int iz1 = hiRange(pz - 0.5, KR, 0, g.layout.nz - 1);
    for (int k = iz0; k <= iz1; ++k) {
      for (int j = iy0; j <= iy1; ++j) {
        for (int i = ix0; i <= ix1; ++i) {
          pushWeightedFace(validFaces, MRFaceKey3D{1, i, j, k, 1, 1},
                           px - (static_cast<double>(i) + 0.5),
                           py - static_cast<double>(j),
                           pz - (static_cast<double>(k) + 0.5),
                           out, sum);
        }
      }
    }
  } else {
    int ix0 = loRange(px - 0.5, KR, 0, g.layout.nx - 1);
    int ix1 = hiRange(px - 0.5, KR, 0, g.layout.nx - 1);
    int iy0 = loRange(py - 0.5, KR, 0, g.layout.ny - 1);
    int iy1 = hiRange(py - 0.5, KR, 0, g.layout.ny - 1);
    int iz0 = loRange(pz, KR, 0, g.layout.nz);
    int iz1 = hiRange(pz, KR, 0, g.layout.nz);
    for (int k = iz0; k <= iz1; ++k) {
      for (int j = iy0; j <= iy1; ++j) {
        for (int i = ix0; i <= ix1; ++i) {
          pushWeightedFace(validFaces, MRFaceKey3D{2, i, j, k, 1, 1},
                           px - (static_cast<double>(i) + 0.5),
                           py - (static_cast<double>(j) + 0.5),
                           pz - static_cast<double>(k),
                           out, sum);
        }
      }
    }
  }

  return sum;
}

double sampleU(const MRMacGrid3D<4>& g, double x, double y, double z) {
  double px = x / g.layout.dx;
  double py = y / g.layout.dx;
  double pz = z / g.layout.dx;
  int i0 = static_cast<int>(std::floor(px));
  int j0 = static_cast<int>(std::floor(py - 0.5));
  int k0 = static_cast<int>(std::floor(pz - 0.5));
  double fx = px - i0;
  double fy = (py - 0.5) - j0;
  double fz = (pz - 0.5) - k0;

  double v[2][2][2] = {};
  for (int dz = 0; dz < 2; ++dz) {
    for (int dy = 0; dy < 2; ++dy) {
      for (int dx = 0; dx < 2; ++dx) {
        int i = std::max(0, std::min(g.layout.nx, i0 + dx));
        int j = std::max(0, std::min(g.layout.ny - 1, j0 + dy));
        int k = std::max(0, std::min(g.layout.nz - 1, k0 + dz));
        v[dx][dy][dz] = static_cast<double>(g.gu(MRFaceKey3D{0, i, j, k, 1, 1}));
      }
    }
  }
  return trilerp(fx, fy, fz, v);
}

double sampleV(const MRMacGrid3D<4>& g, double x, double y, double z) {
  double px = x / g.layout.dx;
  double py = y / g.layout.dx;
  double pz = z / g.layout.dx;
  int i0 = static_cast<int>(std::floor(px - 0.5));
  int j0 = static_cast<int>(std::floor(py));
  int k0 = static_cast<int>(std::floor(pz - 0.5));
  double fx = (px - 0.5) - i0;
  double fy = py - j0;
  double fz = (pz - 0.5) - k0;

  double v[2][2][2] = {};
  for (int dz = 0; dz < 2; ++dz) {
    for (int dy = 0; dy < 2; ++dy) {
      for (int dx = 0; dx < 2; ++dx) {
        int i = std::max(0, std::min(g.layout.nx - 1, i0 + dx));
        int j = std::max(0, std::min(g.layout.ny, j0 + dy));
        int k = std::max(0, std::min(g.layout.nz - 1, k0 + dz));
        v[dx][dy][dz] = static_cast<double>(g.gv(MRFaceKey3D{1, i, j, k, 1, 1}));
      }
    }
  }
  return trilerp(fx, fy, fz, v);
}

double sampleW(const MRMacGrid3D<4>& g, double x, double y, double z) {
  double px = x / g.layout.dx;
  double py = y / g.layout.dx;
  double pz = z / g.layout.dx;
  int i0 = static_cast<int>(std::floor(px - 0.5));
  int j0 = static_cast<int>(std::floor(py - 0.5));
  int k0 = static_cast<int>(std::floor(pz));
  double fx = (px - 0.5) - i0;
  double fy = (py - 0.5) - j0;
  double fz = pz - k0;

  double v[2][2][2] = {};
  for (int dz = 0; dz < 2; ++dz) {
    for (int dy = 0; dy < 2; ++dy) {
      for (int dx = 0; dx < 2; ++dx) {
        int i = std::max(0, std::min(g.layout.nx - 1, i0 + dx));
        int j = std::max(0, std::min(g.layout.ny - 1, j0 + dy));
        int k = std::max(0, std::min(g.layout.nz, k0 + dz));
        v[dx][dy][dz] = static_cast<double>(g.gw(MRFaceKey3D{2, i, j, k, 1, 1}));
      }
    }
  }
  return trilerp(fx, fy, fz, v);
}

} // namespace

void mrP2G3D_tp(MRMacGrid3D<4>& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp) {
  g.ufield.clear();
  g.vfield.clear();
  g.wfield.clear();
  g.mu.clear();
  g.mv.clear();
  g.mw.clear();

  const std::vector<MRFaceKey3D>& ufaces = g.uFaceRefs();
  const std::vector<MRFaceKey3D>& vfaces = g.vFaceRefs();
  const std::vector<MRFaceKey3D>& wfaces = g.wFaceRefs();
  std::vector<WeightedFace> weighted;

  for (size_t p = 0; p < ps.size(); ++p) {
    double rho = ps.type[p] == 0 ? pp.rho_l : pp.rho_g;
    double mp = rho * Vp * ps.volume[p];
    double px = ps.pos[p].x / g.layout.dx;
    double py = ps.pos[p].y / g.layout.dx;
    double pz = ps.pos[p].z / g.layout.dx;

    double wsum = collectWeightedFaces(g, ufaces, 0, px, py, pz, weighted);
    if (wsum > 0.0) {
      for (const WeightedFace& wf : weighted) {
        double w = wf.weight / wsum;
        if (w <= 0.0) continue;
        g.u(wf.face) += static_cast<float>(w * mp * ps.vel[p].x);
        g.mU(wf.face) += static_cast<float>(w * mp);
      }
    }

    wsum = collectWeightedFaces(g, vfaces, 1, px, py, pz, weighted);
    if (wsum > 0.0) {
      for (const WeightedFace& wf : weighted) {
        double w = wf.weight / wsum;
        if (w <= 0.0) continue;
        g.v(wf.face) += static_cast<float>(w * mp * ps.vel[p].y);
        g.mV(wf.face) += static_cast<float>(w * mp);
      }
    }

    wsum = collectWeightedFaces(g, wfaces, 2, px, py, pz, weighted);
    if (wsum > 0.0) {
      for (const WeightedFace& wf : weighted) {
        double w = wf.weight / wsum;
        if (w <= 0.0) continue;
        g.w(wf.face) += static_cast<float>(w * mp * ps.vel[p].z);
        g.mW(wf.face) += static_cast<float>(w * mp);
      }
    }
  }

  for (const auto& kv : g.mu) {
    if (kv.second <= 0.0f) continue;
    auto it = g.ufield.find(kv.first);
    if (it != g.ufield.end()) it->second /= kv.second;
  }
  for (const auto& kv : g.mv) {
    if (kv.second <= 0.0f) continue;
    auto it = g.vfield.find(kv.first);
    if (it != g.vfield.end()) it->second /= kv.second;
  }
  for (const auto& kv : g.mw) {
    if (kv.second <= 0.0f) continue;
    auto it = g.wfield.find(kv.first);
    if (it != g.wfield.end()) it->second /= kv.second;
  }
}

void mrG2P3D_tp(const MRMacGrid3D<4>& g, Particles3DTP& ps, const MRMacGrid3D<4>& saved,
                double aL, double aG) {
  for (size_t p = 0; p < ps.size(); ++p) {
    double a = ps.type[p] == 0 ? aL : aG;
    double un = sampleU(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double vn = sampleV(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double wn = sampleW(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double du = un - sampleU(saved, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double dv = vn - sampleV(saved, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double dw = wn - sampleW(saved, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double flipX = ps.vel[p].x + du;
    double flipY = ps.vel[p].y + dv;
    double flipZ = ps.vel[p].z + dw;
    ps.vel[p].x = a * flipX + (1.0 - a) * un;
    ps.vel[p].y = a * flipY + (1.0 - a) * vn;
    ps.vel[p].z = a * flipZ + (1.0 - a) * wn;
  }
}

void mrAdvect3D_tp(Particles3DTP& ps, const MRMacGrid3D<4>& g, double dt,
                   ParticleEscapeStats3D* stats) {
  double minX = 0.5 * g.layout.dx;
  double maxX = (static_cast<double>(g.layout.nx) - 0.5) * g.layout.dx;
  double minY = 0.5 * g.layout.dx;
  double maxY = (static_cast<double>(g.layout.ny) - 0.5) * g.layout.dx;
  double minZ = 0.5 * g.layout.dx;
  double maxZ = (static_cast<double>(g.layout.nz) - 0.5) * g.layout.dx;

  for (size_t p = 0; p < ps.size(); ++p) {
    double u1 = sampleU(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double v1 = sampleV(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double w1 = sampleW(g, ps.pos[p].x, ps.pos[p].y, ps.pos[p].z);
    double mx = ps.pos[p].x + 0.5 * dt * u1;
    double my = ps.pos[p].y + 0.5 * dt * v1;
    double mz = ps.pos[p].z + 0.5 * dt * w1;
    double u2 = sampleU(g, mx, my, mz);
    double v2 = sampleV(g, mx, my, mz);
    double w2 = sampleW(g, mx, my, mz);
    double nx = ps.pos[p].x + dt * u2;
    double ny = ps.pos[p].y + dt * v2;
    double nz = ps.pos[p].z + dt * w2;
    const bool xLo = nx < minX;
    const bool xHi = nx > maxX;
    const bool yLo = ny < minY;
    const bool yHi = ny > maxY;
    const bool zLo = nz < minZ;
    const bool zHi = nz > maxZ;
    if (stats) stats->recordClamp(ps.type[p], xLo, xHi, yLo, yHi, zLo, zHi);
    ps.pos[p].x = std::max(minX, std::min(maxX, nx));
    ps.pos[p].y = std::max(minY, std::min(maxY, ny));
    ps.pos[p].z = std::max(minZ, std::min(maxZ, nz));
  }
}
