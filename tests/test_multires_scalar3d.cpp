#include "doctest.h"
#include "grid/multires_scalar_grid3d.h"

#include <stdexcept>
#include <vector>

TEST_CASE("multires 3D scalar: write/read leaf cell without activating unrelated leaves") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 12, 12, 12);
  layout.enforceTwoToOneBalance();

  MRScalarGrid3D<4> g(layout);
  auto c = g.cellAtFineCell(5, 6, 7);
  g.ref(c) = 3.25f;

  CHECK(g.get(c) == doctest::Approx(3.25f));
  CHECK(g.activeBlockCount() == 1);
  CHECK(g.sampleCellCenter(5.5, 6.5, 7.5) == doctest::Approx(3.25).epsilon(1e-6));
}

TEST_CASE("multires 3D scalar: centers and sampling cross coarse-fine boundary") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();

  MRScalarGrid3D<4> g(layout);
  MRCellKey3D coarse = g.cellAtFineCell(8, 6, 6);
  CHECK(coarse.block.level == 1);
  CHECK(g.centerX(coarse) == doctest::Approx(9.0));
  CHECK(g.centerY(coarse) == doctest::Approx(7.0));
  CHECK(g.centerZ(coarse) == doctest::Approx(7.0));

  for (const MRCellKey3D& c : g.leafCells()) {
    double x = g.centerX(c);
    double y = g.centerY(c);
    double z = g.centerZ(c);
    g.ref(c) = static_cast<float>(2.0 * x - 0.5 * y + 0.25 * z);
  }

  CHECK(g.sampleCellCenter(7.5, 6.5, 6.5) == doctest::Approx(13.375).epsilon(1e-5));
  CHECK(g.sampleCellCenter(8.5, 6.5, 6.5) == doctest::Approx(16.25).epsilon(1e-5));
}

TEST_CASE("multires 3D scalar: out-of-range lookup returns invalid cell without storage") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid3D<4> g(layout);
  const MRBlockKey3D missing{-1, -1, -1, -1};
  MRCellKey3D c = g.cellAtFineCell(17, 0, 0);

  CHECK(c.block == missing);
  CHECK(c.lx == -1);
  CHECK(c.ly == -1);
  CHECK(c.lz == -1);
  CHECK(g.get(c) == doctest::Approx(0.0));
  CHECK_THROWS_AS(g.ref(c), std::out_of_range);
  CHECK_THROWS_AS(g.centerX(c), std::out_of_range);
  CHECK_THROWS_AS(g.centerY(c), std::out_of_range);
  CHECK_THROWS_AS(g.centerZ(c), std::out_of_range);
  CHECK(g.activeBlockCount() == 0);
}

TEST_CASE("multires 3D scalar: leaf cells omit padded boundary centers") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid3D<4> g(layout);
  std::vector<MRCellKey3D> cells = g.leafCells();

  CHECK(cells.size() == 225);
  for (const MRCellKey3D& c : cells) {
    CHECK(g.centerX(c) >= 0.0);
    CHECK(g.centerX(c) < 18.0);
    CHECK(g.centerY(c) >= 0.0);
    CHECK(g.centerY(c) < 10.0);
    CHECK(g.centerZ(c) >= 0.0);
    CHECK(g.centerZ(c) < 10.0);
  }
}

TEST_CASE("multires 3D scalar: physical sampling honors grid spacing") {
  MRLayout3D<4> layout(16, 16, 16, 0.5);
  layout.setCoarseEverywhere(0);

  MRScalarGrid3D<4> g(layout);
  MRCellKey3D c = g.cellAtFineCell(10, 4, 6);
  g.ref(c) = 7.0f;

  CHECK(g.centerX(c) == doctest::Approx(5.25));
  CHECK(g.centerY(c) == doctest::Approx(2.25));
  CHECK(g.centerZ(c) == doctest::Approx(3.25));
  CHECK(g.sampleCellCenter(5.25, 2.25, 3.25) == doctest::Approx(7.0));
}

TEST_CASE("multires 3D scalar: odd coarse boundary cells are valid if they intersect domain") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid3D<4> g(layout);
  MRCellKey3D edge = g.cellAtFineCell(16, 9, 8);
  CHECK(edge.block.level == 1);
  CHECK(g.centerX(edge) == doctest::Approx(17.0));
  CHECK(g.centerY(edge) == doctest::Approx(9.0));
  CHECK(g.centerZ(edge) == doctest::Approx(9.0));

  g.ref(edge) = 11.0f;
  CHECK(g.sampleCellCenter(16.5, 9.5, 8.5) == doctest::Approx(11.0));
}
