#pragma once

#include "grid/multires_scalar_grid3d.h"

#include <algorithm>
#include <array>
#include <map>
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

  bool operator==(const MRFaceKey3D& o) const {
    return axis == o.axis &&
           fineX == o.fineX &&
           fineY == o.fineY &&
           fineZ == o.fineZ &&
           fineLengthA == o.fineLengthA &&
           fineLengthB == o.fineLengthB;
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

  std::vector<MRFaceKey3D> uFaces() const { return uFaceRefs(); }
  std::vector<MRFaceKey3D> vFaces() const { return vFaceRefs(); }
  std::vector<MRFaceKey3D> wFaces() const { return wFaceRefs(); }

  const std::vector<MRFaceKey3D>& uFaceRefs() const { return faceRefs(0); }
  const std::vector<MRFaceKey3D>& vFaceRefs() const { return faceRefs(1); }
  const std::vector<MRFaceKey3D>& wFaceRefs() const { return faceRefs(2); }

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
  mutable std::array<std::vector<MRFaceKey3D>, 3> faceCache;
  mutable std::array<bool, 3> faceCacheValid{{false, false, false}};
  mutable size_t faceCacheLayoutSignature = 0;

  static float getMap(const std::map<MRFaceKey3D, float>& m, const MRFaceKey3D& f) {
    auto it = m.find(f);
    return it == m.end() ? 0.0f : it->second;
  }

  const std::vector<MRFaceKey3D>& faceRefs(int axis) const {
    size_t sig = layoutSignature();
    if (sig != faceCacheLayoutSignature) {
      faceCacheLayoutSignature = sig;
      faceCacheValid = {{false, false, false}};
    }

    if (!faceCacheValid[axis]) {
      faceCache[axis] = enumerateFaces(axis);
      faceCacheValid[axis] = true;
    }
    return faceCache[axis];
  }

  size_t layoutSignature() const {
    size_t h = 1469598103934665603ull;
    hashCombine(h, layout.nx);
    hashCombine(h, layout.ny);
    hashCombine(h, layout.nz);
    hashCombine(h, static_cast<int>(layout.leaves().size()));
    for (const MRBlockKey3D& b : layout.leaves()) {
      hashCombine(h, b.level);
      hashCombine(h, b.bx);
      hashCombine(h, b.by);
      hashCombine(h, b.bz);
    }
    return h;
  }

  static void hashCombine(size_t& h, int v) {
    h ^= static_cast<size_t>(v) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
  }

  std::vector<MRFaceKey3D> enumerateFaces(int axis) const {
    std::vector<MRFaceKey3D> out;
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
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
    return out;
  }

  bool cellIntersectsDomainFine(int x0, int y0, int z0, int x1, int y1, int z1) const {
    return x0 < layout.nx && x1 > 0 &&
           y0 < layout.ny && y1 > 0 &&
           z0 < layout.nz && z1 > 0;
  }

  void insertUPatches(std::vector<MRFaceKey3D>& out, int fineX,
                      int y0, int y1, int z0, int z1) const {
    if (fineX < 0 || fineX > layout.nx) return;
    for (int z = z0; z < z1; ++z) {
      for (int y = y0; y < y1; ++y) {
        out.push_back(MRFaceKey3D{0, fineX, y, z, 1, 1});
      }
    }
  }

  void insertVPatches(std::vector<MRFaceKey3D>& out, int x0, int x1,
                      int fineY, int z0, int z1) const {
    if (fineY < 0 || fineY > layout.ny) return;
    for (int z = z0; z < z1; ++z) {
      for (int x = x0; x < x1; ++x) {
        out.push_back(MRFaceKey3D{1, x, fineY, z, 1, 1});
      }
    }
  }

  void insertWPatches(std::vector<MRFaceKey3D>& out, int x0, int x1,
                      int y0, int y1, int fineZ) const {
    if (fineZ < 0 || fineZ > layout.nz) return;
    for (int y = y0; y < y1; ++y) {
      for (int x = x0; x < x1; ++x) {
        out.push_back(MRFaceKey3D{2, x, y, fineZ, 1, 1});
      }
    }
  }
};
