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
  CHECK_THROWS_AS(g.centerX(c), std::out_of_range);
  CHECK_THROWS_AS(g.centerY(c), std::out_of_range);
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

TEST_CASE("multires scalar: physical sampling honors grid spacing") {
  MRLayout2D<8> layout(32, 32, 0.5);
  layout.setCoarseEverywhere(0);

  MRScalarGrid2D<8> g(layout);
  MRCellKey c = g.cellAtFineCell(10, 4);
  g.ref(c) = 7.0f;

  CHECK(g.centerX(c) == doctest::Approx(5.25));
  CHECK(g.centerY(c) == doctest::Approx(2.25));
  CHECK(g.sampleCellCenter(5.25, 2.25) == doctest::Approx(7.0));
}

TEST_CASE("multires scalar: odd coarse boundary cells are valid if they intersect domain") {
  MRLayout2D<8> layout(21, 17, 1.0);
  layout.setCoarseEverywhere(1);

  MRScalarGrid2D<8> g(layout);
  std::vector<MRCellKey> cells = g.leafCells();
  CHECK(cells.size() == 99);
  for (const MRCellKey& c : cells) {
    g.ref(c) = 1.0f;
  }

  MRCellKey edge = g.cellAtFineCell(20, 16);
  CHECK(edge.block.level == 1);
  CHECK(g.centerX(edge) == doctest::Approx(21.0));
  CHECK(g.centerY(edge) == doctest::Approx(17.0));

  g.ref(edge) = 11.0f;
  CHECK(g.sampleCellCenter(20.5, 16.5) == doctest::Approx(11.0));
}
