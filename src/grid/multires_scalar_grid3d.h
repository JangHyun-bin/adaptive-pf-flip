#pragma once

#include "grid/multires_layout3d.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <map>
#include <stdexcept>
#include <vector>

struct MRCellKey3D {
  MRBlockKey3D block;
  int lx = 0;
  int ly = 0;
  int lz = 0;
};

template<int B>
struct MRScalarGrid3D {
  MRLayout3D<B> layout;
  std::map<MRBlockKey3D, std::vector<float>> blocks;

  explicit MRScalarGrid3D(const MRLayout3D<B>& l) : layout(l) {}

  double cellSize(int level) const {
    if (level < 0) {
      throw std::out_of_range("MRScalarGrid3D::cellSize invalid level");
    }
    return layout.dx * (1 << level);
  }

  double centerX(const MRCellKey3D& c) const {
    requireValidStorageCell(c, "MRScalarGrid3D::centerX invalid cell");
    return (c.block.bx * B + c.lx + 0.5) * cellSize(c.block.level);
  }

  double centerY(const MRCellKey3D& c) const {
    requireValidStorageCell(c, "MRScalarGrid3D::centerY invalid cell");
    return (c.block.by * B + c.ly + 0.5) * cellSize(c.block.level);
  }

  double centerZ(const MRCellKey3D& c) const {
    requireValidStorageCell(c, "MRScalarGrid3D::centerZ invalid cell");
    return (c.block.bz * B + c.lz + 0.5) * cellSize(c.block.level);
  }

  MRCellKey3D cellAtFineCell(int x, int y, int z) const {
    MRBlockKey3D b = layout.leafAtFineCell(x, y, z);
    if (b.level < 0) return {b, -1, -1, -1};

    int step = 1 << b.level;
    int localFineX = x - b.bx * B * step;
    int localFineY = y - b.by * B * step;
    int localFineZ = z - b.bz * B * step;
    return {b, localFineX / step, localFineY / step, localFineZ / step};
  }

  float& ref(const MRCellKey3D& c) {
    requireValidStorageCell(c, "MRScalarGrid3D::ref invalid cell");

    auto& data = blocks[c.block];
    if (data.empty()) data.assign(B * B * B, 0.0f);
    return data[cellIndex(c)];
  }

  float get(const MRCellKey3D& c) const {
    if (!validStorageCell(c)) return 0.0f;

    auto it = blocks.find(c.block);
    if (it == blocks.end()) return 0.0f;
    return it->second[cellIndex(c)];
  }

  std::vector<MRCellKey3D> leafCells() const {
    std::vector<MRCellKey3D> cells;
    for (const auto& b : layout.leaves()) {
      for (int lz = 0; lz < B; ++lz) {
        for (int ly = 0; ly < B; ++ly) {
          for (int lx = 0; lx < B; ++lx) {
            MRCellKey3D c{b, lx, ly, lz};
            if (cellIntersectsDomainFine(c)) cells.push_back(c);
          }
        }
      }
    }
    return cells;
  }

  double sampleCellCenter(double x, double y, double z) const {
    if (layout.nx <= 0 || layout.ny <= 0 || layout.nz <= 0 || layout.dx <= 0.0) {
      return 0.0;
    }

    int fx = std::max(0, std::min(layout.nx - 1, static_cast<int>(std::floor(x / layout.dx))));
    int fy = std::max(0, std::min(layout.ny - 1, static_cast<int>(std::floor(y / layout.dx))));
    int fz = std::max(0, std::min(layout.nz - 1, static_cast<int>(std::floor(z / layout.dx))));
    return get(cellAtFineCell(fx, fy, fz));
  }

  size_t activeBlockCount() const { return blocks.size(); }

private:
  static size_t cellIndex(const MRCellKey3D& c) {
    return static_cast<size_t>(c.lx + B * (c.ly + B * c.lz));
  }

  void requireValidStorageCell(const MRCellKey3D& c, const char* message) const {
    if (!validStorageCell(c)) {
      throw std::out_of_range(message);
    }
  }

  bool blockIsLeaf(const MRBlockKey3D& b) const {
    const auto& leaves = layout.leaves();
    return std::find(leaves.begin(), leaves.end(), b) != leaves.end();
  }

  bool validCellAddress(const MRCellKey3D& c) const {
    return c.block.level >= 0 &&
           c.lx >= 0 && c.lx < B &&
           c.ly >= 0 && c.ly < B &&
           c.lz >= 0 && c.lz < B;
  }

  bool cellIntersectsDomainFine(const MRCellKey3D& c) const {
    int step = 1 << c.block.level;
    int x0 = c.block.bx * B * step + c.lx * step;
    int y0 = c.block.by * B * step + c.ly * step;
    int z0 = c.block.bz * B * step + c.lz * step;
    int x1 = x0 + step;
    int y1 = y0 + step;
    int z1 = z0 + step;
    return x0 < layout.nx && x1 > 0 &&
           y0 < layout.ny && y1 > 0 &&
           z0 < layout.nz && z1 > 0;
  }

  bool validStorageCell(const MRCellKey3D& c) const {
    return validCellAddress(c) &&
           blockIsLeaf(c.block) &&
           cellIntersectsDomainFine(c);
  }
};
