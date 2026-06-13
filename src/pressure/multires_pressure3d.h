#pragma once

#include <vector>

template<int B>
struct MRMacGrid3D;
struct PhaseParams;

struct MREdge3D {
  int a = -1;
  int b = -1;
  double conductance = 0.0;
};

struct MRPressureSystem3D {
  std::vector<double> volumes;
  std::vector<MREdge3D> edges;

  int cellCount() const { return static_cast<int>(volumes.size()); }
  double volume(int i) const { return volumes[i]; }
  void apply(const std::vector<double>& x, std::vector<double>& out) const;
};

struct MRPressureSolveStats3D {
  int active_cells = 0;
  int pinned_cell = -1;
  int max_iterations = 0;
  int iterations = 0;
  double tolerance = 0.0;
  double initial_residual = 0.0;
  double final_residual = 0.0;
  double min_positive_diag = 0.0;
  double max_diag = 0.0;
  bool converged = false;
  bool breakdown = false;
  bool used_average_projection = false;
};

MRPressureSystem3D buildMRPressureSystem3D(const MRMacGrid3D<4>& g, double dt);
double maxMRDivergence3D(const MRMacGrid3D<4>& g);
void projectMR3D(MRMacGrid3D<4>& g, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats = nullptr);
void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats = nullptr);
