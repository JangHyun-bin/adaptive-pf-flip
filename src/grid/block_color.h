#pragma once
#include <vector>
#include "grid/sparse_block_grid2d.h"

inline int color4(int bx, int by){ return (bx & 1) + 2*(by & 1); }

template<int B>
std::vector<std::vector<int>> partitionByColor4(const SparseBlockGrid2D<B>& g){
  std::vector<std::vector<int>> buckets(4);
  for(int b: g.activeBlocks()){ int bx,by; g.blockCoords(b,bx,by); buckets[color4(bx,by)].push_back(b); }
  return buckets;
}
