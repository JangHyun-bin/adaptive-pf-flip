#pragma once
#include "grid/sparse_mac_grid3d.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <future>
#include <vector>

namespace sparse3d {

inline int cidx(const SparseMacGrid3D<4>& g, int i, int j, int k) {
  return i + g.nx * (j + g.ny * k);
}

template<typename Fn>
void runColor8(size_t workItems, Fn&& fn) {
  if (workItems < 2048) {
    for (int color = 0; color < 8; ++color) fn(color);
    return;
  }
  std::array<std::future<void>, 8> jobs;
  for (int color = 0; color < 8; ++color) {
    jobs[(size_t)color] = std::async(std::launch::async, [&, color]() { fn(color); });
  }
  for (auto& job : jobs) job.get();
}

inline float sampleField(const SparseBlockGrid3D<4>& f, int nx, int ny, int nz,
                         double gx, double gy, double gz) {
  int i0 = (int)std::floor(gx);
  int j0 = (int)std::floor(gy);
  int k0 = (int)std::floor(gz);
  double fx = gx - i0, fy = gy - j0, fz = gz - k0;
  double wx[2] = {1.0 - fx, fx};
  double wy[2] = {1.0 - fy, fy};
  double wz[2] = {1.0 - fz, fz};
  double s = 0.0;
  for (int dk = 0; dk < 2; ++dk) {
    for (int dj = 0; dj < 2; ++dj) {
      for (int di = 0; di < 2; ++di) {
        int i = std::max(0, std::min(nx - 1, i0 + di));
        int j = std::max(0, std::min(ny - 1, j0 + dj));
        int k = std::max(0, std::min(nz - 1, k0 + dk));
        s += wx[di] * wy[dj] * wz[dk] * f.get(i, j, k);
      }
    }
  }
  return (float)s;
}

inline float sampleU(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.uf, g.nx + 1, g.ny, g.nz, px, py - 0.5, pz - 0.5);
}

inline float sampleV(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.vf, g.nx, g.ny + 1, g.nz, px - 0.5, py, pz - 0.5);
}

inline float sampleW(const SparseMacGrid3D<4>& g, double px, double py, double pz) {
  return sampleField(g.wf, g.nx, g.ny, g.nz + 1, px - 0.5, py - 0.5, pz);
}

inline std::vector<int> collectCellsWithMarker(const SparseMacGrid3D<4>& g, int marker) {
  std::vector<int> cells;
  for (int b : g.mkf.activeBlockIds()) {
    int bx, by, bz;
    g.mkf.blockCoords(b, bx, by, bz);
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          int i = bx * 4 + lx;
          int j = by * 4 + ly;
          int k = bz * 4 + lz;
          if (g.inBounds(i, j, k) && g.cell(i, j, k) == marker) {
            cells.push_back(cidx(g, i, j, k));
          }
        }
      }
    }
  }
  std::sort(cells.begin(), cells.end());
  return cells;
}

inline int findSortedIndex(const std::vector<int>& sorted, int value) {
  auto it = std::lower_bound(sorted.begin(), sorted.end(), value);
  return (it != sorted.end() && *it == value) ? (int)(it - sorted.begin()) : -1;
}

inline std::vector<int> collectProjectUFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int q = c / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    if (i > 0) faces.push_back(i + (g.nx + 1) * (j + g.ny * k));
    if (i + 1 < g.nx) faces.push_back((i + 1) + (g.nx + 1) * (j + g.ny * k));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

inline std::vector<int> collectProjectVFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int q = c / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    if (j > 0) faces.push_back(i + g.nx * (j + (g.ny + 1) * k));
    if (j + 1 < g.ny) faces.push_back(i + g.nx * ((j + 1) + (g.ny + 1) * k));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

inline std::vector<int> collectProjectWFaces(const SparseMacGrid3D<4>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int q = c / g.nx;
    int j = q % g.ny;
    int k = q / g.ny;
    if (k > 0) faces.push_back(i + g.nx * (j + g.ny * k));
    if (k + 1 < g.nz) faces.push_back(i + g.nx * (j + g.ny * (k + 1)));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

} // namespace sparse3d
