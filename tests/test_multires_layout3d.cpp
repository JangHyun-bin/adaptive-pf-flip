#include "doctest.h"
#include "grid/multires_layout3d.h"

#include <set>
#include <tuple>

TEST_CASE("multires 3D layout: refine volume creates fine leaves and coarse bulk") {
  MRLayout3D<4> layout(32, 32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 8, 16, 24, 24);
  layout.enforceTwoToOneBalance();

  CHECK(layout.leafCount() > 0);
  CHECK(layout.countLevel(0) > 0);
  CHECK(layout.countLevel(1) > 0);
  CHECK(layout.leafAtFineCell(12, 12, 12).level == 0);
  CHECK(layout.leafAtFineCell(2, 2, 2).level == 1);
  CHECK(layout.isTwoToOneBalanced());
}

TEST_CASE("multires 3D layout: active leaves cover domain exactly once") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 12, 12, 12);
  layout.enforceTwoToOneBalance();

  std::set<std::tuple<int, int, int>> covered;
  for (const MRBlockKey3D& key : layout.leaves()) {
    int step = 1 << key.level;
    int x0 = key.bx * 4 * step;
    int y0 = key.by * 4 * step;
    int z0 = key.bz * 4 * step;
    for (int lz = 0; lz < 4; ++lz) {
      for (int ly = 0; ly < 4; ++ly) {
        for (int lx = 0; lx < 4; ++lx) {
          for (int zz = 0; zz < step; ++zz) {
            for (int yy = 0; yy < step; ++yy) {
              for (int xx = 0; xx < step; ++xx) {
                int x = x0 + lx * step + xx;
                int y = y0 + ly * step + yy;
                int z = z0 + lz * step + zz;
                if (x >= 0 && x < 16 && y >= 0 && y < 16 && z >= 0 && z < 16) {
                  CHECK(covered.insert({x, y, z}).second);
                }
              }
            }
          }
        }
      }
    }
  }
  CHECK(covered.size() == 16 * 16 * 16);
}

TEST_CASE("multires 3D layout: boundary leaves intersect non-multiple domain") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(16, 8, 8, 17, 10, 9);
  layout.enforceTwoToOneBalance();

  for (const MRBlockKey3D& key : layout.leaves()) {
    int s = layout.blockFineSize(key.level);
    int x0 = key.bx * s;
    int y0 = key.by * s;
    int z0 = key.bz * s;
    CHECK(x0 < 17);
    CHECK(x0 + s > 0);
    CHECK(y0 < 10);
    CHECK(y0 + s > 0);
    CHECK(z0 < 9);
    CHECK(z0 + s > 0);
  }
}

TEST_CASE("multires 3D layout: leaf lookup outside domain returns sentinel") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);

  const MRBlockKey3D missing{-1, -1, -1, -1};
  CHECK(layout.leafAtFineCell(-1, 0, 0) == missing);
  CHECK(layout.leafAtFineCell(17, 0, 0) == missing);
  CHECK(layout.leafAtFineCell(0, 10, 0) == missing);
  CHECK(layout.leafAtFineCell(0, 0, 9) == missing);
}
