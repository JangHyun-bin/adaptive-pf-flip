#include "driver/multires_ops3d_tp.h"

#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <vector>

namespace {

constexpr double KR = 1.5;

double kernel(double d2, double r) {
  double q = d2 / (r * r);
  double t = 1.0 - q;
  return t > 0.0 ? t * t * t : 0.0;
}

double faceCenterX(const MRFaceKey3D& f) {
  if (f.axis == 0) return static_cast<double>(f.fineX);
  return static_cast<double>(f.fineX) + 0.5 * f.fineLengthA;
}

double faceCenterY(const MRFaceKey3D& f) {
  if (f.axis == 1) return static_cast<double>(f.fineY);
  return static_cast<double>(f.fineY) + 0.5 * (f.axis == 0 ? f.fineLengthA : f.fineLengthB);
}

double faceCenterZ(const MRFaceKey3D& f) {
  if (f.axis == 2) return static_cast<double>(f.fineZ);
  return static_cast<double>(f.fineZ) + 0.5 * f.fineLengthB;
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

  std::vector<MRFaceKey3D> ufaces = g.uFaces();
  std::vector<MRFaceKey3D> vfaces = g.vFaces();
  std::vector<MRFaceKey3D> wfaces = g.wFaces();

  for (size_t p = 0; p < ps.size(); ++p) {
    double rho = ps.type[p] == 0 ? pp.rho_l : pp.rho_g;
    double mp = rho * Vp;
    double px = ps.pos[p].x / g.layout.dx;
    double py = ps.pos[p].y / g.layout.dx;
    double pz = ps.pos[p].z / g.layout.dx;

    double wsum = 0.0;
    for (const MRFaceKey3D& f : ufaces) {
      double dx = px - faceCenterX(f);
      double dy = py - faceCenterY(f);
      double dz = pz - faceCenterZ(f);
      wsum += kernel(dx * dx + dy * dy + dz * dz, KR);
    }
    if (wsum > 0.0) {
      for (const MRFaceKey3D& f : ufaces) {
        double dx = px - faceCenterX(f);
        double dy = py - faceCenterY(f);
        double dz = pz - faceCenterZ(f);
        double w = kernel(dx * dx + dy * dy + dz * dz, KR) / wsum;
        if (w <= 0.0) continue;
        g.u(f) += static_cast<float>(w * mp * ps.vel[p].x);
        g.mU(f) += static_cast<float>(w * mp);
      }
    }

    wsum = 0.0;
    for (const MRFaceKey3D& f : vfaces) {
      double dx = px - faceCenterX(f);
      double dy = py - faceCenterY(f);
      double dz = pz - faceCenterZ(f);
      wsum += kernel(dx * dx + dy * dy + dz * dz, KR);
    }
    if (wsum > 0.0) {
      for (const MRFaceKey3D& f : vfaces) {
        double dx = px - faceCenterX(f);
        double dy = py - faceCenterY(f);
        double dz = pz - faceCenterZ(f);
        double w = kernel(dx * dx + dy * dy + dz * dz, KR) / wsum;
        if (w <= 0.0) continue;
        g.v(f) += static_cast<float>(w * mp * ps.vel[p].y);
        g.mV(f) += static_cast<float>(w * mp);
      }
    }

    wsum = 0.0;
    for (const MRFaceKey3D& f : wfaces) {
      double dx = px - faceCenterX(f);
      double dy = py - faceCenterY(f);
      double dz = pz - faceCenterZ(f);
      wsum += kernel(dx * dx + dy * dy + dz * dz, KR);
    }
    if (wsum > 0.0) {
      for (const MRFaceKey3D& f : wfaces) {
        double dx = px - faceCenterX(f);
        double dy = py - faceCenterY(f);
        double dz = pz - faceCenterZ(f);
        double w = kernel(dx * dx + dy * dy + dz * dz, KR) / wsum;
        if (w <= 0.0) continue;
        g.w(f) += static_cast<float>(w * mp * ps.vel[p].z);
        g.mW(f) += static_cast<float>(w * mp);
      }
    }
  }

  for (const MRFaceKey3D& f : ufaces) {
    float m = g.gmu(f);
    if (m > 0.0f) g.u(f) = g.gu(f) / m;
  }
  for (const MRFaceKey3D& f : vfaces) {
    float m = g.gmv(f);
    if (m > 0.0f) g.v(f) = g.gv(f) / m;
  }
  for (const MRFaceKey3D& f : wfaces) {
    float m = g.gmw(f);
    if (m > 0.0f) g.w(f) = g.gw(f) / m;
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

void mrAdvect3D_tp(Particles3DTP& ps, const MRMacGrid3D<4>& g, double dt) {
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
    ps.pos[p].x = std::max(minX, std::min(maxX, ps.pos[p].x + dt * u2));
    ps.pos[p].y = std::max(minY, std::min(maxY, ps.pos[p].y + dt * v2));
    ps.pos[p].z = std::max(minZ, std::min(maxZ, ps.pos[p].z + dt * w2));
  }
}
