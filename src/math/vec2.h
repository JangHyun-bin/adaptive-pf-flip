#pragma once
#include <cmath>
struct Vec2 {
  double x = 0.0, y = 0.0;
  Vec2 operator+(const Vec2& o) const { return {x+o.x, y+o.y}; }
  Vec2 operator-(const Vec2& o) const { return {x-o.x, y-o.y}; }
  Vec2 operator*(double s) const { return {x*s, y*s}; }
  Vec2& operator+=(const Vec2& o) { x+=o.x; y+=o.y; return *this; }
  Vec2 operator/(double s) const { return {x/s, y/s}; }
  Vec2& operator-=(const Vec2& o) { x-=o.x; y-=o.y; return *this; }
  Vec2& operator*=(double s) { x*=s; y*=s; return *this; }
  double length() const { return std::sqrt(x*x + y*y); }
};
inline double dot(const Vec2& a, const Vec2& b) { return a.x*b.x + a.y*b.y; }
inline Vec2 operator*(double s, const Vec2& v) { return {v.x*s, v.y*s}; }
