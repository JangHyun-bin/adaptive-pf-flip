#include "doctest.h"
#include "grid/sparse_mac_grid3d.h"

TEST_CASE("sparse 3D MAC: face extents, marker access, and clear lifecycle") {
  SparseMacGrid3D<4> g(8, 6, 5, 1.0);
  CHECK(g.uf.nx == 9);
  CHECK(g.uf.ny == 6);
  CHECK(g.uf.nz == 5);
  CHECK(g.vf.nx == 8);
  CHECK(g.vf.ny == 7);
  CHECK(g.vf.nz == 5);
  CHECK(g.wf.nx == 8);
  CHECK(g.wf.ny == 6);
  CHECK(g.wf.nz == 6);

  CHECK(g.uf.activeBlockCount() == 0);
  g.u(8, 2, 3) = 2.0f;
  g.v(2, 6, 3) = 3.0f;
  g.w(2, 3, 5) = 4.0f;
  CHECK(g.gu(8, 2, 3) == doctest::Approx(2.0f));
  CHECK(g.gv(2, 6, 3) == doctest::Approx(3.0f));
  CHECK(g.gw(2, 3, 5) == doctest::Approx(4.0f));

  g.setCell(2, 3, 4, 1);
  CHECK(g.cell(2, 3, 4) == 1);
  CHECK(g.cell(7, 5, 4) == 0);
  CHECK(g.inBounds(7, 5, 4));
  CHECK(!g.inBounds(8, 5, 4));

  g.clearAll();
  CHECK(g.uf.activeBlockCount() == 0);
  CHECK(g.gu(8, 2, 3) == doctest::Approx(0.0f));
  CHECK(g.cell(2, 3, 4) == 0);

  g.w(2, 3, 5) = 6.0f;
  CHECK(g.gw(2, 3, 5) == doctest::Approx(6.0f));
  CHECK(g.wf.activeBlockCount() == 1);
}

TEST_CASE("sparse 3D MAC: pressure cell block metrics mirror pressure field") {
  SparseMacGrid3D<4> g(16, 16, 16, 1.0);
  CHECK(g.activeCellBlocks() == 0);
  g.p(2, 2, 2) = 1.0f;
  g.p(10, 10, 10) = 2.0f;
  CHECK(g.activeCellBlocks() == 2);
  CHECK(g.totalCellBlocks() == g.pf.totalBlocks());
}
