cmake_minimum_required(VERSION 3.16)
project(pfflip2d CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include_directories(external src)
enable_testing()
add_library(pfflip2d
  src/grid/uniform_grid2d.cpp
  src/driver/sparse_ops2d.cpp
  src/driver/sparse_ops2d_tp.cpp
  src/driver/sparse_ops3d.cpp
  src/driver/sparse_ops3d_tp.cpp
  src/driver/interface_diagnostics3d.cpp
  src/driver/multires_ops2d_tp.cpp
  src/driver/multires_ops3d_tp.cpp
  src/driver/multires_sim2d_tp.cpp
  src/driver/multires_sim3d_tp.cpp
  src/driver/sparse_sim2d.cpp
  src/driver/sparse_sim3d.cpp
  src/driver/sparse_sim2d_tp.cpp
  src/driver/sparse_sim3d_tp.cpp
  src/transfer/transfer2d.cpp
  src/transfer/transfer2d_tp.cpp
  src/transfer/transfer3d.cpp
  src/transfer/transfer3d_tp.cpp
  src/pressure/multires_pressure2d.cpp
  src/pressure/multires_pressure3d.cpp
  src/pressure/pressure2d.cpp
  src/pressure/pressure2d_vc.cpp
  src/pressure/pressure3d.cpp
  src/pressure/pressure3d_vc.cpp
  src/advect/advect2d.cpp
  src/advect/advect3d.cpp
  src/driver/sim2d.cpp
  src/driver/sim3d.cpp
  src/driver/sim2d_tp.cpp
  src/driver/sim3d_tp.cpp)
add_executable(unit_tests
  tests/test_main.cpp
  tests/test_sanity.cpp
  tests/test_vec2.cpp
  tests/test_secondary_particles3d.cpp
  tests/test_grid.cpp
  tests/test_particles.cpp
  tests/test_p2g.cpp
  tests/test_g2p.cpp
  tests/test_divergence.cpp
  tests/test_pressure.cpp
  tests/test_advect.cpp
  tests/test_sim.cpp
  tests/test_grid3d.cpp
  tests/test_transfer3d.cpp
  tests/test_sparse_transfer3d.cpp
  tests/test_pressure3d.cpp
  tests/test_advect3d.cpp
  tests/test_viscosity.cpp
  tests/test_sim3d.cpp
  tests/test_phasefield.cpp
  tests/test_transfer_tp.cpp
  tests/test_pressure_vc.cpp
  tests/test_sim_tp.cpp
  tests/test_rt.cpp
  tests/test_transfer3d_tp.cpp
  tests/test_pressure3d_vc.cpp
  tests/test_sparse_transfer3d_tp.cpp
  tests/test_sparse_vc3d.cpp
  tests/test_sim3d_tp.cpp
  tests/test_multires_layout.cpp
  tests/test_multires_layout3d.cpp
  tests/test_multires_scalar.cpp
  tests/test_multires_scalar3d.cpp
  tests/test_multires_mac.cpp
  tests/test_multires_mac3d.cpp
  tests/test_multires_transfer_tp.cpp
  tests/test_multires_transfer3d_tp.cpp
  tests/test_multires_pressure.cpp
  tests/test_multires_pressure3d.cpp
  tests/test_multires_sim_tp.cpp
  tests/test_multires_sim3d_tp.cpp
  tests/test_sparse_grid.cpp
  tests/test_sparse_grid3d.cpp
  tests/test_sparse_stencil.cpp
  tests/test_block_color.cpp
  tests/test_sparse_splat.cpp
  tests/test_sparse_mac.cpp
  tests/test_sparse_mac3d.cpp
  tests/test_sparse_pressure.cpp
  tests/test_sparse_pressure3d.cpp
  tests/test_sparse_sim.cpp
  tests/test_sparse_sim3d.cpp
  tests/test_sparse_sim3d_tp.cpp
  tests/test_sparse_transfer_tp.cpp
  tests/test_sparse_vc.cpp
  tests/test_sparse_sim_tp.cpp
  tests/test_sparse_bubble.cpp)
target_link_libraries(unit_tests pfflip2d)
add_test(NAME unit_tests COMMAND unit_tests)
add_executable(run_dambreak apps/run_dambreak.cpp)
target_link_libraries(run_dambreak pfflip2d)
add_executable(run_dambreak3d apps/run_dambreak3d.cpp)
target_link_libraries(run_dambreak3d pfflip2d)
add_executable(run_rt2d apps/run_rt2d.cpp)
target_link_libraries(run_rt2d pfflip2d)
add_executable(run_rt3d apps/run_rt3d.cpp)
target_link_libraries(run_rt3d pfflip2d)
add_executable(dump_render apps/dump_render.cpp)
target_link_libraries(dump_render pfflip2d)
add_executable(run_sparse_dambreak apps/run_sparse_dambreak.cpp)
target_link_libraries(run_sparse_dambreak pfflip2d)
add_executable(run_sparse_bubble apps/run_sparse_bubble.cpp)
target_link_libraries(run_sparse_bubble pfflip2d)
add_executable(run_sparse_rt3d apps/run_sparse_rt3d.cpp)
target_link_libraries(run_sparse_rt3d pfflip2d)
add_executable(run_sparse_bubble3d apps/run_sparse_bubble3d.cpp)
target_link_libraries(run_sparse_bubble3d pfflip2d)
add_executable(validate_sparse3d_tp apps/validate_sparse3d_tp.cpp)
target_link_libraries(validate_sparse3d_tp pfflip2d)
add_executable(validate_multires3d_tp apps/validate_multires3d_tp.cpp)
target_link_libraries(validate_multires3d_tp pfflip2d)
add_executable(validate_surface_tension3d apps/validate_surface_tension3d.cpp)
target_link_libraries(validate_surface_tension3d pfflip2d)
add_executable(bench_multires_sparse3d_tp apps/bench_multires_sparse3d_tp.cpp)
target_link_libraries(bench_multires_sparse3d_tp pfflip2d)
add_executable(bench_multires3d_solver apps/bench_multires3d_solver.cpp)
target_link_libraries(bench_multires3d_solver pfflip2d)
add_executable(run_multires_bubble apps/run_multires_bubble.cpp)
target_link_libraries(run_multires_bubble pfflip2d)
add_executable(run_multires_bubble3d apps/run_multires_bubble3d.cpp)
target_link_libraries(run_multires_bubble3d pfflip2d)
