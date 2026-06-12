#pragma once
template<int B> struct SparseMacGrid3D;
struct Particles3D;

// Single-phase sparse 3D pressure projection (rho=1).
void spP2G3D(SparseMacGrid3D<4>& g, const Particles3D& ps);
void spG2P3D(const SparseMacGrid3D<4>& g, Particles3D& ps, const SparseMacGrid3D<4>& saved, double alpha);
void spAdvect3D(Particles3D& ps, const SparseMacGrid3D<4>& g, double dt);
void spProjectStep3D(SparseMacGrid3D<4>& g, double dt, int cg_iters, double cg_tol);
