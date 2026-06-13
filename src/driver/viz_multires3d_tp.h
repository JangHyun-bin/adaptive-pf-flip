#pragma once

#include "driver/multires_sim3d_tp.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

inline void writeMR3DTPPM(const MRSim3DTP& sim, const std::string& path, int scale = 6, double zhalf = 0.12) {
  if (sim.layout.nx <= 0 || sim.layout.ny <= 0 || sim.layout.nz <= 0 ||
      !std::isfinite(sim.layout.dx) || sim.layout.dx <= 0.0 ||
      !std::isfinite(zhalf) || zhalf < 0.0 || scale <= 0) {
    throw std::invalid_argument("writeMR3DTPPM invalid dimensions");
  }
  if (sim.layout.nx > std::numeric_limits<int>::max() / scale ||
      sim.layout.ny > std::numeric_limits<int>::max() / scale) {
    throw std::overflow_error("writeMR3DTPPM image dimensions overflow");
  }

  int W = sim.layout.nx * scale;
  int H = sim.layout.ny * scale;
  if (static_cast<size_t>(W) > std::numeric_limits<size_t>::max() / static_cast<size_t>(H)) {
    throw std::overflow_error("writeMR3DTPPM image buffer overflow");
  }
  size_t pixels = static_cast<size_t>(W) * static_cast<size_t>(H);
  if (pixels > std::numeric_limits<size_t>::max() / 3 ||
      pixels * 3 > static_cast<size_t>(std::numeric_limits<std::streamsize>::max())) {
    throw std::overflow_error("writeMR3DTPPM image buffer overflow");
  }

  std::vector<unsigned char> img(pixels * 3, 16);
  double zc = sim.layout.nz * 0.5 * sim.layout.dx;
  double band = zhalf * sim.layout.nz * sim.layout.dx;

  for (const MRBlockKey3D& b : sim.layout.leaves()) {
    int s = sim.layout.blockFineSize(b.level);
    int x0 = std::max(0, b.bx * s);
    int y0 = std::max(0, b.by * s);
    int z0 = std::max(0, b.bz * s);
    int x1 = std::min(sim.layout.nx, b.bx * s + s);
    int y1 = std::min(sim.layout.ny, b.by * s + s);
    int z1 = std::min(sim.layout.nz, b.bz * s + s);
    double physZ0 = z0 * sim.layout.dx;
    double physZ1 = z1 * sim.layout.dx;
    if (physZ0 > zc + band || physZ1 < zc - band) continue;

    unsigned char r = b.level == 0 ? 24 : 28;
    unsigned char g = b.level == 0 ? 40 : 32;
    unsigned char bl = b.level == 0 ? 28 : 48;
    for (int j = y0; j < y1; ++j) {
      for (int i = x0; i < x1; ++i) {
        int px = i * scale;
        int py = H - 1 - j * scale;
        for (int yy = 0; yy < scale; ++yy) {
          for (int xx = 0; xx < scale; ++xx) {
            int X = px + xx;
            int Y = py - yy;
            if (X < 0 || X >= W || Y < 0 || Y >= H) continue;
            int o = (X + W * Y) * 3;
            img[o] = r;
            img[o + 1] = g;
            img[o + 2] = bl;
          }
        }
      }
    }
  }

  double maxX = sim.layout.nx * sim.layout.dx;
  double maxY = sim.layout.ny * sim.layout.dx;
  double maxZ = sim.layout.nz * sim.layout.dx;
  for (size_t k = 0; k < sim.particles.size(); ++k) {
    const Vec3& p = sim.particles.pos[k];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z) ||
        p.x < 0.0 || p.y < 0.0 || p.z < 0.0 ||
        p.x >= maxX || p.y >= maxY || p.z >= maxZ ||
        std::abs(p.z - zc) > band) {
      continue;
    }
    int px = static_cast<int>(std::floor(p.x / sim.layout.dx * scale));
    int py = H - 1 - static_cast<int>(std::floor(p.y / sim.layout.dx * scale));
    if (px < 0 || px >= W || py < 0 || py >= H) continue;
    int o = (px + W * py) * 3;
    if (sim.particles.type[k] == 0) {
      img[o] = 60;
      img[o + 1] = 140;
      img[o + 2] = 230;
    } else {
      img[o] = 235;
      img[o + 1] = 160;
      img[o + 2] = 60;
    }
  }

  std::ofstream f(path, std::ios::binary);
  if (!f) throw std::runtime_error("writeMR3DTPPM open failed: " + path);
  f << "P6\n" << W << " " << H << "\n255\n";
  if (!f) throw std::runtime_error("writeMR3DTPPM header write failed: " + path);
  f.write(reinterpret_cast<const char*>(img.data()), static_cast<std::streamsize>(img.size()));
  if (!f) throw std::runtime_error("writeMR3DTPPM image write failed: " + path);
}
