#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include <vector>
#include <cmath>

TEST_CASE("particle splat: sparse storage + matches uniform in active region") {
  const int NX=128, NY=128, B=8;
  SparseBlockGrid2D<B> g(NX,NY,1.0);
  std::vector<float> uni(NX*NY,0.0f);
  struct P{double x,y;}; std::vector<P> ps;
  for(int n=0;n<400;++n){ double a=0.0173*n, r=6.0*((n*37)%100)/100.0; ps.push_back({30+r*std::cos(a),30+r*std::sin(a)}); }
  auto splat=[&](auto setter){ for(auto& p: ps){ int i=(int)p.x,j=(int)p.y; double fx=p.x-i,fy=p.y-j;
    setter(i,j,(float)((1-fx)*(1-fy))); setter(i+1,j,(float)(fx*(1-fy))); setter(i,j+1,(float)((1-fx)*fy)); setter(i+1,j+1,(float)(fx*fy)); } };
  splat([&](int i,int j,float w){ if(i>=0&&i<NX&&j>=0&&j<NY) uni[i+NX*j]+=w; });
  splat([&](int i,int j,float w){ if(i>=0&&i<NX&&j>=0&&j<NY) g.ref(i,j)+=w; });
  CHECK(g.activeBlockCount() < 16);
  CHECK(g.activeBlockCount() > 0);
  double maxdiff=0; for(int j=0;j<NY;++j)for(int i=0;i<NX;++i) maxdiff=std::max(maxdiff,(double)std::abs(g.get(i,j)-uni[i+NX*j]));
  CHECK(maxdiff < 1e-6);
  CHECK(g.pool.size() == g.activeBlockCount());
}
