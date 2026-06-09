#pragma once
struct UniformGrid3D;
struct Particles3D;
void p2g(UniformGrid3D& g, const Particles3D& ps);
void g2p(const UniformGrid3D& g, Particles3D& ps, const UniformGrid3D& saved, double alpha);
double sampleU(const UniformGrid3D& g, double px,double py,double pz);
double sampleV(const UniformGrid3D& g, double px,double py,double pz);
double sampleW(const UniformGrid3D& g, double px,double py,double pz);
