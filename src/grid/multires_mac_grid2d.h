#pragma once

#include "grid/multires_scalar_grid2d.h"

#include <algorithm>
#include <map>
#include <set>
#include <tuple>
#include <vector>

struct MRFaceKey {
  int axis = 0;       // 0 = u vertical face, 1 = v horizontal face
  int fineX = 0;      // segment start in fine-grid coordinates
  int fineY = 0;
  int fineLength = 1; // segment length in fine cells

  bool operator<(const MRFaceKey& o) const {
    return std::tie(axis, fineX, fineY, fineLength) <
           std::tie(o.axis, o.fineX, o.fineY, o.fineLength);
  }
};

template<int B>
struct MRMacGrid2D {
  MRLayout2D<B> layout;
  MRScalarGrid2D<B> p;
  MRScalarGrid2D<B> marker;
  std::map<MRFaceKey, float> ufield, vfield, mu, mv;

  explicit MRMacGrid2D(const MRLayout2D<B>& l)
    : layout(l), p(l), marker(l) {}

  std::vector<MRFaceKey> uFaces() const { return enumerateFaces(0); }
  std::vector<MRFaceKey> vFaces() const { return enumerateFaces(1); }

  float& u(const MRFaceKey& f) { return ufield[f]; }
  float& v(const MRFaceKey& f) { return vfield[f]; }
  float& mU(const MRFaceKey& f) { return mu[f]; }
  float& mV(const MRFaceKey& f) { return mv[f]; }

  float gu(const MRFaceKey& f) const {
    auto it = ufield.find(f);
    return it == ufield.end() ? 0.0f : it->second;
  }

  float gv(const MRFaceKey& f) const {
    auto it = vfield.find(f);
    return it == vfield.end() ? 0.0f : it->second;
  }

  float gmu(const MRFaceKey& f) const {
    auto it = mu.find(f);
    return it == mu.end() ? 0.0f : it->second;
  }

  float gmv(const MRFaceKey& f) const {
    auto it = mv.find(f);
    return it == mv.end() ? 0.0f : it->second;
  }

private:
  std::vector<MRFaceKey> enumerateFaces(int axis) const {
    std::set<MRFaceKey> out;
    for (const MRBlockKey& b : layout.leaves()) {
      int step = 1 << b.level;
      int blockX0 = b.bx * B * step;
      int blockY0 = b.by * B * step;

      for (int ly = 0; ly < B; ++ly) {
        for (int lx = 0; lx < B; ++lx) {
          int x0 = blockX0 + lx * step;
          int y0 = blockY0 + ly * step;
          int x1 = x0 + step;
          int y1 = y0 + step;
          if (!cellIntersectsDomainFine(x0, y0, x1, y1)) continue;

          if (axis == 0) {
            int segY0 = std::max(0, y0);
            int segY1 = std::min(layout.ny, y1);
            insertVerticalSegments(out, x0, segY0, segY1);
            insertVerticalSegments(out, std::min(x1, layout.nx), segY0, segY1);
          } else {
            int segX0 = std::max(0, x0);
            int segX1 = std::min(layout.nx, x1);
            insertHorizontalSegments(out, segX0, segX1, y0);
            insertHorizontalSegments(out, segX0, segX1, std::min(y1, layout.ny));
          }
        }
      }
    }
    return std::vector<MRFaceKey>(out.begin(), out.end());
  }

  bool cellIntersectsDomainFine(int x0, int y0, int x1, int y1) const {
    return x0 < layout.nx && x1 > 0 && y0 < layout.ny && y1 > 0;
  }

  void insertVerticalSegments(std::set<MRFaceKey>& out, int fineX, int y0, int y1) const {
    if (fineX < 0 || fineX > layout.nx) return;
    for (int y = y0; y < y1; ++y) {
      out.insert(MRFaceKey{0, fineX, y, 1});
    }
  }

  void insertHorizontalSegments(std::set<MRFaceKey>& out, int x0, int x1, int fineY) const {
    if (fineY < 0 || fineY > layout.ny) return;
    for (int x = x0; x < x1; ++x) {
      out.insert(MRFaceKey{1, x, fineY, 1});
    }
  }
};
