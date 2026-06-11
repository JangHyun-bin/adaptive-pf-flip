#pragma once

#include "grid/multires_scalar_grid2d.h"

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
    for (const MRCellKey& c : p.leafCells()) {
      int step = 1 << c.block.level;
      int x0 = c.block.bx * B * step + c.lx * step;
      int y0 = c.block.by * B * step + c.ly * step;

      if (axis == 0) {
        for (int s = 0; s < step; ++s) {
          insertIfInDomain(out, MRFaceKey{0, x0, y0 + s, 1});
          insertIfInDomain(out, MRFaceKey{0, x0 + step, y0 + s, 1});
        }
      } else {
        for (int s = 0; s < step; ++s) {
          insertIfInDomain(out, MRFaceKey{1, x0 + s, y0, 1});
          insertIfInDomain(out, MRFaceKey{1, x0 + s, y0 + step, 1});
        }
      }
    }
    return std::vector<MRFaceKey>(out.begin(), out.end());
  }

  void insertIfInDomain(std::set<MRFaceKey>& out, const MRFaceKey& f) const {
    if (faceOverlapsDomain(f)) out.insert(f);
  }

  bool faceOverlapsDomain(const MRFaceKey& f) const {
    if (f.fineLength <= 0) return false;
    if (f.axis == 0) {
      return f.fineX >= 0 && f.fineX <= layout.nx &&
             f.fineY < layout.ny && f.fineY + f.fineLength > 0;
    }
    return f.axis == 1 &&
           f.fineY >= 0 && f.fineY <= layout.ny &&
           f.fineX < layout.nx && f.fineX + f.fineLength > 0;
  }
};
