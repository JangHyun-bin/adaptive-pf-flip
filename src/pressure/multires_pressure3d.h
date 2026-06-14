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
  int restarts = 0;
  int relaxation_sweeps = 0;
  int relaxation_accepted = 0;
  int relaxation_rejected = 0;
  double tolerance = 0.0;
  double relative_tolerance = 0.0;
  double effective_tolerance = 0.0;
  double restart_growth_threshold = 0.0;
  double relaxation_omega = 0.0;
  double relaxation_min_omega = 0.0;
  double relaxation_final_omega = 0.0;
  double initial_residual = 0.0;
  double final_residual = 0.0;
  double min_residual = 0.0;
  double max_residual = 0.0;
  double min_positive_diag = 0.0;
  double max_diag = 0.0;
  int residual_history_stride = 0;
  int residual_history_limit = 0;
  bool residual_history_truncated = false;
  std::vector<double> residual_history;
  bool converged = false;
  bool breakdown = false;
  bool adaptive_restart = true;
  bool used_average_projection = false;
  bool used_jacobi_preconditioner = true;
};

struct MRPressureSolveConfig3D {
  int max_iterations = 0;
  double absolute_tolerance = 0.0;
  double relative_tolerance = 0.0;
  bool use_jacobi_preconditioner = true;
  bool adaptive_restart = true;
  double restart_growth_threshold = 10.0;
  int relaxation_sweeps = 0;
  double relaxation_omega = 0.67;
  double relaxation_min_omega = 0.05;
  int residual_history_stride = 0;
  int residual_history_limit = 0;
};

MRPressureSystem3D buildMRPressureSystem3D(const MRMacGrid3D<4>& g, double dt);
double maxMRDivergence3D(const MRMacGrid3D<4>& g);
void projectMR3D(MRMacGrid3D<4>& g, double dt, const MRPressureSolveConfig3D& config,
                 MRPressureSolveStats3D* stats = nullptr);
void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt,
                 const MRPressureSolveConfig3D& config,
                 MRPressureSolveStats3D* stats = nullptr);
void projectMR3D(MRMacGrid3D<4>& g, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats = nullptr);
void projectMR3D(MRMacGrid3D<4>& g, const PhaseParams& pp, double dt, int maxIter, double tol,
                 MRPressureSolveStats3D* stats = nullptr);
