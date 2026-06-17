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
