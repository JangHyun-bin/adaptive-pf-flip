#pragma once
#include <vector>
#include <cstddef>

// Treeless sparse block grid: dense flat array of block slots, blocks allocated on demand.
// Single-resolution, scalar float. B = block edge length (compile-time).
template<int B>
struct SparseBlockGrid2D {
  int nx, ny, nbx, nby;
  double dx, ox = 0.0, oy = 0.0;
  std::vector<int> blockmap;                  // bid -> pool index, or -1 (inactive)
  std::vector<std::vector<float>> pool;       // active block data (B*B each)

  SparseBlockGrid2D(int nx_, int ny_, double dx_)
    : nx(nx_), ny(ny_), nbx((nx_+B-1)/B), nby((ny_+B-1)/B), dx(dx_),
      blockmap((size_t)((nx_+B-1)/B)*((ny_+B-1)/B), -1) {}

  static constexpr int blockVol() { return B*B; }
  int bid(int bx, int by) const { return bx + nbx*by; }
  bool inBlockRange(int bx, int by) const { return bx>=0 && bx<nbx && by>=0 && by<nby; }
  bool blockActive(int bx, int by) const { return inBlockRange(bx,by) && blockmap[bid(bx,by)]>=0; }
  size_t activeBlockCount() const { size_t c=0; for(int m: blockmap) if(m>=0) ++c; return c; }
  size_t totalBlocks() const { return blockmap.size(); }

  int activateBlock(int bx, int by) {
    int b = bid(bx,by);
    if (blockmap[b] < 0) { blockmap[b] = (int)pool.size(); pool.emplace_back(blockVol(), 0.0f); }
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
    std::vector<int> v; for(size_t b=0;b<blockmap.size();++b) if(blockmap[b]>=0) v.push_back((int)b); return v;
  }
  void blockCoords(int b, int& bx, int& by) const { bx = b % nbx; by = b / nbx; }
};
