#pragma once
#include <cmath>
#include <algorithm>
struct PhaseParams {
  double rho_l = 1.0;
  double rho_g = 0.01;
  double alpha_phi = 1.0;
  double rho_tilde_0 = 1.0;
};
inline double etaPhi(const PhaseParams& pp){ return std::log(pp.rho_l/pp.rho_g); }
inline double phiFromRawDensity(double rt, const PhaseParams& pp){
  double rmin = etaPhi(pp)*pp.rho_g*pp.rho_tilde_0;
  if(rt < rmin) return 0.0;
  double v = std::sqrt(std::max(rt-rmin,0.0)/(pp.alpha_phi*pp.rho_tilde_0*pp.rho_l));
  return std::min(v, 1.0);
}
inline double densityFromPhi(double phi, const PhaseParams& pp){ return phi*pp.rho_l + (1.0-phi)*pp.rho_g; }
inline double betaFromPhi(double phi, const PhaseParams& pp){ return 1.0/densityFromPhi(phi, pp); }
