#include "doctest.h"
#include "grid/multires_mac_grid2d.h"

#include <set>
#include <vector>

TEST_CASE("multires MAC: coarse-fine vertical face is split into fine segments") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  MRMacGrid2D<8> g(layout);
  std::vector<MRFaceKey> ufaces = g.uFaces();
  std::set<MRFaceKey> faces(ufaces.begin(), ufaces.end());

  for (int fineY = 8; fineY < 24; ++fineY) {
    CHECK(faces.count(MRFaceKey{0, 16, fineY, 1}) == 1);
  }
}

TEST_CASE("multires MAC: face keys are unique") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();

  MRMacGrid2D<8> g(layout);
  std::set<MRFaceKey> keys;
  for (const MRFaceKey& f : g.uFaces()) CHECK(keys.insert(f).second);
  for (const MRFaceKey& f : g.vFaces()) CHECK(keys.insert(f).second);
}

TEST_CASE("multires MAC: odd domains omit padded face segments") {
  MRLayout2D<8> layout(21, 17, 1.0);
  layout.setCoarseEverywhere(1);

  MRMacGrid2D<8> g(layout);

  for (const MRFaceKey& f : g.uFaces()) {
    CHECK(f.axis == 0);
    CHECK(f.fineLength == 1);
    CHECK(f.fineX >= 0);
    CHECK(f.fineX <= 21);
    CHECK(f.fineY >= 0);
    CHECK(f.fineY + f.fineLength <= 17);
  }

  for (const MRFaceKey& f : g.vFaces()) {
    CHECK(f.axis == 1);
    CHECK(f.fineLength == 1);
    CHECK(f.fineX >= 0);
    CHECK(f.fineX + f.fineLength <= 21);
    CHECK(f.fineY >= 0);
    CHECK(f.fineY <= 17);
  }
}

TEST_CASE("multires MAC: absent reads do not allocate and mutating access allocates one field") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);

  MRMacGrid2D<8> g(layout);
  MRFaceKey uf{0, 0, 0, 1};
  MRFaceKey vf{1, 0, 0, 1};

  CHECK(g.gu(uf) == doctest::Approx(0.0f));
  CHECK(g.gv(vf) == doctest::Approx(0.0f));
  CHECK(g.gmu(uf) == doctest::Approx(0.0f));
  CHECK(g.gmv(vf) == doctest::Approx(0.0f));
  CHECK(g.ufield.empty());
  CHECK(g.vfield.empty());
  CHECK(g.mu.empty());
  CHECK(g.mv.empty());

  g.u(uf) = 2.0f;
  CHECK(g.ufield.size() == 1);
  CHECK(g.vfield.empty());
  CHECK(g.mu.empty());
  CHECK(g.mv.empty());
  CHECK(g.gu(uf) == doctest::Approx(2.0f));

  g.v(vf) = 3.0f;
  CHECK(g.vfield.size() == 1);
  CHECK(g.gv(vf) == doctest::Approx(3.0f));

  g.mU(uf) = 4.0f;
  CHECK(g.mu.size() == 1);
  CHECK(g.gmu(uf) == doctest::Approx(4.0f));

  g.mV(vf) = 5.0f;
  CHECK(g.mv.size() == 1);
  CHECK(g.gmv(vf) == doctest::Approx(5.0f));
}
