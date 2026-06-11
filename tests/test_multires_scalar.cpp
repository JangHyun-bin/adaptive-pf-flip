#include "doctest.h"
#include "grid/multires_scalar_grid2d.h"
#include <stdexcept>
#include <vector>

TEST_CASE("multires scalar: write/read leaf cell without activating unrelated leaves") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();

  MRScalarGrid2D<8> g(layout);
  auto c = g.cellAtFineCell(10, 10);
  g.ref(c) = 3.25f;

  CHECK(g.get(c) == doctest::Approx(3.25f));
  CHECK(g.activeBlockCount() == 1);
  CHECK(g.sampleCellCenter(10.5, 10.5) == doctest::Approx(3.25).epsilon(1e-6));
}

TEST_CASE("multires scalar: linear field samples geometric centers across coarse-fine boundary") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  MRScalarGrid2D<8> g(layout);
  MRCellKey coarse = g.cellAtFineCell(16, 12);
  CHECK(coarse.block.level == 1);
  CHECK(g.centerX(coarse) == doctest::Approx(17.0));
  CHECK(g.centerY(coarse) == doctest::Approx(13.0));

  for (const MRCellKey& c : g.leafCells()) {
    double x = g.centerX(c);
    double y = g.centerY(c);
    g.ref(c) = static_cast<float>(2.0 * x - 0.5 * y);
  }

  CHECK(g.sampleCellCenter(15.5, 12.5) == doctest::Approx(24.75).epsilon(1e-5));
  CHECK(g.sampleCellCenter(16.5, 12.5) == doctest::Approx(27.5).epsilon(1e-5));
}

TEST_CASE("multires scalar: out-of-range lookup returns invalid cell without storage") {
  MRLayout2D<8> layout(20, 18, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid2D<8> g(layout);
  const MRBlockKey missing{-1, -1, -1};
  MRCellKey c = g.cellAtFineCell(20, 0);

  CHECK(c.block == missing);
  CHECK(c.lx == -1);
  CHECK(c.ly == -1);
  CHECK(g.get(c) == doctest::Approx(0.0));
  CHECK_THROWS_AS(g.ref(c), std::out_of_range);
  CHECK(g.activeBlockCount() == 0);
}

TEST_CASE("multires scalar: leaf cells omit padded boundary centers") {
  MRLayout2D<8> layout(20, 18, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid2D<8> g(layout);
  std::vector<MRCellKey> cells = g.leafCells();

  CHECK(cells.size() == 90);
  for (const MRCellKey& c : cells) {
    CHECK(g.centerX(c) >= 0.0);
    CHECK(g.centerX(c) < 20.0);
    CHECK(g.centerY(c) >= 0.0);
    CHECK(g.centerY(c) < 18.0);
  }
}
