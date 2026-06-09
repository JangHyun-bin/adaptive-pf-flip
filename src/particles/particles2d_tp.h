#pragma once
#include <vector>
#include "math/vec2.h"
struct Particles2DTP {
  std::vector<Vec2> pos, vel;
  std::vector<unsigned char> type;  // 0=liquid, 1=gas
  size_t size() const { return pos.size(); }
  void add(const Vec2& p, const Vec2& v, unsigned char t){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
