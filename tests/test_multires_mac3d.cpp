#include "doctest.h"
#include "grid/multires_mac_grid3d.h"

#include <set>
#include <vector>

TEST_CASE("multires 3D MAC: coarse-fine u face is split into fine patches") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 8, 12, 12);
  layout.enforceTwoToOneBalance();

  MRMacGrid3D<4> g(layout);
  std::vector<MRFaceKey3D> ufaces = g.uFaces();
  std::set<MRFaceKey3D> faces(ufaces.begin(), ufaces.end());

  for (int fineZ = 4; fineZ < 12; ++fineZ) {
    for (int fineY = 4; fineY < 12; ++fineY) {
      CHECK(faces.count(MRFaceKey3D{0, 8, fineY, fineZ, 1, 1}) == 1);
    }
  }
}

TEST_CASE("multires 3D MAC: face keys are unique across all axes") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(4, 4, 4, 12, 12, 12);
  layout.enforceTwoToOneBalance();

  MRMacGrid3D<4> g(layout);
  std::set<MRFaceKey3D> keys;
  for (const MRFaceKey3D& f : g.uFaces()) CHECK(keys.insert(f).second);
  for (const MRFaceKey3D& f : g.vFaces()) CHECK(keys.insert(f).second);
  for (const MRFaceKey3D& f : g.wFaces()) CHECK(keys.insert(f).second);
}

TEST_CASE("multires 3D MAC: odd domains omit padded face patches") {
  MRLayout3D<4> layout(17, 10, 9, 1.0);
  layout.setCoarseEverywhere(1);

  MRMacGrid3D<4> g(layout);
  std::vector<MRFaceKey3D> ufaces = g.uFaces();
  std::vector<MRFaceKey3D> vfaces = g.vFaces();
  std::vector<MRFaceKey3D> wfaces = g.wFaces();
  std::set<MRFaceKey3D> ukeys(ufaces.begin(), ufaces.end());
  std::set<MRFaceKey3D> vkeys(vfaces.begin(), vfaces.end());
  std::set<MRFaceKey3D> wkeys(wfaces.begin(), wfaces.end());

  for (int fineZ = 0; fineZ < 9; ++fineZ) {
    for (int fineY = 0; fineY < 10; ++fineY) {
      CHECK(ukeys.count(MRFaceKey3D{0, 17, fineY, fineZ, 1, 1}) == 1);
    }
  }
  for (int fineZ = 0; fineZ < 9; ++fineZ) {
    for (int fineX = 0; fineX < 17; ++fineX) {
      CHECK(vkeys.count(MRFaceKey3D{1, fineX, 10, fineZ, 1, 1}) == 1);
    }
  }
  for (int fineY = 0; fineY < 10; ++fineY) {
    for (int fineX = 0; fineX < 17; ++fineX) {
      CHECK(wkeys.count(MRFaceKey3D{2, fineX, fineY, 9, 1, 1}) == 1);
    }
  }

  for (const MRFaceKey3D& f : ufaces) {
    CHECK(f.axis == 0);
    CHECK(f.fineLengthA == 1);
    CHECK(f.fineLengthB == 1);
    CHECK(f.fineX >= 0);
    CHECK(f.fineX <= 17);
    CHECK(f.fineY >= 0);
    CHECK(f.fineY + f.fineLengthA <= 10);
    CHECK(f.fineZ >= 0);
    CHECK(f.fineZ + f.fineLengthB <= 9);
  }

  for (const MRFaceKey3D& f : vfaces) {
    CHECK(f.axis == 1);
    CHECK(f.fineX >= 0);
    CHECK(f.fineX + f.fineLengthA <= 17);
    CHECK(f.fineY >= 0);
    CHECK(f.fineY <= 10);
    CHECK(f.fineZ >= 0);
    CHECK(f.fineZ + f.fineLengthB <= 9);
  }

  for (const MRFaceKey3D& f : wfaces) {
    CHECK(f.axis == 2);
    CHECK(f.fineX >= 0);
    CHECK(f.fineX + f.fineLengthA <= 17);
    CHECK(f.fineY >= 0);
    CHECK(f.fineY + f.fineLengthB <= 10);
    CHECK(f.fineZ >= 0);
    CHECK(f.fineZ <= 9);
  }
}

TEST_CASE("multires 3D MAC: face enumeration follows MAC layout if scalar layout diverges") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);

  MRMacGrid3D<4> g(layout);
  g.p.layout.leaf_blocks.clear();
  g.marker.layout.leaf_blocks.clear();

  std::vector<MRFaceKey3D> ufaces = g.uFaces();
  std::vector<MRFaceKey3D> vfaces = g.vFaces();
  std::vector<MRFaceKey3D> wfaces = g.wFaces();
  std::set<MRFaceKey3D> ukeys(ufaces.begin(), ufaces.end());
  std::set<MRFaceKey3D> vkeys(vfaces.begin(), vfaces.end());
  std::set<MRFaceKey3D> wkeys(wfaces.begin(), wfaces.end());

  CHECK(ukeys.count(MRFaceKey3D{0, 16, 0, 0, 1, 1}) == 1);
  CHECK(vkeys.count(MRFaceKey3D{1, 0, 16, 0, 1, 1}) == 1);
  CHECK(wkeys.count(MRFaceKey3D{2, 0, 0, 16, 1, 1}) == 1);
}

TEST_CASE("multires 3D MAC: absent reads do not allocate and mutating access allocates one field") {
  MRLayout3D<4> layout(16, 16, 16, 1.0);
  layout.setCoarseEverywhere(1);

  MRMacGrid3D<4> g(layout);
  MRFaceKey3D uf{0, 0, 0, 0, 1, 1};
  MRFaceKey3D vf{1, 0, 0, 0, 1, 1};
  MRFaceKey3D wf{2, 0, 0, 0, 1, 1};

  CHECK(g.gu(uf) == doctest::Approx(0.0f));
  CHECK(g.gv(vf) == doctest::Approx(0.0f));
  CHECK(g.gw(wf) == doctest::Approx(0.0f));
  CHECK(g.gmu(uf) == doctest::Approx(0.0f));
  CHECK(g.gmv(vf) == doctest::Approx(0.0f));
  CHECK(g.gmw(wf) == doctest::Approx(0.0f));
  CHECK(g.ufield.empty());
  CHECK(g.vfield.empty());
  CHECK(g.wfield.empty());
  CHECK(g.mu.empty());
  CHECK(g.mv.empty());
  CHECK(g.mw.empty());

  g.u(uf) = 2.0f;
  CHECK(g.ufield.size() == 1);
  CHECK(g.gu(uf) == doctest::Approx(2.0f));

  g.v(vf) = 3.0f;
  CHECK(g.vfield.size() == 1);
  CHECK(g.gv(vf) == doctest::Approx(3.0f));

  g.w(wf) = 4.0f;
  CHECK(g.wfield.size() == 1);
  CHECK(g.gw(wf) == doctest::Approx(4.0f));

  g.mU(uf) = 5.0f;
  CHECK(g.mu.size() == 1);
  CHECK(g.gmu(uf) == doctest::Approx(5.0f));

  g.mV(vf) = 6.0f;
  CHECK(g.mv.size() == 1);
  CHECK(g.gmv(vf) == doctest::Approx(6.0f));

  g.mW(wf) = 7.0f;
  CHECK(g.mw.size() == 1);
  CHECK(g.gmw(wf) == doctest::Approx(7.0f));
}
