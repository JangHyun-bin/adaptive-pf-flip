#include "pressure/multires_pressure3d.h"

#include "grid/multires_mac_grid3d.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <stdexcept>
#include <utility>
#include <vector>

namespace {

struct PressureCellInfo3D {
  int index = -1;
  double x0 = 0.0;
  double y0 = 0.0;
  double z0 = 0.0;
  double x1 = 0.0;
  double y1 = 0.0;
  double z1 = 0.0;
  double h = 0.0;
};

bool nearlyEqual(double a, double b) {
  double scale = std::max(1.0, std::max(std::abs(a), std::abs(b)));
  return std::abs(a - b) <= 1e-12 * scale;
}

double clippedOverlap(double a0, double a1, double b0, double b1, double domain1) {
  double lo = std::max(std::max(a0, b0), 0.0);
  double hi = std::min(std::min(a1, b1), domain1);
  return std::max(0.0, hi - lo);
}

double edgeConductance(const PressureCellInfo3D& a,
                       const PressureCellInfo3D& b,
                       double domainWidth,
                       double domainHeight,
                       double domainDepth) {
  double faceArea = 0.0;

  if (nearlyEqual(a.x1, b.x0) || nearlyEqual(b.x1, a.x0)) {
    double faceX = nearlyEqual(a.x1, b.x0) ? a.x1 : b.x1;
    if (faceX >= 0.0 && faceX <= domainWidth) {
      double oy = clippedOverlap(a.y0, a.y1, b.y0, b.y1, domainHeight);
      double oz = clippedOverlap(a.z0, a.z1, b.z0, b.z1, domainDepth);
      faceArea = oy * oz;
    }
  } else if (nearlyEqual(a.y1, b.y0) || nearlyEqual(b.y1, a.y0)) {
    double faceY = nearlyEqual(a.y1, b.y0) ? a.y1 : b.y1;
    if (faceY >= 0.0 && faceY <= domainHeight) {
      double ox = clippedOverlap(a.x0, a.x1, b.x0, b.x1, domainWidth);
      double oz = clippedOverlap(a.z0, a.z1, b.z0, b.z1, domainDepth);
      faceArea = ox * oz;
    }
  } else if (nearlyEqual(a.z1, b.z0) || nearlyEqual(b.z1, a.z0)) {
    double faceZ = nearlyEqual(a.z1, b.z0) ? a.z1 : b.z1;
    if (faceZ >= 0.0 && faceZ <= domainDepth) {
      double ox = clippedOverlap(a.x0, a.x1, b.x0, b.x1, domainWidth);
      double oy = clippedOverlap(a.y0, a.y1, b.y0, b.y1, domainHeight);
      faceArea = ox * oy;
    }
  }

  if (faceArea <= 0.0) return 0.0;

  double centerDistance = 0.5 * a.h + 0.5 * b.h;
  return centerDistance > 0.0 ? faceArea / centerDistance : 0.0;
}

PressureCellInfo3D pressureCellInfo(const MRCellKey3D& c, int index, double dx) {
  constexpr int B = 4;
  int step = 1 << c.block.level;
  double h = dx * static_cast<double>(step);
  double x0 = static_cast<double>(c.block.bx * B * step + c.lx * step) * dx;
  double y0 = static_cast<double>(c.block.by * B * step + c.ly * step) * dx;
  double z0 = static_cast<double>(c.block.bz * B * step + c.lz * step) * dx;
  return PressureCellInfo3D{index, x0, y0, z0, x0 + h, y0 + h, z0 + h, h};
}

} // namespace

void MRPressureSystem3D::apply(const std::vector<double>& x, std::vector<double>& out) const {
  if (x.size() != volumes.size()) {
    throw std::invalid_argument("MRPressureSystem3D::apply input size must match volume count");
  }

  out.assign(volumes.size(), 0.0);

  for (const MREdge3D& e : edges) {
    double flux = e.conductance * (x[e.b] - x[e.a]);
    out[e.a] -= flux / volumes[e.a];
    out[e.b] += flux / volumes[e.b];
  }
}

MRPressureSystem3D buildMRPressureSystem3D(const MRMacGrid3D<4>& g, double dt) {
  (void)dt;

  MRPressureSystem3D sys;
  const auto& layout = g.p.layout;
  std::vector<PressureCellInfo3D> cells;
  std::vector<MRCellKey3D> leafCells = g.p.leafCells();
  cells.reserve(leafCells.size());
  sys.volumes.reserve(leafCells.size());

  for (const MRCellKey3D& c : leafCells) {
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h * h);
    cells.push_back(pressureCellInfo(c, static_cast<int>(cells.size()), layout.dx));
  }

  std::map<std::pair<int, int>, double> conductanceByPair;
  double domainWidth = static_cast<double>(layout.nx) * layout.dx;
  double domainHeight = static_cast<double>(layout.ny) * layout.dx;
  double domainDepth = static_cast<double>(layout.nz) * layout.dx;
  for (size_t i = 0; i < cells.size(); ++i) {
    for (size_t j = i + 1; j < cells.size(); ++j) {
      double conductance = edgeConductance(cells[i], cells[j], domainWidth, domainHeight, domainDepth);
      if (conductance > 0.0) {
        conductanceByPair[{cells[i].index, cells[j].index}] += conductance;
      }
    }
  }

  sys.edges.reserve(conductanceByPair.size());
  for (const auto& entry : conductanceByPair) {
    if (entry.second > 0.0) {
      sys.edges.push_back(MREdge3D{entry.first.first, entry.first.second, entry.second});
    }
  }
  return sys;
}

double maxMRDivergence3D(const MRMacGrid3D<4>& g) {
  double mn = 0.0;
  double mx = 0.0;
  bool first = true;

  for (const MRFaceKey3D& f : g.uFaces()) {
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
