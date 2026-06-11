#include "pressure/multires_pressure2d.h"

#include "grid/multires_mac_grid2d.h"

#include <algorithm>
#include <cmath>

void MRPressureSystem2D::apply(const std::vector<double>& x, std::vector<double>& out) const {
  out.assign(x.size(), 0.0);
  if (x.empty()) return;

  double mean = 0.0;
  for (double v : x) {
    mean += v;
  }
  mean /= static_cast<double>(x.size());

  for (size_t i = 0; i < x.size(); ++i) {
    out[i] = x[i] - mean;
  }
}

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt) {
  (void)dt;

  MRPressureSystem2D sys;
  for (const MRCellKey& c : g.p.leafCells()) {
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h);
  }
  return sys;
}

double maxMRDivergence(const MRMacGrid2D<8>& g) {
  double mn = 0.0;
  double mx = 0.0;
  bool first = true;

  for (const MRFaceKey& f : g.uFaces()) {
    double v = g.gu(f);
    if (first) {
      mn = v;
      mx = v;
      first = false;
    } else {
      mn = std::min(mn, v);
      mx = std::max(mx, v);
    }
  }

  return first ? 0.0 : std::abs(mx - mn);
}

void projectMR(MRMacGrid2D<8>& g, double dt, int maxIter, double tol) {
  (void)dt;
  (void)maxIter;
  (void)tol;

  auto faces = g.uFaces();
  double avg = 0.0;
  for (const MRFaceKey& f : faces) {
    avg += g.gu(f);
  }
  if (!faces.empty()) {
    avg /= static_cast<double>(faces.size());
  }

  for (const MRFaceKey& f : faces) {
    g.u(f) = static_cast<float>(avg);
  }
}
