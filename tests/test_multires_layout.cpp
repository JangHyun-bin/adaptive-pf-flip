#include "doctest.h"
#include "grid/multires_layout2d.h"
#include <set>

TEST_CASE("multires layout: refine band creates fine leaves and coarse bulk") {
  MRLayout2D<8> layout(64, 64, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(24, 24, 40, 40);
  layout.enforceTwoToOneBalance();

  CHECK(layout.leafCount() > 0);
  CHECK(layout.countLevel(0) > 0);
  CHECK(layout.countLevel(1) > 0);
  CHECK(layout.leafAtFineCell(32, 32).level == 0);
  CHECK(layout.leafAtFineCell(4, 4).level == 1);
  CHECK(layout.isTwoToOneBalanced());
}

TEST_CASE("multires layout: active leaves cover domain exactly once") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  std::set<std::pair<int,int>> covered;
  for (const MRBlockKey& key : layout.leaves()) {
    int step = 1 << key.level;
    int x0 = key.bx * 8 * step;
    int y0 = key.by * 8 * step;
    for (int ly = 0; ly < 8; ++ly) {
      for (int lx = 0; lx < 8; ++lx) {
        for (int yy = 0; yy < step; ++yy) {
          for (int xx = 0; xx < step; ++xx) {
            int x = x0 + lx * step + xx;
            int y = y0 + ly * step + yy;
            if (x >= 0 && x < 32 && y >= 0 && y < 32) {
              CHECK(covered.insert({x,y}).second);
            }
          }
        }
      }
    }
  }
  CHECK(covered.size() == 32 * 32);
}

TEST_CASE("multires layout: refined boundary leaves intersect non-multiple domain") {
  MRLayout2D<8> layout(20, 18, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(16, 16, 20, 18);
  layout.enforceTwoToOneBalance();

  for (const MRBlockKey& key : layout.leaves()) {
    int s = layout.blockFineSize(key.level);
    int x0 = key.bx * s;
    int y0 = key.by * s;
    int x1 = x0 + s;
    int y1 = y0 + s;
    CHECK(x0 < 20);
    CHECK(x1 > 0);
    CHECK(y0 < 18);
    CHECK(y1 > 0);
  }
}

TEST_CASE("multires layout: leaf lookup outside domain returns sentinel") {
  MRLayout2D<8> layout(20, 18, 1.0);
  layout.setCoarseEverywhere(1);

  const MRBlockKey missing{-1, -1, -1};
  CHECK(layout.leafAtFineCell(-1, 0) == missing);
  CHECK(layout.leafAtFineCell(20, 0) == missing);
  CHECK(layout.leafAtFineCell(0, 18) == missing);
}
