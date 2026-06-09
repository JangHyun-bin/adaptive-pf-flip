#pragma once
#include <vector>
#include "math/vec3.h"
struct Particles3DTP {
  std::vector<Vec3> pos, vel;
  std::vector<unsigned char> type;  // 0=liquid,1=gas
  size_t size() const { return pos.size(); }
  void add(const Vec3& p, const Vec3& v, unsigned char t){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
