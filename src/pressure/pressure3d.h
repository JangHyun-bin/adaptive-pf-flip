#pragma once
#include <vector>
struct UniformGrid3D;
std::vector<double> divergence(const UniformGrid3D& g);
double solvePressure(UniformGrid3D& g, const std::vector<double>& div, double dt, double rho, int max_iter, double tol);
void project(UniformGrid3D& g, double dt, double rho);
