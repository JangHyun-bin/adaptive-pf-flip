#pragma once

#include "particles/particles3d_tp.h"

#include <algorithm>
#include <cmath>

struct TimestepStats3D {
  double requested_dt = 0.0;
  double effective_dt = 0.0;
  double max_particle_speed = 0.0;
  double cfl_limit_dt = 0.0;
  int limited = 0;
};

inline TimestepStats3D computeAdaptiveParticleTimestep3D(const Particles3DTP& particles,
                                                         double dx,
                                                         double requestedDt,
                                                         bool enabled,
                                                         double cfl,
                                                         double minDt) {
  TimestepStats3D stats;
  stats.requested_dt = requestedDt;
  stats.effective_dt = requestedDt;
  stats.cfl_limit_dt = requestedDt;

  for (size_t i = 0; i < particles.size(); ++i) {
    const Vec3& v = particles.vel[i];
    if (!std::isfinite(v.x) || !std::isfinite(v.y) || !std::isfinite(v.z)) continue;
    stats.max_particle_speed =
      std::max(stats.max_particle_speed, std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z));
  }

  if (!enabled ||
      requestedDt <= 0.0 ||
      dx <= 0.0 ||
      cfl <= 0.0 ||
      stats.max_particle_speed <= 0.0) {
    return stats;
  }

  stats.cfl_limit_dt = cfl * dx / stats.max_particle_speed;
  double limitedDt = std::min(requestedDt, stats.cfl_limit_dt);
  if (minDt > 0.0) {
    limitedDt = std::max(minDt, limitedDt);
  }
  stats.effective_dt = std::min(requestedDt, limitedDt);
  stats.limited = stats.effective_dt < requestedDt ? 1 : 0;
  return stats;
}
