#pragma once

#include <vector>

template<int B>
struct MRMacGrid2D;
struct PhaseParams;

struct MREdge {
  int a = -1;
  int b = -1;
  double conductance = 0.0;
};

struct MRPressureSystem2D {
  std::vector<double> volumes;
  std::vector<MREdge> edges;

  int cellCount() const { return static_cast<int>(volumes.size()); }
  double volume(int i) const { return volumes[i]; }
  void apply(const std::vector<double>& x, std::vector<double>& out) const;
};

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt);
double maxMRDivergence(const MRMacGrid2D<8>& g);
void projectMR(MRMacGrid2D<8>& g, double dt, int maxIter, double tol);
void projectMR(MRMacGrid2D<8>& g, const PhaseParams& pp, double dt, int maxIter, double tol);
