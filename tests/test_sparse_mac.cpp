#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
TEST_CASE("sparse MAC: splat activates only touched blocks; access; clear") {
  SparseMacGrid2D<8> g(64,64,1.0);                 // 8x8=64 cell-blocks
  CHECK(g.uf.activeBlockCount()==0);
  g.u(10,5) = 2.0f;  g.mu(10,5) = 1.0f;            // touches one u-block
  CHECK(g.gu(10,5)==doctest::Approx(2.0f));
  CHECK(g.uf.activeBlockCount()==1);
  g.setCell(10,5,1);                                // FLUID
  CHECK(g.cell(10,5)==1);
  CHECK(g.cell(60,60)==0);                          // inactive -> AIR(0)
  g.u(64,5) = 1.0f;  CHECK(g.gu(64,5)==doctest::Approx(1.0f));   // u extends to i=nx (staggered)
  g.v(5,64) = 1.0f;  CHECK(g.gv(5,64)==doctest::Approx(1.0f));   // v extends to j=ny (staggered)
  g.clearAll();
  CHECK(g.uf.activeBlockCount()==0);
  CHECK(g.gu(10,5)==doctest::Approx(0.0f));
  g.u(10,5) = 4.0f;                                 // write-after-clear lifecycle (clear -> ref -> get)
  CHECK(g.gu(10,5)==doctest::Approx(4.0f));
  CHECK(g.uf.activeBlockCount()==1);
}
