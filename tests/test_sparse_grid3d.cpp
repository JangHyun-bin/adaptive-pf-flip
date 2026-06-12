#include "doctest.h"
#include "grid/sparse_block_grid3d.h"
#include <cmath>
#include <vector>

TEST_CASE("sparse 3D grid allocate/access/sparsity") {
  SparseBlockGrid3D<4> g(17, 10, 9, 1.0);
  CHECK(g.nbx == 5);
  CHECK(g.nby == 3);
  CHECK(g.nbz == 3);
  CHECK(g.activeBlockCount() == 0);
  CHECK(g.get(10, 5, 3) == doctest::Approx(0.0f));

  g.ref(10, 5, 3) = 3.5f;
  CHECK(g.get(10, 5, 3) == doctest::Approx(3.5f));
  CHECK(g.activeBlockCount() == 1);

  g.ref(11, 6, 2) = 1.0f;
  CHECK(g.activeBlockCount() == 1);

  g.ref(16, 9, 8) = 2.0f;
  CHECK(g.activeBlockCount() == 2);
  CHECK(g.blockActive(2, 1, 0));
  CHECK(g.blockActive(4, 2, 2));
  CHECK(!g.blockActive(0, 0, 0));
}

TEST_CASE("sparse 3D grid clear reuses block pool storage") {
  SparseBlockGrid3D<4> g(16, 16, 16, 1.0);
  g.ref(2, 3, 1) = 1.0f;
  g.ref(12, 8, 9) = 2.0f;
  REQUIRE(g.activeBlockCount() == 2);
  REQUIRE(g.pool.size() == 2);
  auto* firstStorage = g.pool.data();

  g.clear();

  CHECK(g.activeBlockCount() == 0);
  CHECK(g.pool.size() == 2);
  CHECK(g.pool.data() == firstStorage);
  CHECK(g.get(2, 3, 1) == doctest::Approx(0.0f));

  g.ref(12, 8, 9) = 7.0f;
  CHECK(g.activeBlockCount() == 1);
  CHECK(g.pool.size() == 2);
  CHECK(g.pool.data() == firstStorage);
  CHECK(g.get(12, 8, 9) == doctest::Approx(7.0f));
  CHECK(g.get(2, 3, 1) == doctest::Approx(0.0f));
}

TEST_CASE("sparse 3D 7-point Laplacian matches uniform reference in active region") {
  const int NX=16, NY=16, NZ=16, B=4;
  SparseBlockGrid3D<B> g(NX,NY,NZ,1.0);
  std::vector<float> uni(NX*NY*NZ, 0.0f);
  auto idx=[&](int i,int j,int k){ return i + NX*(j + NY*k); };
  for(int k=4;k<12;++k)for(int j=4;j<12;++j)for(int i=4;i<12;++i){
    float v=(float)(i*i + 2*j + 3*k);
    g.ref(i,j,k)=v;
    uni[idx(i,j,k)]=v;
  }
  auto lap=[&](auto getter,int i,int j,int k){
    return getter(i+1,j,k)+getter(i-1,j,k)+getter(i,j+1,k)+getter(i,j-1,k)+getter(i,j,k+1)+getter(i,j,k-1)-6*getter(i,j,k);
  };
  auto ug=[&](int i,int j,int k)->float{
    if(i<0||i>=NX||j<0||j>=NY||k<0||k>=NZ) return 0.0f;
    return uni[idx(i,j,k)];
  };
  auto sg=[&](int i,int j,int k)->float{ return g.get(i,j,k); };
  double maxdiff=0.0;
  for(int k=5;k<11;++k)for(int j=5;j<11;++j)for(int i=5;i<11;++i){
    maxdiff=std::max(maxdiff,(double)std::abs(lap(ug,i,j,k)-lap(sg,i,j,k)));
  }
  CHECK(maxdiff < 1e-5);
  CHECK(g.activeBlockCount() == 8);
}

TEST_CASE("sparse 3D active block iteration covers all written cells") {
  SparseBlockGrid3D<4> g(16,16,16,1.0);
  g.ref(3,3,3)=1.0f;
  g.ref(12,10,9)=2.0f;
  int seen=0;
  for(int b: g.activeBlockIds()){ int bx,by,bz; g.blockCoords(b,bx,by,bz);
    for(int lz=0;lz<4;++lz)for(int ly=0;ly<4;++ly)for(int lx=0;lx<4;++lx){
      int i=bx*4+lx, j=by*4+ly, k=bz*4+lz;
      if(g.get(i,j,k)!=0.0f) ++seen;
    }
  }
  CHECK(seen == 2);
}
