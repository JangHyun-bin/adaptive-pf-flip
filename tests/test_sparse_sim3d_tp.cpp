#include "doctest.h"
#include "driver/sparse_sim3d_tp.h"
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

bool finiteParticles(const Particles3DTP& particles) {
  for (size_t i = 0; i < particles.size(); ++i) {
    const auto& p = particles.pos[i];
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) {
      return false;
    }
  }
  return true;
}

} // namespace

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

  const size_t n0 = coarse.particles.size();
  coarse.dt = 0.02;
  coarse.step();
  CHECK(coarse.particles.size() <= n0);
  CHECK(countType(coarse.particles, 0) == fullLiquid);
  CHECK(finiteParticles(coarse.particles));
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
