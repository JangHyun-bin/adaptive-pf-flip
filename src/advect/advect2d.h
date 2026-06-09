#pragma once
struct UniformGrid2D;
struct Particles2D;
void advect(Particles2D& ps, const UniformGrid2D& g, double dt);
