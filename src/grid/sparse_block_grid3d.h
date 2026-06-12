#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <vector>

// Treeless sparse block grid for 3D scalar float fields.
// Single-resolution; blocks are allocated on demand and reused across clear().
template<int B>
struct SparseBlockGrid3D {
  int nx, ny, nz, nbx, nby, nbz;
  double dx, ox = 0.0, oy = 0.0, oz = 0.0;
  std::vector<int> blockmap;                  // bid -> pool index, or -1 (inactive)
  using Block = std::array<float, B*B*B>;
  std::vector<Block> pool;                    // reusable block storage; size is high-water mark
  std::vector<int> active_block_ids;          // active block ids in allocation order

  SparseBlockGrid3D(int nx_, int ny_, int nz_, double dx_)
    : nx(nx_), ny(ny_), nz(nz_),
      nbx((nx_+B-1)/B), nby((ny_+B-1)/B), nbz((nz_+B-1)/B), dx(dx_),
      blockmap((size_t)((nx_+B-1)/B)*((ny_+B-1)/B)*((nz_+B-1)/B), -1) {}

  static constexpr int blockVol() { return B*B*B; }
  int bid(int bx, int by, int bz) const { return bx + nbx*(by + nby*bz); }
  bool inBlockRange(int bx, int by, int bz) const {
    return bx>=0 && bx<nbx && by>=0 && by<nby && bz>=0 && bz<nbz;
  }
  bool blockActive(int bx, int by, int bz) const {
    return inBlockRange(bx,by,bz) && blockmap[bid(bx,by,bz)]>=0;
  }
  size_t activeBlockCount() const { return active_block_ids.size(); }
  size_t totalBlocks() const { return blockmap.size(); }

  int activateBlock(int bx, int by, int bz) {
    int b = bid(bx,by,bz);
    if (blockmap[b] < 0) {
      int pi = (int)active_block_ids.size();
      blockmap[b] = pi;
      active_block_ids.push_back(b);
      if (pi == (int)pool.size()) pool.emplace_back();
      pool[pi].fill(0.0f);
    }
    return blockmap[b];
  }

  float& ref(int i, int j, int k) {
    int bx=i/B, by=j/B, bz=k/B, pi=activateBlock(bx,by,bz);
    return pool[pi][(i%B) + B*((j%B) + B*(k%B))];
  }
  float get(int i, int j, int k) const {
    if (i<0||i>=nx||j<0||j>=ny||k<0||k>=nz) return 0.0f;
    int bx=i/B, by=j/B, bz=k/B, m=blockmap[bid(bx,by,bz)];
    if (m<0) return 0.0f;
    return pool[m][(i%B) + B*((j%B) + B*(k%B))];
  }
  std::vector<int> activeBlocks() const { return active_block_ids; }
  const std::vector<int>& activeBlockIds() const { return active_block_ids; }
  void blockCoords(int b, int& bx, int& by, int& bz) const {
    bx = b % nbx;
    int t = b / nbx;
    by = t % nby;
    bz = t / nby;
  }
  void clear() {
    for (int b : active_block_ids) blockmap[(size_t)b] = -1;
    active_block_ids.clear();
  }
};
