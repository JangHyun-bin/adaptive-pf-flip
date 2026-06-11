#pragma once
template<int B> struct SparseMacGrid2D;
struct Particles2DTP;
struct PhaseParams;
// two-phase sparse FLIP ops: typed masses m_p = rho_type*Vp; face beta = 1/rho(phi(raw)) computed on the fly
void spP2G_tp(SparseMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void spProjectStepVC(SparseMacGrid2D<8>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol);
void spG2P_tp(const SparseMacGrid2D<8>& g, Particles2DTP& ps, const SparseMacGrid2D<8>& saved, double aL, double aG);
void spAdvect_tp(Particles2DTP& ps, const SparseMacGrid2D<8>& g, double dt);
