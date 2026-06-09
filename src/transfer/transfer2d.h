#pragma once
struct UniformGrid2D;
struct Particles2D;
void p2g(UniformGrid2D& g, const Particles2D& ps);
void g2p(const UniformGrid2D& g, Particles2D& ps,
         const UniformGrid2D& saved, double alpha);
double sampleU(const UniformGrid2D& g, double px, double py);
double sampleV(const UniformGrid2D& g, double px, double py);
