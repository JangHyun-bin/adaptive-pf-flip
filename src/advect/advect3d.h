#pragma once
struct UniformGrid3D;
struct Particles3D;
void extrapolateVelocity(UniformGrid3D& g, int sweeps);
void advect(Particles3D& ps, const UniformGrid3D& g, double dt);
