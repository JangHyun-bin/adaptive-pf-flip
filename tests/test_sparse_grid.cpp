#include "doctest.h"
#include "grid/sparse_block_grid2d.h"

TEST_CASE("sparse grid allocate/access/sparsity") {
  SparseBlockGrid2D<8> g(64, 32, 1.0);      // 8x4 = 32 blocks total
  CHECK(g.nbx == 8); CHECK(g.nby == 4);
  CHECK(g.activeBlockCount() == 0);
  CHECK(g.get(10, 5) == doctest::Approx(0.0));
  g.ref(10, 5) = 3.5;
  CHECK(g.get(10, 5) == doctest::Approx(3.5));
  CHECK(g.activeBlockCount() == 1);
  g.ref(11, 6) = 1.0;                         // same block (10/8==11/8==1, 5/8==6/8==0)
  CHECK(g.activeBlockCount() == 1);
  g.ref(40, 20) = 2.0;                        // different block
  CHECK(g.activeBlockCount() == 2);
  CHECK(g.blockActive(1, 0));
  CHECK(!g.blockActive(0, 0));
}
