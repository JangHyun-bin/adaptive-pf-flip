#pragma once
#include <vector>
#include "math/vec3.h"
struct Particles3DTP {
  std::vector<Vec3> pos, vel;
  std::vector<unsigned char> type;  // 0=liquid,1=gas
  size_t size() const { return pos.size(); }
  void add(const Vec3& p, const Vec3& v, unsigned char t){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
  template<class Predicate>
  size_t eraseIf(Predicate shouldErase) {
    size_t write = 0;
    size_t removed = 0;
    for (size_t read = 0; read < size(); ++read) {
      if (shouldErase(read)) {
        ++removed;
        continue;
      }
      if (write != read) {
        pos[write] = pos[read];
        vel[write] = vel[read];
        type[write] = type[read];
      }
      ++write;
    }
    pos.resize(write);
    vel.resize(write);
    type.resize(write);
    return removed;
  }
};
