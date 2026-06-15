#include "doctest.h"
#include "driver/multires_sim3d_tp.h"
#include "driver/viz_multires3d_tp.h"

#include <cmath>
#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

double meanY(const MRSim3DTP& sim, unsigned char type) {
  double sum = 0.0;
  int count = 0;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    if (sim.particles.type[i] == type) {
      sum += sim.particles.pos[i].y;
      ++count;
    }
  }
  return count ? sum / count : 0.0;
}

bool finiteParticles(const MRSim3DTP& sim) {
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) {
      return false;
    }
  }
  return true;
}

size_t countType(const Particles3DTP& ps, unsigned char type) {
  size_t count = 0;
  for (size_t i = 0; i < ps.size(); ++i) {
    if (ps.type[i] == type) ++count;
  }
  return count;
}

bool sameParticleState(const Particles3DTP& a, const Particles3DTP& b) {
  if (a.size() != b.size()) return false;
  for (size_t i = 0; i < a.size(); ++i) {
    if (a.type[i] != b.type[i]) return false;
    if (a.pos[i].x != b.pos[i].x ||
        a.pos[i].y != b.pos[i].y ||
        a.pos[i].z != b.pos[i].z) {
      return false;
    }
  }
  return true;
}

std::vector<unsigned char> readP6(const std::string& path, int& W, int& H) {
  std::ifstream f(path, std::ios::binary);
  std::string magic;
  int maxv = 0;
  f >> magic >> W >> H >> maxv;
  f.get();
  std::vector<unsigned char> img(static_cast<size_t>(W * H * 3));
  f.read(reinterpret_cast<char*>(img.data()), static_cast<std::streamsize>(img.size()));
  return img;
}

} // namespace

TEST_CASE("multires 3D viz validates output settings and writes") {
  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(1);

  CHECK_THROWS_AS(writeMR3DTPPM(sim, "test_mr3_invalid_scale.ppm", 0), std::invalid_argument);
  CHECK_THROWS_AS(writeMR3DTPPM(sim, "", 2), std::runtime_error);
}

TEST_CASE("multires 3D viz skips negative and out-of-slice particles") {
  const char* path = "test_mr3_slice_skip.ppm";
  std::remove(path);

  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(1);
  sim.particles.add({-0.1, 0.5, 2.0}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({1.5, 1.5, 0.0}, {0.0, 0.0, 0.0}, 1);

  writeMR3DTPPM(sim, path, 2, 0.1);

  int W = 0, H = 0;
  std::vector<unsigned char> img = readP6(path, W, H);
  std::remove(path);

  REQUIRE(W == 8);
  REQUIRE(H == 8);
  int o = (0 + W * 6) * 3;
  CHECK(img[o] == 28);
  CHECK(img[o + 1] == 32);
  CHECK(img[o + 2] == 48);
}

TEST_CASE("multires 3D viz writes in-slice liquid and gas particles") {
  const char* path = "test_mr3_slice_particles.ppm";
  std::remove(path);

  MRSim3DTP sim(4, 4, 4, 1.0);
  sim.layout.setCoarseEverywhere(0);
  sim.particles.add({1.5, 1.5, 2.0}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({2.5, 1.5, 2.0}, {0.0, 0.0, 0.0}, 1);

  writeMR3DTPPM(sim, path, 2, 0.1);

  int W = 0, H = 0;
  std::vector<unsigned char> img = readP6(path, W, H);
  std::remove(path);

  REQUIRE(W == 8);
  REQUIRE(H == 8);
  int liquid = (3 + W * 4) * 3;
  int gas = (5 + W * 4) * 3;
  CHECK(img[liquid] == 60);
  CHECK(img[liquid + 1] == 140);
  CHECK(img[liquid + 2] == 230);
  CHECK(img[gas] == 235);
  CHECK(img[gas + 1] == 160);
  CHECK(img[gas + 2] == 60);
}

TEST_CASE("multires 3D bubble tank initializes refined lower band and coarse headspace") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.initBubbleTankInterfaceBand();

  CHECK(sim.layout.countLevel(0) > 0);
  CHECK(sim.layout.countLevel(1) > 0);
  CHECK(sim.particles.size() > 0);
  CHECK(meanY(sim, 1) > 0.0);
  CHECK(sim.activePressureCellCount() < 8 * 12 * 8);
  CHECK(sim.uFaceCount() > 0);
  CHECK(sim.vFaceCount() > 0);
  CHECK(sim.wFaceCount() > 0);
}

TEST_CASE("multires 3D particle adaptivity prunes and coarsens gas particles") {
  MRSim3DTP full(8, 12, 8, 1.0);
  full.initBubbleTankInterfaceBand();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);

  REQUIRE(fullLiquid > 0);
  REQUIRE(fullGas > 8);
  REQUIRE(fullGas % 8 == 0);

  MRSim3DTP band(8, 12, 8, 1.0);
  band.narrow_band_air = true;
  band.narrow_band_air_radius = 0;
  band.initBubbleTankInterfaceBand();

  CHECK(countType(band.particles, 0) == fullLiquid);
  CHECK(countType(band.particles, 1) == 0);
  CHECK(band.narrow_band_air_removed_total == static_cast<int>(fullGas));
  CHECK(band.narrow_band_air_gas_particles_before_last == static_cast<int>(fullGas));
  CHECK(band.narrow_band_air_gas_particles_after_last == 0);

  MRSim3DTP coarse(8, 12, 8, 1.0);
  coarse.gas_particle_coarsening = true;
  coarse.gas_particles_per_cell_target = 2;
  coarse.gas_particle_coarsening_seed = 12345u;
  coarse.initBubbleTankInterfaceBand();

  const size_t gasCells = fullGas / 8;
  CHECK(countType(coarse.particles, 0) == fullLiquid);
  CHECK(countType(coarse.particles, 1) == gasCells * 2);
  CHECK(coarse.gas_particle_coarsening_removed_total ==
        static_cast<int>(fullGas - gasCells * 2));
  CHECK(coarse.gas_particle_coarsening_cells_last == static_cast<int>(gasCells));
  CHECK(coarse.gas_particle_coarsening_overfull_cells_last == static_cast<int>(gasCells));

  MRSim3DTP repeat(8, 12, 8, 1.0);
  repeat.gas_particle_coarsening = true;
  repeat.gas_particles_per_cell_target = 2;
  repeat.gas_particle_coarsening_seed = 12345u;
  repeat.initBubbleTankInterfaceBand();
  CHECK(sameParticleState(coarse.particles, repeat.particles));

  const size_t n0 = coarse.particles.size();
  coarse.dt = 0.02;
  coarse.cg_iters = 120;
  coarse.step();

  CHECK(coarse.particles.size() <= n0);
  CHECK(countType(coarse.particles, 0) == fullLiquid);
  CHECK(finiteParticles(coarse));
  CHECK(coarse.activePressureCellCount() < 8 * 12 * 8);
}

TEST_CASE("multires 3D particle adaptivity coarsens liquid particles") {
  MRSim3DTP full(8, 12, 8, 1.0);
  full.initBubbleTankInterfaceBand();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);

  REQUIRE(fullLiquid > 8);
  REQUIRE(fullLiquid % 8 == 0);

  MRSim3DTP coarse(8, 12, 8, 1.0);
  coarse.liquid_particle_coarsening = true;
  coarse.liquid_particles_per_cell_target = 2;
  coarse.liquid_particle_coarsening_seed = 54321u;
  coarse.initBubbleTankInterfaceBand();

  const size_t liquidCells = fullLiquid / 8;
  const size_t expectedLiquid = liquidCells * 2;
  CHECK(countType(coarse.particles, 0) == expectedLiquid);
  CHECK(countType(coarse.particles, 1) == fullGas);
  CHECK(coarse.liquid_particle_coarsening_removed_total ==
        static_cast<int>(fullLiquid - expectedLiquid));
  CHECK(coarse.liquid_particle_coarsening_cells_last == static_cast<int>(liquidCells));
  CHECK(coarse.liquid_particle_coarsening_overfull_cells_last == static_cast<int>(liquidCells));
  CHECK(coarse.liquid_particle_coarsening_before_last == static_cast<int>(fullLiquid));
  CHECK(coarse.liquid_particle_coarsening_after_last == static_cast<int>(expectedLiquid));

  MRSim3DTP repeat(8, 12, 8, 1.0);
  repeat.liquid_particle_coarsening = true;
  repeat.liquid_particles_per_cell_target = 2;
  repeat.liquid_particle_coarsening_seed = 54321u;
  repeat.initBubbleTankInterfaceBand();
  CHECK(sameParticleState(coarse.particles, repeat.particles));
  CHECK(finiteParticles(coarse));
  CHECK(coarse.activePressureCellCount() < 8 * 12 * 8);
}

TEST_CASE("multires 3D particle adaptivity refills underfilled liquid cells") {
  MRSim3DTP full(8, 12, 8, 1.0);
  full.initBubbleTankInterfaceBand();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);

  REQUIRE(fullLiquid > 8);
  REQUIRE(fullLiquid % 8 == 0);

  MRSim3DTP refill(8, 12, 8, 1.0);
  refill.liquid_particle_coarsening = true;
  refill.liquid_particles_per_cell_target = 2;
  refill.liquid_particle_coarsening_seed = 54321u;
  refill.liquid_particle_refill = true;
  refill.liquid_refill_particles_per_cell_target = 4;
  refill.liquid_particle_refill_seed = 24680u;
  refill.initBubbleTankInterfaceBand();

  const size_t liquidCells = fullLiquid / 8;
  const size_t coarsenedLiquid = liquidCells * 2;
  const size_t expectedLiquid = liquidCells * 4;

  CHECK(countType(refill.particles, 0) == expectedLiquid);
  CHECK(countType(refill.particles, 1) == fullGas);
  CHECK(refill.liquid_particle_coarsening_removed_total ==
        static_cast<int>(fullLiquid - coarsenedLiquid));
  CHECK(refill.liquid_particle_refill_added_total ==
        static_cast<int>(expectedLiquid - coarsenedLiquid));
  CHECK(refill.liquid_particle_refill_added_last ==
        refill.liquid_particle_refill_added_total);
  CHECK(refill.liquid_particle_refill_cells_last == static_cast<int>(liquidCells));
  CHECK(refill.liquid_particle_refill_underfull_cells_last == static_cast<int>(liquidCells));
  CHECK(refill.liquid_particle_refill_before_last == static_cast<int>(coarsenedLiquid));
  CHECK(refill.liquid_particle_refill_after_last == static_cast<int>(expectedLiquid));

  MRSim3DTP repeat(8, 12, 8, 1.0);
  repeat.liquid_particle_coarsening = true;
  repeat.liquid_particles_per_cell_target = 2;
  repeat.liquid_particle_coarsening_seed = 54321u;
  repeat.liquid_particle_refill = true;
  repeat.liquid_refill_particles_per_cell_target = 4;
  repeat.liquid_particle_refill_seed = 24680u;
  repeat.initBubbleTankInterfaceBand();
  CHECK(sameParticleState(refill.particles, repeat.particles));
  CHECK(finiteParticles(refill));
  CHECK(refill.activePressureCellCount() < 8 * 12 * 8);
}

TEST_CASE("multires 3D particle adaptivity refills interface liquid cells only") {
  MRSim3DTP refill(6, 6, 6, 1.0);
  refill.liquid_particle_refill = true;
  refill.liquid_particle_refill_interface_only = true;
  refill.liquid_particle_refill_interface_radius = 1;
  refill.liquid_refill_particles_per_cell_target = 4;
  refill.liquid_particle_refill_seed = 24680u;
  refill.particles.add({1.25, 1.25, 1.25}, {1.0, 0.0, 0.0}, 0);
  refill.particles.add({3.25, 3.25, 3.25}, {2.0, 0.0, 0.0}, 0);
  refill.particles.add({2.25, 1.25, 1.25}, {0.0, 0.0, 0.0}, 1);

  refill.applyLiquidParticleRefill();

  CHECK(countType(refill.particles, 0) == 5);
  CHECK(countType(refill.particles, 1) == 1);
  CHECK(refill.liquid_particle_refill_added_last == 3);
  CHECK(refill.liquid_particle_refill_cells_last == 2);
  CHECK(refill.liquid_particle_refill_interface_cells_last == 1);
  CHECK(refill.liquid_particle_refill_underfull_cells_last == 1);
  CHECK(refill.liquid_particle_refill_before_last == 2);
  CHECK(refill.liquid_particle_refill_after_last == 5);
  CHECK(finiteParticles(refill));
}

TEST_CASE("multires 3D particle adaptivity refill honors per-step add budget") {
  MRSim3DTP refill(6, 6, 6, 1.0);
  refill.liquid_particle_refill = true;
  refill.liquid_particle_refill_interface_only = true;
  refill.liquid_particle_refill_interface_radius = 1;
  refill.liquid_particle_refill_max_added_per_step = 4;
  refill.liquid_refill_particles_per_cell_target = 4;
  refill.liquid_particle_refill_seed = 24680u;
  refill.particles.add({1.25, 1.25, 1.25}, {1.0, 0.0, 0.0}, 0);
  refill.particles.add({3.25, 1.25, 1.25}, {2.0, 0.0, 0.0}, 0);
  refill.particles.add({2.25, 1.25, 1.25}, {0.0, 0.0, 0.0}, 1);

  refill.applyLiquidParticleRefill();

  CHECK(countType(refill.particles, 0) == 6);
  CHECK(countType(refill.particles, 1) == 1);
  CHECK(refill.liquid_particle_refill_added_last == 4);
  CHECK(refill.liquid_particle_refill_budget_limited_last == 1);
  CHECK(refill.liquid_particle_refill_cells_last == 2);
  CHECK(refill.liquid_particle_refill_interface_cells_last == 2);
  CHECK(refill.liquid_particle_refill_underfull_cells_last == 2);
  CHECK(refill.liquid_particle_refill_before_last == 2);
  CHECK(refill.liquid_particle_refill_after_last == 6);
  CHECK(finiteParticles(refill));
}

TEST_CASE("multires 3D dynamic refinement follows particle occupancy") {
  MRSim3DTP sim(16, 16, 16, 1.0);
  sim.dynamic_particle_padding = 0;
  sim.dynamic_gas_padding = 1;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({3.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 1);

  sim.updateDynamicRefinement();

  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 0);
  CHECK(sim.layout.leafAtFineCell(14, 14, 14).level == 1);
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());

  sim.particles.pos[0] = {13.5, 13.5, 13.5};
  sim.particles.pos[1] = {12.5, 13.5, 13.5};
  sim.updateDynamicRefinement();

  CHECK(sim.layout.leafAtFineCell(13, 13, 13).level == 0);
  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 1);
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());
}

TEST_CASE("multires 3D dynamic refinement hysteresis retains small moves") {
  MRSim3DTP sim(16, 16, 16, 1.0);
  sim.dynamic_particle_padding = 0;
  sim.dynamic_gas_padding = 0;
  sim.dynamic_hysteresis_cells = 2;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);

  sim.updateDynamicRefinement();
  size_t initialLeaves = sim.layout.countLevel(0);

  sim.particles.pos[0] = {4.5, 2.5, 2.5};
  sim.updateDynamicRefinement();

  CHECK(sim.dynamic_retained_box_valid);
  CHECK(sim.layout.countLevel(0) == initialLeaves);
  CHECK(sim.layout.leafAtFineCell(2, 2, 2).level == 0);
  CHECK(sim.layout.leafAtFineCell(4, 2, 2).level == 0);
}

TEST_CASE("multires 3D dynamic refinement respects fine leaf budget") {
  MRSim3DTP sim(32, 32, 32, 1.0);
  sim.dynamic_particle_padding = 8;
  sim.dynamic_gas_padding = 0;
  sim.dynamic_hysteresis_cells = 0;
  sim.dynamic_max_fine_leaves = 8;
  sim.particles.add({2.5, 2.5, 2.5}, {0.0, 0.0, 0.0}, 0);
  sim.particles.add({29.5, 29.5, 29.5}, {0.0, 0.0, 0.0}, 0);

  sim.updateDynamicRefinement();

  CHECK(sim.dynamic_budget_limited);
  CHECK(sim.dynamic_last_fine_leaves == static_cast<int>(sim.layout.countLevel(0)));
  CHECK(sim.layout.countLevel(0) <= static_cast<size_t>(sim.dynamic_max_fine_leaves));
  CHECK(sim.grid.layout.leaves() == sim.layout.leaves());
}

TEST_CASE("multires 3D bubble tank step conserves particles and stays finite") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.cg_iters = 120;
  sim.initBubbleTankInterfaceBand();
  size_t n0 = sim.particles.size();
  double gas0 = meanY(sim, 1);

  for (int step = 0; step < 4; ++step) {
    sim.step();
  }

  CHECK(sim.particles.size() == n0);
  CHECK(finiteParticles(sim));
  CHECK(std::isfinite(meanY(sim, 1)));
  CHECK(meanY(sim, 1) >= gas0 - 0.05);
  CHECK(sim.activePressureCellCount() < 8 * 12 * 8);
}

TEST_CASE("multires 3D bubble high density ratio pressure converges") {
  MRSim3DTP sim(8, 12, 8, 1.0);
  sim.phase.rho_l = 1000.0;
  sim.phase.rho_g = 1.0;
  sim.dt = 0.02;
  sim.cg_iters = 160;
  sim.cg_rel_tol = 1e-5;
  sim.initBubbleTankInterfaceBand();
  size_t n0 = sim.particles.size();

  sim.step();

  CHECK(sim.particles.size() == n0);
  CHECK(finiteParticles(sim));
  CHECK(sim.last_pressure_stats.converged);
  CHECK(sim.last_pressure_stats.final_residual <= sim.last_pressure_stats.effective_tolerance);
  CHECK(std::isfinite(sim.last_pressure_stats.min_positive_diag));
  CHECK(sim.last_pressure_stats.min_positive_diag > 0.0);
  CHECK(!sim.last_pressure_stats.breakdown);
}
