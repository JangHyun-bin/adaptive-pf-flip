#pragma once
template<int B> struct SparseMacGrid3D;

// Single-phase sparse 3D pressure projection (rho=1).
void spProjectStep3D(SparseMacGrid3D<4>& g, double dt, int cg_iters, double cg_tol);
