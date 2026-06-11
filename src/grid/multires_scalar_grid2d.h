#pragma once

#include "grid/multires_layout2d.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <map>
#include <stdexcept>
#include <vector>

struct MRCellKey {
  MRBlockKey block;
  int lx = 0;
  int ly = 0;
};

template<int B>
struct MRScalarGrid2D {
  MRLayout2D<B> layout;
  std::map<MRBlockKey, std::vector<float>> blocks;

  explicit MRScalarGrid2D(const MRLayout2D<B>& l) : layout(l) {}

  double cellSize(int level) const {
    if (level < 0) {
      throw std::out_of_range("MRScalarGrid2D::cellSize invalid level");
    }
    return layout.dx * (1 << level);
  }

  double centerX(const MRCellKey& c) const {
    requireValidStorageCell(c, "MRScalarGrid2D::centerX invalid cell");
    return (c.block.bx * B + c.lx + 0.5) * cellSize(c.block.level);
  }

  double centerY(const MRCellKey& c) const {
    requireValidStorageCell(c, "MRScalarGrid2D::centerY invalid cell");
    return (c.block.by * B + c.ly + 0.5) * cellSize(c.block.level);
  }

  MRCellKey cellAtFineCell(int x, int y) const {
    MRBlockKey b = layout.leafAtFineCell(x, y);
    if (b.level < 0) return {b, -1, -1};

    int step = 1 << b.level;
    int localFineX = x - b.bx * B * step;
    int localFineY = y - b.by * B * step;
    return {b, localFineX / step, localFineY / step};
  }

  float& ref(const MRCellKey& c) {
    requireValidStorageCell(c, "MRScalarGrid2D::ref invalid cell");

    auto& data = blocks[c.block];
    if (data.empty()) data.assign(B * B, 0.0f);
    return data[cellIndex(c)];
  }

  float get(const MRCellKey& c) const {
    if (!validStorageCell(c)) return 0.0f;

    auto it = blocks.find(c.block);
    if (it == blocks.end()) return 0.0f;
    return it->second[cellIndex(c)];
  }

  std::vector<MRCellKey> leafCells() const {
    std::vector<MRCellKey> cells;
    for (const auto& b : layout.leaves()) {
      for (int ly = 0; ly < B; ++ly) {
        for (int lx = 0; lx < B; ++lx) {
          MRCellKey c{b, lx, ly};
          if (cellIntersectsDomainFine(c)) cells.push_back(c);
        }
      }
    }
    return cells;
  }

  double sampleCellCenter(double x, double y) const {
    if (layout.nx <= 0 || layout.ny <= 0 || layout.dx <= 0.0) return 0.0;

    int fx = std::max(0, std::min(layout.nx - 1, static_cast<int>(std::floor(x / layout.dx))));
    int fy = std::max(0, std::min(layout.ny - 1, static_cast<int>(std::floor(y / layout.dx))));
    return get(cellAtFineCell(fx, fy));
  }

  size_t activeBlockCount() const { return blocks.size(); }

private:
  static size_t cellIndex(const MRCellKey& c) {
    return static_cast<size_t>(c.lx + B * c.ly);
  }

  void requireValidStorageCell(const MRCellKey& c, const char* message) const {
    if (!validStorageCell(c)) {
      throw std::out_of_range(message);
    }
  }

  bool blockIsLeaf(const MRBlockKey& b) const {
    const auto& leaves = layout.leaves();
    return std::find(leaves.begin(), leaves.end(), b) != leaves.end();
  }

  bool validCellAddress(const MRCellKey& c) const {
    return c.block.level >= 0 &&
           c.lx >= 0 && c.lx < B &&
           c.ly >= 0 && c.ly < B;
  }

  bool cellIntersectsDomainFine(const MRCellKey& c) const {
    int step = 1 << c.block.level;
    int x0 = c.block.bx * B * step + c.lx * step;
    int y0 = c.block.by * B * step + c.ly * step;
    int x1 = x0 + step;
    int y1 = y0 + step;
    return x0 < layout.nx && x1 > 0 && y0 < layout.ny && y1 > 0;
  }

  bool validStorageCell(const MRCellKey& c) const {
    return validCellAddress(c) &&
           blockIsLeaf(c.block) &&
           cellIntersectsDomainFine(c);
  }
};
