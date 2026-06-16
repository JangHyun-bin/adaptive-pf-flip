#pragma once

#include "driver/particle_escape3d.h"
#include "grid/multires_mac_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"

void mrP2G3D_tp(MRMacGrid3D<4>& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp);
void mrG2P3D_tp(const MRMacGrid3D<4>& g, Particles3DTP& ps, const MRMacGrid3D<4>& saved,
                double aL, double aG);
void mrAdvect3D_tp(Particles3DTP& ps, const MRMacGrid3D<4>& g, double dt,
                   ParticleEscapeStats3D* stats = nullptr,
                   int advectionOrder = 2);
