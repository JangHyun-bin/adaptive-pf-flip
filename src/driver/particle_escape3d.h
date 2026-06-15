#pragma once

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
