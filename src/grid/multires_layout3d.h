#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <tuple>
#include <vector>

struct MRBlockKey3D {
  int level = 0;
  int bx = 0;
  int by = 0;
  int bz = 0;

  bool operator==(const MRBlockKey3D& o) const {
    return level == o.level && bx == o.bx && by == o.by && bz == o.bz;
  }
};

inline bool operator<(const MRBlockKey3D& a, const MRBlockKey3D& b) {
  return std::tie(a.level, a.bx, a.by, a.bz) <
         std::tie(b.level, b.bx, b.by, b.bz);
}

// First 3D multires foundation mirrors Phase C's two-level layout:
// level 0 is fine, level 1 is coarse. Full multi-level balancing is deferred.
template<int B>
struct MRLayout3D {
  int nx, ny, nz;
  double dx;
  std::vector<MRBlockKey3D> leaf_blocks;

  MRLayout3D(int nx_, int ny_, int nz_, double dx_)
    : nx(nx_), ny(ny_), nz(nz_), dx(dx_) {}

  int blockFineSize(int level) const { return B * (1 << level); }
  int levelBlockCountX(int level) const {
    int s = blockFineSize(level);
    return (nx + s - 1) / s;
  }
  int levelBlockCountY(int level) const {
    int s = blockFineSize(level);
    return (ny + s - 1) / s;
  }
  int levelBlockCountZ(int level) const {
    int s = blockFineSize(level);
    return (nz + s - 1) / s;
  }

  void setCoarseEverywhere(int level) {
    leaf_blocks.clear();
    for (int bz = 0; bz < levelBlockCountZ(level); ++bz) {
      for (int by = 0; by < levelBlockCountY(level); ++by) {
        for (int bx = 0; bx < levelBlockCountX(level); ++bx) {
          leaf_blocks.push_back({level, bx, by, bz});
        }
      }
    }
  }

  void refineFineCellBox(int x0, int y0, int z0, int x1, int y1, int z1) {
    std::vector<MRBlockKey3D> next;
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int bx0 = key.bx * s;
      int by0 = key.by * s;
      int bz0 = key.bz * s;
      int bx1 = std::min(nx, bx0 + s);
      int by1 = std::min(ny, by0 + s);
      int bz1 = std::min(nz, bz0 + s);
      bool overlaps = bx0 < x1 && bx1 > x0 &&
                      by0 < y1 && by1 > y0 &&
                      bz0 < z1 && bz1 > z0;
      if (!overlaps || key.level == 0) {
        next.push_back(key);
        continue;
      }
      for (int cz = 0; cz < 2; ++cz) {
        for (int cy = 0; cy < 2; ++cy) {
          for (int cx = 0; cx < 2; ++cx) {
            MRBlockKey3D child{key.level - 1,
                               key.bx * 2 + cx,
                               key.by * 2 + cy,
                               key.bz * 2 + cz};
            if (intersectsDomain(child)) {
              next.push_back(child);
            }
          }
        }
      }
    }
    leaf_blocks = next;
    sortUnique();
  }

  void enforceTwoToOneBalance() {
    sortUnique();
  }

  bool isTwoToOneBalanced() const {
    for (const auto& a : leaf_blocks) {
      for (const auto& b : leaf_blocks) {
        if (a == b) continue;
        if (std::abs(a.level - b.level) > 1) return false;
      }
    }
    return true;
  }

  MRBlockKey3D leafAtFineCell(int x, int y, int z) const {
    if (x < 0 || x >= nx || y < 0 || y >= ny || z < 0 || z >= nz) {
      return {-1, -1, -1, -1};
    }
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int x0 = key.bx * s;
      int y0 = key.by * s;
      int z0 = key.bz * s;
      if (x >= x0 && x < x0 + s &&
          y >= y0 && y < y0 + s &&
          z >= z0 && z < z0 + s) {
        return key;
      }
    }
    return {-1, -1, -1, -1};
  }

  const std::vector<MRBlockKey3D>& leaves() const { return leaf_blocks; }
  size_t leafCount() const { return leaf_blocks.size(); }
  size_t countLevel(int level) const {
    size_t n = 0;
    for (const auto& key : leaf_blocks) {
      if (key.level == level) ++n;
    }
    return n;
  }

private:
  bool intersectsDomain(const MRBlockKey3D& key) const {
    int s = blockFineSize(key.level);
    int x0 = key.bx * s;
    int y0 = key.by * s;
    int z0 = key.bz * s;
    int x1 = x0 + s;
    int y1 = y0 + s;
    int z1 = z0 + s;
    int clipped_x0 = std::max(0, x0);
    int clipped_y0 = std::max(0, y0);
    int clipped_z0 = std::max(0, z0);
    int clipped_x1 = std::min(nx, x1);
    int clipped_y1 = std::min(ny, y1);
    int clipped_z1 = std::min(nz, z1);
    return clipped_x0 < clipped_x1 &&
           clipped_y0 < clipped_y1 &&
           clipped_z0 < clipped_z1;
  }

  void sortUnique() {
    std::sort(leaf_blocks.begin(), leaf_blocks.end());
    leaf_blocks.erase(std::unique(leaf_blocks.begin(), leaf_blocks.end()), leaf_blocks.end());
  }
};
