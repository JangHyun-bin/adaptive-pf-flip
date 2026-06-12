#pragma once

#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"

void mrP2G_tp(MRMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void mrG2P_tp(const MRMacGrid2D<8>& g, Particles2DTP& ps, const MRMacGrid2D<8>& saved,
              double aL, double aG);
void mrAdvect_tp(Particles2DTP& ps, const MRMacGrid2D<8>& g, double dt);
