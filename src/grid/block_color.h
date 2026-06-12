#pragma once
#include <vector>
#include "grid/sparse_block_grid2d.h"
#include "grid/sparse_block_grid3d.h"

inline int color4(int bx, int by){ return (bx & 1) + 2*(by & 1); }
inline int color8(int bx, int by, int bz){ return (bx & 1) + 2*(by & 1) + 4*(bz & 1); }

template<int B>
std::vector<std::vector<int>> partitionByColor4(const SparseBlockGrid2D<B>& g){
  std::vector<std::vector<int>> buckets(4);
  for(int b: g.activeBlockIds()){ int bx,by; g.blockCoords(b,bx,by); buckets[color4(bx,by)].push_back(b); }
  return buckets;
}

template<int B>
std::vector<std::vector<int>> partitionByColor8(const SparseBlockGrid3D<B>& g){
  std::vector<std::vector<int>> buckets(8);
  for(int b: g.activeBlockIds()){ int bx,by,bz; g.blockCoords(b,bx,by,bz); buckets[color8(bx,by,bz)].push_back(b); }
  return buckets;
}
