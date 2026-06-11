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

  double cellSize(int level) const { return layout.dx * (1 << level); }

  double centerX(const MRCellKey& c) const {
    return (c.block.bx * B + c.lx + 0.5) * cellSize(c.block.level);
  }

  double centerY(const MRCellKey& c) const {
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
    if (!validStorageCell(c)) {
      throw std::out_of_range("MRScalarGrid2D::ref invalid cell");
    }

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
          if (cellCenterInsideDomain(c)) cells.push_back(c);
        }
      }
    }
    return cells;
  }

  double sampleCellCenter(double x, double y) const {
    if (layout.nx <= 0 || layout.ny <= 0) return 0.0;

    int fx = std::max(0, std::min(layout.nx - 1, static_cast<int>(std::floor(x))));
    int fy = std::max(0, std::min(layout.ny - 1, static_cast<int>(std::floor(y))));
    return get(cellAtFineCell(fx, fy));
  }

  size_t activeBlockCount() const { return blocks.size(); }

private:
  static size_t cellIndex(const MRCellKey& c) {
    return static_cast<size_t>(c.lx + B * c.ly);
  }

  bool blockIsLeaf(const MRBlockKey& b) const {
    const auto& leaves = layout.leaves();
    return std::find(leaves.begin(), leaves.end(), b) != leaves.end();
  }

  bool cellCenterInsideDomain(const MRCellKey& c) const {
    double xmax = layout.nx * layout.dx;
    double ymax = layout.ny * layout.dx;
    double x = centerX(c);
    double y = centerY(c);
    return x >= 0.0 && x < xmax && y >= 0.0 && y < ymax;
  }

  bool validStorageCell(const MRCellKey& c) const {
    return c.block.level >= 0 &&
           c.lx >= 0 && c.lx < B &&
           c.ly >= 0 && c.ly < B &&
           blockIsLeaf(c.block) &&
           cellCenterInsideDomain(c);
  }
};
