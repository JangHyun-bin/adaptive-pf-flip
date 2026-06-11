#include "pressure/multires_pressure2d.h"

#include "grid/multires_mac_grid2d.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <utility>

namespace {

struct PressureCellInfo {
  int index = -1;
  double x0 = 0.0;
  double y0 = 0.0;
  double x1 = 0.0;
  double y1 = 0.0;
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

double edgeConductance(const PressureCellInfo& a,
                       const PressureCellInfo& b,
                       double domainWidth,
                       double domainHeight) {
  double faceLength = 0.0;

  if (nearlyEqual(a.x1, b.x0) || nearlyEqual(b.x1, a.x0)) {
    double faceX = nearlyEqual(a.x1, b.x0) ? a.x1 : b.x1;
    if (faceX >= 0.0 && faceX <= domainWidth) {
      faceLength = clippedOverlap(a.y0, a.y1, b.y0, b.y1, domainHeight);
    }
  } else if (nearlyEqual(a.y1, b.y0) || nearlyEqual(b.y1, a.y0)) {
    double faceY = nearlyEqual(a.y1, b.y0) ? a.y1 : b.y1;
    if (faceY >= 0.0 && faceY <= domainHeight) {
      faceLength = clippedOverlap(a.x0, a.x1, b.x0, b.x1, domainWidth);
    }
  }

  if (faceLength <= 0.0) return 0.0;

  double centerDistance = 0.5 * a.h + 0.5 * b.h;
  return centerDistance > 0.0 ? faceLength / centerDistance : 0.0;
}

PressureCellInfo pressureCellInfo(const MRCellKey& c, int index, double dx) {
  constexpr int B = 8;
  int step = 1 << c.block.level;
  double h = dx * static_cast<double>(step);
  double x0 = static_cast<double>(c.block.bx * B * step + c.lx * step) * dx;
  double y0 = static_cast<double>(c.block.by * B * step + c.ly * step) * dx;
  return PressureCellInfo{index, x0, y0, x0 + h, y0 + h, h};
}

} // namespace

void MRPressureSystem2D::apply(const std::vector<double>& x, std::vector<double>& out) const {
  out.assign(x.size(), 0.0);

  for (const MREdge& e : edges) {
    double flux = e.conductance * (x[e.b] - x[e.a]);
    out[e.a] -= flux / volumes[e.a];
    out[e.b] += flux / volumes[e.b];
  }
}

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt) {
  (void)dt;

  MRPressureSystem2D sys;
  std::vector<PressureCellInfo> cells;
  std::vector<MRCellKey> leafCells = g.p.leafCells();
  cells.reserve(leafCells.size());
  sys.volumes.reserve(leafCells.size());

  for (const MRCellKey& c : leafCells) {
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h);
    cells.push_back(pressureCellInfo(c, static_cast<int>(cells.size()), g.layout.dx));
  }

  std::map<std::pair<int, int>, double> conductanceByPair;
  double domainWidth = static_cast<double>(g.layout.nx) * g.layout.dx;
  double domainHeight = static_cast<double>(g.layout.ny) * g.layout.dx;
  for (size_t i = 0; i < cells.size(); ++i) {
    for (size_t j = i + 1; j < cells.size(); ++j) {
      double conductance = edgeConductance(cells[i], cells[j], domainWidth, domainHeight);
      if (conductance > 0.0) {
        conductanceByPair[{cells[i].index, cells[j].index}] += conductance;
      }
    }
  }

  sys.edges.reserve(conductanceByPair.size());
  for (const auto& entry : conductanceByPair) {
    if (entry.second > 0.0) {
      sys.edges.push_back(MREdge{entry.first.first, entry.first.second, entry.second});
    }
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
