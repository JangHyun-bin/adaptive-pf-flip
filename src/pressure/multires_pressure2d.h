#pragma once

#include <vector>

template<int B>
struct MRMacGrid2D;

struct MRPressureSystem2D {
  std::vector<double> volumes;

  int cellCount() const { return static_cast<int>(volumes.size()); }
  double volume(int i) const { return volumes[i]; }
  void apply(const std::vector<double>& x, std::vector<double>& out) const;
};

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt);
double maxMRDivergence(const MRMacGrid2D<8>& g);
void projectMR(MRMacGrid2D<8>& g, double dt, int maxIter, double tol);
