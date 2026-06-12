#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <tuple>
#include <vector>

struct MRBlockKey {
  int level = 0;
  int bx = 0;
  int by = 0;

  bool operator==(const MRBlockKey& o) const {
    return level == o.level && bx == o.bx && by == o.by;
  }
};

inline bool operator<(const MRBlockKey& a, const MRBlockKey& b) {
  return std::tie(a.level, a.bx, a.by) < std::tie(b.level, b.bx, b.by);
}

// Phase C Task 1 supports levels {0,1}: level 0 fine and level 1 coarse.
// Multi-level 2:1 balancing is intentionally deferred to a later phase.
template<int B>
struct MRLayout2D {
  int nx, ny;
  double dx;
  std::vector<MRBlockKey> leaf_blocks;

  MRLayout2D(int nx_, int ny_, double dx_) : nx(nx_), ny(ny_), dx(dx_) {}

  int blockFineSize(int level) const { return B * (1 << level); }
  int levelBlockCountX(int level) const {
    int s = blockFineSize(level);
    return (nx + s - 1) / s;
  }
  int levelBlockCountY(int level) const {
    int s = blockFineSize(level);
    return (ny + s - 1) / s;
  }

  void setCoarseEverywhere(int level) {
    leaf_blocks.clear();
    for (int by = 0; by < levelBlockCountY(level); ++by) {
      for (int bx = 0; bx < levelBlockCountX(level); ++bx) {
        leaf_blocks.push_back({level, bx, by});
      }
    }
  }

  void refineFineCellBox(int x0, int y0, int x1, int y1) {
    std::vector<MRBlockKey> next;
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int bx0 = key.bx * s;
      int by0 = key.by * s;
      int bx1 = std::min(nx, bx0 + s);
      int by1 = std::min(ny, by0 + s);
      bool overlaps = bx0 < x1 && bx1 > x0 && by0 < y1 && by1 > y0;
      if (!overlaps || key.level == 0) {
        next.push_back(key);
        continue;
      }
      for (int cy = 0; cy < 2; ++cy) {
        for (int cx = 0; cx < 2; ++cx) {
          MRBlockKey child{key.level - 1, key.bx * 2 + cx, key.by * 2 + cy};
          if (intersectsDomain(child)) {
            next.push_back(child);
          }
        }
      }
    }
    leaf_blocks = next;
    sortUnique();
  }

  void enforceTwoToOneBalance() {
    // With only levels {0,1}, one refinement pass already satisfies 2:1.
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

  MRBlockKey leafAtFineCell(int x, int y) const {
    if (x < 0 || x >= nx || y < 0 || y >= ny) return {-1, -1, -1};
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int x0 = key.bx * s;
      int y0 = key.by * s;
      if (x >= x0 && x < x0 + s && y >= y0 && y < y0 + s) return key;
    }
    return {-1, -1, -1};
  }

  const std::vector<MRBlockKey>& leaves() const { return leaf_blocks; }
  size_t leafCount() const { return leaf_blocks.size(); }
  size_t countLevel(int level) const {
    size_t n = 0;
    for (const auto& key : leaf_blocks) {
      if (key.level == level) ++n;
    }
    return n;
  }

private:
  bool intersectsDomain(const MRBlockKey& key) const {
    int s = blockFineSize(key.level);
    int x0 = key.bx * s;
    int y0 = key.by * s;
    int x1 = x0 + s;
    int y1 = y0 + s;
    int clipped_x0 = std::max(0, x0);
    int clipped_y0 = std::max(0, y0);
    int clipped_x1 = std::min(nx, x1);
    int clipped_y1 = std::min(ny, y1);
    return clipped_x0 < clipped_x1 && clipped_y0 < clipped_y1;
  }

  void sortUnique() {
    std::sort(leaf_blocks.begin(), leaf_blocks.end());
    leaf_blocks.erase(std::unique(leaf_blocks.begin(), leaf_blocks.end()), leaf_blocks.end());
  }
};
