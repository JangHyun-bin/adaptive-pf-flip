#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include <vector>
#include <cmath>

TEST_CASE("sparse 5-point Laplacian matches uniform reference in active region") {
  const int NX=24, NY=24, B=8;
  SparseBlockGrid2D<B> g(NX,NY,1.0);
  std::vector<float> uni(NX*NY, 0.0f);
  for(int j=4;j<20;++j)for(int i=4;i<20;++i){ float v=(float)(i*i + 2*j); g.ref(i,j)=v; uni[i+NX*j]=v; }
  auto lap=[&](auto getter,int i,int j){ return getter(i+1,j)+getter(i-1,j)+getter(i,j+1)+getter(i,j-1)-4*getter(i,j); };
  auto ug=[&](int i,int j)->float{ if(i<0||i>=NX||j<0||j>=NY) return 0.f; return uni[i+NX*j]; };
  auto sg=[&](int i,int j)->float{ return g.get(i,j); };
  double maxdiff=0;
  for(int j=5;j<19;++j)for(int i=5;i<19;++i) maxdiff=std::max(maxdiff,(double)std::abs(lap(ug,i,j)-lap(sg,i,j)));
  CHECK(maxdiff < 1e-5);
  CHECK(g.activeBlockCount() <= 9);
}

TEST_CASE("iterate active blocks covers all written cells") {
  SparseBlockGrid2D<8> g(32,32,1.0);
  g.ref(3,3)=1; g.ref(20,20)=2;
  int seen=0;
  for(int b: g.activeBlocks()){ int bx,by; g.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx, j=by*8+ly; if(g.get(i,j)!=0.f) ++seen; } }
  CHECK(seen == 2);
}
