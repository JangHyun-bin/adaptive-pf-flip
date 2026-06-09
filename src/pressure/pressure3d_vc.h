#pragma once
#include <vector>
struct UniformGrid3D;
std::vector<double> divergenceVC(const UniformGrid3D& g);
double solvePressureVC(UniformGrid3D& g, const std::vector<double>& div, double dt, int max_iter, double tol);
void projectVC(UniformGrid3D& g, double dt);
