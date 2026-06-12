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

TEST_CASE("8-color: same-color blocks are never 6-neighbors") {
  SparseBlockGrid3D<4> g(16,12,8,1.0);
  for(int bz=0;bz<g.nbz;++bz)for(int by=0;by<g.nby;++by)for(int bx=0;bx<g.nbx;++bx) g.activateBlock(bx,by,bz);
  auto buckets = partitionByColor8(g);
  CHECK(buckets.size()==8);
  for(int c=0;c<8;++c){
    for(int b: buckets[c]){ int bx,by,bz; g.blockCoords(b,bx,by,bz);
      int nb[6][3]={{bx+1,by,bz},{bx-1,by,bz},{bx,by+1,bz},{bx,by-1,bz},{bx,by,bz+1},{bx,by,bz-1}};
      for(auto& n: nb){ if(g.inBlockRange(n[0],n[1],n[2])) CHECK(color8(n[0],n[1],n[2])!=c); } }
  }
  size_t tot=0; for(auto& v: buckets) tot+=v.size();
  CHECK(tot == g.activeBlockCount());
}
