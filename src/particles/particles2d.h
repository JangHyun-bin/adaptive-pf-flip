#pragma once
#include <vector>
#include "math/vec2.h"
struct Particles2D {
  std::vector<Vec2> pos, vel;
  size_t size() const { return pos.size(); }
  void add(const Vec2& p, const Vec2& vv) { pos.push_back(p); vel.push_back(vv); }
};
