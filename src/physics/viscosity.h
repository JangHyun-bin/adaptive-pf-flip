#pragma once
#include <algorithm>
inline double numericalViscosity(double alpha, double dx, double dt){
  return (1.0-alpha)*dx*dx/(6.0*dt);
}
inline double alphaForViscosity(double nu, double dx, double dt){
  double a = 1.0 - 6.0*nu*dt/(dx*dx);
  return std::max(0.0, std::min(1.0, a));
}
