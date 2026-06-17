#pragma once
#include "driver/particle_escape3d.h"

template<int B> struct SparseMacGrid3D;
struct Particles3DTP;
struct PhaseParams;

void spP2G3D_tp(SparseMacGrid3D<4>& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp);
void spProjectStepVC3D(SparseMacGrid3D<4>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol,
                       double divergenceCorrection = 0.0);
void spG2P3D_tp(const SparseMacGrid3D<4>& g, Particles3DTP& ps, const SparseMacGrid3D<4>& saved, double aL, double aG);
void spAdvect3D_tp(Particles3DTP& ps, const SparseMacGrid3D<4>& g, double dt,
                   ParticleEscapeStats3D* stats = nullptr,
                   int advectionOrder = 2);
