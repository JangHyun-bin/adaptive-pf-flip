#pragma once
#include <vector>
struct UniformGrid2D;
std::vector<double> divergenceVC(const UniformGrid2D& g);
double solvePressureVC(UniformGrid2D& g, const std::vector<double>& div, double dt, int max_iter, double tol);
void projectVC(UniformGrid2D& g, double dt);
