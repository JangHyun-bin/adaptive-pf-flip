cmake_minimum_required(VERSION 3.16)
project(pfflip2d CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include_directories(external src)
enable_testing()
add_library(pfflip2d
  src/grid/uniform_grid2d.cpp
  src/transfer/transfer2d.cpp
  src/pressure/pressure2d.cpp
  src/advect/advect2d.cpp
  src/driver/sim2d.cpp)
add_executable(unit_tests
  tests/test_main.cpp
  tests/test_sanity.cpp
  tests/test_vec2.cpp
  tests/test_grid.cpp
  tests/test_particles.cpp
  tests/test_p2g.cpp
  tests/test_g2p.cpp
  tests/test_divergence.cpp
  tests/test_pressure.cpp
  tests/test_advect.cpp
  tests/test_sim.cpp)
target_link_libraries(unit_tests pfflip2d)
add_test(NAME unit_tests COMMAND unit_tests)
