#pragma once
#include <vector>
#include <cstddef>
#include <algorithm>
#include <array>

// Treeless sparse block grid: dense flat array of block slots, blocks allocated on demand.
// Single-resolution, scalar float. B = block edge length (compile-time).
template<int B>
struct SparseBlockGrid2D {
  int nx, ny, nbx, nby;
  double dx, ox = 0.0, oy = 0.0;
  std::vector<int> blockmap;                  // bid -> pool index, or -1 (inactive)
  using Block = std::array<float, B*B>;
  std::vector<Block> pool;                    // reusable block storage; size is high-water mark
  std::vector<int> active_block_ids;          // active block ids in allocation order

  SparseBlockGrid2D(int nx_, int ny_, double dx_)
    : nx(nx_), ny(ny_), nbx((nx_+B-1)/B), nby((ny_+B-1)/B), dx(dx_),
      blockmap((size_t)((nx_+B-1)/B)*((ny_+B-1)/B), -1) {}

  static constexpr int blockVol() { return B*B; }
  int bid(int bx, int by) const { return bx + nbx*by; }
  bool inBlockRange(int bx, int by) const { return bx>=0 && bx<nbx && by>=0 && by<nby; }
  bool blockActive(int bx, int by) const { return inBlockRange(bx,by) && blockmap[bid(bx,by)]>=0; }
  size_t activeBlockCount() const { return active_block_ids.size(); }
  size_t totalBlocks() const { return blockmap.size(); }

  int activateBlock(int bx, int by) {
    int b = bid(bx,by);
    if (blockmap[b] < 0) {
      int pi = (int)active_block_ids.size();
      blockmap[b] = pi;
      active_block_ids.push_back(b);
      if (pi == (int)pool.size()) pool.emplace_back();
      pool[pi].fill(0.0f);
    }
    return blockmap[b];
  }
  float& ref(int i, int j) {
    int bx=i/B, by=j/B, pi=activateBlock(bx,by);
    return pool[pi][(i%B) + B*(j%B)];
  }
  float get(int i, int j) const {
    if (i<0||i>=nx||j<0||j>=ny) return 0.0f;
    int bx=i/B, by=j/B, m=blockmap[bid(bx,by)];
    if (m<0) return 0.0f;
    return pool[m][(i%B) + B*(j%B)];
  }
  std::vector<int> activeBlocks() const {
    return active_block_ids;
  }
  const std::vector<int>& activeBlockIds() const { return active_block_ids; }
  void blockCoords(int b, int& bx, int& by) const { bx = b % nbx; by = b / nbx; }
  void clear() {
    for (int b : active_block_ids) blockmap[(size_t)b] = -1;
    active_block_ids.clear();
  }
};
