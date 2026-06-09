#pragma once
struct UniformGrid2D;
struct Particles2DTP;
struct PhaseParams;
double calibrateRhoTilde0_2d(const PhaseParams& pp, double Vp);
void p2g_tp(UniformGrid2D& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void g2p_tp(const UniformGrid2D& g, Particles2DTP& ps, const UniformGrid2D& saved,
            double alpha_liquid, double alpha_gas);
