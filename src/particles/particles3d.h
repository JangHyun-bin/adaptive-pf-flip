#pragma once
#include <vector>
#include "math/vec3.h"
struct Particles3D {
  std::vector<Vec3> pos, vel;
  std::vector<unsigned char> type;   // 0=liquid; Phase 1 all 0
  size_t size() const { return pos.size(); }
  void add(const Vec3& p, const Vec3& v, unsigned char t=0){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
