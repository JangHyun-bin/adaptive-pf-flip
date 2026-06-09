#include "doctest.h"
#include "math/vec2.h"
TEST_CASE("vec2 ops") {
  Vec2 a{1.0,2.0}, b{3.0,4.0};
  CHECK((a+b).x == doctest::Approx(4.0));
  CHECK((b-a).y == doctest::Approx(2.0));
  CHECK((a*2.0).x == doctest::Approx(2.0));
  CHECK(dot(a,b) == doctest::Approx(11.0));
  CHECK(a.length() == doctest::Approx(std::sqrt(5.0)));
}
