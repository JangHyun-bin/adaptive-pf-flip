#pragma once

#include "grid/multires_scalar_grid3d.h"

#include <algorithm>
#include <map>
#include <set>
#include <tuple>
#include <vector>

struct MRFaceKey3D {
  int axis = 0;        // 0 = u/x-normal, 1 = v/y-normal, 2 = w/z-normal
  int fineX = 0;       // patch start in fine-grid coordinates
  int fineY = 0;
  int fineZ = 0;
  int fineLengthA = 1; // tangential fine-cell span
  int fineLengthB = 1;

  bool operator<(const MRFaceKey3D& o) const {
    return std::tie(axis, fineX, fineY, fineZ, fineLengthA, fineLengthB) <
           std::tie(o.axis, o.fineX, o.fineY, o.fineZ, o.fineLengthA, o.fineLengthB);
  }
};

template<int B>
struct MRMacGrid3D {
  MRLayout3D<B> layout;
  MRScalarGrid3D<B> p;
  MRScalarGrid3D<B> marker;
  std::map<MRFaceKey3D, float> ufield, vfield, wfield, mu, mv, mw;

  explicit MRMacGrid3D(const MRLayout3D<B>& l)
    : layout(l), p(l), marker(l) {}

  std::vector<MRFaceKey3D> uFaces() const { return enumerateFaces(0); }
  std::vector<MRFaceKey3D> vFaces() const { return enumerateFaces(1); }
  std::vector<MRFaceKey3D> wFaces() const { return enumerateFaces(2); }

  float& u(const MRFaceKey3D& f) { return ufield[f]; }
  float& v(const MRFaceKey3D& f) { return vfield[f]; }
  float& w(const MRFaceKey3D& f) { return wfield[f]; }
  float& mU(const MRFaceKey3D& f) { return mu[f]; }
  float& mV(const MRFaceKey3D& f) { return mv[f]; }
  float& mW(const MRFaceKey3D& f) { return mw[f]; }

  float gu(const MRFaceKey3D& f) const { return getMap(ufield, f); }
  float gv(const MRFaceKey3D& f) const { return getMap(vfield, f); }
  float gw(const MRFaceKey3D& f) const { return getMap(wfield, f); }
  float gmu(const MRFaceKey3D& f) const { return getMap(mu, f); }
  float gmv(const MRFaceKey3D& f) const { return getMap(mv, f); }
  float gmw(const MRFaceKey3D& f) const { return getMap(mw, f); }

private:
  static float getMap(const std::map<MRFaceKey3D, float>& m, const MRFaceKey3D& f) {
    auto it = m.find(f);
    return it == m.end() ? 0.0f : it->second;
  }

  std::vector<MRFaceKey3D> enumerateFaces(int axis) const {
    std::set<MRFaceKey3D> out;
    for (const MRBlockKey3D& b : layout.leaves()) {
      int step = 1 << b.level;
      int blockX0 = b.bx * B * step;
      int blockY0 = b.by * B * step;
      int blockZ0 = b.bz * B * step;

      for (int lz = 0; lz < B; ++lz) {
        for (int ly = 0; ly < B; ++ly) {
          for (int lx = 0; lx < B; ++lx) {
            int x0 = blockX0 + lx * step;
            int y0 = blockY0 + ly * step;
            int z0 = blockZ0 + lz * step;
            int x1 = x0 + step;
            int y1 = y0 + step;
            int z1 = z0 + step;
            if (!cellIntersectsDomainFine(x0, y0, z0, x1, y1, z1)) continue;

            int sx0 = std::max(0, x0);
            int sy0 = std::max(0, y0);
            int sz0 = std::max(0, z0);
            int sx1 = std::min(layout.nx, x1);
            int sy1 = std::min(layout.ny, y1);
            int sz1 = std::min(layout.nz, z1);

            if (axis == 0) {
              insertUPatches(out, x0, sy0, sy1, sz0, sz1);
              insertUPatches(out, std::min(x1, layout.nx), sy0, sy1, sz0, sz1);
            } else if (axis == 1) {
              insertVPatches(out, sx0, sx1, y0, sz0, sz1);
              insertVPatches(out, sx0, sx1, std::min(y1, layout.ny), sz0, sz1);
            } else {
              insertWPatches(out, sx0, sx1, sy0, sy1, z0);
              insertWPatches(out, sx0, sx1, sy0, sy1, std::min(z1, layout.nz));
            }
          }
        }
      }
    }
    return std::vector<MRFaceKey3D>(out.begin(), out.end());
  }

  bool cellIntersectsDomainFine(int x0, int y0, int z0, int x1, int y1, int z1) const {
    return x0 < layout.nx && x1 > 0 &&
           y0 < layout.ny && y1 > 0 &&
           z0 < layout.nz && z1 > 0;
  }

  void insertUPatches(std::set<MRFaceKey3D>& out, int fineX,
                      int y0, int y1, int z0, int z1) const {
    if (fineX < 0 || fineX > layout.nx) return;
    for (int z = z0; z < z1; ++z) {
      for (int y = y0; y < y1; ++y) {
        out.insert(MRFaceKey3D{0, fineX, y, z, 1, 1});
      }
    }
  }

  void insertVPatches(std::set<MRFaceKey3D>& out, int x0, int x1,
                      int fineY, int z0, int z1) const {
    if (fineY < 0 || fineY > layout.ny) return;
    for (int z = z0; z < z1; ++z) {
      for (int x = x0; x < x1; ++x) {
        out.insert(MRFaceKey3D{1, x, fineY, z, 1, 1});
      }
    }
  }

  void insertWPatches(std::set<MRFaceKey3D>& out, int x0, int x1,
                      int y0, int y1, int fineZ) const {
    if (fineZ < 0 || fineZ > layout.nz) return;
    for (int y = y0; y < y1; ++y) {
      for (int x = x0; x < x1; ++x) {
        out.insert(MRFaceKey3D{2, x, y, fineZ, 1, 1});
      }
    }
  }
};
