#include "driver/interface_diagnostics3d.h"

#include "driver/sparse_ops3d_common.h"
#include "math/vec3.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace {

constexpr double kInterfacePhiLo = 0.05;
constexpr double kInterfacePhiHi = 0.95;
constexpr double kGradientThreshold = 1e-5;
constexpr double kNormalEps = 1e-12;
constexpr double kPi = 3.14159265358979323846;

int clampInt(int v, int lo, int hi) {
  return std::max(lo, std::min(hi, v));
}

bool finiteValue(double v) {
  return std::isfinite(v);
}

void accumulate(InterfaceDiagnostics3D& stats, double phi, double gradMag, double curvature) {
  if (!finiteValue(phi) || !finiteValue(gradMag) || !finiteValue(curvature)) {
    stats.finite = 0;
    return;
  }

  if (stats.sample_cells == 0) {
    stats.phi_min = phi;
    stats.phi_max = phi;
  } else {
    stats.phi_min = std::min(stats.phi_min, phi);
    stats.phi_max = std::max(stats.phi_max, phi);
  }

  ++stats.sample_cells;
  stats.phi_mean += phi;

  const bool interfaceCell = phi > kInterfacePhiLo && phi < kInterfacePhiHi;
  if (!interfaceCell) return;

  ++stats.interface_cells;
  stats.grad_mean += gradMag;
  stats.grad_max = std::max(stats.grad_max, gradMag);

  const double absCurvature = std::abs(curvature);
  stats.curvature_abs_mean += absCurvature;
  stats.curvature_abs_max = std::max(stats.curvature_abs_max, absCurvature);
}

void finishStats(InterfaceDiagnostics3D& stats) {
  if (stats.sample_cells > 0) {
    stats.phi_mean /= static_cast<double>(stats.sample_cells);
  }
  if (stats.interface_cells > 0) {
    stats.grad_mean /= static_cast<double>(stats.interface_cells);
    stats.curvature_abs_mean /= static_cast<double>(stats.interface_cells);
  }
  stats.surface_tension_candidate =
    stats.finite && stats.interface_cells > 0 && stats.grad_max > kGradientThreshold;
}

bool interfacePhi(double phi) {
  return phi > kInterfacePhiLo && phi < kInterfacePhiHi;
}

Vec3 limitedDelta(Vec3 delta, double maxDeltaSpeed) {
  const double mag = delta.length();
  if (!finiteValue(mag)) return {};
  if (maxDeltaSpeed > 0.0 && mag > maxDeltaSpeed) {
    return delta * (maxDeltaSpeed / mag);
  }
  return delta;
}

double capillaryDtLimit(const PhaseParams& phase, double dx, double strength) {
  if (dx <= 0.0 || strength <= 0.0) return 0.0;
  const double rhoMin = std::min(phase.rho_l, phase.rho_g);
  if (rhoMin <= 0.0 || !finiteValue(rhoMin)) return 0.0;
  return std::sqrt((rhoMin * dx * dx * dx) / (2.0 * kPi * strength));
}

void initSurfaceStats(SurfaceTensionStats3D& stats,
                      const PhaseParams& phase,
                      double dx,
                      double dt,
                      double strength,
                      double maxDeltaSpeed,
                      int curvatureSmoothingRadius) {
  stats.enabled = strength > 0.0 && dt > 0.0;
  stats.strength = strength;
  stats.max_delta_speed_limit = maxDeltaSpeed;
  stats.curvature_smoothing_radius = clampInt(curvatureSmoothingRadius, 0, 3);
  stats.capillary_dt_limit = capillaryDtLimit(phase, dx, strength);
  stats.capillary_stable =
    !stats.enabled ||
    stats.capillary_dt_limit <= 0.0 ||
    dt <= stats.capillary_dt_limit + 1e-12;
}

void accumulateSurfaceStats(SurfaceTensionStats3D& stats,
                            const Vec3& delta,
                            double rawCurvature,
                            double smoothedCurvature) {
  const double mag = delta.length();
  if (!finiteValue(mag) ||
      !finiteValue(rawCurvature) ||
      !finiteValue(smoothedCurvature)) {
    stats.finite = 0;
    return;
  }
  ++stats.applied_cells;
  stats.mean_delta_speed += mag;
  stats.max_delta_speed = std::max(stats.max_delta_speed, mag);

  const double rawAbs = std::abs(rawCurvature);
  const double smoothedAbs = std::abs(smoothedCurvature);
  stats.raw_curvature_abs_mean += rawAbs;
  stats.raw_curvature_abs_max = std::max(stats.raw_curvature_abs_max, rawAbs);
  stats.smoothed_curvature_abs_mean += smoothedAbs;
  stats.smoothed_curvature_abs_max = std::max(stats.smoothed_curvature_abs_max, smoothedAbs);
}

void finishSurfaceStats(SurfaceTensionStats3D& stats) {
  if (stats.applied_cells > 0) {
    const double denom = static_cast<double>(stats.applied_cells);
    stats.mean_delta_speed /= denom;
    stats.raw_curvature_abs_mean /= denom;
    stats.smoothed_curvature_abs_mean /= denom;
  }
}

double sparseCellPhi(const SparseMacGrid3D<4>& g, const PhaseParams& phase,
                     int i, int j, int k) {
  if (!g.inBounds(i, j, k)) return 0.0;
  double sum = 0.0;
  sum += phiFromRawDensity(g.gmu(i, j, k), phase);
  sum += phiFromRawDensity(g.gmu(i + 1, j, k), phase);
  sum += phiFromRawDensity(g.gmv(i, j, k), phase);
  sum += phiFromRawDensity(g.gmv(i, j + 1, k), phase);
  sum += phiFromRawDensity(g.gmw(i, j, k), phase);
  sum += phiFromRawDensity(g.gmw(i, j, k + 1), phase);
  return sum / 6.0;
}

double sparsePhiClamped(const SparseMacGrid3D<4>& g, const PhaseParams& phase,
                        int i, int j, int k) {
  i = clampInt(i, 0, g.nx - 1);
  j = clampInt(j, 0, g.ny - 1);
  k = clampInt(k, 0, g.nz - 1);
  return sparseCellPhi(g, phase, i, j, k);
}

Vec3 sparseGradient(const SparseMacGrid3D<4>& g, const PhaseParams& phase,
                    int i, int j, int k) {
  const int im = clampInt(i - 1, 0, g.nx - 1);
  const int ip = clampInt(i + 1, 0, g.nx - 1);
  const int jm = clampInt(j - 1, 0, g.ny - 1);
  const int jp = clampInt(j + 1, 0, g.ny - 1);
  const int km = clampInt(k - 1, 0, g.nz - 1);
  const int kp = clampInt(k + 1, 0, g.nz - 1);
  const double dx = g.dx;
  return {
    (sparsePhiClamped(g, phase, ip, j, k) - sparsePhiClamped(g, phase, im, j, k)) /
      (std::max(1, ip - im) * dx),
    (sparsePhiClamped(g, phase, i, jp, k) - sparsePhiClamped(g, phase, i, jm, k)) /
      (std::max(1, jp - jm) * dx),
    (sparsePhiClamped(g, phase, i, j, kp) - sparsePhiClamped(g, phase, i, j, km)) /
      (std::max(1, kp - km) * dx)
  };
}

Vec3 normalizeGradient(const Vec3& grad) {
  const double mag = grad.length();
  if (mag <= kNormalEps || !finiteValue(mag)) return {};
  return grad * (1.0 / mag);
}

Vec3 sparseNormal(const SparseMacGrid3D<4>& g, const PhaseParams& phase,
                  int i, int j, int k) {
  return normalizeGradient(sparseGradient(g, phase, i, j, k));
}

double sparseCurvature(const SparseMacGrid3D<4>& g, const PhaseParams& phase,
                       int i, int j, int k) {
  const int im = clampInt(i - 1, 0, g.nx - 1);
  const int ip = clampInt(i + 1, 0, g.nx - 1);
  const int jm = clampInt(j - 1, 0, g.ny - 1);
  const int jp = clampInt(j + 1, 0, g.ny - 1);
  const int km = clampInt(k - 1, 0, g.nz - 1);
  const int kp = clampInt(k + 1, 0, g.nz - 1);
  const double dx = g.dx;

  const Vec3 nxm = sparseNormal(g, phase, im, j, k);
  const Vec3 nxp = sparseNormal(g, phase, ip, j, k);
  const Vec3 nym = sparseNormal(g, phase, i, jm, k);
  const Vec3 nyp = sparseNormal(g, phase, i, jp, k);
  const Vec3 nzm = sparseNormal(g, phase, i, j, km);
  const Vec3 nzp = sparseNormal(g, phase, i, j, kp);

  return (nxp.x - nxm.x) / (std::max(1, ip - im) * dx) +
         (nyp.y - nym.y) / (std::max(1, jp - jm) * dx) +
         (nzp.z - nzm.z) / (std::max(1, kp - km) * dx);
}

double sparseSmoothedCurvature(const SparseMacGrid3D<4>& g,
                               const PhaseParams& phase,
                               int i,
                               int j,
                               int k,
                               double rawCurvature,
                               int radius) {
  if (radius <= 0 || !finiteValue(rawCurvature)) return rawCurvature;

  double sum = 0.0;
  int count = 0;
  for (int dz = -radius; dz <= radius; ++dz) {
    for (int dy = -radius; dy <= radius; ++dy) {
      for (int dx = -radius; dx <= radius; ++dx) {
        const int ni = clampInt(i + dx, 0, g.nx - 1);
        const int nj = clampInt(j + dy, 0, g.ny - 1);
        const int nk = clampInt(k + dz, 0, g.nz - 1);
        if (!interfacePhi(sparseCellPhi(g, phase, ni, nj, nk))) continue;
        const double curvature = sparseCurvature(g, phase, ni, nj, nk);
        if (!finiteValue(curvature)) continue;
        sum += curvature;
        ++count;
      }
    }
  }
  return count > 0 ? sum / static_cast<double>(count) : rawCurvature;
}

double mrFacePhi(const MRMacGrid3D<4>& g, const PhaseParams& phase,
                 int axis, int x, int y, int z) {
  if (axis == 0) {
    if (x < 0 || x > g.layout.nx || y < 0 || y >= g.layout.ny || z < 0 || z >= g.layout.nz) return 0.0;
    return phiFromRawDensity(g.gmu(MRFaceKey3D{0, x, y, z, 1, 1}), phase);
  }
  if (axis == 1) {
    if (x < 0 || x >= g.layout.nx || y < 0 || y > g.layout.ny || z < 0 || z >= g.layout.nz) return 0.0;
    return phiFromRawDensity(g.gmv(MRFaceKey3D{1, x, y, z, 1, 1}), phase);
  }
  if (x < 0 || x >= g.layout.nx || y < 0 || y >= g.layout.ny || z < 0 || z > g.layout.nz) return 0.0;
  return phiFromRawDensity(g.gmw(MRFaceKey3D{2, x, y, z, 1, 1}), phase);
}

double mrCellPhiFine(const MRMacGrid3D<4>& g, const PhaseParams& phase,
                     int i, int j, int k) {
  if (i < 0 || i >= g.layout.nx ||
      j < 0 || j >= g.layout.ny ||
      k < 0 || k >= g.layout.nz) {
    return 0.0;
  }
  double sum = 0.0;
  sum += mrFacePhi(g, phase, 0, i, j, k);
  sum += mrFacePhi(g, phase, 0, i + 1, j, k);
  sum += mrFacePhi(g, phase, 1, i, j, k);
  sum += mrFacePhi(g, phase, 1, i, j + 1, k);
  sum += mrFacePhi(g, phase, 2, i, j, k);
  sum += mrFacePhi(g, phase, 2, i, j, k + 1);
  return sum / 6.0;
}

double mrPhiClamped(const MRMacGrid3D<4>& g, const PhaseParams& phase,
                    int i, int j, int k) {
  i = clampInt(i, 0, g.layout.nx - 1);
  j = clampInt(j, 0, g.layout.ny - 1);
  k = clampInt(k, 0, g.layout.nz - 1);
  return mrCellPhiFine(g, phase, i, j, k);
}

Vec3 mrGradient(const MRMacGrid3D<4>& g, const PhaseParams& phase,
                int i, int j, int k) {
  const int im = clampInt(i - 1, 0, g.layout.nx - 1);
  const int ip = clampInt(i + 1, 0, g.layout.nx - 1);
  const int jm = clampInt(j - 1, 0, g.layout.ny - 1);
  const int jp = clampInt(j + 1, 0, g.layout.ny - 1);
  const int km = clampInt(k - 1, 0, g.layout.nz - 1);
  const int kp = clampInt(k + 1, 0, g.layout.nz - 1);
  const double dx = g.layout.dx;
  return {
    (mrPhiClamped(g, phase, ip, j, k) - mrPhiClamped(g, phase, im, j, k)) /
      (std::max(1, ip - im) * dx),
    (mrPhiClamped(g, phase, i, jp, k) - mrPhiClamped(g, phase, i, jm, k)) /
      (std::max(1, jp - jm) * dx),
    (mrPhiClamped(g, phase, i, j, kp) - mrPhiClamped(g, phase, i, j, km)) /
      (std::max(1, kp - km) * dx)
  };
}

Vec3 mrNormal(const MRMacGrid3D<4>& g, const PhaseParams& phase,
              int i, int j, int k) {
  return normalizeGradient(mrGradient(g, phase, i, j, k));
}

double mrCurvature(const MRMacGrid3D<4>& g, const PhaseParams& phase,
                   int i, int j, int k) {
  const int im = clampInt(i - 1, 0, g.layout.nx - 1);
  const int ip = clampInt(i + 1, 0, g.layout.nx - 1);
  const int jm = clampInt(j - 1, 0, g.layout.ny - 1);
  const int jp = clampInt(j + 1, 0, g.layout.ny - 1);
  const int km = clampInt(k - 1, 0, g.layout.nz - 1);
  const int kp = clampInt(k + 1, 0, g.layout.nz - 1);
  const double dx = g.layout.dx;

  const Vec3 nxm = mrNormal(g, phase, im, j, k);
  const Vec3 nxp = mrNormal(g, phase, ip, j, k);
  const Vec3 nym = mrNormal(g, phase, i, jm, k);
  const Vec3 nyp = mrNormal(g, phase, i, jp, k);
  const Vec3 nzm = mrNormal(g, phase, i, j, km);
  const Vec3 nzp = mrNormal(g, phase, i, j, kp);

  return (nxp.x - nxm.x) / (std::max(1, ip - im) * dx) +
         (nyp.y - nym.y) / (std::max(1, jp - jm) * dx) +
         (nzp.z - nzm.z) / (std::max(1, kp - km) * dx);
}

double mrSmoothedCurvature(const MRMacGrid3D<4>& g,
                           const PhaseParams& phase,
                           int i,
                           int j,
                           int k,
                           double rawCurvature,
                           int radius) {
  if (radius <= 0 || !finiteValue(rawCurvature)) return rawCurvature;

  double sum = 0.0;
  int count = 0;
  for (int dz = -radius; dz <= radius; ++dz) {
    for (int dy = -radius; dy <= radius; ++dy) {
      for (int dx = -radius; dx <= radius; ++dx) {
        const int ni = clampInt(i + dx, 0, g.layout.nx - 1);
        const int nj = clampInt(j + dy, 0, g.layout.ny - 1);
        const int nk = clampInt(k + dz, 0, g.layout.nz - 1);
        if (!interfacePhi(mrCellPhiFine(g, phase, ni, nj, nk))) continue;
        const double curvature = mrCurvature(g, phase, ni, nj, nk);
        if (!finiteValue(curvature)) continue;
        sum += curvature;
        ++count;
      }
    }
  }
  return count > 0 ? sum / static_cast<double>(count) : rawCurvature;
}

void mrCellFineCenter(const MRCellKey3D& c, int& i, int& j, int& k) {
  const int step = 1 << c.block.level;
  const int x0 = c.block.bx * 4 * step + c.lx * step;
  const int y0 = c.block.by * 4 * step + c.ly * step;
  const int z0 = c.block.bz * 4 * step + c.lz * step;
  i = x0 + step / 2;
  j = y0 + step / 2;
  k = z0 + step / 2;
}

} // namespace

InterfaceDiagnostics3D diagnoseSparseInterface3D(const SparseMacGrid3D<4>& g,
                                                 const PhaseParams& phase) {
  InterfaceDiagnostics3D stats;
  const std::vector<int> cells = sparse3d::collectCellsWithMarker(g, 1);
  for (int c : cells) {
    const int i = c % g.nx;
    const int q = c / g.nx;
    const int j = q % g.ny;
    const int k = q / g.ny;
    const double phi = sparseCellPhi(g, phase, i, j, k);
    const Vec3 grad = sparseGradient(g, phase, i, j, k);
    const double curvature = sparseCurvature(g, phase, i, j, k);
    accumulate(stats, phi, grad.length(), curvature);
  }
  finishStats(stats);
  return stats;
}

InterfaceDiagnostics3D diagnoseMRInterface3D(const MRMacGrid3D<4>& g,
                                             const PhaseParams& phase) {
  InterfaceDiagnostics3D stats;
  for (const MRCellKey3D& c : g.marker.leafCells()) {
    const int marker = static_cast<int>(g.marker.get(c) + 0.5f);
    if (marker != 1) continue;

    int i = 0;
    int j = 0;
    int k = 0;
    mrCellFineCenter(c, i, j, k);
    i = clampInt(i, 0, g.layout.nx - 1);
    j = clampInt(j, 0, g.layout.ny - 1);
    k = clampInt(k, 0, g.layout.nz - 1);

    const double phi = mrCellPhiFine(g, phase, i, j, k);
    const Vec3 grad = mrGradient(g, phase, i, j, k);
    const double curvature = mrCurvature(g, phase, i, j, k);
    accumulate(stats, phi, grad.length(), curvature);
  }
  finishStats(stats);
  return stats;
}

SurfaceTensionStats3D applySparseSurfaceTension3D(SparseMacGrid3D<4>& g,
                                                  const PhaseParams& phase,
                                                  double dt,
                                                  double strength,
                                                  double maxDeltaSpeed,
                                                  int curvatureSmoothingRadius) {
  SurfaceTensionStats3D stats;
  initSurfaceStats(stats, phase, g.dx, dt, strength, maxDeltaSpeed,
                   curvatureSmoothingRadius);
  if (!stats.enabled) return stats;

  const int smoothingRadius = stats.curvature_smoothing_radius;
  const std::vector<int> cells = sparse3d::collectCellsWithMarker(g, 1);
  for (int c : cells) {
    const int i = c % g.nx;
    const int q = c / g.nx;
    const int j = q % g.ny;
    const int k = q / g.ny;
    const double phi = sparseCellPhi(g, phase, i, j, k);
    if (!interfacePhi(phi)) continue;

    const Vec3 grad = sparseGradient(g, phase, i, j, k);
    const double gradMag = grad.length();
    if (gradMag <= kGradientThreshold) continue;

    const double rawCurvature = sparseCurvature(g, phase, i, j, k);
    const double smoothedCurvature =
      sparseSmoothedCurvature(g, phase, i, j, k, rawCurvature, smoothingRadius);
    Vec3 delta = limitedDelta(grad * (-strength * smoothedCurvature * dt), maxDeltaSpeed);
    accumulateSurfaceStats(stats, delta, rawCurvature, smoothedCurvature);
    if (!stats.finite) continue;

    if (g.gmu(i, j, k) > 0.0f) g.u(i, j, k) += static_cast<float>(0.5 * delta.x);
    if (g.gmu(i + 1, j, k) > 0.0f) g.u(i + 1, j, k) += static_cast<float>(0.5 * delta.x);
    if (g.gmv(i, j, k) > 0.0f) g.v(i, j, k) += static_cast<float>(0.5 * delta.y);
    if (g.gmv(i, j + 1, k) > 0.0f) g.v(i, j + 1, k) += static_cast<float>(0.5 * delta.y);
    if (g.gmw(i, j, k) > 0.0f) g.w(i, j, k) += static_cast<float>(0.5 * delta.z);
    if (g.gmw(i, j, k + 1) > 0.0f) g.w(i, j, k + 1) += static_cast<float>(0.5 * delta.z);
  }
  finishSurfaceStats(stats);
  return stats;
}

SurfaceTensionStats3D applyMRSurfaceTension3D(MRMacGrid3D<4>& g,
                                              const PhaseParams& phase,
                                              double dt,
                                              double strength,
                                              double maxDeltaSpeed,
                                              int curvatureSmoothingRadius) {
  SurfaceTensionStats3D stats;
  initSurfaceStats(stats, phase, g.layout.dx, dt, strength, maxDeltaSpeed,
                   curvatureSmoothingRadius);
  if (!stats.enabled) return stats;

  const int smoothingRadius = stats.curvature_smoothing_radius;
  for (const MRCellKey3D& c : g.marker.leafCells()) {
    const int marker = static_cast<int>(g.marker.get(c) + 0.5f);
    if (marker != 1) continue;

    int i = 0;
    int j = 0;
    int k = 0;
    mrCellFineCenter(c, i, j, k);
    i = clampInt(i, 0, g.layout.nx - 1);
    j = clampInt(j, 0, g.layout.ny - 1);
    k = clampInt(k, 0, g.layout.nz - 1);

    const double phi = mrCellPhiFine(g, phase, i, j, k);
    if (!interfacePhi(phi)) continue;

    const Vec3 grad = mrGradient(g, phase, i, j, k);
    const double gradMag = grad.length();
    if (gradMag <= kGradientThreshold) continue;

    const double rawCurvature = mrCurvature(g, phase, i, j, k);
    const double smoothedCurvature =
      mrSmoothedCurvature(g, phase, i, j, k, rawCurvature, smoothingRadius);
    Vec3 delta = limitedDelta(grad * (-strength * smoothedCurvature * dt), maxDeltaSpeed);
    accumulateSurfaceStats(stats, delta, rawCurvature, smoothedCurvature);
    if (!stats.finite) continue;

    const MRFaceKey3D u0{0, i, j, k, 1, 1};
    const MRFaceKey3D u1{0, i + 1, j, k, 1, 1};
    const MRFaceKey3D v0{1, i, j, k, 1, 1};
    const MRFaceKey3D v1{1, i, j + 1, k, 1, 1};
    const MRFaceKey3D w0{2, i, j, k, 1, 1};
    const MRFaceKey3D w1{2, i, j, k + 1, 1, 1};
    if (g.gmu(u0) > 0.0f) g.u(u0) += static_cast<float>(0.5 * delta.x);
    if (g.gmu(u1) > 0.0f) g.u(u1) += static_cast<float>(0.5 * delta.x);
    if (g.gmv(v0) > 0.0f) g.v(v0) += static_cast<float>(0.5 * delta.y);
    if (g.gmv(v1) > 0.0f) g.v(v1) += static_cast<float>(0.5 * delta.y);
    if (g.gmw(w0) > 0.0f) g.w(w0) += static_cast<float>(0.5 * delta.z);
    if (g.gmw(w1) > 0.0f) g.w(w1) += static_cast<float>(0.5 * delta.z);
  }
  finishSurfaceStats(stats);
  return stats;
}
