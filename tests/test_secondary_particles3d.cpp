#include "driver/secondary_particles3d.h"

#include "doctest.h"

#include <cmath>

TEST_CASE("3D secondary lifecycle reabsorbs and expires with volume accounting") {
  Particles3DTP droplets;
  Particles3DTP bubbles;
  std::vector<int> dropletAges;
  std::vector<int> bubbleAges;

  droplets.add({0.51, 4.0, 4.0}, {20.0, 0.0, 0.0}, 0, 2.0);
  bubbles.add({4.0, 4.0, 7.49}, {0.0, 0.0, 0.0}, 1, 3.0);
  dropletAges.push_back(0);
  bubbleAges.push_back(0);

  SecondaryParticleDomain3D domain{8, 8, 8, 1.0, 0.0, 0.0, 0.0};
  SecondaryParticleLifecycleConfig3D config;
  config.enabled = true;
  config.droplet_lifetime_steps = 8;
  config.bubble_lifetime_steps = 1;
  config.velocity_damping = 1.0;
  config.reabsorb_margin_cells = 1.0;
  config.gravity = 0.0;
  config.bubble_buoyancy_scale = 0.0;
  config.particle_volume_scale = 0.5;

  const SecondaryParticleLifecycleStats3D stats =
    advanceSecondaryParticles3D(droplets, bubbles, dropletAges, bubbleAges,
                                domain, config, 0.1);

  CHECK(stats.enabled == 1);
  CHECK(stats.finite == 1);
  CHECK(stats.advected_droplets == 1);
  CHECK(stats.advected_bubbles == 1);
  CHECK(stats.reabsorbed_droplets == 1);
  CHECK(stats.expired_bubbles == 1);
  CHECK(stats.reabsorbed_droplet_volume == doctest::Approx(1.0));
  CHECK(stats.expired_bubble_volume == doctest::Approx(1.5));
  CHECK(stats.current_droplet_volume == doctest::Approx(0.0));
  CHECK(stats.current_bubble_volume == doctest::Approx(0.0));
  CHECK(droplets.size() == 0);
  CHECK(bubbles.size() == 0);
  CHECK(dropletAges.empty());
  CHECK(bubbleAges.empty());
}

TEST_CASE("3D secondary lifecycle disabled keeps particles and syncs ages") {
  Particles3DTP droplets;
  Particles3DTP bubbles;
  std::vector<int> dropletAges;
  std::vector<int> bubbleAges;

  droplets.add({0.51, 4.0, 4.0}, {20.0, 0.0, 0.0}, 0, 2.0);
  bubbles.add({4.0, 4.0, 7.49}, {0.0, 0.0, 0.0}, 1, 3.0);

  SecondaryParticleDomain3D domain{8, 8, 8, 1.0, 0.0, 0.0, 0.0};
  SecondaryParticleLifecycleConfig3D config;
  config.enabled = false;
  config.particle_volume_scale = 0.5;

  const SecondaryParticleLifecycleStats3D stats =
    advanceSecondaryParticles3D(droplets, bubbles, dropletAges, bubbleAges,
                                domain, config, 0.1);

  CHECK(stats.enabled == 0);
  CHECK(stats.advected_droplets == 0);
  CHECK(stats.advected_bubbles == 0);
  CHECK(stats.current_droplet_volume == doctest::Approx(1.0));
  CHECK(stats.current_bubble_volume == doctest::Approx(1.5));
  CHECK(droplets.size() == 1);
  CHECK(bubbles.size() == 1);
  CHECK(dropletAges.size() == 1);
  CHECK(bubbleAges.size() == 1);
  CHECK(droplets.pos[0].x == doctest::Approx(0.51));
}

TEST_CASE("3D secondary physics applies drag gravity and buoyancy") {
  Particles3DTP droplets;
  Particles3DTP bubbles;
  std::vector<int> dropletAges;
  std::vector<int> bubbleAges;

  droplets.add({0.51, 4.0, 4.0}, {10.0, 0.0, 0.0}, 0, 1.0);
  bubbles.add({7.49, 4.0, 4.0}, {0.0, 0.0, 0.0}, 1, 1.0);
  dropletAges.push_back(0);
  bubbleAges.push_back(0);

  SecondaryParticleDomain3D domain{8, 8, 8, 1.0, 0.0, 0.0, 0.0};
  SecondaryParticleLifecycleConfig3D config;
  config.enabled = true;
  config.droplet_lifetime_steps = 8;
  config.bubble_lifetime_steps = 8;
  config.velocity_damping = 1.0;
  config.reabsorb_margin_cells = 1.0;
  config.gravity = -10.0;
  config.droplet_gravity_scale = 0.5;
  config.bubble_buoyancy_scale = 0.25;
  config.droplet_drag = 1.0;
  config.bubble_drag = 0.0;

  const SecondaryParticleLifecycleStats3D stats =
    advanceSecondaryParticles3D(droplets, bubbles, dropletAges, bubbleAges,
                                domain, config, 0.1);

  const double dropletDamping = std::exp(-0.1);
  CHECK(stats.enabled == 1);
  CHECK(stats.finite == 1);
  CHECK(stats.dragged_droplets == 1);
  CHECK(stats.dragged_bubbles == 0);
  CHECK(stats.reabsorbed_droplets == 0);
  CHECK(stats.reabsorbed_bubbles == 0);
  REQUIRE(droplets.size() == 1);
  REQUIRE(bubbles.size() == 1);
  CHECK(droplets.vel[0].x == doctest::Approx(10.0 * dropletDamping));
  CHECK(droplets.vel[0].y == doctest::Approx(-0.5 * dropletDamping));
  CHECK(droplets.pos[0].x == doctest::Approx(0.51 + 10.0 * dropletDamping * 0.1));
  CHECK(bubbles.vel[0].y == doctest::Approx(0.25));
  CHECK(bubbles.pos[0].y == doctest::Approx(4.025));
}
