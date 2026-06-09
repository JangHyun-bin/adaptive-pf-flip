#pragma once
#include <vector>
struct UniformGrid2D;
std::vector<double> divergence(const UniformGrid2D& g);
double solvePressure(UniformGrid2D& g, const std::vector<double>& div,
                     double dt, double rho, int max_iter, double tol);
void project(UniformGrid2D& g, double dt, double rho);
