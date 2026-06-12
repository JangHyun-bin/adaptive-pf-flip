#pragma once
#include "grid/sparse_mac_grid2d.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <future>
#include <vector>

namespace sparse2d {

template<int B>
std::vector<int> collectCellsWithMarker(const SparseMacGrid2D<B>& g, int marker) {
  std::vector<int> cells;
  for (int b : g.mkf.activeBlockIds()) {
    int bx, by;
    g.mkf.blockCoords(b, bx, by);
    for (int ly = 0; ly < B; ++ly) {
      for (int lx = 0; lx < B; ++lx) {
        int i = bx * B + lx;
        int j = by * B + ly;
        if (g.inBounds(i, j) && g.cell(i, j) == marker) {
          cells.push_back(i + g.nx * j);
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

template<typename Fn>
void runColor4(size_t workItems, Fn&& fn) {
  if (workItems < 2048) {
    for (int color = 0; color < 4; ++color) fn(color);
    return;
  }
  std::array<std::future<void>, 4> jobs;
  for (int color = 0; color < 4; ++color) {
    jobs[(size_t)color] = std::async(std::launch::async, [&, color]() { fn(color); });
  }
  for (auto& job : jobs) job.get();
}

template<int B>
std::vector<int> collectProjectUFaces(const SparseMacGrid2D<B>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int j = c / g.nx;
    if (i > 0) faces.push_back(i + (g.nx + 1) * j);
    if (i + 1 < g.nx) faces.push_back((i + 1) + (g.nx + 1) * j);
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

template<int B>
std::vector<int> collectProjectVFaces(const SparseMacGrid2D<B>& g, const std::vector<int>& cells) {
  std::vector<int> faces;
  faces.reserve(cells.size() * 2);
  for (int c : cells) {
    int i = c % g.nx;
    int j = c / g.nx;
    if (j > 0) faces.push_back(i + g.nx * j);
    if (j + 1 < g.ny) faces.push_back(i + g.nx * (j + 1));
  }
  std::sort(faces.begin(), faces.end());
  faces.erase(std::unique(faces.begin(), faces.end()), faces.end());
  return faces;
}

template<int B>
float sampleU(const SparseMacGrid2D<B>& g, double px, double py) {
  int i0 = (int)std::floor(px);
  int j0 = (int)std::floor(py - 0.5);
  double fx = px - i0;
  double fy = (py - 0.5) - j0;
  auto v = [&](int i, int j) {
    return g.gu(std::max(0, std::min(g.nx, i)), std::max(0, std::min(g.ny - 1, j)));
  };
  return (float)((1 - fx) * (1 - fy) * v(i0, j0) +
                 fx * (1 - fy) * v(i0 + 1, j0) +
                 (1 - fx) * fy * v(i0, j0 + 1) +
                 fx * fy * v(i0 + 1, j0 + 1));
}

template<int B>
float sampleV(const SparseMacGrid2D<B>& g, double px, double py) {
  int i0 = (int)std::floor(px - 0.5);
  int j0 = (int)std::floor(py);
  double fx = (px - 0.5) - i0;
  double fy = py - j0;
  auto v = [&](int i, int j) {
    return g.gv(std::max(0, std::min(g.nx - 1, i)), std::max(0, std::min(g.ny, j)));
  };
  return (float)((1 - fx) * (1 - fy) * v(i0, j0) +
                 fx * (1 - fy) * v(i0 + 1, j0) +
                 (1 - fx) * fy * v(i0, j0 + 1) +
                 fx * fy * v(i0 + 1, j0 + 1));
}

} // namespace sparse2d
