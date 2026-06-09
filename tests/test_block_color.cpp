#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include "grid/block_color.h"

TEST_CASE("4-color: same-color blocks are never 4-neighbors") {
  SparseBlockGrid2D<8> g(64,64,1.0);
  for(int by=0;by<g.nby;++by)for(int bx=0;bx<g.nbx;++bx) g.activateBlock(bx,by);
  auto buckets = partitionByColor4(g);
  CHECK(buckets.size()==4);
  for(int c=0;c<4;++c){
    for(int b: buckets[c]){ int bx,by; g.blockCoords(b,bx,by);
      int nb[4][2]={{bx+1,by},{bx-1,by},{bx,by+1},{bx,by-1}};
      for(auto& n: nb){ if(g.inBlockRange(n[0],n[1])) CHECK(color4(n[0],n[1])!=c); } }
  }
  size_t tot=0; for(auto& v: buckets) tot+=v.size();
  CHECK(tot == g.activeBlockCount());
}
