#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d.h"
#include <cmath>
TEST_CASE("sparse projection removes divergence in fluid blob") {
  SparseMacGrid2D<8> g(32,32,1.0);
  // fluid blob [10,20)x[10,20); solid border ring of cells
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c = (i==0||i==g.nx-1||j==0||j==g.ny-1)?2 : ((i>=10&&i<20&&j>=10&&j<20)?1:0);
    if(c!=0) g.setCell(i,j,c);
  }
  // divergent u field on the fluid faces
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.u(i,j)=(float)i;
  spProjectStep(g, 1.0, 500, 1e-9);            // divergence -> solvePressure -> project
  // pressure stored sparsely: blob [10,20)^2 spans exactly blocks {1,2}x{1,2}
  CHECK(g.pf.activeBlockCount()==4);
  // post divergence in fluid ~0
  double mx=0; for(int j=10;j<20;++j)for(int i=10;i<20;++i){
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j)); mx=std::max(mx,std::abs(d)); }
  CHECK(mx < 1e-4);
}
