#include "doctest.h"
#include "driver/render_cache3d.h"

#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

namespace {

std::string readTextFile(const std::string& path) {
  std::ifstream f(path);
  std::ostringstream ss;
  ss << f.rdbuf();
  return ss.str();
}

bool contains(const std::string& text, const char* needle) {
  return text.find(needle) != std::string::npos;
}

} // namespace

TEST_CASE("sparse 3D render cache writes schema sections") {
  const char* path = "test_sparse_render_cache3d.jsonl";
  std::remove(path);

  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.cg_iters = 20;
  sim.escaped_particle_branching = true;
  sim.initBubbleTank();
  sim.step();
  sim.escaped_droplets.add({1.0, 2.0, 3.0}, {0.1, 0.2, 0.3}, 0, 0.5);
  sim.escaped_droplet_ages.push_back(7);

  const RenderCacheCamera3D camera =
    defaultRenderCacheCamera3D(sim.grid.nx, sim.grid.ny, sim.grid.nz, sim.grid.dx);
  writeSparseRenderCache3D(sim, path, 3, 0.06, camera);

  const std::string text = readTextFile(path);
  std::remove(path);

  CHECK(contains(text, "\"lsfs_cache3d_version\":1"));
  CHECK(contains(text, "\"sim_kind\":\"sparse3d_tp\""));
  CHECK(contains(text, "\"section\":\"camera\""));
  CHECK(contains(text, "\"section\":\"water_volume\""));
  CHECK(contains(text, "\"section\":\"phase_field\""));
  CHECK(contains(text, "\"section\":\"particles\",\"kind\":\"primary\""));
  CHECK(contains(text, "\"section\":\"particles\",\"kind\":\"secondary_droplet\""));
  CHECK(contains(text, "\"age\":7"));
}

TEST_CASE("multires 3D render cache writes schema sections") {
  const char* path = "test_mr_render_cache3d.jsonl";
  std::remove(path);

  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.cg_iters = 20;
  sim.escaped_particle_branching = true;
  sim.initBubbleTankInterfaceBand();
  sim.step();
  sim.escaped_bubbles.add({2.0, 3.0, 4.0}, {0.0, 0.1, 0.0}, 1, 0.25);
  sim.escaped_bubble_ages.push_back(5);

  const RenderCacheCamera3D camera =
    defaultRenderCacheCamera3D(sim.layout.nx, sim.layout.ny, sim.layout.nz, sim.layout.dx);
  writeMRRenderCache3D(sim, path, 4, 0.08, camera);

  const std::string text = readTextFile(path);
  std::remove(path);

  CHECK(contains(text, "\"lsfs_cache3d_version\":1"));
  CHECK(contains(text, "\"sim_kind\":\"multires3d_tp\""));
  CHECK(contains(text, "\"section\":\"camera\""));
  CHECK(contains(text, "\"section\":\"water_volume\""));
  CHECK(contains(text, "\"section\":\"phase_field\""));
  CHECK(contains(text, "\"section\":\"particles\",\"kind\":\"primary\""));
  CHECK(contains(text, "\"section\":\"particles\",\"kind\":\"secondary_bubble\""));
  CHECK(contains(text, "\"age\":5"));
}
