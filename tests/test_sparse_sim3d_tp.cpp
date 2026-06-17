#include "doctest.h"
#include "driver/sparse_sim3d_tp.h"
#include "driver/timestep3d.h"
#include <algorithm>
#include <cmath>

namespace {

size_t countType(const Particles3DTP& particles, unsigned char type) {
  size_t count = 0;
  for (size_t i = 0; i < particles.size(); ++i) {
    if (particles.type[i] == type) ++count;
  }
  return count;
}

double volumeType(const Particles3DTP& particles, unsigned char type) {
  double volume = 0.0;
  for (size_t i = 0; i < particles.size(); ++i) {
    if (particles.type[i] == type) volume += particles.volume[i];
  }
  return volume;
}

bool finiteParticles(const Particles3DTP& particles) {
  for (size_t i = 0; i < particles.size(); ++i) {
    const auto& p = particles.pos[i];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) {
      return false;
    }
  }
  return true;
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

} // namespace

TEST_CASE("adaptive 3D timestep clamps by particle speed") {
  Particles3DTP particles;
  particles.add({1.0, 1.0, 1.0}, {10.0, 0.0, 0.0}, 0);
  particles.add({2.0, 1.0, 1.0}, {0.0, 3.0, 4.0}, 1);

  const TimestepStats3D stats =
    computeAdaptiveParticleTimestep3D(particles, 1.0, 0.2, true, 0.5, 1e-5);

  CHECK(stats.max_particle_speed == doctest::Approx(10.0));
  CHECK(stats.effective_dt == doctest::Approx(0.05));
  CHECK(stats.limited == 1);
}

TEST_CASE("disabled adaptive 3D timestep preserves requested dt") {
  Particles3DTP particles;
  particles.add({1.0, 1.0, 1.0}, {10.0, 0.0, 0.0}, 0);

  const TimestepStats3D stats =
    computeAdaptiveParticleTimestep3D(particles, 1.0, 0.2, false, 0.5, 1e-5);

  CHECK(stats.max_particle_speed == doctest::Approx(10.0));
  CHECK(stats.effective_dt == doctest::Approx(0.2));
  CHECK(stats.limited == 0);
}

TEST_CASE("sparse 3D two-phase RT step stays stable") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.03;
  sim.initRayleighTaylor();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);

  auto meanY = [&](unsigned char type) {
    double sum = 0.0;
    int count = 0;
    for (size_t i = 0; i < sim.particles.size(); ++i) {
      if (sim.particles.type[i] == type) {
        sum += sim.particles.pos[i].y;
        ++count;
      }
    }
    return count ? sum / count : 0.0;
  };
  double heavy0 = meanY(0);
  double gas0 = meanY(1);
  CHECK(heavy0 > gas0);

  size_t maxActive = 0;
  for (int step = 0; step < 12; ++step) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }

  CHECK(sim.particles.size() == n0);
  bool finite = true;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    finite = finite && std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z);
  }
  CHECK(finite);
  CHECK(meanY(0) < heavy0);
  CHECK(std::isfinite(meanY(1)));
  CHECK(maxActive > 0);
}

TEST_CASE("sparse 3D two-phase adaptive timestep reports effective dt") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.2;
  sim.adaptive_timestep = true;
  sim.adaptive_cfl = 0.5;
  sim.adaptive_min_dt = 1e-5;
  sim.initBubbleTank();
  REQUIRE(!sim.particles.vel.empty());
  sim.particles.vel[0] = {100.0, 0.0, 0.0};

  sim.step();

  CHECK(sim.dt == doctest::Approx(0.2));
  CHECK(sim.max_particle_speed_last == doctest::Approx(100.0));
  CHECK(sim.effective_dt_last == doctest::Approx(0.005));
  CHECK(sim.adaptive_timestep_limited_last == 1);
}

TEST_CASE("sparse 3D two-phase c_div uses liquid volume error") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.c_div_volume_correction = true;
  sim.c_div_strength = 1.0;
  sim.initBubbleTank();
  const double liquidVolume = volumeType(sim.particles, 0);
  sim.liquid_volume_target = liquidVolume + 1.0;

  sim.step();

  CHECK(sim.liquid_volume_current_last == doctest::Approx(liquidVolume));
  CHECK(sim.liquid_volume_error_last == doctest::Approx(1.0));
  CHECK(sim.c_div_last == doctest::Approx(1.0 / (sim.dt * sim.liquid_volume_target)));
}

TEST_CASE("sparse 3D two-phase interface diagnostics report surface candidates") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.initBubbleTank();

  sim.step();

  CHECK(sim.interface_diagnostics_last.finite == 1);
  CHECK(sim.interface_diagnostics_last.sample_cells > 0);
  CHECK(sim.interface_diagnostics_last.interface_cells > 0);
  CHECK(sim.interface_diagnostics_last.phi_min <= sim.interface_diagnostics_last.phi_max);
  CHECK(sim.interface_diagnostics_last.grad_max >= 0.0);
  CHECK(sim.interface_diagnostics_last.curvature_abs_max >= 0.0);
  CHECK(sim.interface_diagnostics_last.surface_tension_candidate == 1);
}

TEST_CASE("sparse 3D two-phase surface tension applies bounded grid force") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.surface_tension = true;
  sim.surface_tension_strength = 0.02;
  sim.surface_tension_max_delta_speed = 0.05;
  sim.initBubbleTank();

  sim.step();

  CHECK(sim.surface_tension_stats_last.enabled == 1);
  CHECK(sim.surface_tension_stats_last.finite == 1);
  CHECK(sim.surface_tension_stats_last.applied_cells > 0);
  CHECK(sim.surface_tension_stats_last.mean_delta_speed > 0.0);
  CHECK(sim.surface_tension_stats_last.max_delta_speed > 0.0);
  CHECK(sim.surface_tension_stats_last.max_delta_speed <=
        sim.surface_tension_max_delta_speed + 1e-12);
}

TEST_CASE("sparse 3D surface tension smoothing reports capillary gate") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.02;
  sim.surface_tension = true;
  sim.surface_tension_strength = 0.02;
  sim.surface_tension_max_delta_speed = 0.05;
  sim.surface_tension_curvature_smoothing_radius = 1;
  sim.initBubbleTank();

  sim.step();

  CHECK(sim.surface_tension_stats_last.enabled == 1);
  CHECK(sim.surface_tension_stats_last.finite == 1);
  CHECK(sim.surface_tension_stats_last.curvature_smoothing_radius == 1);
  CHECK(sim.surface_tension_stats_last.capillary_dt_limit > sim.effective_dt_last);
  CHECK(sim.surface_tension_stats_last.capillary_stable == 1);
  CHECK(sim.surface_tension_stats_last.raw_curvature_abs_max >= 0.0);
  CHECK(sim.surface_tension_stats_last.smoothed_curvature_abs_max >= 0.0);
  CHECK(sim.surface_tension_stats_last.smoothed_curvature_abs_max <=
        sim.surface_tension_stats_last.raw_curvature_abs_max + 1e-12);
}

TEST_CASE("sparse 3D secondary lifecycle reabsorbs tracked droplets") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.1;
  sim.gravity = 0.0;
  sim.escaped_particle_branching = true;
  sim.secondary_particle_lifecycle = true;
  sim.secondary_velocity_damping = 1.0;
  sim.secondary_reabsorb_margin_cells = 1.0;
  sim.initBubbleTank();
  sim.escaped_droplets.add({0.51, 4.0, 4.0}, {20.0, 0.0, 0.0}, 0, 2.0);
  sim.escaped_droplet_ages.push_back(0);
  sim.escaped_droplet_volume_added_total = 2.0 * sim.Vp;
  sim.secondary_droplet_volume_current_last = 2.0 * sim.Vp;

  sim.step();

  CHECK(sim.secondary_lifecycle_stats_last.enabled == 1);
  CHECK(sim.secondary_lifecycle_stats_last.finite == 1);
  CHECK(sim.secondary_droplets_advected_total >= 1);
  CHECK(sim.secondary_droplets_reabsorbed_total == 1);
  CHECK(sim.secondary_droplet_volume_reabsorbed_total == doctest::Approx(2.0 * sim.Vp));
  CHECK(sim.escaped_droplets.size() == 0);
  CHECK(sim.escaped_droplet_ages.empty());
  CHECK(sim.escaped_droplet_volume_added_total ==
        doctest::Approx(sim.secondary_droplet_volume_reabsorbed_total +
                        sim.secondary_droplet_volume_expired_total +
                        sim.secondary_droplet_volume_current_last));
}

TEST_CASE("sparse 3D secondary lifecycle can reabsorb droplets into primary particles") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.1;
  sim.gravity = 0.0;
  sim.escaped_particle_branching = true;
  sim.secondary_particle_lifecycle = true;
  sim.secondary_reabsorb_to_primary = true;
  sim.secondary_velocity_damping = 1.0;
  sim.secondary_reabsorb_margin_cells = 1.0;
  sim.initBubbleTank();
  const size_t liquidCount0 = countType(sim.particles, 0);
  const double liquidVolume0 = volumeType(sim.particles, 0);
  sim.escaped_droplets.add({0.51, 4.0, 4.0}, {20.0, 0.0, 0.0}, 0, 2.0);
  sim.escaped_droplet_ages.push_back(0);
  sim.escaped_droplet_volume_added_total = 2.0 * sim.Vp;
  sim.secondary_droplet_volume_current_last = 2.0 * sim.Vp;

  sim.step();

  CHECK(sim.escaped_droplets.size() == 0);
  CHECK(sim.secondary_droplets_reabsorbed_to_primary_total == 1);
  CHECK(sim.secondary_droplet_volume_reabsorbed_to_primary_total == doctest::Approx(2.0 * sim.Vp));
  CHECK(countType(sim.particles, 0) == liquidCount0 + 1);
  CHECK(volumeType(sim.particles, 0) == doctest::Approx(liquidVolume0 + 2.0));
}

TEST_CASE("sparse 3D two-phase narrow-band air prunes far gas particles") {
  SparseSim3DTP full(12, 12, 8, 1.0);
  full.initTwoPhaseDamBreak();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);
  CHECK(fullLiquid > 0);
  CHECK(fullGas > 0);

  SparseSim3DTP narrow(12, 12, 8, 1.0);
  narrow.narrow_band_air = true;
  narrow.narrow_band_air_radius = 1;
  narrow.initTwoPhaseDamBreak();
  const size_t narrowLiquid = countType(narrow.particles, 0);
  const size_t narrowGas = countType(narrow.particles, 1);

  CHECK(narrowLiquid == fullLiquid);
  CHECK(narrowGas > 0);
  CHECK(narrowGas < fullGas);
  CHECK(narrow.particles.size() < full.particles.size());
  CHECK(narrow.narrow_band_air_removed_total == static_cast<int>(fullGas - narrowGas));
  CHECK(narrow.narrow_band_air_removed_last == narrow.narrow_band_air_removed_total);
  CHECK(narrow.narrow_band_air_liquid_cells_last > 0);
  CHECK(narrow.narrow_band_air_gas_particles_before_last == static_cast<int>(fullGas));
  CHECK(narrow.narrow_band_air_gas_particles_after_last == static_cast<int>(narrowGas));

  const size_t n0 = narrow.particles.size();
  narrow.dt = 0.02;
  narrow.step();
  CHECK(narrow.particles.size() <= n0);
  CHECK(countType(narrow.particles, 0) == fullLiquid);
  CHECK(finiteParticles(narrow.particles));
}

TEST_CASE("sparse 3D two-phase gas particle coarsening caps gas per cell") {
  SparseSim3DTP full(12, 12, 8, 1.0);
  full.initTwoPhaseDamBreak();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);
  CHECK(fullGas > 8);
  CHECK(fullGas % 8 == 0);

  SparseSim3DTP coarse(12, 12, 8, 1.0);
  coarse.gas_particle_coarsening = true;
  coarse.gas_particles_per_cell_target = 2;
  coarse.gas_particle_coarsening_seed = 12345u;
  coarse.initTwoPhaseDamBreak();
  const size_t coarseLiquid = countType(coarse.particles, 0);
  const size_t coarseGas = countType(coarse.particles, 1);
  const size_t fullGasCells = fullGas / 8;
  const size_t expectedGas = fullGasCells * 2;

  CHECK(coarseLiquid == fullLiquid);
  CHECK(coarseGas == expectedGas);
  CHECK(coarse.particles.size() == coarseLiquid + coarseGas);
  CHECK(coarse.gas_particle_coarsening_removed_total ==
        static_cast<int>(fullGas - expectedGas));
  CHECK(coarse.gas_particle_coarsening_removed_last ==
        coarse.gas_particle_coarsening_removed_total);
  CHECK(coarse.gas_particle_coarsening_cells_last == static_cast<int>(fullGasCells));
  CHECK(coarse.gas_particle_coarsening_overfull_cells_last == static_cast<int>(fullGasCells));
  CHECK(coarse.gas_particle_coarsening_before_last == static_cast<int>(fullGas));
  CHECK(coarse.gas_particle_coarsening_after_last == static_cast<int>(expectedGas));

  SparseSim3DTP repeat(12, 12, 8, 1.0);
  repeat.gas_particle_coarsening = true;
  repeat.gas_particles_per_cell_target = 2;
  repeat.gas_particle_coarsening_seed = 12345u;
  repeat.initTwoPhaseDamBreak();
  CHECK(sameParticleState(coarse.particles, repeat.particles));

  const size_t n0 = coarse.particles.size();
  coarse.dt = 0.02;
  coarse.step();
  CHECK(coarse.particles.size() <= n0);
  CHECK(countType(coarse.particles, 0) == fullLiquid);
  CHECK(finiteParticles(coarse.particles));
}

TEST_CASE("sparse 3D two-phase liquid particle coarsening caps liquid per cell") {
  SparseSim3DTP full(12, 12, 8, 1.0);
  full.initTwoPhaseDamBreak();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);
  const double fullLiquidVolume = volumeType(full.particles, 0);
  const double fullGasVolume = volumeType(full.particles, 1);
  CHECK(fullLiquid > 8);
  CHECK(fullLiquid % 8 == 0);

  SparseSim3DTP coarse(12, 12, 8, 1.0);
  coarse.liquid_particle_coarsening = true;
  coarse.liquid_particles_per_cell_target = 2;
  coarse.liquid_particle_coarsening_seed = 54321u;
  coarse.initTwoPhaseDamBreak();
  const size_t coarseLiquid = countType(coarse.particles, 0);
  const size_t coarseGas = countType(coarse.particles, 1);
  const size_t fullLiquidCells = fullLiquid / 8;
  const size_t expectedLiquid = fullLiquidCells * 2;

  CHECK(coarseLiquid == expectedLiquid);
  CHECK(coarseGas == fullGas);
  CHECK(volumeType(coarse.particles, 0) == doctest::Approx(fullLiquidVolume));
  CHECK(volumeType(coarse.particles, 1) == doctest::Approx(fullGasVolume));
  CHECK(coarse.particles.size() == coarseLiquid + coarseGas);
  CHECK(coarse.liquid_particle_coarsening_removed_total ==
        static_cast<int>(fullLiquid - expectedLiquid));
  CHECK(coarse.liquid_particle_coarsening_removed_last ==
        coarse.liquid_particle_coarsening_removed_total);
  CHECK(coarse.liquid_particle_coarsening_cells_last == static_cast<int>(fullLiquidCells));
  CHECK(coarse.liquid_particle_coarsening_overfull_cells_last ==
        static_cast<int>(fullLiquidCells));
  CHECK(coarse.liquid_particle_coarsening_before_last == static_cast<int>(fullLiquid));
  CHECK(coarse.liquid_particle_coarsening_after_last == static_cast<int>(expectedLiquid));

  SparseSim3DTP repeat(12, 12, 8, 1.0);
  repeat.liquid_particle_coarsening = true;
  repeat.liquid_particles_per_cell_target = 2;
  repeat.liquid_particle_coarsening_seed = 54321u;
  repeat.initTwoPhaseDamBreak();
  CHECK(sameParticleState(coarse.particles, repeat.particles));
  CHECK(finiteParticles(coarse.particles));
}

TEST_CASE("sparse 3D two-phase liquid refill restores underfilled liquid cells") {
  SparseSim3DTP full(12, 12, 8, 1.0);
  full.initTwoPhaseDamBreak();
  const size_t fullLiquid = countType(full.particles, 0);
  const size_t fullGas = countType(full.particles, 1);
  const double fullLiquidVolume = volumeType(full.particles, 0);
  const double fullGasVolume = volumeType(full.particles, 1);
  REQUIRE(fullLiquid > 8);
  REQUIRE(fullLiquid % 8 == 0);

  SparseSim3DTP refill(12, 12, 8, 1.0);
  refill.liquid_particle_coarsening = true;
  refill.liquid_particles_per_cell_target = 2;
  refill.liquid_particle_coarsening_seed = 54321u;
  refill.liquid_particle_refill = true;
  refill.liquid_refill_particles_per_cell_target = 4;
  refill.liquid_particle_refill_seed = 24680u;
  refill.initTwoPhaseDamBreak();

  const size_t liquidCells = fullLiquid / 8;
  const size_t coarsenedLiquid = liquidCells * 2;
  const size_t expectedLiquid = liquidCells * 4;

  CHECK(countType(refill.particles, 0) == expectedLiquid);
  CHECK(countType(refill.particles, 1) == fullGas);
  CHECK(volumeType(refill.particles, 0) == doctest::Approx(fullLiquidVolume));
  CHECK(volumeType(refill.particles, 1) == doctest::Approx(fullGasVolume));
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

  SparseSim3DTP repeat(12, 12, 8, 1.0);
  repeat.liquid_particle_coarsening = true;
  repeat.liquid_particles_per_cell_target = 2;
  repeat.liquid_particle_coarsening_seed = 54321u;
  repeat.liquid_particle_refill = true;
  repeat.liquid_refill_particles_per_cell_target = 4;
  repeat.liquid_particle_refill_seed = 24680u;
  repeat.initTwoPhaseDamBreak();
  CHECK(sameParticleState(refill.particles, repeat.particles));
  CHECK(finiteParticles(refill.particles));
}

TEST_CASE("sparse 3D two-phase liquid refill can target interface cells only") {
  SparseSim3DTP refill(6, 6, 6, 1.0);
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
  CHECK(finiteParticles(refill.particles));
}

TEST_CASE("sparse 3D two-phase liquid refill honors per-step add budget") {
  SparseSim3DTP refill(6, 6, 6, 1.0);
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
  CHECK(finiteParticles(refill.particles));
}

TEST_CASE("sparse 3D two-phase bubble tank rises and keeps headspace sparse") {
  SparseSim3DTP sim(8, 12, 8, 1.0);
  sim.dt = 0.03;
  sim.initBubbleTank();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);

  auto meanY = [&](unsigned char type) {
    double sum = 0.0;
    int count = 0;
    for (size_t i = 0; i < sim.particles.size(); ++i) {
      if (sim.particles.type[i] == type) {
        sum += sim.particles.pos[i].y;
        ++count;
      }
    }
    return count ? sum / count : 0.0;
  };
  double gas0 = meanY(1);
  CHECK(gas0 > 0.0);

  size_t maxActive = 0;
  for (int step = 0; step < 24; ++step) {
    sim.step();
    maxActive = std::max(maxActive, sim.grid.activeCellBlocks());
  }

  CHECK(sim.particles.size() == n0);
  bool finite = true;
  for (size_t i = 0; i < sim.particles.size(); ++i) {
    const auto& p = sim.particles.pos[i];
    finite = finite && std::isfinite(p.x) && std::isfinite(p.y) && std::isfinite(p.z);
  }
  CHECK(finite);
  CHECK(meanY(1) > gas0 + 0.2);
  CHECK(maxActive > 0);
  CHECK(maxActive < sim.grid.totalCellBlocks());
}
