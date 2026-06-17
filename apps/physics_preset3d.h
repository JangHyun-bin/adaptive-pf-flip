#pragma once

constexpr int kPhysicsPresetSteps3D = 16;
constexpr int kLongPhysicsPresetSteps3D = 80;
constexpr int kPhysicsPresetBenchSteps3D = 8;
constexpr int kLongPhysicsPresetBenchSteps3D = 40;

template <typename Sim>
void applyCorePhysicsPreset3D(Sim& sim) {
  sim.adaptive_timestep = true;
  sim.advection_order = 3;
  sim.c_div_volume_correction = true;
  sim.surface_tension = true;
  sim.escaped_particle_branching = true;
  sim.secondary_particle_lifecycle = true;
}

template <typename Sim>
void applyParticleAdaptivityPreset3D(Sim& sim) {
  sim.narrow_band_air = true;
  sim.narrow_band_air_radius = 2;
  sim.gas_particle_coarsening = true;
  sim.gas_particles_per_cell_target = 2;
  sim.liquid_particle_coarsening = true;
  sim.liquid_particles_per_cell_target = 2;
  sim.liquid_particle_refill = true;
  sim.liquid_refill_particles_per_cell_target = 4;
  sim.liquid_particle_refill_max_added_per_step = 160;
  sim.liquid_particle_refill_interface_only = true;
  sim.liquid_particle_refill_interface_radius = 1;
}

template <typename Sim>
void applyFullPhysicsPreset3D(Sim& sim) {
  applyCorePhysicsPreset3D(sim);
  applyParticleAdaptivityPreset3D(sim);
}

template <typename Sim>
bool corePhysicsPresetActive3D(const Sim& sim) {
  return sim.adaptive_timestep &&
         sim.advection_order == 3 &&
         sim.c_div_volume_correction &&
         sim.surface_tension &&
         sim.escaped_particle_branching &&
         sim.secondary_particle_lifecycle;
}

template <typename Sim>
bool particleAdaptivityPresetActive3D(const Sim& sim) {
  return sim.narrow_band_air &&
         sim.narrow_band_air_radius >= 0 &&
         sim.gas_particle_coarsening &&
         sim.gas_particles_per_cell_target > 0 &&
         sim.liquid_particle_coarsening &&
         sim.liquid_particles_per_cell_target > 0 &&
         sim.liquid_particle_refill &&
         sim.liquid_refill_particles_per_cell_target > 0 &&
         sim.liquid_particle_refill_max_added_per_step > 0 &&
         sim.liquid_particle_refill_interface_only &&
         sim.liquid_particle_refill_interface_radius >= 0;
}

template <typename Sim>
bool fullPhysicsPresetActive3D(const Sim& sim) {
  return corePhysicsPresetActive3D(sim) &&
         particleAdaptivityPresetActive3D(sim);
}
