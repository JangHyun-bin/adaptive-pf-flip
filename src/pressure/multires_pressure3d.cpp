#include "pressure/multires_pressure3d.h"

#include "grid/multires_mac_grid3d.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <map>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

namespace {

struct ProjectionCell3D {
  MRCellKey3D key;
  int index = -1;
  double h = 0.0;
  double volume = 0.0;
};

struct ProjectionTerm3D {
  int index = -1;
  double coeff = 0.0;
};

struct ProjectionRow3D {
  double divergence = 0.0;
  double diag = 0.0;
  std::vector<ProjectionTerm3D> offdiag;
};

std::tuple<int, int, int, int, int, int, int> cellTuple(const MRCellKey3D& c) {
  return std::make_tuple(c.block.level, c.block.bx, c.block.by, c.block.bz, c.lx, c.ly, c.lz);
}

std::tuple<int, int, int> level1ParentTuple(const MRCellKey3D& c) {
  constexpr int B = 4;
  if (c.block.level < 0 || c.block.level > 1) {
    throw std::invalid_argument("level-1 pressure aggregation supports levels 0 and 1");
  }

  int step = 1 << c.block.level;
  int x0 = c.block.bx * B * step + c.lx * step;
  int y0 = c.block.by * B * step + c.ly * step;
  int z0 = c.block.bz * B * step + c.lz * step;
  return std::make_tuple(x0 / 2, y0 / 2, z0 / 2);
}

MRPressureAggregation3D buildLevel1AggregationFromCells(
  const std::vector<MRCellKey3D>& cells,
  const std::vector<double>& volumes) {
  if (cells.size() != volumes.size()) {
    throw std::invalid_argument("buildLevel1AggregationFromCells cell and volume sizes must match");
  }

  std::vector<int> fineToCoarse(cells.size(), 0);
  std::map<std::tuple<int, int, int>, int> coarseIds;
  for (size_t i = 0; i < cells.size(); ++i) {
    auto inserted = coarseIds.emplace(level1ParentTuple(cells[i]),
                                      static_cast<int>(coarseIds.size()));
    fineToCoarse[i] = inserted.first->second;
  }

  MRPressureSystem3D sys;
  sys.volumes = volumes;
  return buildMRPressureAggregation3D(sys, fineToCoarse);
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

template<class Fn>
void visitPressureCellFaces(const MRScalarGrid3D<4>& p, const MRCellKey3D& c, Fn&& fn) {
  constexpr int B = 4;
  int step = 1 << c.block.level;
  int x0 = c.block.bx * B * step + c.lx * step;
  int y0 = c.block.by * B * step + c.ly * step;
  int z0 = c.block.bz * B * step + c.lz * step;
  int x1 = x0 + step;
  int y1 = y0 + step;
  int z1 = z0 + step;
  int cx0 = std::max(0, x0);
  int cx1 = std::min(p.layout.nx, x1);
  int cy0 = std::max(0, y0);
  int cy1 = std::min(p.layout.ny, y1);
  int cz0 = std::max(0, z0);
  int cz1 = std::min(p.layout.nz, z1);
  double area = p.layout.dx * p.layout.dx;

  for (int z = cz0; z < cz1; ++z) {
    for (int y = cy0; y < cy1; ++y) {
      fn(x0 - 1, y, z, area);
      fn(x1, y, z, area);
    }
  }
  for (int z = cz0; z < cz1; ++z) {
    for (int x = cx0; x < cx1; ++x) {
      fn(x, y0 - 1, z, area);
      fn(x, y1, z, area);
    }
  }
  for (int y = cy0; y < cy1; ++y) {
    for (int x = cx0; x < cx1; ++x) {
      fn(x, y, z0 - 1, area);
      fn(x, y, z1, area);
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
  const std::vector<MRFaceKey3D>& averageU = g.uFaceRefs();
  double avg = 0.0;
  for (const MRFaceKey3D& f : averageU) avg += g.gu(f);
  if (!averageU.empty()) avg /= static_cast<double>(averageU.size());
  for (const MRFaceKey3D& f : averageU) g.u(f) = static_cast<float>(avg);

  const std::vector<MRFaceKey3D>& averageV = g.vFaceRefs();
  avg = 0.0;
  for (const MRFaceKey3D& f : averageV) avg += g.gv(f);
  if (!averageV.empty()) avg /= static_cast<double>(averageV.size());
  for (const MRFaceKey3D& f : averageV) g.v(f) = static_cast<float>(avg);

  const std::vector<MRFaceKey3D>& averageW = g.wFaceRefs();
  avg = 0.0;
  for (const MRFaceKey3D& f : averageW) avg += g.gw(f);
  if (!averageW.empty()) avg /= static_cast<double>(averageW.size());
  for (const MRFaceKey3D& f : averageW) g.w(f) = static_cast<float>(avg);
}

MRPressureSolveConfig3D makeSolveConfig(int maxIter, double tol) {
  MRPressureSolveConfig3D config;
  config.max_iterations = maxIter;
  config.absolute_tolerance = tol;
  return config;
}

MRPressureSolveStats3D makeInitialStats(const MRPressureSolveConfig3D& config) {
  MRPressureSolveStats3D stats;
  stats.max_iterations = config.max_iterations;
  stats.tolerance = config.absolute_tolerance;
  stats.relative_tolerance = config.relative_tolerance;
  stats.effective_tolerance = config.absolute_tolerance;
  stats.restart_growth_threshold = config.restart_growth_threshold;
  stats.adaptive_restart = config.adaptive_restart;
  stats.used_jacobi_preconditioner = config.use_jacobi_preconditioner;
  stats.used_flexible_cg_beta = config.use_flexible_cg_beta;
  stats.relaxation_sweeps = config.relaxation_sweeps;
  stats.relaxation_omega = config.relaxation_omega;
  stats.relaxation_min_omega = config.relaxation_min_omega;
  stats.relaxation_final_omega = config.relaxation_omega;
  stats.residual_history_stride = config.residual_history_stride;
  stats.residual_history_limit = config.residual_history_limit;
  stats.used_coarse_correction = config.use_coarse_correction;
  stats.coarse_correction_max_iterations = config.coarse_correction_iterations;
  stats.coarse_correction_tolerance = config.coarse_correction_absolute_tolerance;
  stats.coarse_correction_relative_tolerance = config.coarse_correction_relative_tolerance;
  return stats;
}

void validateSolveConfig(const MRPressureSolveConfig3D& config) {
  if (config.max_iterations < 0 ||
      config.absolute_tolerance < 0.0 ||
      config.relative_tolerance < 0.0 ||
      config.restart_growth_threshold < 0.0 ||
      config.relaxation_sweeps < 0 ||
      config.relaxation_omega < 0.0 ||
      config.relaxation_min_omega < 0.0 ||
      config.residual_history_stride < 0 ||
      config.residual_history_limit < 0 ||
      config.coarse_correction_iterations < 0 ||
      config.coarse_correction_absolute_tolerance < 0.0 ||
      config.coarse_correction_relative_tolerance < 0.0) {
    throw std::invalid_argument("projectMR3D invalid solve config");
  }
}

void recordResidualHistory(MRPressureSolveStats3D& stats,
                           const MRPressureSolveConfig3D& config,
                           int iteration,
                           double residual) {
  if (config.residual_history_stride <= 0 || config.residual_history_limit <= 0) {
    return;
  }
  if (iteration > 0 && iteration % config.residual_history_stride != 0) {
    return;
  }
  if (static_cast<int>(stats.residual_history.size()) >= config.residual_history_limit) {
    stats.residual_history_truncated = true;
    return;
  }
  stats.residual_history.push_back(residual);
}

double maxAbs(const std::vector<double>& v) {
  double mx = 0.0;
  for (double x : v) {
    if (!std::isfinite(x)) {
      return std::numeric_limits<double>::infinity();
    }
    mx = std::max(mx, std::abs(x));
  }
  return mx;
}

void requireSize(const std::vector<double>& v, size_t n, const char* message) {
  if (v.size() != n) {
    throw std::invalid_argument(message);
  }
}

double weightedDotVolumes(const std::vector<double>& volumes,
                          const std::vector<double>& a,
                          const std::vector<double>& b) {
  requireSize(a, volumes.size(), "weighted dot input size must match volume count");
  requireSize(b, volumes.size(), "weighted dot input size must match volume count");

  double sum = 0.0;
  for (size_t i = 0; i < volumes.size(); ++i) {
    sum += volumes[i] * a[i] * b[i];
  }
  return sum;
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

void MRPressureSystem3D::residual(const std::vector<double>& x,
                                  const std::vector<double>& rhs,
                                  std::vector<double>& out) const {
  requireSize(rhs, volumes.size(), "MRPressureSystem3D::residual rhs size must match volume count");

  std::vector<double> Ax;
  apply(x, Ax);
  out.resize(volumes.size());
  for (size_t i = 0; i < volumes.size(); ++i) {
    out[i] = rhs[i] - Ax[i];
  }
}

double MRPressureSystem3D::weightedDot(const std::vector<double>& a,
                                       const std::vector<double>& b) const {
  return weightedDotVolumes(volumes, a, b);
}

double MRPressureSystem3D::weightedL2Norm(const std::vector<double>& x) const {
  double norm2 = weightedDot(x, x);
  return norm2 > 0.0 ? std::sqrt(norm2) : 0.0;
}

MRPressureSystem3D buildMRPressureSystem3D(const MRMacGrid3D<4>& g, double dt) {
  (void)dt;

  MRPressureSystem3D sys;
  const auto& layout = g.p.layout;
  std::vector<MRCellKey3D> leafCells = g.p.leafCells();
  sys.volumes.reserve(leafCells.size());

  std::map<std::tuple<int, int, int, int, int, int, int>, int> idx;
  for (size_t n = 0; n < leafCells.size(); ++n) {
    const MRCellKey3D& c = leafCells[n];
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h * h);
    idx[cellTuple(c)] = static_cast<int>(n);
  }

  std::map<std::pair<int, int>, double> conductanceByPair;
  for (size_t i = 0; i < leafCells.size(); ++i) {
    const MRCellKey3D& c = leafCells[i];
    double h = g.p.cellSize(c.block.level);
    visitPressureCellFaces(g.p, c, [&](int nx, int ny, int nz, double area) {
      if (nx < 0 || nx >= layout.nx ||
          ny < 0 || ny >= layout.ny ||
          nz < 0 || nz >= layout.nz) {
        return;
      }
      MRCellKey3D other = g.p.cellAtFineCell(nx, ny, nz);
      auto it = idx.find(cellTuple(other));
      if (it == idx.end()) return;
      int j = it->second;
      if (static_cast<int>(i) >= j) return;

      double otherH = g.p.cellSize(other.block.level);
      double distance = 0.5 * h + 0.5 * otherH;
      if (distance > 0.0) {
        conductanceByPair[{static_cast<int>(i), j}] += area / distance;
      }
    });
  }

  sys.edges.reserve(conductanceByPair.size());
  for (const auto& entry : conductanceByPair) {
    if (entry.second > 0.0) {
      sys.edges.push_back(MREdge3D{entry.first.first, entry.first.second, entry.second});
    }
  }
  return sys;
}

MRPressureAggregation3D buildMRPressureAggregation3D(
  const MRPressureSystem3D& sys,
  const std::vector<int>& fineToCoarse) {
  if (fineToCoarse.size() != static_cast<size_t>(sys.cellCount())) {
    throw std::invalid_argument("buildMRPressureAggregation3D fine map size must match cell count");
  }

  int coarseCount = 0;
  for (int coarse : fineToCoarse) {
    if (coarse < 0) {
      throw std::invalid_argument("buildMRPressureAggregation3D coarse index must be non-negative");
    }
    coarseCount = std::max(coarseCount, coarse + 1);
  }

  MRPressureAggregation3D aggregation;
  aggregation.fine_to_coarse = fineToCoarse;
  aggregation.fine_volumes = sys.volumes;
  aggregation.coarse_volumes.assign(static_cast<size_t>(coarseCount), 0.0);

  for (int i = 0; i < sys.cellCount(); ++i) {
    double volume = sys.volume(i);
    if (volume <= 0.0 || !std::isfinite(volume)) {
      throw std::invalid_argument("buildMRPressureAggregation3D fine volume must be positive and finite");
    }
    aggregation.coarse_volumes[static_cast<size_t>(fineToCoarse[static_cast<size_t>(i)])] += volume;
  }

  for (double volume : aggregation.coarse_volumes) {
    if (volume <= 0.0 || !std::isfinite(volume)) {
      throw std::invalid_argument("buildMRPressureAggregation3D coarse ids must be dense");
    }
  }

  return aggregation;
}

MRPressureAggregation3D buildMRPressureLevel1Aggregation3D(
  const MRMacGrid3D<4>& g,
  const MRPressureSystem3D& sys) {
  std::vector<MRCellKey3D> leafCells = g.p.leafCells();
  if (leafCells.size() != static_cast<size_t>(sys.cellCount())) {
    throw std::invalid_argument("buildMRPressureLevel1Aggregation3D cell count must match system");
  }

  return buildLevel1AggregationFromCells(leafCells, sys.volumes);
}

void restrictMRPressureVolumeWeighted3D(
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& fineValues,
  std::vector<double>& coarseValues) {
  requireSize(fineValues, aggregation.fine_to_coarse.size(),
              "restrictMRPressureVolumeWeighted3D fine size must match aggregation");

  coarseValues.assign(aggregation.coarse_volumes.size(), 0.0);
  for (size_t i = 0; i < fineValues.size(); ++i) {
    int coarse = aggregation.fine_to_coarse[i];
    double fineVolume = aggregation.fine_volumes[i];
    coarseValues[static_cast<size_t>(coarse)] += fineVolume * fineValues[i];
  }

  for (size_t c = 0; c < coarseValues.size(); ++c) {
    double coarseVolume = aggregation.coarse_volumes[c];
    if (coarseVolume <= 0.0) {
      throw std::invalid_argument("restrictMRPressureVolumeWeighted3D coarse volume must be positive");
    }
    coarseValues[c] /= coarseVolume;
  }
}

void prolongMRPressurePiecewiseConstant3D(
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& coarseValues,
  std::vector<double>& fineValues) {
  requireSize(coarseValues, aggregation.coarse_volumes.size(),
              "prolongMRPressurePiecewiseConstant3D coarse size must match aggregation");

  fineValues.resize(aggregation.fine_to_coarse.size());
  for (size_t i = 0; i < fineValues.size(); ++i) {
    fineValues[i] = coarseValues[static_cast<size_t>(aggregation.fine_to_coarse[i])];
  }
}

MRPressureSystem3D buildGalerkinCoarseSystem3D(
  const MRPressureSystem3D& fine,
  const MRPressureAggregation3D& aggregation) {
  if (aggregation.fine_to_coarse.size() != static_cast<size_t>(fine.cellCount()) ||
      aggregation.fine_volumes.size() != static_cast<size_t>(fine.cellCount())) {
    throw std::invalid_argument("buildGalerkinCoarseSystem3D aggregation size must match fine system");
  }

  MRPressureSystem3D coarse;
  coarse.volumes = aggregation.coarse_volumes;

  std::map<std::pair<int, int>, double> conductanceByPair;
  for (const MREdge3D& e : fine.edges) {
    int a = aggregation.fine_to_coarse[static_cast<size_t>(e.a)];
    int b = aggregation.fine_to_coarse[static_cast<size_t>(e.b)];
    if (a == b) continue;
    if (a > b) std::swap(a, b);
    conductanceByPair[{a, b}] += e.conductance;
  }

  coarse.edges.reserve(conductanceByPair.size());
  for (const auto& entry : conductanceByPair) {
    if (entry.second > 0.0) {
      coarse.edges.push_back(MREdge3D{entry.first.first, entry.first.second, entry.second});
    }
  }
  return coarse;
}

void applyGalerkinCoarseCorrection3D(
  const MRPressureSystem3D& fine,
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& fineResidual,
  const MRPressureCoarseCorrectionConfig3D& config,
  std::vector<double>& fineCorrection,
  MRPressureCoarseCorrectionStats3D* stats) {
  if (config.max_iterations < 0 ||
      config.absolute_tolerance < 0.0 ||
      config.relative_tolerance < 0.0) {
    throw std::invalid_argument("applyGalerkinCoarseCorrection3D invalid solve config");
  }

  MRPressureSystem3D coarse = buildGalerkinCoarseSystem3D(fine, aggregation);
  std::vector<double> coarseRhs;
  restrictMRPressureVolumeWeighted3D(aggregation, fineResidual, coarseRhs);

  MRPressureCoarseCorrectionStats3D localStats;
  localStats.coarse_cells = coarse.cellCount();
  localStats.coarse_edges = static_cast<int>(coarse.edges.size());
  localStats.max_iterations = config.max_iterations;
  localStats.tolerance = config.absolute_tolerance;
  localStats.relative_tolerance = config.relative_tolerance;

  if (coarse.cellCount() == 0) {
    fineCorrection.clear();
    localStats.converged = true;
    if (stats) *stats = localStats;
    return;
  }

  int pin = config.pinned_cell < 0 ? 0 : config.pinned_cell;
  if (pin >= coarse.cellCount()) {
    throw std::invalid_argument("applyGalerkinCoarseCorrection3D pinned cell out of range");
  }
  localStats.pinned_cell = pin;

  std::vector<double> x(static_cast<size_t>(coarse.cellCount()), 0.0);
  std::vector<double> r = coarseRhs;
  std::vector<double> p = r;
  std::vector<double> Ap;
  r[static_cast<size_t>(pin)] = 0.0;
  p[static_cast<size_t>(pin)] = 0.0;

  auto applyPinned = [&](const std::vector<double>& in, std::vector<double>& out) {
    coarse.apply(in, out);
    out[static_cast<size_t>(pin)] = in[static_cast<size_t>(pin)];
  };

  double res0 = coarse.weightedL2Norm(r);
  localStats.initial_residual = res0;
  localStats.final_residual = res0;
  localStats.effective_tolerance =
    std::max(config.absolute_tolerance, config.relative_tolerance * res0);
  localStats.converged = res0 <= localStats.effective_tolerance;

  double rr = coarse.weightedDot(r, r);
  if (!std::isfinite(rr)) {
    localStats.breakdown = true;
  }

  for (int it = 0;
       !localStats.converged && !localStats.breakdown && it < config.max_iterations;
       ++it) {
    applyPinned(p, Ap);
    double pAp = coarse.weightedDot(p, Ap);
    if (!std::isfinite(pAp) || std::abs(pAp) < 1e-30) {
      localStats.breakdown = true;
      break;
    }

    double alpha = rr / pAp;
    if (!std::isfinite(alpha)) {
      localStats.breakdown = true;
      break;
    }

    for (int i = 0; i < coarse.cellCount(); ++i) {
      size_t n = static_cast<size_t>(i);
      x[n] += alpha * p[n];
      r[n] -= alpha * Ap[n];
    }
    x[static_cast<size_t>(pin)] = 0.0;
    r[static_cast<size_t>(pin)] = 0.0;

    localStats.iterations = it + 1;
    double res = coarse.weightedL2Norm(r);
    localStats.final_residual = res;
    if (!std::isfinite(res)) {
      localStats.breakdown = true;
      break;
    }
    if (res <= localStats.effective_tolerance) {
      localStats.converged = true;
      break;
    }

    double rrNext = coarse.weightedDot(r, r);
    if (!std::isfinite(rrNext) || std::abs(rr) < 1e-30) {
      localStats.breakdown = true;
      break;
    }
    double beta = rrNext / rr;
    if (!std::isfinite(beta)) {
      localStats.breakdown = true;
      break;
    }
    rr = rrNext;
    for (int i = 0; i < coarse.cellCount(); ++i) {
      size_t n = static_cast<size_t>(i);
      p[n] = r[n] + beta * p[n];
    }
    p[static_cast<size_t>(pin)] = 0.0;
  }

  prolongMRPressurePiecewiseConstant3D(aggregation, x, fineCorrection);
  if (stats) *stats = localStats;
}

double maxMRDivergence3D(const MRMacGrid3D<4>& g) {
  double mn = 0.0;
  double mx = 0.0;
  bool first = true;

  for (const MRFaceKey3D& f : g.uFaceRefs()) {
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

void projectMR3D(MRMacGrid3D<4>& g, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats) {
  projectMR3D(g, dt, makeSolveConfig(maxIter, tol), stats);
}

void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats) {
  projectMR3D(g, pp, dt, makeSolveConfig(maxIter, tol), stats);
}

void projectMR3D(MRMacGrid3D<4>& g, double dt, const MRPressureSolveConfig3D& config,
                 MRPressureSolveStats3D* stats) {
  validateSolveConfig(config);
  MRPressureSolveStats3D localStats = makeInitialStats(config);
  if (!hasAnyMarker(g)) {
    (void)dt;
    localStats.used_average_projection = true;
    localStats.converged = true;
    averageVelocityProjection(g);
    if (stats) *stats = localStats;
    return;
  }

  PhaseParams pp;
  projectMR3D(g, pp, dt, config, stats);
}

void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt,
                 const MRPressureSolveConfig3D& config,
                 MRPressureSolveStats3D* stats) {
  validateSolveConfig(config);
  MRPressureSolveStats3D localStats = makeInitialStats(config);
  std::vector<ProjectionCell3D> cells = fluidProjectionCells(g);
  const int N = static_cast<int>(cells.size());
  localStats.active_cells = N;
  g.p.blocks.clear();
  if (N == 0) {
    localStats.converged = true;
    if (stats) *stats = localStats;
    return;
  }

  std::map<std::tuple<int, int, int, int, int, int, int>, int> idx;
  for (const ProjectionCell3D& c : cells) {
    idx[cellTuple(c.key)] = c.index;
  }

  int pinCell = findPinCell(g, cells);
  localStats.pinned_cell = pinCell;

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

  std::vector<ProjectionRow3D> rows(N);
  for (const ProjectionCell3D& c : cells) {
    if (c.index == pinCell) {
      rows[c.index].diag = 1.0;
      continue;
    }

    visitCellFaces(g, c.key, [&](const MRFaceKey3D& f, int nx, int ny, int nz, double sign) {
      if (markerAtFineCell(g, nx, ny, nz) == 2) return;
      double coeff = projectionCoefficient(g, c, f, nx, ny, nz, pp, dt);
      rows[c.index].diag += coeff;
      int nidx = pressureIndexAtFine(nx, ny, nz);
      if (nidx >= 0 && nidx != pinCell) {
        rows[c.index].offdiag.push_back(ProjectionTerm3D{nidx, coeff});
      }

      double v = 0.0;
      if (f.axis == 0) {
        v = static_cast<double>(g.gu(f));
      } else if (f.axis == 1) {
        v = static_cast<double>(g.gv(f));
      } else {
        v = static_cast<double>(g.gw(f));
      }
      rows[c.index].divergence += sign * v * faceArea(g, f) / c.volume;
    });
  }

  for (const ProjectionRow3D& row : rows) {
    if (row.diag > 0.0) {
      localStats.min_positive_diag = localStats.min_positive_diag == 0.0
        ? row.diag
        : std::min(localStats.min_positive_diag, row.diag);
      localStats.max_diag = std::max(localStats.max_diag, row.diag);
    }
  }

  auto applyA = [&](const std::vector<double>& x, std::vector<double>& out) {
    out.assign(N, 0.0);
    for (const ProjectionCell3D& c : cells) {
      if (c.index == pinCell) {
        out[c.index] = x[c.index];
        continue;
      }

      double off = 0.0;
      for (const ProjectionTerm3D& term : rows[c.index].offdiag) {
        off += term.coeff * x[term.index];
      }
      out[c.index] = rows[c.index].diag * x[c.index] - off;
    }
  };

  std::vector<double> x(N, 0.0);
  std::vector<double> rhs(N, 0.0);
  std::vector<double> r(N, 0.0);
  std::vector<double> z(N, 0.0);
  std::vector<double> zPrev(N, 0.0);
  std::vector<double> p(N, 0.0);
  std::vector<double> Ap(N, 0.0);
  std::vector<double> candidateX(N, 0.0);
  std::vector<double> candidateR(N, 0.0);

  double res0 = 0.0;
  for (const ProjectionCell3D& c : cells) {
    rhs[c.index] = c.index == pinCell ? 0.0 : -rows[c.index].divergence;
    r[c.index] = rhs[c.index];
    res0 = std::max(res0, std::abs(r[c.index]));
  }
  localStats.initial_residual = res0;
  localStats.final_residual = res0;
  localStats.min_residual = res0;
  localStats.max_residual = res0;
  double absTol = std::max(0.0, config.absolute_tolerance);
  double relTol = std::max(0.0, config.relative_tolerance);
  double effectiveTol = std::max(absTol, relTol * res0);
  localStats.effective_tolerance = effectiveTol;
  recordResidualHistory(localStats, config, 0, res0);
  localStats.converged = res0 < effectiveTol;
  if (res0 >= effectiveTol) {
    auto applyPreconditioner = [&]() {
      for (const ProjectionCell3D& c : cells) {
        double d = rows[c.index].diag;
        z[c.index] = (config.use_jacobi_preconditioner && d > 0.0) ? r[c.index] / d : r[c.index];
      }
    };

    auto residualFromPressure = [&](const std::vector<double>& pressure,
                                    std::vector<double>& outResidual) {
      applyA(pressure, Ap);
      double res = 0.0;
      for (int i = 0; i < N; ++i) {
        outResidual[i] = rhs[i] - Ap[i];
        if (!std::isfinite(outResidual[i])) {
          return std::numeric_limits<double>::infinity();
        }
        res = std::max(res, std::abs(outResidual[i]));
      }
      return res;
    };

    double currentRes = res0;
    if (config.use_coarse_correction && currentRes >= effectiveTol) {
      std::vector<MRCellKey3D> activeKeys;
      std::vector<double> activeVolumes;
      activeKeys.reserve(cells.size());
      activeVolumes.reserve(cells.size());
      for (const ProjectionCell3D& c : cells) {
        activeKeys.push_back(c.key);
        activeVolumes.push_back(c.volume);
      }

      MRPressureAggregation3D aggregation = buildLevel1AggregationFromCells(activeKeys, activeVolumes);
      localStats.coarse_correction_cells = aggregation.coarseCount();
      localStats.coarse_correction_initial_residual = currentRes;
      localStats.coarse_correction_final_residual = currentRes;

      if (aggregation.coarseCount() > 0 && aggregation.coarseCount() < N) {
        std::vector<double> coarseRhs;
        restrictMRPressureVolumeWeighted3D(aggregation, r, coarseRhs);

        int coarsePin = pinCell >= 0
          ? aggregation.fine_to_coarse[static_cast<size_t>(pinCell)]
          : -1;
        std::vector<double> coarseX(coarseRhs.size(), 0.0);
        std::vector<double> coarseR = coarseRhs;
        std::vector<double> coarseP = coarseR;
        std::vector<double> coarseAp(coarseRhs.size(), 0.0);
        std::vector<double> fineP;
        std::vector<double> fineAp;
        std::vector<double> fineCorrection;

        if (coarsePin >= 0) {
          coarseR[static_cast<size_t>(coarsePin)] = 0.0;
          coarseP[static_cast<size_t>(coarsePin)] = 0.0;
        }

        auto coarseNorm = [&](const std::vector<double>& v) {
          double n2 = weightedDotVolumes(aggregation.coarse_volumes, v, v);
          return n2 > 0.0 ? std::sqrt(n2) : 0.0;
        };

        auto applyCoarse = [&](const std::vector<double>& in, std::vector<double>& out) {
          prolongMRPressurePiecewiseConstant3D(aggregation, in, fineP);
          applyA(fineP, fineAp);
          restrictMRPressureVolumeWeighted3D(aggregation, fineAp, out);
          if (coarsePin >= 0) {
            out[static_cast<size_t>(coarsePin)] = in[static_cast<size_t>(coarsePin)];
          }
        };

        double coarseRes0 = coarseNorm(coarseR);
        localStats.coarse_correction_effective_tolerance =
          std::max(config.coarse_correction_absolute_tolerance,
                   config.coarse_correction_relative_tolerance * coarseRes0);
        localStats.coarse_correction_converged =
          coarseRes0 <= localStats.coarse_correction_effective_tolerance;

        double rr = weightedDotVolumes(aggregation.coarse_volumes, coarseR, coarseR);
        if (!std::isfinite(rr)) {
          localStats.coarse_correction_breakdown = true;
        }

        for (int it = 0;
             !localStats.coarse_correction_converged &&
             !localStats.coarse_correction_breakdown &&
             it < config.coarse_correction_iterations;
             ++it) {
          applyCoarse(coarseP, coarseAp);
          double pAp = weightedDotVolumes(aggregation.coarse_volumes, coarseP, coarseAp);
          if (!std::isfinite(pAp) || std::abs(pAp) < 1e-30) {
            localStats.coarse_correction_breakdown = true;
            break;
          }

          double alpha = rr / pAp;
          if (!std::isfinite(alpha)) {
            localStats.coarse_correction_breakdown = true;
            break;
          }

          for (size_t i = 0; i < coarseX.size(); ++i) {
            coarseX[i] += alpha * coarseP[i];
            coarseR[i] -= alpha * coarseAp[i];
          }
          if (coarsePin >= 0) {
            coarseX[static_cast<size_t>(coarsePin)] = 0.0;
            coarseR[static_cast<size_t>(coarsePin)] = 0.0;
          }

          localStats.coarse_correction_iterations = it + 1;
          double coarseRes = coarseNorm(coarseR);
          if (!std::isfinite(coarseRes)) {
            localStats.coarse_correction_breakdown = true;
            break;
          }
          if (coarseRes <= localStats.coarse_correction_effective_tolerance) {
            localStats.coarse_correction_converged = true;
            break;
          }

          double rrNext = weightedDotVolumes(aggregation.coarse_volumes, coarseR, coarseR);
          if (!std::isfinite(rrNext) || std::abs(rr) < 1e-30) {
            localStats.coarse_correction_breakdown = true;
            break;
          }
          double beta = rrNext / rr;
          if (!std::isfinite(beta)) {
            localStats.coarse_correction_breakdown = true;
            break;
          }
          rr = rrNext;
          for (size_t i = 0; i < coarseP.size(); ++i) {
            coarseP[i] = coarseR[i] + beta * coarseP[i];
          }
          if (coarsePin >= 0) {
            coarseP[static_cast<size_t>(coarsePin)] = 0.0;
          }
        }

        if (!localStats.coarse_correction_breakdown) {
          prolongMRPressurePiecewiseConstant3D(aggregation, coarseX, fineCorrection);
          double bestRes = currentRes;
          std::vector<double> bestX;
          std::vector<double> bestR;
          for (double scale = 1.0; scale >= 1.0 / 64.0; scale *= 0.5) {
            candidateX = x;
            for (int i = 0; i < N; ++i) {
              candidateX[i] += scale * fineCorrection[static_cast<size_t>(i)];
            }

            double candidateRes = residualFromPressure(candidateX, candidateR);
            if (std::isfinite(candidateRes) && candidateRes <= bestRes) {
              bestRes = candidateRes;
              bestX = candidateX;
              bestR = candidateR;
            }
          }

          localStats.coarse_correction_final_residual = bestRes;
          if (bestRes < currentRes && !bestX.empty()) {
            x.swap(bestX);
            r.swap(bestR);
            currentRes = bestRes;
            localStats.final_residual = currentRes;
            localStats.min_residual = std::min(localStats.min_residual, currentRes);
            localStats.max_residual = std::max(localStats.max_residual, currentRes);
            localStats.coarse_correction_accepted = true;
          }
        }
      }
    }

    double relaxationOmega = std::max(0.0, config.relaxation_omega);
    double minRelaxationOmega = std::max(0.0, config.relaxation_min_omega);
    if (minRelaxationOmega > relaxationOmega) {
      minRelaxationOmega = relaxationOmega;
    }
    localStats.relaxation_final_omega = relaxationOmega;
    for (int sweep = 0;
         sweep < config.relaxation_sweeps && currentRes >= effectiveTol;
         ++sweep) {
      applyPreconditioner();
      double trialOmega = relaxationOmega;
      bool accepted = false;
      while (trialOmega >= minRelaxationOmega && trialOmega > 0.0) {
        candidateX = x;
        for (int i = 0; i < N; ++i) {
          candidateX[i] += trialOmega * z[i];
        }

        double candidateRes = residualFromPressure(candidateX, candidateR);
        if (std::isfinite(candidateRes) && candidateRes <= currentRes) {
          x.swap(candidateX);
          r.swap(candidateR);
          currentRes = candidateRes;
          localStats.final_residual = currentRes;
          localStats.min_residual = std::min(localStats.min_residual, currentRes);
          localStats.max_residual = std::max(localStats.max_residual, currentRes);
          relaxationOmega = trialOmega;
          localStats.relaxation_final_omega = relaxationOmega;
          ++localStats.relaxation_accepted;
          accepted = true;
          break;
        }

        ++localStats.relaxation_rejected;
        if (trialOmega <= minRelaxationOmega) {
          break;
        }
        trialOmega = std::max(minRelaxationOmega, trialOmega * 0.5);
      }

      if (!accepted) {
        break;
      }
    }
    localStats.converged = currentRes < effectiveTol;
    if (localStats.converged) {
      localStats.final_residual = currentRes;
    }
  }

  if (!localStats.converged && res0 >= effectiveTol) {
    auto applyPreconditioner = [&]() {
      for (const ProjectionCell3D& c : cells) {
        double d = rows[c.index].diag;
        z[c.index] = (config.use_jacobi_preconditioner && d > 0.0) ? r[c.index] / d : r[c.index];
      }
    };

    applyPreconditioner();
    for (const ProjectionCell3D& c : cells) {
      p[c.index] = z[c.index];
    }

    auto dot = [](const std::vector<double>& a, const std::vector<double>& b) {
      double s = 0.0;
      for (size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
      return s;
    };

    double rz = dot(r, z);
    if (!std::isfinite(rz)) {
      localStats.breakdown = true;
      localStats.final_residual = maxAbs(r);
    }
    double previousRes = localStats.final_residual;
    for (int it = 0; !localStats.breakdown && it < config.max_iterations; ++it) {
      applyA(p, Ap);
      double pAp = dot(p, Ap);
      if (!std::isfinite(pAp) || std::abs(pAp) < 1e-30) {
        localStats.breakdown = true;
        localStats.final_residual = maxAbs(r);
        break;
      }

      double alpha = rz / pAp;
      if (!std::isfinite(alpha)) {
        localStats.breakdown = true;
        localStats.final_residual = maxAbs(r);
        break;
      }
      double res = 0.0;
      bool finiteState = true;
      for (int i = 0; i < N; ++i) {
        x[i] += alpha * p[i];
        r[i] -= alpha * Ap[i];
        finiteState = finiteState && std::isfinite(x[i]) && std::isfinite(r[i]);
        if (std::isfinite(r[i])) {
          res = std::max(res, std::abs(r[i]));
        }
      }
      localStats.iterations = it + 1;
      localStats.final_residual = res;
      if (!finiteState || !std::isfinite(res)) {
        localStats.breakdown = true;
        localStats.final_residual = maxAbs(r);
        localStats.max_residual = std::numeric_limits<double>::infinity();
        break;
      }
      localStats.min_residual = std::min(localStats.min_residual, res);
      localStats.max_residual = std::max(localStats.max_residual, res);
      recordResidualHistory(localStats, config, it + 1, res);
      if (res < effectiveTol) {
        localStats.converged = true;
        break;
      }

      if (config.adaptive_restart &&
          config.restart_growth_threshold > 0.0 &&
          res > previousRes * config.restart_growth_threshold &&
          res > res0 * config.restart_growth_threshold &&
          it + 1 < config.max_iterations) {
        applyPreconditioner();
        rz = dot(r, z);
        if (!std::isfinite(rz)) {
          localStats.breakdown = true;
          localStats.final_residual = maxAbs(r);
          break;
        }
        for (int i = 0; i < N; ++i) {
          p[i] = z[i];
        }
        ++localStats.restarts;
        previousRes = res;
        continue;
      }
      previousRes = res;

      zPrev = z;
      applyPreconditioner();
      double rzNext = dot(r, z);
      if (!std::isfinite(rzNext)) {
        localStats.breakdown = true;
        localStats.final_residual = maxAbs(r);
        break;
      }
      double beta = 0.0;
      if (rz != 0.0) {
        if (config.use_flexible_cg_beta) {
          double flexNumerator = 0.0;
          for (int i = 0; i < N; ++i) {
            flexNumerator += r[i] * (z[i] - zPrev[i]);
          }
          beta = flexNumerator / rz;
        } else {
          beta = rzNext / rz;
        }
      }
      if (!std::isfinite(beta)) {
        beta = 0.0;
        ++localStats.beta_resets;
      }
      if (beta < 0.0) {
        beta = 0.0;
        ++localStats.beta_resets;
      }
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

  for (const MRFaceKey3D& f : g.uFaceRefs()) {
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

  for (const MRFaceKey3D& f : g.vFaceRefs()) {
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

  for (const MRFaceKey3D& f : g.wFaceRefs()) {
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

  if (stats) *stats = localStats;
}
