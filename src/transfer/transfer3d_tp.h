#pragma once
struct UniformGrid3D;
struct Particles3DTP;
struct PhaseParams;
double calibrateRhoTilde0(const PhaseParams& pp, double Vp);
void p2g_tp(UniformGrid3D& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp);
void g2p_tp(const UniformGrid3D& g, Particles3DTP& ps, const UniformGrid3D& saved, double aL, double aG);
