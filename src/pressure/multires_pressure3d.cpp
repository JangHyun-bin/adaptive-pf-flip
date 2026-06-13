#include "pressure/multires_pressure3d.h"

#include "grid/multires_mac_grid3d.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <stdexcept>
#include <tuple>
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

struct ProjectionCell3D {
  MRCellKey3D key;
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

std::tuple<int, int, int, int, int, int, int> cellTuple(const MRCellKey3D& c) {
  return std::make_tuple(c.block.level, c.block.bx, c.block.by, c.block.bz, c.lx, c.ly, c.lz);
}

bool validCell(const MRCellKey3D& c) {
  return c.block.level >= 0 && c.lx >= 0 && c.ly >= 0 && c.lz >= 0;
}

int markerAtCell(const MRMacGrid3D<4>& g, const MRCellKey3D& c) {
  if (!validCell(c)) return 2;
  return static_cast<int>(g.marker.get(c) + 0.5f);
}

int markerAtFineCell(const MRMacGrid3D<4>& g, int x, int y, int z) {
  if (x < 0 || x >= g.marker.layout.nx ||
      y < 0 || y >= g.marker.layout.ny ||
      z < 0 || z >= g.marker.layout.nz) {
    return 2;
  }
  return markerAtCell(g, g.marker.cellAtFineCell(x, y, z));
}

double cellSize(const MRMacGrid3D<4>& g, const MRCellKey3D& c) {
  return g.p.cellSize(c.block.level);
}

double betaFromRawMass(double raw, const PhaseParams& pp) {
  double rmin = etaPhi(pp) * pp.rho_g * pp.rho_tilde_0;
  double invden = 1.0 / (pp.alpha_phi * pp.rho_tilde_0 * pp.rho_l);
  double phi = raw < rmin ? 0.0 : std::min(std::sqrt((raw - rmin) * invden), 1.0);
  return 1.0 / (phi * pp.rho_l + (1.0 - phi) * pp.rho_g);
}

template<class Fn>
void visitCellFaces(const MRMacGrid3D<4>& g, const MRCellKey3D& c, Fn&& fn) {
  constexpr int B = 4;
  int step = 1 << c.block.level;
  int x0 = c.block.bx * B * step + c.lx * step;
  int y0 = c.block.by * B * step + c.ly * step;
  int z0 = c.block.bz * B * step + c.lz * step;
  int x1 = x0 + step;
  int y1 = y0 + step;
  int z1 = z0 + step;
  int cx0 = std::max(0, x0);
  int cx1 = std::min(g.layout.nx, x1);
  int cy0 = std::max(0, y0);
  int cy1 = std::min(g.layout.ny, y1);
  int cz0 = std::max(0, z0);
  int cz1 = std::min(g.layout.nz, z1);

  for (int z = cz0; z < cz1; ++z) {
    for (int y = cy0; y < cy1; ++y) {
      fn(MRFaceKey3D{0, x0, y, z, 1, 1}, x0 - 1, y, z, -1.0);
      fn(MRFaceKey3D{0, std::min(x1, g.layout.nx), y, z, 1, 1}, x1, y, z, 1.0);
    }
  }
  for (int z = cz0; z < cz1; ++z) {
    for (int x = cx0; x < cx1; ++x) {
      fn(MRFaceKey3D{1, x, y0, z, 1, 1}, x, y0 - 1, z, -1.0);
      fn(MRFaceKey3D{1, x, std::min(y1, g.layout.ny), z, 1, 1}, x, y1, z, 1.0);
    }
  }
  for (int y = cy0; y < cy1; ++y) {
    for (int x = cx0; x < cx1; ++x) {
      fn(MRFaceKey3D{2, x, y, z0, 1, 1}, x, y, z0 - 1, -1.0);
      fn(MRFaceKey3D{2, x, y, std::min(z1, g.layout.nz), 1, 1}, x, y, z1, 1.0);
    }
  }
}

std::vector<ProjectionCell3D> fluidProjectionCells(const MRMacGrid3D<4>& g) {
  std::vector<ProjectionCell3D> cells;
  for (const MRCellKey3D& c : g.marker.leafCells()) {
    if (markerAtCell(g, c) != 1) continue;
    double h = cellSize(g, c);
    cells.push_back(ProjectionCell3D{c, static_cast<int>(cells.size()), h, h * h * h});
  }
  return cells;
}

bool hasAnyMarker(const MRMacGrid3D<4>& g) {
  return !g.marker.blocks.empty();
}

int findPinCell(const MRMacGrid3D<4>& g, const std::vector<ProjectionCell3D>& cells) {
  bool hasDirichletAir = false;
  for (const ProjectionCell3D& c : cells) {
    visitCellFaces(g, c.key, [&](const MRFaceKey3D&, int nx, int ny, int nz, double) {
      if (markerAtFineCell(g, nx, ny, nz) == 0) {
        hasDirichletAir = true;
      }
    });
  }
  return hasDirichletAir || cells.empty() ? -1 : cells.front().index;
}

double faceBeta(const MRMacGrid3D<4>& g, const MRFaceKey3D& f, const PhaseParams& pp) {
  double raw = 0.0;
  if (f.axis == 0) {
    raw = static_cast<double>(g.gmu(f));
  } else if (f.axis == 1) {
    raw = static_cast<double>(g.gmv(f));
  } else {
    raw = static_cast<double>(g.gmw(f));
  }
  return betaFromRawMass(raw, pp);
}

double neighborDistance(const MRMacGrid3D<4>& g, const ProjectionCell3D& c, int nx, int ny, int nz) {
  double otherH = c.h;
  if (nx >= 0 && nx < g.layout.nx &&
      ny >= 0 && ny < g.layout.ny &&
      nz >= 0 && nz < g.layout.nz) {
    MRCellKey3D other = g.p.cellAtFineCell(nx, ny, nz);
    if (validCell(other)) {
      otherH = cellSize(g, other);
    }
  }
  return 0.5 * c.h + 0.5 * otherH;
}

double faceArea(const MRMacGrid3D<4>& g, const MRFaceKey3D& f) {
  return g.layout.dx * g.layout.dx *
         static_cast<double>(f.fineLengthA) *
         static_cast<double>(f.fineLengthB);
}

double projectionCoefficient(const MRMacGrid3D<4>& g,
                             const ProjectionCell3D& c,
                             const MRFaceKey3D& f,
                             int nx,
                             int ny,
                             int nz,
                             const PhaseParams& pp,
                             double dt) {
  double distance = neighborDistance(g, c, nx, ny, nz);
  if (distance <= 0.0 || c.volume <= 0.0) return 0.0;
  return dt * faceBeta(g, f, pp) * faceArea(g, f) / distance / c.volume;
}

void averageVelocityProjection(MRMacGrid3D<4>& g) {
  auto averageU = g.uFaces();
  double avg = 0.0;
  for (const MRFaceKey3D& f : averageU) avg += g.gu(f);
  if (!averageU.empty()) avg /= static_cast<double>(averageU.size());
  for (const MRFaceKey3D& f : averageU) g.u(f) = static_cast<float>(avg);

  auto averageV = g.vFaces();
  avg = 0.0;
  for (const MRFaceKey3D& f : averageV) avg += g.gv(f);
  if (!averageV.empty()) avg /= static_cast<double>(averageV.size());
  for (const MRFaceKey3D& f : averageV) g.v(f) = static_cast<float>(avg);

  auto averageW = g.wFaces();
  avg = 0.0;
  for (const MRFaceKey3D& f : averageW) avg += g.gw(f);
  if (!averageW.empty()) avg /= static_cast<double>(averageW.size());
  for (const MRFaceKey3D& f : averageW) g.w(f) = static_cast<float>(avg);
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

void projectMR3D(MRMacGrid3D<4>& g, double dt, int maxIter, double tol) {
  if (!hasAnyMarker(g)) {
    (void)dt;
    (void)maxIter;
    (void)tol;
    averageVelocityProjection(g);
    return;
  }

  PhaseParams pp;
  projectMR3D(g, pp, dt, maxIter, tol);
}

void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt, int maxIter, double tol) {
  std::vector<ProjectionCell3D> cells = fluidProjectionCells(g);
  const int N = static_cast<int>(cells.size());
  g.p.blocks.clear();
  if (N == 0) return;

  std::map<std::tuple<int, int, int, int, int, int, int>, int> idx;
  for (const ProjectionCell3D& c : cells) {
    idx[cellTuple(c.key)] = c.index;
  }

  int pinCell = findPinCell(g, cells);

  auto pressureIndexAtFine = [&](int x, int y, int z) {
    if (x < 0 || x >= g.layout.nx ||
        y < 0 || y >= g.layout.ny ||
        z < 0 || z >= g.layout.nz) {
      return -1;
    }
    MRCellKey3D c = g.p.cellAtFineCell(x, y, z);
    auto it = idx.find(cellTuple(c));
    return it == idx.end() ? -1 : it->second;
  };

  auto divergence = [&](const ProjectionCell3D& c) {
    double flux = 0.0;
    visitCellFaces(g, c.key, [&](const MRFaceKey3D& f, int nx, int ny, int nz, double sign) {
      if (markerAtFineCell(g, nx, ny, nz) == 2) return;
      double v = 0.0;
      if (f.axis == 0) {
        v = static_cast<double>(g.gu(f));
      } else if (f.axis == 1) {
        v = static_cast<double>(g.gv(f));
      } else {
        v = static_cast<double>(g.gw(f));
      }
      flux += sign * v * faceArea(g, f);
    });
    return flux / c.volume;
  };

  auto rowDiagonal = [&](const ProjectionCell3D& c) {
    if (c.index == pinCell) return 1.0;
    double diag = 0.0;
    visitCellFaces(g, c.key, [&](const MRFaceKey3D& f, int nx, int ny, int nz, double) {
      if (markerAtFineCell(g, nx, ny, nz) == 2) return;
      diag += projectionCoefficient(g, c, f, nx, ny, nz, pp, dt);
    });
    return diag;
  };

  auto applyA = [&](const std::vector<double>& x, std::vector<double>& out) {
    out.assign(N, 0.0);
    for (const ProjectionCell3D& c : cells) {
      if (c.index == pinCell) {
        out[c.index] = x[c.index];
        continue;
      }

      double diag = 0.0;
      double off = 0.0;
      visitCellFaces(g, c.key, [&](const MRFaceKey3D& f, int nx, int ny, int nz, double) {
        if (markerAtFineCell(g, nx, ny, nz) == 2) return;
        double coeff = projectionCoefficient(g, c, f, nx, ny, nz, pp, dt);
        diag += coeff;
        int nidx = pressureIndexAtFine(nx, ny, nz);
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
  for (const ProjectionCell3D& c : cells) {
    r[c.index] = c.index == pinCell ? 0.0 : -divergence(c);
    res0 = std::max(res0, std::abs(r[c.index]));
  }
  if (res0 >= tol) {
    for (const ProjectionCell3D& c : cells) {
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

      for (const ProjectionCell3D& c : cells) {
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

  for (const ProjectionCell3D& c : cells) {
    g.p.ref(c.key) = static_cast<float>(x[c.index]);
  }

  auto pressureAt = [&](int xFine, int yFine, int zFine) {
    int nidx = pressureIndexAtFine(xFine, yFine, zFine);
    return nidx >= 0 ? x[nidx] : 0.0;
  };

  for (const MRFaceKey3D& f : g.uFaces()) {
    int lm = markerAtFineCell(g, f.fineX - 1, f.fineY, f.fineZ);
    int rm = markerAtFineCell(g, f.fineX, f.fineY, f.fineZ);
    bool lf = lm == 1;
    bool rf = rm == 1;
    if (!lf && !rf) continue;
    if (lm == 2 || rm == 2) {
      g.u(f) = 0.0f;
      continue;
    }
    double distance = g.layout.dx;
    int refX = lf ? f.fineX - 1 : f.fineX;
    int refIdx = pressureIndexAtFine(refX, f.fineY, f.fineZ);
    if (refIdx >= 0) {
      distance = neighborDistance(g, cells[refIdx], lf ? f.fineX : f.fineX - 1, f.fineY, f.fineZ);
    }
    double pl = lf ? pressureAt(f.fineX - 1, f.fineY, f.fineZ) : 0.0;
    double pr = rf ? pressureAt(f.fineX, f.fineY, f.fineZ) : 0.0;
    double beta = faceBeta(g, f, pp);
    g.u(f) = static_cast<float>(g.gu(f) - dt * beta * (pr - pl) / distance);
  }

  for (const MRFaceKey3D& f : g.vFaces()) {
    int bm = markerAtFineCell(g, f.fineX, f.fineY - 1, f.fineZ);
    int tm = markerAtFineCell(g, f.fineX, f.fineY, f.fineZ);
    bool bf = bm == 1;
    bool tf = tm == 1;
    if (!bf && !tf) continue;
    if (bm == 2 || tm == 2) {
      g.v(f) = 0.0f;
      continue;
    }
    double distance = g.layout.dx;
    int refY = bf ? f.fineY - 1 : f.fineY;
    int refIdx = pressureIndexAtFine(f.fineX, refY, f.fineZ);
    if (refIdx >= 0) {
      distance = neighborDistance(g, cells[refIdx], f.fineX, bf ? f.fineY : f.fineY - 1, f.fineZ);
    }
    double pb = bf ? pressureAt(f.fineX, f.fineY - 1, f.fineZ) : 0.0;
    double pt = tf ? pressureAt(f.fineX, f.fineY, f.fineZ) : 0.0;
    double beta = faceBeta(g, f, pp);
    g.v(f) = static_cast<float>(g.gv(f) - dt * beta * (pt - pb) / distance);
  }

  for (const MRFaceKey3D& f : g.wFaces()) {
    int bm = markerAtFineCell(g, f.fineX, f.fineY, f.fineZ - 1);
    int fm = markerAtFineCell(g, f.fineX, f.fineY, f.fineZ);
    bool bf = bm == 1;
    bool ff = fm == 1;
    if (!bf && !ff) continue;
    if (bm == 2 || fm == 2) {
      g.w(f) = 0.0f;
      continue;
    }
    double distance = g.layout.dx;
    int refZ = bf ? f.fineZ - 1 : f.fineZ;
    int refIdx = pressureIndexAtFine(f.fineX, f.fineY, refZ);
    if (refIdx >= 0) {
      distance = neighborDistance(g, cells[refIdx], f.fineX, f.fineY, bf ? f.fineZ : f.fineZ - 1);
    }
    double pb = bf ? pressureAt(f.fineX, f.fineY, f.fineZ - 1) : 0.0;
    double pf = ff ? pressureAt(f.fineX, f.fineY, f.fineZ) : 0.0;
    double beta = faceBeta(g, f, pp);
    g.w(f) = static_cast<float>(g.gw(f) - dt * beta * (pf - pb) / distance);
  }
}
