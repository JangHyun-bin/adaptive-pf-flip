#include "pressure/multires_pressure2d.h"

#include "grid/multires_mac_grid2d.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

namespace {

struct PressureCellInfo {
  int index = -1;
  double x0 = 0.0;
  double y0 = 0.0;
  double x1 = 0.0;
  double y1 = 0.0;
  double h = 0.0;
};

struct ProjectionCell {
  MRCellKey key;
  int index = -1;
  double h = 0.0;
  double volume = 0.0;
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

std::tuple<int, int, int, int, int> cellTuple(const MRCellKey& c) {
  return std::make_tuple(c.block.level, c.block.bx, c.block.by, c.lx, c.ly);
}

bool validCell(const MRCellKey& c) {
  return c.block.level >= 0 && c.lx >= 0 && c.ly >= 0;
}

int markerAtCell(const MRMacGrid2D<8>& g, const MRCellKey& c) {
  if (!validCell(c)) return 2;
  return static_cast<int>(g.marker.get(c) + 0.5f);
}

int markerAtFineCell(const MRMacGrid2D<8>& g, int x, int y) {
  if (x < 0 || x >= g.marker.layout.nx || y < 0 || y >= g.marker.layout.ny) {
    return 2;
  }
  return markerAtCell(g, g.marker.cellAtFineCell(x, y));
}

double cellSize(const MRMacGrid2D<8>& g, const MRCellKey& c) {
  return g.p.cellSize(c.block.level);
}

double betaFromRawMass(double raw, const PhaseParams& pp) {
  double rmin = etaPhi(pp) * pp.rho_g * pp.rho_tilde_0;
  double invden = 1.0 / (pp.alpha_phi * pp.rho_tilde_0 * pp.rho_l);
  double phi = raw < rmin ? 0.0 : std::min(std::sqrt((raw - rmin) * invden), 1.0);
  return 1.0 / (phi * pp.rho_l + (1.0 - phi) * pp.rho_g);
}

template<class Fn>
void visitCellFaces(const MRMacGrid2D<8>& g, const MRCellKey& c, Fn&& fn) {
  constexpr int B = 8;
  int step = 1 << c.block.level;
  int x0 = c.block.bx * B * step + c.lx * step;
  int y0 = c.block.by * B * step + c.ly * step;
  int x1 = x0 + step;
  int y1 = y0 + step;
  int cy0 = std::max(0, y0);
  int cy1 = std::min(g.layout.ny, y1);
  int cx0 = std::max(0, x0);
  int cx1 = std::min(g.layout.nx, x1);

  for (int y = cy0; y < cy1; ++y) {
    fn(MRFaceKey{0, x0, y, 1}, x0 - 1, y, -1.0);
    fn(MRFaceKey{0, std::min(x1, g.layout.nx), y, 1}, x1, y, 1.0);
  }
  for (int x = cx0; x < cx1; ++x) {
    fn(MRFaceKey{1, x, y0, 1}, x, y0 - 1, -1.0);
    fn(MRFaceKey{1, x, std::min(y1, g.layout.ny), 1}, x, y1, 1.0);
  }
}

std::vector<ProjectionCell> fluidProjectionCells(const MRMacGrid2D<8>& g) {
  std::vector<ProjectionCell> cells;
  for (const MRCellKey& c : g.marker.leafCells()) {
    if (markerAtCell(g, c) != 1) continue;
    double h = cellSize(g, c);
    cells.push_back(ProjectionCell{c, static_cast<int>(cells.size()), h, h * h});
  }
  return cells;
}

bool hasAnyMarker(const MRMacGrid2D<8>& g) {
  return !g.marker.blocks.empty();
}

int findPinCell(const MRMacGrid2D<8>& g, const std::vector<ProjectionCell>& cells) {
  bool hasDirichletAir = false;
  for (const ProjectionCell& c : cells) {
    visitCellFaces(g, c.key, [&](const MRFaceKey&, int nx, int ny, double) {
      if (markerAtFineCell(g, nx, ny) == 0) {
        hasDirichletAir = true;
      }
    });
  }
  return hasDirichletAir || cells.empty() ? -1 : cells.front().index;
}

double faceBeta(const MRMacGrid2D<8>& g, const MRFaceKey& f, const PhaseParams& pp) {
  double raw = f.axis == 0 ? static_cast<double>(g.gmu(f)) : static_cast<double>(g.gmv(f));
  return betaFromRawMass(raw, pp);
}

double neighborDistance(const MRMacGrid2D<8>& g, const ProjectionCell& c, int nx, int ny) {
  double otherH = c.h;
  if (nx >= 0 && nx < g.layout.nx && ny >= 0 && ny < g.layout.ny) {
    MRCellKey other = g.p.cellAtFineCell(nx, ny);
    if (validCell(other)) {
      otherH = cellSize(g, other);
    }
  }
  return 0.5 * c.h + 0.5 * otherH;
}

double projectionCoefficient(const MRMacGrid2D<8>& g,
                             const ProjectionCell& c,
                             const MRFaceKey& f,
                             int nx,
                             int ny,
                             const PhaseParams& pp,
                             double dt) {
  double distance = neighborDistance(g, c, nx, ny);
  if (distance <= 0.0 || c.volume <= 0.0) return 0.0;
  double length = g.layout.dx * static_cast<double>(f.fineLength);
  return dt * faceBeta(g, f, pp) * length / distance / c.volume;
}

void averageUProjection(MRMacGrid2D<8>& g) {
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

} // namespace

void MRPressureSystem2D::apply(const std::vector<double>& x, std::vector<double>& out) const {
  if (x.size() != volumes.size()) {
    throw std::invalid_argument("MRPressureSystem2D::apply input size must match volume count");
  }

  out.assign(volumes.size(), 0.0);

  for (const MREdge& e : edges) {
    double flux = e.conductance * (x[e.b] - x[e.a]);
    out[e.a] -= flux / volumes[e.a];
    out[e.b] += flux / volumes[e.b];
  }
}

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt) {
  (void)dt;

  MRPressureSystem2D sys;
  const auto& layout = g.p.layout;
  std::vector<PressureCellInfo> cells;
  std::vector<MRCellKey> leafCells = g.p.leafCells();
  cells.reserve(leafCells.size());
  sys.volumes.reserve(leafCells.size());

  for (const MRCellKey& c : leafCells) {
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h);
    cells.push_back(pressureCellInfo(c, static_cast<int>(cells.size()), layout.dx));
  }

  std::map<std::pair<int, int>, double> conductanceByPair;
  double domainWidth = static_cast<double>(layout.nx) * layout.dx;
  double domainHeight = static_cast<double>(layout.ny) * layout.dx;
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
  if (!hasAnyMarker(g)) {
    (void)dt;
    (void)maxIter;
    (void)tol;
    averageUProjection(g);
    return;
  }

  PhaseParams pp;
  projectMR(g, pp, dt, maxIter, tol);
}

void projectMR(MRMacGrid2D<8>& g, const PhaseParams& pp, double dt, int maxIter, double tol) {
  std::vector<ProjectionCell> cells = fluidProjectionCells(g);
  const int N = static_cast<int>(cells.size());
  g.p.blocks.clear();
  if (N == 0) return;

  std::map<std::tuple<int, int, int, int, int>, int> idx;
  for (const ProjectionCell& c : cells) {
    idx[cellTuple(c.key)] = c.index;
  }

  int pinCell = findPinCell(g, cells);

  auto pressureIndexAtFine = [&](int x, int y) {
    if (x < 0 || x >= g.layout.nx || y < 0 || y >= g.layout.ny) return -1;
    MRCellKey c = g.p.cellAtFineCell(x, y);
    auto it = idx.find(cellTuple(c));
    return it == idx.end() ? -1 : it->second;
  };

  auto divergence = [&](const ProjectionCell& c) {
    double flux = 0.0;
    visitCellFaces(g, c.key, [&](const MRFaceKey& f, int nx, int ny, double sign) {
      if (markerAtFineCell(g, nx, ny) == 2) return;
      double v = f.axis == 0 ? static_cast<double>(g.gu(f)) : static_cast<double>(g.gv(f));
      flux += sign * v * g.layout.dx * static_cast<double>(f.fineLength);
    });
    return flux / c.volume;
  };

  auto rowDiagonal = [&](const ProjectionCell& c) {
    if (c.index == pinCell) return 1.0;
    double diag = 0.0;
    visitCellFaces(g, c.key, [&](const MRFaceKey& f, int nx, int ny, double) {
      if (markerAtFineCell(g, nx, ny) == 2) return;
      diag += projectionCoefficient(g, c, f, nx, ny, pp, dt);
    });
    return diag;
  };

  auto applyA = [&](const std::vector<double>& x, std::vector<double>& out) {
    out.assign(N, 0.0);
    for (const ProjectionCell& c : cells) {
      if (c.index == pinCell) {
        out[c.index] = x[c.index];
        continue;
      }

      double diag = 0.0;
      double off = 0.0;
      visitCellFaces(g, c.key, [&](const MRFaceKey& f, int nx, int ny, double) {
        if (markerAtFineCell(g, nx, ny) == 2) return;
        double coeff = projectionCoefficient(g, c, f, nx, ny, pp, dt);
        diag += coeff;
        int nidx = pressureIndexAtFine(nx, ny);
        if (nidx >= 0 && nidx != pinCell) {
          off += coeff * x[nidx];
        }
      });
      out[c.index] = diag * x[c.index] - off;
    }
  };

  std::vector<double> x(N, 0.0);
  std::vector<double> r(N, 0.0);
  std::vector<double> z(N, 0.0);
  std::vector<double> p(N, 0.0);
  std::vector<double> Ap(N, 0.0);

  double res0 = 0.0;
  for (const ProjectionCell& c : cells) {
    r[c.index] = c.index == pinCell ? 0.0 : -divergence(c);
    res0 = std::max(res0, std::abs(r[c.index]));
  }
  if (res0 >= tol) {
    for (const ProjectionCell& c : cells) {
      double d = rowDiagonal(c);
      z[c.index] = d > 0.0 ? r[c.index] / d : 0.0;
      p[c.index] = z[c.index];
    }

    auto dot = [](const std::vector<double>& a, const std::vector<double>& b) {
      double s = 0.0;
      for (size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
      return s;
    };

    double rz = dot(r, z);
    for (int it = 0; it < maxIter; ++it) {
      applyA(p, Ap);
      double pAp = dot(p, Ap);
      if (std::abs(pAp) < 1e-30) break;

      double alpha = rz / pAp;
      double res = 0.0;
      for (int i = 0; i < N; ++i) {
        x[i] += alpha * p[i];
        r[i] -= alpha * Ap[i];
        res = std::max(res, std::abs(r[i]));
      }
      if (res < tol) break;

      for (const ProjectionCell& c : cells) {
        double d = rowDiagonal(c);
        z[c.index] = d > 0.0 ? r[c.index] / d : 0.0;
      }
      double rzNext = dot(r, z);
      double beta = rz == 0.0 ? 0.0 : rzNext / rz;
      rz = rzNext;
      for (int i = 0; i < N; ++i) {
        p[i] = z[i] + beta * p[i];
      }
    }
  }

  for (const ProjectionCell& c : cells) {
    g.p.ref(c.key) = static_cast<float>(x[c.index]);
  }

  auto pressureAt = [&](int xFine, int yFine) {
    int nidx = pressureIndexAtFine(xFine, yFine);
    return nidx >= 0 ? x[nidx] : 0.0;
  };

  for (const MRFaceKey& f : g.uFaces()) {
    int lm = markerAtFineCell(g, f.fineX - 1, f.fineY);
    int rm = markerAtFineCell(g, f.fineX, f.fineY);
    bool lf = lm == 1;
    bool rf = rm == 1;
    if (!lf && !rf) continue;
    if (lm == 2 || rm == 2) {
      g.u(f) = 0.0f;
      continue;
    }
    double distance = g.layout.dx;
    int refX = lf ? f.fineX - 1 : f.fineX;
    int refY = f.fineY;
    int refIdx = pressureIndexAtFine(refX, refY);
    if (refIdx >= 0) {
      distance = neighborDistance(g, cells[refIdx], lf ? f.fineX : f.fineX - 1, refY);
    }
    double pl = lf ? pressureAt(f.fineX - 1, f.fineY) : 0.0;
    double pr = rf ? pressureAt(f.fineX, f.fineY) : 0.0;
    double beta = faceBeta(g, f, pp);
    g.u(f) = static_cast<float>(g.gu(f) - dt * beta * (pr - pl) / distance);
  }

  for (const MRFaceKey& f : g.vFaces()) {
    int bm = markerAtFineCell(g, f.fineX, f.fineY - 1);
    int tm = markerAtFineCell(g, f.fineX, f.fineY);
    bool bf = bm == 1;
    bool tf = tm == 1;
    if (!bf && !tf) continue;
    if (bm == 2 || tm == 2) {
      g.v(f) = 0.0f;
      continue;
    }
    double distance = g.layout.dx;
    int refX = f.fineX;
    int refY = bf ? f.fineY - 1 : f.fineY;
    int refIdx = pressureIndexAtFine(refX, refY);
    if (refIdx >= 0) {
      distance = neighborDistance(g, cells[refIdx], refX, bf ? f.fineY : f.fineY - 1);
    }
    double pb = bf ? pressureAt(f.fineX, f.fineY - 1) : 0.0;
    double pt = tf ? pressureAt(f.fineX, f.fineY) : 0.0;
    double beta = faceBeta(g, f, pp);
    g.v(f) = static_cast<float>(g.gv(f) - dt * beta * (pt - pb) / distance);
  }
}
