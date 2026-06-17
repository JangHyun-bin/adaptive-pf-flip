#pragma once

#include "math/vec3.h"

#include <vector>

struct EscapedParticleRecord3D {
  Vec3 pos{};
  Vec3 vel{};
  double volume = 1.0;
  unsigned char type = 0;
};

struct ParticleEscapeBuffer3D {
  std::vector<EscapedParticleRecord3D> records;

  void record(unsigned char type, const Vec3& pos, const Vec3& vel, double volume) {
    records.push_back(EscapedParticleRecord3D{pos, vel, volume, type});
  }

  int droplet_count() const {
    int count = 0;
    for (const EscapedParticleRecord3D& r : records) {
      if (r.type == 0) ++count;
    }
    return count;
  }

  int bubble_count() const {
    int count = 0;
    for (const EscapedParticleRecord3D& r : records) {
      if (r.type == 1) ++count;
    }
    return count;
  }
};

struct ParticleEscapeStats3D {
  int clamped_liquid = 0;
  int clamped_gas = 0;
  int clamped_x_lo = 0;
  int clamped_x_hi = 0;
  int clamped_y_lo = 0;
  int clamped_y_hi = 0;
  int clamped_z_lo = 0;
  int clamped_z_hi = 0;

  int clamped_total() const {
    return clamped_liquid + clamped_gas;
  }

  int droplet_candidates() const {
    return clamped_liquid;
  }

  int bubble_candidates() const {
    return clamped_gas;
  }

  void recordClamp(unsigned char type,
                   bool xLo,
                   bool xHi,
                   bool yLo,
                   bool yHi,
                   bool zLo,
                   bool zHi) {
    if (!(xLo || xHi || yLo || yHi || zLo || zHi)) return;
    if (type == 0) {
      ++clamped_liquid;
    } else if (type == 1) {
      ++clamped_gas;
    }
    if (xLo) ++clamped_x_lo;
    if (xHi) ++clamped_x_hi;
    if (yLo) ++clamped_y_lo;
    if (yHi) ++clamped_y_hi;
    if (zLo) ++clamped_z_lo;
    if (zHi) ++clamped_z_hi;
  }
};
