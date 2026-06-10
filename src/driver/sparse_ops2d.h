#pragma once
template<int B> struct SparseMacGrid2D;
struct Particles2D;
// single-phase sparse FLIP ops (m_p=1, rho=1)
void spP2G(SparseMacGrid2D<8>& g, const Particles2D& ps);
void spProjectStep(SparseMacGrid2D<8>& g, double dt, int cg_iters, double cg_tol);
void spG2P(const SparseMacGrid2D<8>& g, Particles2D& ps, const SparseMacGrid2D<8>& saved, double alpha);
void spAdvect(Particles2D& ps, const SparseMacGrid2D<8>& g, double dt);
