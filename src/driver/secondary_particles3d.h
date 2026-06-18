#pragma once

#include "particles/particles3d_tp.h"

#include <algorithm>
#include <cmath>
#include <vector>

struct SecondaryParticleDomain3D {
  int nx = 0;
  int ny = 0;
  int nz = 0;
  double dx = 1.0;
  double ox = 0.0;
  double oy = 0.0;
  double oz = 0.0;
};

struct SecondaryParticleLifecycleConfig3D {
  bool enabled = false;
  int droplet_lifetime_steps = 48;
  int bubble_lifetime_steps = 48;
  double velocity_damping = 0.98;
  double reabsorb_margin_cells = 1.0;
  double gravity = -9.81;
  double droplet_gravity_scale = 1.0;
  double bubble_buoyancy_scale = 0.25;
  double droplet_drag = 0.0;
  double bubble_drag = 0.0;
  double particle_volume_scale = 1.0;
};

struct SecondaryParticleLifecycleStats3D {
  int enabled = 0;
  int finite = 1;
  int advected_droplets = 0;
  int advected_bubbles = 0;
  int reabsorbed_droplets = 0;
  int reabsorbed_bubbles = 0;
  int expired_droplets = 0;
  int expired_bubbles = 0;
  int dragged_droplets = 0;
  int dragged_bubbles = 0;
  int reabsorbed_droplets_to_primary = 0;
  int reabsorbed_bubbles_to_primary = 0;
  double current_droplet_volume = 0.0;
  double current_bubble_volume = 0.0;
  double reabsorbed_droplet_volume = 0.0;
  double reabsorbed_bubble_volume = 0.0;
  double expired_droplet_volume = 0.0;
  double expired_bubble_volume = 0.0;
  double reabsorbed_droplet_volume_to_primary = 0.0;
  double reabsorbed_bubble_volume_to_primary = 0.0;
};

struct SecondarySprayEmissionConfig3D {
  bool enabled = false;
  int requested_particles = 0;
  double droplet_fraction = 0.9;
  double droplet_volume = 0.55;
  double bubble_volume = 0.45;
  double particle_volume_scale = 1.0;
  bool interface_gate = false;
  int interface_cells = 0;
  double interface_grad_max = 0.0;
  double interface_curvature_abs_max = 0.0;
  int min_interface_cells = 1;
  double min_interface_grad_max = 1e-5;
  double min_interface_curvature_abs_max = 0.0;
  bool impact_splash_candidates = false;
  double impact_region_fraction = 0.55;
  double impact_downward_speed_min = 1.0;
};

struct SecondarySprayEmissionStats3D {
  int enabled = 0;
  int finite = 1;
  int requested_particles = 0;
  int effective_requested_particles = 0;
  int interface_gate_enabled = 0;
  int interface_gate_passed = 1;
  int interface_cells = 0;
  int candidate_liquid_particles = 0;
  int impact_candidate_liquid_particles = 0;
  int emitted_droplets = 0;
  int emitted_bubbles = 0;
  double interface_grad_max = 0.0;
  double interface_curvature_abs_max = 0.0;
  double emitted_droplet_volume = 0.0;
  double emitted_bubble_volume = 0.0;
};

struct SecondarySprayCandidate3D {
  Vec3 pos{0.0, 0.0, 0.0};
  Vec3 vel{0.0, 0.0, 0.0};
  double score = 0.0;
};

struct SecondaryParticleBounds3D {
  Vec3 min{0.0, 0.0, 0.0};
  Vec3 max{0.0, 0.0, 0.0};
  bool valid = false;
};

inline bool finiteSecondaryParticle3D(const Particles3DTP& ps, size_t p);

inline void includeSecondaryParticleBounds3D(SecondaryParticleBounds3D& bounds,
                                             const Vec3& p) {
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

inline SecondaryParticleBounds3D liquidParticleBounds3D(const Particles3DTP& particles) {
  SecondaryParticleBounds3D bounds;
  for (size_t i = 0; i < particles.size(); ++i) {
    if (particles.type[i] == 0) includeSecondaryParticleBounds3D(bounds, particles.pos[i]);
  }
  return bounds;
}

inline SecondarySprayEmissionStats3D emitSecondarySpraySeeds3D(
    const Particles3DTP& primary,
    Particles3DTP& droplets,
    Particles3DTP& bubbles,
    std::vector<int>& dropletAges,
    std::vector<int>& bubbleAges,
    const SecondarySprayEmissionConfig3D& config,
    int frameIndex) {
  SecondarySprayEmissionStats3D stats;
  stats.enabled = config.enabled ? 1 : 0;
  stats.requested_particles = std::max(0, config.requested_particles);
  stats.interface_gate_enabled = config.interface_gate ? 1 : 0;
  stats.interface_cells = config.interface_cells;
  stats.interface_grad_max = config.interface_grad_max;
  stats.interface_curvature_abs_max = config.interface_curvature_abs_max;
  if (!config.enabled || config.requested_particles <= 0) return stats;

  if (config.interface_gate) {
    const bool finiteInterface =
      std::isfinite(config.interface_grad_max) &&
      std::isfinite(config.interface_curvature_abs_max);
    const bool pass =
      finiteInterface &&
      config.interface_cells >= std::max(0, config.min_interface_cells) &&
      config.interface_grad_max >= config.min_interface_grad_max &&
      config.interface_curvature_abs_max >= config.min_interface_curvature_abs_max;
    stats.interface_gate_passed = pass ? 1 : 0;
    if (!finiteInterface) stats.finite = 0;
    if (!pass) return stats;
  }

  const SecondaryParticleBounds3D bounds = liquidParticleBounds3D(primary);
  if (!bounds.valid) return stats;

  const double surfaceY = bounds.min.y + 0.68 * (bounds.max.y - bounds.min.y);
  const double impactY =
    bounds.min.y +
    std::max(0.0, std::min(1.0, config.impact_region_fraction)) *
      (bounds.max.y - bounds.min.y);
  const double cx = 0.5 * (bounds.min.x + bounds.max.x);
  const double cz = 0.5 * (bounds.min.z + bounds.max.z);
  std::vector<SecondarySprayCandidate3D> candidates;
  candidates.reserve(primary.size());
  for (size_t i = 0; i < primary.size(); ++i) {
    if (primary.type[i] != 0) continue;
    if (!finiteSecondaryParticle3D(primary, i)) {
      stats.finite = 0;
      continue;
    }
    const Vec3& p = primary.pos[i];
    const Vec3& v = primary.vel[i];
    const double hspeed = std::sqrt(v.x * v.x + v.z * v.z);
    const double upward = std::max(0.0, v.y);
    const double downward = std::max(0.0, -v.y);
    const double nearSurface = std::max(0.0, p.y - surfaceY);
    const bool impactCandidate =
      config.impact_splash_candidates &&
      p.y <= impactY &&
      downward >= config.impact_downward_speed_min;
    const double lateral = std::sqrt((p.x - cx) * (p.x - cx) + (p.z - cz) * (p.z - cz));
    const double impactDepth = std::max(0.0, impactY - p.y);
    const double score = nearSurface * 4.0 + upward * 2.0 +
      hspeed * 0.25 + lateral * 0.03 +
      (impactCandidate ? downward * 2.5 + impactDepth * 0.8 : 0.0);
    if (p.y >= surfaceY || upward > 0.02 || hspeed > 0.25 || impactCandidate) {
      if (impactCandidate) ++stats.impact_candidate_liquid_particles;
      candidates.push_back(SecondarySprayCandidate3D{p, v, score});
    }
  }
  if (candidates.empty()) {
    for (size_t i = 0; i < primary.size(); ++i) {
      if (primary.type[i] != 0 || !finiteSecondaryParticle3D(primary, i)) continue;
      candidates.push_back(SecondarySprayCandidate3D{
        primary.pos[i], primary.vel[i], primary.pos[i].y});
    }
  }
  stats.candidate_liquid_particles = static_cast<int>(candidates.size());
  if (candidates.empty()) return stats;

  std::sort(candidates.begin(), candidates.end(),
            [](const SecondarySprayCandidate3D& a, const SecondarySprayCandidate3D& b) {
              return a.score > b.score;
            });
  const int requested = std::max(0, config.requested_particles);
  stats.effective_requested_particles = requested;
  const double dropletFraction = std::max(0.0, std::min(1.0, config.droplet_fraction));
  const int dropletCount = std::max(0, std::min(requested,
    static_cast<int>(std::floor(static_cast<double>(requested) * dropletFraction + 0.5))));
  const int bubbleCount = std::max(0, requested - dropletCount);
  const size_t window = std::min(candidates.size(), static_cast<size_t>(std::max(1, requested * 3)));
  for (int n = 0; n < dropletCount; ++n) {
    const size_t idx = (static_cast<size_t>(n) * 37u + static_cast<size_t>(frameIndex) * 11u) % window;
    const SecondarySprayCandidate3D& c = candidates[idx];
    const double dx = c.pos.x - cx;
    const double dz = c.pos.z - cz;
    const double len = std::sqrt(dx * dx + dz * dz);
    const double ox = len > 1e-8 ? dx / len : 0.0;
    const double oz = len > 1e-8 ? dz / len : 0.0;
    const double lift = 0.18 + 0.035 * static_cast<double>((n + frameIndex) % 5);
    const Vec3 pos{
      c.pos.x + 0.035 * ox,
      c.pos.y + 0.04 + 0.01 * static_cast<double>(n % 3),
      c.pos.z + 0.035 * oz
    };
    const Vec3 vel{
      c.vel.x + 0.16 * ox,
      c.vel.y + lift,
      c.vel.z + 0.16 * oz
    };
    const double speed = vel.length();
    const int age = speed > 1.0 ? 0 : (n % 4 == 0 ? 5 : 2);
    droplets.add(pos, vel, 0, config.droplet_volume);
    dropletAges.push_back(age);
    ++stats.emitted_droplets;
    stats.emitted_droplet_volume += config.droplet_volume * config.particle_volume_scale;
  }
  for (int n = 0; n < bubbleCount; ++n) {
    const size_t idx = (static_cast<size_t>(n) * 53u + static_cast<size_t>(frameIndex) * 7u) % window;
    const SecondarySprayCandidate3D& c = candidates[idx];
    const Vec3 pos{c.pos.x, std::max(bounds.min.y + 0.25, c.pos.y - 0.12), c.pos.z};
    bubbles.add(pos, Vec3{0.0, 0.16, 0.0}, 1, config.bubble_volume);
    bubbleAges.push_back(0);
    ++stats.emitted_bubbles;
    stats.emitted_bubble_volume += config.bubble_volume * config.particle_volume_scale;
  }
  return stats;
}

inline bool finiteSecondaryParticle3D(const Particles3DTP& ps, size_t p) {
  return std::isfinite(ps.pos[p].x) &&
         std::isfinite(ps.pos[p].y) &&
         std::isfinite(ps.pos[p].z) &&
         std::isfinite(ps.vel[p].x) &&
         std::isfinite(ps.vel[p].y) &&
         std::isfinite(ps.vel[p].z) &&
         std::isfinite(ps.volume[p]);
}

inline double secondaryVolume3D(const Particles3DTP& ps,
                                size_t p,
                                double particleVolumeScale) {
  return ps.volume[p] * particleVolumeScale;
}

inline double secondaryVolumeSum3D(const Particles3DTP& ps,
                                   double particleVolumeScale) {
  double volume = 0.0;
  for (size_t p = 0; p < ps.size(); ++p) {
    volume += secondaryVolume3D(ps, p, particleVolumeScale);
  }
  return volume;
}

inline void syncSecondaryAges3D(std::vector<int>& ages, size_t count) {
  if (ages.size() < count) {
    ages.resize(count, 0);
  } else if (ages.size() > count) {
    ages.resize(count);
  }
}

inline double clampSecondaryCoord3D(double value, double lo, double hi) {
  return std::max(lo, std::min(hi, value));
}

inline bool secondaryInsideReabsorbBand3D(const Vec3& pos,
                                          const SecondaryParticleDomain3D& domain,
                                          double marginCells) {
  const double margin = std::max(0.0, marginCells) * domain.dx;
  const double x0 = domain.ox + (0.5 * domain.dx) + margin;
  const double y0 = domain.oy + (0.5 * domain.dx) + margin;
  const double z0 = domain.oz + (0.5 * domain.dx) + margin;
  const double x1 = domain.ox + (static_cast<double>(domain.nx) - 0.5) * domain.dx - margin;
  const double y1 = domain.oy + (static_cast<double>(domain.ny) - 0.5) * domain.dx - margin;
  const double z1 = domain.oz + (static_cast<double>(domain.nz) - 0.5) * domain.dx - margin;
  if (x0 >= x1 || y0 >= y1 || z0 >= z1) return false;
  return pos.x > x0 && pos.x < x1 &&
         pos.y > y0 && pos.y < y1 &&
         pos.z > z0 && pos.z < z1;
}

inline void compactSecondaryParticles3D(Particles3DTP& ps,
                                        std::vector<int>& ages,
                                        const std::vector<char>& remove) {
  size_t write = 0;
  for (size_t read = 0; read < ps.size(); ++read) {
    if (remove[read]) continue;
    if (write != read) {
      ps.pos[write] = ps.pos[read];
      ps.vel[write] = ps.vel[read];
      ps.type[write] = ps.type[read];
      ps.volume[write] = ps.volume[read];
      ages[write] = ages[read];
    }
    ++write;
  }
  ps.pos.resize(write);
  ps.vel.resize(write);
  ps.type.resize(write);
  ps.volume.resize(write);
  ages.resize(write);
}

inline void advanceSecondarySet3D(Particles3DTP& ps,
                                  std::vector<int>& ages,
                                  const SecondaryParticleDomain3D& domain,
                                  const SecondaryParticleLifecycleConfig3D& config,
                                  double dt,
                                  unsigned char type,
                                  int lifetimeSteps,
                                  double accelY,
                                  double dragPerSecond,
                                  Particles3DTP* reabsorbedToPrimary,
                                  SecondaryParticleLifecycleStats3D& stats) {
  syncSecondaryAges3D(ages, ps.size());
  if (ps.size() == 0) return;

  const double xLo = domain.ox + 0.5 * domain.dx;
  const double yLo = domain.oy + 0.5 * domain.dx;
  const double zLo = domain.oz + 0.5 * domain.dx;
  const double xHi = domain.ox + (static_cast<double>(domain.nx) - 0.5) * domain.dx;
  const double yHi = domain.oy + (static_cast<double>(domain.ny) - 0.5) * domain.dx;
  const double zHi = domain.oz + (static_cast<double>(domain.nz) - 0.5) * domain.dx;
  std::vector<char> remove(ps.size(), 0);

  for (size_t p = 0; p < ps.size(); ++p) {
    if (!finiteSecondaryParticle3D(ps, p)) {
      stats.finite = 0;
      remove[p] = 1;
      if (type == 0) {
        ++stats.expired_droplets;
        stats.expired_droplet_volume += secondaryVolume3D(ps, p, config.particle_volume_scale);
      } else {
        ++stats.expired_bubbles;
        stats.expired_bubble_volume += secondaryVolume3D(ps, p, config.particle_volume_scale);
      }
      continue;
    }

    const int nextAge = ages[p] + 1;
    ages[p] = nextAge;
    if (type == 0) ++stats.advected_droplets;
    else ++stats.advected_bubbles;

    ps.vel[p].y += accelY * dt;
    double damping = std::max(0.0, config.velocity_damping);
    if (dragPerSecond > 0.0) {
      damping *= std::exp(-dragPerSecond * dt);
      if (type == 0) ++stats.dragged_droplets;
      else ++stats.dragged_bubbles;
    }
    ps.vel[p] = ps.vel[p] * damping;
    ps.pos[p] += ps.vel[p] * dt;
    ps.pos[p].x = clampSecondaryCoord3D(ps.pos[p].x, xLo, xHi);
    ps.pos[p].y = clampSecondaryCoord3D(ps.pos[p].y, yLo, yHi);
    ps.pos[p].z = clampSecondaryCoord3D(ps.pos[p].z, zLo, zHi);

    const double volume = secondaryVolume3D(ps, p, config.particle_volume_scale);
    if (secondaryInsideReabsorbBand3D(ps.pos[p], domain,
                                      config.reabsorb_margin_cells)) {
      remove[p] = 1;
      if (reabsorbedToPrimary) {
        reabsorbedToPrimary->add(ps.pos[p], ps.vel[p], type, ps.volume[p]);
      }
      if (type == 0) {
        ++stats.reabsorbed_droplets;
        stats.reabsorbed_droplet_volume += volume;
        if (reabsorbedToPrimary) {
          ++stats.reabsorbed_droplets_to_primary;
          stats.reabsorbed_droplet_volume_to_primary += volume;
        }
      } else {
        ++stats.reabsorbed_bubbles;
        stats.reabsorbed_bubble_volume += volume;
        if (reabsorbedToPrimary) {
          ++stats.reabsorbed_bubbles_to_primary;
          stats.reabsorbed_bubble_volume_to_primary += volume;
        }
      }
    } else if (lifetimeSteps >= 0 && nextAge >= lifetimeSteps) {
      remove[p] = 1;
      if (type == 0) {
        ++stats.expired_droplets;
        stats.expired_droplet_volume += volume;
      } else {
        ++stats.expired_bubbles;
        stats.expired_bubble_volume += volume;
      }
    }
  }

  compactSecondaryParticles3D(ps, ages, remove);
}

inline SecondaryParticleLifecycleStats3D advanceSecondaryParticles3D(
    Particles3DTP& droplets,
    Particles3DTP& bubbles,
    std::vector<int>& dropletAges,
    std::vector<int>& bubbleAges,
    const SecondaryParticleDomain3D& domain,
    const SecondaryParticleLifecycleConfig3D& config,
    double dt,
    Particles3DTP* reabsorbedDropletsToPrimary = nullptr,
    Particles3DTP* reabsorbedBubblesToPrimary = nullptr) {
  SecondaryParticleLifecycleStats3D stats;
  stats.enabled = config.enabled ? 1 : 0;
  syncSecondaryAges3D(dropletAges, droplets.size());
  syncSecondaryAges3D(bubbleAges, bubbles.size());

  if (config.enabled && dt > 0.0) {
    advanceSecondarySet3D(droplets, dropletAges, domain, config, dt, 0,
                          config.droplet_lifetime_steps,
                          config.gravity * config.droplet_gravity_scale,
                          config.droplet_drag,
                          reabsorbedDropletsToPrimary,
                          stats);
    advanceSecondarySet3D(bubbles, bubbleAges, domain, config, dt, 1,
                          config.bubble_lifetime_steps,
                          -config.gravity * config.bubble_buoyancy_scale,
                          config.bubble_drag,
                          reabsorbedBubblesToPrimary,
                          stats);
  }

  stats.current_droplet_volume =
    secondaryVolumeSum3D(droplets, config.particle_volume_scale);
  stats.current_bubble_volume =
    secondaryVolumeSum3D(bubbles, config.particle_volume_scale);
  return stats;
}
