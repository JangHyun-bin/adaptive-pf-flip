#pragma once
#include <cmath>
struct Vec3 {
  double x=0.0, y=0.0, z=0.0;
  Vec3 operator+(const Vec3& o) const { return {x+o.x,y+o.y,z+o.z}; }
  Vec3 operator-(const Vec3& o) const { return {x-o.x,y-o.y,z-o.z}; }
  Vec3 operator*(double s) const { return {x*s,y*s,z*s}; }
  Vec3& operator+=(const Vec3& o){ x+=o.x;y+=o.y;z+=o.z; return *this; }
  double length() const { return std::sqrt(x*x+y*y+z*z); }
};
inline Vec3 operator*(double s, const Vec3& v){ return {v.x*s,v.y*s,v.z*s}; }
inline double dot(const Vec3& a, const Vec3& b){ return a.x*b.x+a.y*b.y+a.z*b.z; }
