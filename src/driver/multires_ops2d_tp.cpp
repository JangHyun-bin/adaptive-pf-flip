#include "driver/multires_ops2d_tp.h"

#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
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

double faceCenterX(const MRFaceKey& f) {
  return f.axis == 0 ? static_cast<double>(f.fineX)
                     : static_cast<double>(f.fineX) + 0.5 * f.fineLength;
}

double faceCenterY(const MRFaceKey& f) {
  return f.axis == 0 ? static_cast<double>(f.fineY) + 0.5 * f.fineLength
                     : static_cast<double>(f.fineY);
}

double sampleU(const MRMacGrid2D<8>& g) {
  std::vector<MRFaceKey> faces = g.uFaces();
  double sum = 0.0;
  for (const MRFaceKey& f : faces) {
    sum += g.gu(f);
  }
  return faces.empty() ? 0.0 : sum / static_cast<double>(faces.size());
}

double sampleV(const MRMacGrid2D<8>& g) {
  std::vector<MRFaceKey> faces = g.vFaces();
  double sum = 0.0;
  for (const MRFaceKey& f : faces) {
    sum += g.gv(f);
  }
  return faces.empty() ? 0.0 : sum / static_cast<double>(faces.size());
}

} // namespace

void mrP2G_tp(MRMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp) {
  g.ufield.clear();
  g.vfield.clear();
  g.mu.clear();
  g.mv.clear();

  std::vector<MRFaceKey> ufaces = g.uFaces();
  std::vector<MRFaceKey> vfaces = g.vFaces();

  for (size_t k = 0; k < ps.size(); ++k) {
    double rho = ps.type[k] == 0 ? pp.rho_l : pp.rho_g;
    double mp = rho * Vp;
    double px = ps.pos[k].x / g.layout.dx;
    double py = ps.pos[k].y / g.layout.dx;

    double wsum = 0.0;
    for (const MRFaceKey& f : ufaces) {
      double dx = px - faceCenterX(f);
      double dy = py - faceCenterY(f);
      wsum += kernel(dx * dx + dy * dy, KR);
    }
    if (wsum > 0.0) {
      for (const MRFaceKey& f : ufaces) {
        double dx = px - faceCenterX(f);
        double dy = py - faceCenterY(f);
        double w = kernel(dx * dx + dy * dy, KR) / wsum;
        if (w <= 0.0) continue;
        g.u(f) += static_cast<float>(w * mp * ps.vel[k].x);
        g.mU(f) += static_cast<float>(w * mp);
      }
    }

    wsum = 0.0;
    for (const MRFaceKey& f : vfaces) {
      double dx = px - faceCenterX(f);
      double dy = py - faceCenterY(f);
      wsum += kernel(dx * dx + dy * dy, KR);
    }
    if (wsum > 0.0) {
      for (const MRFaceKey& f : vfaces) {
        double dx = px - faceCenterX(f);
        double dy = py - faceCenterY(f);
        double w = kernel(dx * dx + dy * dy, KR) / wsum;
        if (w <= 0.0) continue;
        g.v(f) += static_cast<float>(w * mp * ps.vel[k].y);
        g.mV(f) += static_cast<float>(w * mp);
      }
    }
  }

  for (const MRFaceKey& f : ufaces) {
    float m = g.gmu(f);
    if (m > 0.0f) {
      g.u(f) = g.gu(f) / m;
    }
  }
  for (const MRFaceKey& f : vfaces) {
    float m = g.gmv(f);
    if (m > 0.0f) {
      g.v(f) = g.gv(f) / m;
    }
  }
}

void mrG2P_tp(const MRMacGrid2D<8>& g, Particles2DTP& ps, const MRMacGrid2D<8>& saved,
              double aL, double aG) {
  double un = sampleU(g);
  double vn = sampleV(g);
  double du = un - sampleU(saved);
  double dv = vn - sampleV(saved);

  for (size_t k = 0; k < ps.size(); ++k) {
    double a = ps.type[k] == 0 ? aL : aG;
    double flipX = ps.vel[k].x + du;
    double flipY = ps.vel[k].y + dv;
    ps.vel[k].x = a * flipX + (1.0 - a) * un;
    ps.vel[k].y = a * flipY + (1.0 - a) * vn;
  }
}

void mrAdvect_tp(Particles2DTP& ps, const MRMacGrid2D<8>& g, double dt) {
  double u = sampleU(g);
  double v = sampleV(g);
  double minX = 0.5 * g.layout.dx;
  double maxX = (static_cast<double>(g.layout.nx) - 0.5) * g.layout.dx;
  double minY = 0.5 * g.layout.dx;
  double maxY = (static_cast<double>(g.layout.ny) - 0.5) * g.layout.dx;

  for (size_t k = 0; k < ps.size(); ++k) {
    ps.pos[k].x = std::max(minX, std::min(maxX, ps.pos[k].x + dt * u));
    ps.pos[k].y = std::max(minY, std::min(maxY, ps.pos[k].y + dt * v));
  }
}
