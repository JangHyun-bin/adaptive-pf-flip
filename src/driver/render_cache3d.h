#pragma once

#include "driver/multires_sim3d_tp.h"
#include "driver/sparse_sim3d_tp.h"
#include "math/vec3.h"
#include "physics/phasefield.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct RenderCacheCamera3D {
  Vec3 position;
  Vec3 target;
  Vec3 up;
  double fov_degrees = 45.0;
  double near_clip = 0.1;
  double far_clip = 1000.0;
  double focal_length_mm = 50.0;
};

struct RenderCacheCell3D {
  int i = 0;
  int j = 0;
  int k = 0;
  int level = 0;
  int marker = 0;
  double phi = 0.0;
  double liquid_volume = 0.0;
};

struct RenderCacheManifestFrame3D {
  int frame = 0;
  int step = 0;
  double time = 0.0;
  std::string path;
  long long bytes = 0;
};

inline RenderCacheCamera3D defaultRenderCacheCamera3D(int nx, int ny, int nz, double dx) {
  const double cx = 0.5 * nx * dx;
  const double cy = 0.5 * ny * dx;
  const double cz = 0.5 * nz * dx;
  const double span = std::max({nx * dx, ny * dx, nz * dx, dx});
  return {
    Vec3{cx, cy + 0.2 * span, cz + 2.0 * span},
    Vec3{cx, cy, cz},
    Vec3{0.0, 1.0, 0.0},
    45.0,
    0.05 * dx,
    5.0 * span,
    50.0
  };
}

namespace render_cache3d_detail {

constexpr int kCacheSchemaVersion = 2;
constexpr const char* kWorldUnits = "cell";

struct Bounds3D {
  Vec3 min;
  Vec3 max;
  bool valid = false;
};

inline bool finiteVec(const Vec3& v) {
  return std::isfinite(v.x) && std::isfinite(v.y) && std::isfinite(v.z);
}

inline Bounds3D emptyBounds() {
  const double inf = std::numeric_limits<double>::infinity();
  return Bounds3D{Vec3{inf, inf, inf}, Vec3{-inf, -inf, -inf}, false};
}

inline Bounds3D domainBounds(int nx, int ny, int nz, double dx) {
  return Bounds3D{
    Vec3{0.0, 0.0, 0.0},
    Vec3{nx * dx, ny * dx, nz * dx},
    true
  };
}

inline void includePoint(Bounds3D& bounds, const Vec3& p) {
  if (!finiteVec(p)) return;
  if (!bounds.valid) {
    bounds.min = p;
    bounds.max = p;
    bounds.valid = true;
    return;
  }
  bounds.min.x = std::min(bounds.min.x, p.x);
  bounds.min.y = std::min(bounds.min.y, p.y);
  bounds.min.z = std::min(bounds.min.z, p.z);
  bounds.max.x = std::max(bounds.max.x, p.x);
  bounds.max.y = std::max(bounds.max.y, p.y);
  bounds.max.z = std::max(bounds.max.z, p.z);
}

inline void includeBox(Bounds3D& bounds, const Vec3& lo, const Vec3& hi) {
  includePoint(bounds, lo);
  includePoint(bounds, hi);
}

inline void requireValidPath(const std::string& path) {
  if (path.empty()) {
    throw std::runtime_error("render cache path is empty");
  }
}

inline void writeJsonString(std::ostream& out, const std::string& text) {
  static const char* hex = "0123456789abcdef";
  out << '"';
  for (unsigned char c : text) {
    switch (c) {
      case '"': out << "\\\""; break;
      case '\\': out << "\\\\"; break;
      case '\b': out << "\\b"; break;
      case '\f': out << "\\f"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default:
        if (c < 0x20) {
          out << "\\u00" << hex[(c >> 4) & 0x0f] << hex[c & 0x0f];
        } else {
          out << static_cast<char>(c);
        }
        break;
    }
  }
  out << '"';
}

inline void requireManifestArgs(const char* simKind,
                                int nx,
                                int ny,
                                int nz,
                                double dx,
                                const std::vector<RenderCacheManifestFrame3D>& frames) {
  if (!simKind || simKind[0] == '\0' ||
      nx <= 0 || ny <= 0 || nz <= 0 ||
      dx <= 0.0 || !std::isfinite(dx)) {
    throw std::invalid_argument("invalid render cache manifest metadata");
  }
  for (const RenderCacheManifestFrame3D& f : frames) {
    if (f.frame < 0 || f.step < 0 || f.path.empty() || f.bytes < 0 ||
        !std::isfinite(f.time)) {
      throw std::invalid_argument("invalid render cache manifest frame");
    }
  }
}

inline void writeVec3(std::ostream& out, const char* key, const Vec3& v) {
  out << "\"" << key << "\":[" << v.x << "," << v.y << "," << v.z << "]";
}

inline void writeBounds(std::ostream& out,
                        const char* minKey,
                        const char* maxKey,
                        const Bounds3D& bounds,
                        const Bounds3D& fallback) {
  const Bounds3D& b = bounds.valid ? bounds : fallback;
  writeVec3(out, minKey, b.min);
  out << ",";
  writeVec3(out, maxKey, b.max);
}

inline const char* particlePhaseName(unsigned char type) {
  return type == 0 ? "liquid" : "gas";
}

inline size_t particleCountByType(const Particles3DTP& ps, unsigned char type) {
  size_t count = 0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) ++count;
  }
  return count;
}

inline double particleVolume(const Particles3DTP& ps, size_t p, double volumeScale) {
  return p < ps.volume.size() ? ps.volume[p] * volumeScale : volumeScale;
}

inline double particleVolumeByType(const Particles3DTP& ps,
                                   unsigned char type,
                                   double volumeScale) {
  double volume = 0.0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) volume += particleVolume(ps, i, volumeScale);
  }
  return volume;
}

inline double secondaryVolume(const Particles3DTP& ps, double volumeScale) {
  double volume = 0.0;
  for (size_t i = 0; i < ps.size(); ++i) {
    volume += particleVolume(ps, i, volumeScale);
  }
  return volume;
}

inline std::pair<int, int> secondaryAgeRange(const Particles3DTP& ps,
                                             const std::vector<int>& ages) {
  if (ps.size() == 0) return {0, 0};
  int minAge = std::numeric_limits<int>::max();
  int maxAge = 0;
  for (size_t i = 0; i < ps.size(); ++i) {
    const int age = i < ages.size() ? std::max(0, ages[i]) : 0;
    minAge = std::min(minAge, age);
    maxAge = std::max(maxAge, age);
  }
  return {minAge == std::numeric_limits<int>::max() ? 0 : minAge, maxAge};
}

inline Bounds3D particleBounds(const Particles3DTP& ps, int phaseFilter = -1) {
  Bounds3D bounds = emptyBounds();
  for (size_t i = 0; i < ps.size(); ++i) {
    if (phaseFilter >= 0 && ps.type[i] != static_cast<unsigned char>(phaseFilter)) continue;
    includePoint(bounds, ps.pos[i]);
  }
  return bounds;
}

inline Bounds3D secondaryBounds(const Particles3DTP& droplets,
                                const Particles3DTP& bubbles) {
  Bounds3D bounds = emptyBounds();
  for (size_t i = 0; i < droplets.size(); ++i) includePoint(bounds, droplets.pos[i]);
  for (size_t i = 0; i < bubbles.size(); ++i) includePoint(bounds, bubbles.pos[i]);
  return bounds;
}

inline Bounds3D waterBounds(const std::vector<RenderCacheCell3D>& cells,
                            const Particles3DTP& primary,
                            double dx) {
  Bounds3D bounds = particleBounds(primary, 0);
  for (const RenderCacheCell3D& c : cells) {
    if (c.phi <= 0.0 && c.liquid_volume <= 0.0) continue;
    const int step = 1 << std::max(0, c.level);
    includeBox(bounds,
               Vec3{c.i * dx, c.j * dx, c.k * dx},
               Vec3{(c.i + step) * dx, (c.j + step) * dx, (c.k + step) * dx});
  }
  return bounds;
}

inline double sparseFacePhi(const SparseMacGrid3D<4>& g,
                            const PhaseParams& phase,
                            int axis,
                            int i,
                            int j,
                            int k) {
  if (axis == 0) return phiFromRawDensity(g.gmu(i, j, k), phase);
  if (axis == 1) return phiFromRawDensity(g.gmv(i, j, k), phase);
  return phiFromRawDensity(g.gmw(i, j, k), phase);
}

inline double sparseCellPhi(const SparseMacGrid3D<4>& g,
                            const PhaseParams& phase,
                            int i,
                            int j,
                            int k) {
  double sum = 0.0;
  sum += sparseFacePhi(g, phase, 0, i, j, k);
  sum += sparseFacePhi(g, phase, 0, i + 1, j, k);
  sum += sparseFacePhi(g, phase, 1, i, j, k);
  sum += sparseFacePhi(g, phase, 1, i, j + 1, k);
  sum += sparseFacePhi(g, phase, 2, i, j, k);
  sum += sparseFacePhi(g, phase, 2, i, j, k + 1);
  return sum / 6.0;
}

inline double mrFacePhi(const MRMacGrid3D<4>& g,
                        const PhaseParams& phase,
                        int axis,
                        int x,
                        int y,
                        int z) {
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

inline double mrCellPhi(const MRMacGrid3D<4>& g,
                        const PhaseParams& phase,
                        int i,
                        int j,
                        int k) {
  double sum = 0.0;
  sum += mrFacePhi(g, phase, 0, i, j, k);
  sum += mrFacePhi(g, phase, 0, i + 1, j, k);
  sum += mrFacePhi(g, phase, 1, i, j, k);
  sum += mrFacePhi(g, phase, 1, i, j + 1, k);
  sum += mrFacePhi(g, phase, 2, i, j, k);
  sum += mrFacePhi(g, phase, 2, i, j, k + 1);
  return sum / 6.0;
}

inline void writeHeader(std::ostream& out,
                        const char* simKind,
                        int nx,
                        int ny,
                        int nz,
                        double dx,
                        double dt,
                        int frame,
                        double time,
                        const PhaseParams& phase,
                        const RenderCacheCamera3D& camera) {
  if (nx <= 0 || ny <= 0 || nz <= 0 || dx <= 0.0 || !std::isfinite(dx) ||
      !std::isfinite(dt) || !std::isfinite(time) ||
      !finiteVec(camera.position) || !finiteVec(camera.target) || !finiteVec(camera.up) ||
      camera.fov_degrees <= 0.0 || !std::isfinite(camera.fov_degrees) ||
      camera.near_clip <= 0.0 || camera.far_clip <= camera.near_clip ||
      !std::isfinite(camera.near_clip) || !std::isfinite(camera.far_clip) ||
      camera.focal_length_mm <= 0.0 || !std::isfinite(camera.focal_length_mm)) {
    throw std::invalid_argument("invalid render cache metadata");
  }
  const Bounds3D domain = domainBounds(nx, ny, nz, dx);
  const double shutterClose = time + std::max(0.0, dt);

  out << "{\"section\":\"header\",\"lsfs_cache3d_version\":1"
      << ",\"cache_schema_version\":" << kCacheSchemaVersion
      << ",\"sim_kind\":\"" << simKind << "\""
      << ",\"frame\":" << frame
      << ",\"time\":" << time
      << ",\"dt\":" << dt
      << ",\"dims\":[" << nx << "," << ny << "," << nz << "]"
      << ",\"dx\":" << dx
      << ",\"world_units\":\"" << kWorldUnits << "\""
      << ",\"shutter_open\":" << time
      << ",\"shutter_close\":" << shutterClose
      << ",\"frame_bounds_min\":[" << domain.min.x << "," << domain.min.y << "," << domain.min.z << "]"
      << ",\"frame_bounds_max\":[" << domain.max.x << "," << domain.max.y << "," << domain.max.z << "]"
      << ",\"phase\":{\"rho_l\":" << phase.rho_l
      << ",\"rho_g\":" << phase.rho_g
      << ",\"alpha_phi\":" << phase.alpha_phi
      << ",\"rho_tilde_0\":" << phase.rho_tilde_0 << "}}\n";

  out << "{\"section\":\"camera\",";
  writeVec3(out, "position", camera.position);
  out << ",";
  writeVec3(out, "target", camera.target);
  out << ",";
  writeVec3(out, "up", camera.up);
  out << ",\"fov_degrees\":" << camera.fov_degrees
      << ",\"vertical_fov_degrees\":" << camera.fov_degrees
      << ",\"near_clip\":" << camera.near_clip
      << ",\"far_clip\":" << camera.far_clip
      << ",\"focal_length_mm\":" << camera.focal_length_mm << "}\n";
}

inline void writeWaterSummary(std::ostream& out,
                              const Particles3DTP& primary,
                              const Particles3DTP& droplets,
                              const Particles3DTP& bubbles,
                              const std::vector<int>& dropletAges,
                              const std::vector<int>& bubbleAges,
                              double volumeScale,
                              double phaseFieldLiquidVolume,
                              size_t phaseFieldCells) {
  const std::pair<int, int> dropletAgesRange = secondaryAgeRange(droplets, dropletAges);
  const std::pair<int, int> bubbleAgesRange = secondaryAgeRange(bubbles, bubbleAges);
  out << "{\"section\":\"water_volume\""
      << ",\"primary_liquid_volume\":" << particleVolumeByType(primary, 0, volumeScale)
      << ",\"primary_gas_volume\":" << particleVolumeByType(primary, 1, volumeScale)
      << ",\"secondary_droplet_volume\":" << secondaryVolume(droplets, volumeScale)
      << ",\"secondary_bubble_volume\":" << secondaryVolume(bubbles, volumeScale)
      << ",\"phase_field_liquid_volume\":" << phaseFieldLiquidVolume
      << ",\"phase_field_cells\":" << phaseFieldCells
      << ",\"primary_liquid_count\":" << particleCountByType(primary, 0)
      << ",\"primary_gas_count\":" << particleCountByType(primary, 1)
      << ",\"secondary_droplet_count\":" << droplets.size()
      << ",\"secondary_bubble_count\":" << bubbles.size()
      << ",\"secondary_particle_count\":" << (droplets.size() + bubbles.size())
      << ",\"secondary_droplet_age_min\":" << dropletAgesRange.first
      << ",\"secondary_droplet_age_max\":" << dropletAgesRange.second
      << ",\"secondary_bubble_age_min\":" << bubbleAgesRange.first
      << ",\"secondary_bubble_age_max\":" << bubbleAgesRange.second << "}\n";
}

inline void writeCinematicMetadata(std::ostream& out,
                                   int nx,
                                   int ny,
                                   int nz,
                                   double dx,
                                   double dt,
                                   double time,
                                   const std::vector<RenderCacheCell3D>& cells,
                                   const Particles3DTP& primary,
                                   const Particles3DTP& droplets,
                                   const Particles3DTP& bubbles) {
  const Bounds3D domain = domainBounds(nx, ny, nz, dx);
  const Bounds3D water = waterBounds(cells, primary, dx);
  const Bounds3D secondary = secondaryBounds(droplets, bubbles);
  const double shutterClose = time + std::max(0.0, dt);

  out << "{\"section\":\"cinematic_metadata\""
      << ",\"cache_schema_version\":" << kCacheSchemaVersion
      << ",\"world_units\":\"" << kWorldUnits << "\""
      << ",\"shutter_open\":" << time
      << ",\"shutter_close\":" << shutterClose
      << ",\"frame_time\":" << time
      << ",\"phase_field_sampling_stride\":1"
      << ",\"water_bounds_valid\":" << (water.valid ? "true" : "false")
      << ",\"secondary_bounds_valid\":" << (secondary.valid ? "true" : "false")
      << ",\"primary_particle_count\":" << primary.size()
      << ",\"primary_liquid_count\":" << particleCountByType(primary, 0)
      << ",\"primary_gas_count\":" << particleCountByType(primary, 1)
      << ",\"secondary_droplet_count\":" << droplets.size()
      << ",\"secondary_bubble_count\":" << bubbles.size();
  out << ",";
  writeBounds(out, "frame_bounds_min", "frame_bounds_max", domain, domain);
  out << ",";
  writeBounds(out, "water_bounds_min", "water_bounds_max", water, domain);
  out << ",";
  writeBounds(out, "secondary_bounds_min", "secondary_bounds_max", secondary, domain);
  out << "}\n";
}

inline void writePhaseField(std::ostream& out, const std::vector<RenderCacheCell3D>& cells) {
  out << "{\"section\":\"phase_field\",\"encoding\":\"jsonl_cells\",\"count\":"
      << cells.size() << "}\n";
  for (const RenderCacheCell3D& c : cells) {
    out << "{\"section\":\"phase_cell\""
        << ",\"i\":" << c.i
        << ",\"j\":" << c.j
        << ",\"k\":" << c.k
        << ",\"level\":" << c.level
        << ",\"marker\":" << c.marker
        << ",\"phi\":" << c.phi
        << ",\"liquid_volume\":" << c.liquid_volume << "}\n";
  }
}

inline void writeParticleSection(std::ostream& out,
                                 const Particles3DTP& ps,
                                 const char* kind,
                                 const std::vector<int>* ages,
                                 double volumeScale) {
  out << "{\"section\":\"particles\",\"kind\":\"" << kind
      << "\",\"count\":" << ps.size() << "}\n";
  for (size_t i = 0; i < ps.size(); ++i) {
    out << "{\"section\":\"particle\""
        << ",\"kind\":\"" << kind << "\""
        << ",\"index\":" << i
        << ",\"phase\":\"" << particlePhaseName(ps.type[i]) << "\""
        << ",\"position\":[" << ps.pos[i].x << "," << ps.pos[i].y << "," << ps.pos[i].z << "]"
        << ",\"velocity\":[" << ps.vel[i].x << "," << ps.vel[i].y << "," << ps.vel[i].z << "]"
        << ",\"volume\":" << particleVolume(ps, i, volumeScale);
    if (ages && i < ages->size()) out << ",\"age\":" << (*ages)[i];
    out << "}\n";
  }
}

inline std::vector<RenderCacheCell3D> sparsePhaseCells(const SparseSim3DTP& sim,
                                                       double& liquidVolume) {
  std::vector<RenderCacheCell3D> cells;
  liquidVolume = 0.0;
  std::vector<int> active = sim.grid.mkf.activeBlockIds();
  if (active.empty()) active = sim.grid.pf.activeBlockIds();

  for (int b : active) {
    int bx = 0;
    int by = 0;
    int bz = 0;
    sim.grid.mkf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          const int i = bx * 4 + lx;
          const int j = by * 4 + ly;
          const int k = bz * 4 + lz;
          if (!sim.grid.inBounds(i, j, k)) continue;
          const int marker = sim.grid.cell(i, j, k);
          const double phi = sparseCellPhi(sim.grid, sim.phase, i, j, k);
          if (marker == 0 && phi <= 1e-8) continue;
          const double cellVolume = sim.grid.dx * sim.grid.dx * sim.grid.dx;
          const double waterVolume = phi * cellVolume;
          liquidVolume += waterVolume;
          cells.push_back(RenderCacheCell3D{i, j, k, 0, marker, phi, waterVolume});
        }
      }
    }
  }
  return cells;
}

inline std::vector<RenderCacheCell3D> mrPhaseCells(const MRSim3DTP& sim,
                                                   double& liquidVolume) {
  std::vector<RenderCacheCell3D> cells;
  liquidVolume = 0.0;
  for (const MRCellKey3D& c : sim.grid.marker.leafCells()) {
    const int step = 1 << c.block.level;
    const int i = c.block.bx * 4 * step + c.lx * step;
    const int j = c.block.by * 4 * step + c.ly * step;
    const int k = c.block.bz * 4 * step + c.lz * step;
    if (i >= sim.layout.nx || j >= sim.layout.ny || k >= sim.layout.nz) continue;
    const int ci = std::min(sim.layout.nx - 1, i + step / 2);
    const int cj = std::min(sim.layout.ny - 1, j + step / 2);
    const int ck = std::min(sim.layout.nz - 1, k + step / 2);
    const int marker = static_cast<int>(sim.grid.marker.get(c) + 0.5f);
    const double phi = mrCellPhi(sim.grid, sim.phase, ci, cj, ck);
    if (marker == 0 && phi <= 1e-8) continue;
    const double cellDx = sim.layout.dx * static_cast<double>(step);
    const double waterVolume = phi * cellDx * cellDx * cellDx;
    liquidVolume += waterVolume;
    cells.push_back(RenderCacheCell3D{i, j, k, c.block.level, marker, phi, waterVolume});
  }
  return cells;
}

} // namespace render_cache3d_detail

inline void writeSparseRenderCache3D(const SparseSim3DTP& sim,
                                     const std::string& path,
                                     int frame,
                                     double time,
                                     const RenderCacheCamera3D& camera) {
  render_cache3d_detail::requireValidPath(path);
  double phaseFieldLiquidVolume = 0.0;
  std::vector<RenderCacheCell3D> cells =
    render_cache3d_detail::sparsePhaseCells(sim, phaseFieldLiquidVolume);

  std::ofstream out(path);
  if (!out) throw std::runtime_error("render cache open failed: " + path);
  out << std::setprecision(17);
  render_cache3d_detail::writeHeader(out, "sparse3d_tp",
                                     sim.grid.nx, sim.grid.ny, sim.grid.nz,
                                     sim.grid.dx, sim.effective_dt_last,
                                     frame, time, sim.phase, camera);
  render_cache3d_detail::writeWaterSummary(out, sim.particles,
                                           sim.escaped_droplets,
                                           sim.escaped_bubbles,
                                           sim.escaped_droplet_ages,
                                           sim.escaped_bubble_ages,
                                           sim.Vp,
                                           phaseFieldLiquidVolume,
                                           cells.size());
  render_cache3d_detail::writeCinematicMetadata(out,
                                                sim.grid.nx, sim.grid.ny, sim.grid.nz,
                                                sim.grid.dx, sim.effective_dt_last,
                                                time, cells, sim.particles,
                                                sim.escaped_droplets,
                                                sim.escaped_bubbles);
  render_cache3d_detail::writePhaseField(out, cells);
  render_cache3d_detail::writeParticleSection(out, sim.particles, "primary", nullptr, sim.Vp);
  render_cache3d_detail::writeParticleSection(out, sim.escaped_droplets, "secondary_droplet",
                                              &sim.escaped_droplet_ages, sim.Vp);
  render_cache3d_detail::writeParticleSection(out, sim.escaped_bubbles, "secondary_bubble",
                                              &sim.escaped_bubble_ages, sim.Vp);
  if (!out) throw std::runtime_error("render cache write failed: " + path);
}

inline void writeMRRenderCache3D(const MRSim3DTP& sim,
                                 const std::string& path,
                                 int frame,
                                 double time,
                                 const RenderCacheCamera3D& camera) {
  render_cache3d_detail::requireValidPath(path);
  double phaseFieldLiquidVolume = 0.0;
  std::vector<RenderCacheCell3D> cells =
    render_cache3d_detail::mrPhaseCells(sim, phaseFieldLiquidVolume);

  std::ofstream out(path);
  if (!out) throw std::runtime_error("render cache open failed: " + path);
  out << std::setprecision(17);
  render_cache3d_detail::writeHeader(out, "multires3d_tp",
                                     sim.layout.nx, sim.layout.ny, sim.layout.nz,
                                     sim.layout.dx, sim.effective_dt_last,
                                     frame, time, sim.phase, camera);
  render_cache3d_detail::writeWaterSummary(out, sim.particles,
                                           sim.escaped_droplets,
                                           sim.escaped_bubbles,
                                           sim.escaped_droplet_ages,
                                           sim.escaped_bubble_ages,
                                           sim.Vp,
                                           phaseFieldLiquidVolume,
                                           cells.size());
  render_cache3d_detail::writeCinematicMetadata(out,
                                                sim.layout.nx, sim.layout.ny, sim.layout.nz,
                                                sim.layout.dx, sim.effective_dt_last,
                                                time, cells, sim.particles,
                                                sim.escaped_droplets,
                                                sim.escaped_bubbles);
  render_cache3d_detail::writePhaseField(out, cells);
  render_cache3d_detail::writeParticleSection(out, sim.particles, "primary", nullptr, sim.Vp);
  render_cache3d_detail::writeParticleSection(out, sim.escaped_droplets, "secondary_droplet",
                                              &sim.escaped_droplet_ages, sim.Vp);
  render_cache3d_detail::writeParticleSection(out, sim.escaped_bubbles, "secondary_bubble",
                                              &sim.escaped_bubble_ages, sim.Vp);
  if (!out) throw std::runtime_error("render cache write failed: " + path);
}

inline void writeRenderCacheManifest3D(const std::string& path,
                                       const char* simKind,
                                       int nx,
                                       int ny,
                                       int nz,
                                       double dx,
                                       const std::vector<RenderCacheManifestFrame3D>& frames) {
  render_cache3d_detail::requireValidPath(path);
  render_cache3d_detail::requireManifestArgs(simKind, nx, ny, nz, dx, frames);

  std::ofstream out(path);
  if (!out) throw std::runtime_error("render cache manifest open failed: " + path);
  out << std::setprecision(17);
  out << "{\n";
  out << "  \"lsfs_cache3d_manifest_version\":1,\n";
  out << "  \"cache_schema_version\":" << render_cache3d_detail::kCacheSchemaVersion << ",\n";
  out << "  \"world_units\":\"" << render_cache3d_detail::kWorldUnits << "\",\n";
  out << "  \"sim_kind\":";
  render_cache3d_detail::writeJsonString(out, simKind);
  out << ",\n";
  out << "  \"dims\":[" << nx << "," << ny << "," << nz << "],\n";
  out << "  \"dx\":" << dx << ",\n";
  out << "  \"frame_bounds_min\":[0,0,0],\n";
  out << "  \"frame_bounds_max\":[" << nx * dx << "," << ny * dx << "," << nz * dx << "],\n";
  out << "  \"frame_count\":" << frames.size() << ",\n";
  out << "  \"frames\":[\n";
  for (size_t i = 0; i < frames.size(); ++i) {
    const RenderCacheManifestFrame3D& f = frames[i];
    out << "    {\"frame\":" << f.frame
        << ",\"step\":" << f.step
        << ",\"time\":" << f.time
        << ",\"shutter_open\":" << f.time
        << ",\"shutter_close\":" << f.time
        << ",\"frame_bounds_min\":[0,0,0]"
        << ",\"frame_bounds_max\":[" << nx * dx << "," << ny * dx << "," << nz * dx << "]"
        << ",\"path\":";
    render_cache3d_detail::writeJsonString(out, f.path);
    out << ",\"bytes\":" << f.bytes << "}";
    if (i + 1 < frames.size()) out << ",";
    out << "\n";
  }
  out << "  ]\n";
  out << "}\n";
  if (!out) throw std::runtime_error("render cache manifest write failed: " + path);
}
