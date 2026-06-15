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
  void residual(const std::vector<double>& x,
                const std::vector<double>& rhs,
                std::vector<double>& out) const;
  double weightedDot(const std::vector<double>& a, const std::vector<double>& b) const;
  double weightedL2Norm(const std::vector<double>& x) const;
};

struct MRPressureAggregation3D {
  std::vector<int> fine_to_coarse;
  std::vector<double> fine_volumes;
  std::vector<double> coarse_volumes;

  int fineCount() const { return static_cast<int>(fine_to_coarse.size()); }
  int coarseCount() const { return static_cast<int>(coarse_volumes.size()); }
};

struct MRPressureCoarseCorrectionConfig3D {
  int max_iterations = 64;
  double absolute_tolerance = 1e-12;
  double relative_tolerance = 1e-10;
  int pinned_cell = 0;
};

struct MRPressureCoarseCorrectionStats3D {
  int coarse_cells = 0;
  int coarse_edges = 0;
  int pinned_cell = -1;
  int max_iterations = 0;
  int iterations = 0;
  double tolerance = 0.0;
  double relative_tolerance = 0.0;
  double effective_tolerance = 0.0;
  double initial_residual = 0.0;
  double final_residual = 0.0;
  bool converged = false;
  bool breakdown = false;
};

struct MRPressureSolveStats3D {
  int active_cells = 0;
  int pinned_cell = -1;
  int max_iterations = 0;
  int iterations = 0;
  int restarts = 0;
  int beta_resets = 0;
  int relaxation_sweeps = 0;
  int relaxation_accepted = 0;
  int relaxation_rejected = 0;
  int coarse_correction_cells = 0;
  int coarse_correction_iterations = 0;
  int coarse_correction_max_iterations = 0;
  int coarse_correction_sweeps = 0;
  int coarse_correction_accepted_sweeps = 0;
  int coarse_correction_rejected_sweeps = 0;
  int coarse_preconditioner_cells = 0;
  int coarse_preconditioner_applications = 0;
  int coarse_preconditioner_accepted_applications = 0;
  int coarse_preconditioner_rejected_applications = 0;
  int coarse_preconditioner_iterations = 0;
  int coarse_preconditioner_max_iterations = 0;
  double tolerance = 0.0;
  double relative_tolerance = 0.0;
  double effective_tolerance = 0.0;
  double restart_growth_threshold = 0.0;
  double relaxation_omega = 0.0;
  double relaxation_min_omega = 0.0;
  double relaxation_final_omega = 0.0;
  double coarse_correction_tolerance = 0.0;
  double coarse_correction_relative_tolerance = 0.0;
  double coarse_correction_effective_tolerance = 0.0;
  double coarse_correction_initial_residual = 0.0;
  double coarse_correction_final_residual = 0.0;
  double coarse_correction_min_scale = 0.0;
  double coarse_correction_last_scale = 0.0;
  double coarse_preconditioner_tolerance = 0.0;
  double coarse_preconditioner_relative_tolerance = 0.0;
  double coarse_preconditioner_effective_tolerance = 0.0;
  double coarse_preconditioner_scale = 0.0;
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
  bool used_flexible_cg_beta = false;
  bool used_average_projection = false;
  bool used_jacobi_preconditioner = true;
  bool used_coarse_correction = false;
  bool coarse_correction_accepted = false;
  bool coarse_correction_converged = false;
  bool coarse_correction_breakdown = false;
  bool used_coarse_preconditioner = false;
  bool coarse_preconditioner_breakdown = false;
};

struct MRPressureSolveConfig3D {
  int max_iterations = 0;
  double absolute_tolerance = 0.0;
  double relative_tolerance = 0.0;
  bool use_jacobi_preconditioner = true;
  bool use_flexible_cg_beta = false;
  bool adaptive_restart = true;
  double restart_growth_threshold = 10.0;
  int relaxation_sweeps = 0;
  double relaxation_omega = 0.67;
  double relaxation_min_omega = 0.05;
  int residual_history_stride = 0;
  int residual_history_limit = 0;
  bool use_coarse_correction = false;
  int coarse_correction_iterations = 32;
  int coarse_correction_sweeps = 1;
  double coarse_correction_absolute_tolerance = 0.0;
  double coarse_correction_relative_tolerance = 1e-3;
  double coarse_correction_min_scale = 1.0 / 64.0;
  bool use_coarse_preconditioner = false;
  int coarse_preconditioner_iterations = 8;
  double coarse_preconditioner_absolute_tolerance = 0.0;
  double coarse_preconditioner_relative_tolerance = 1e-2;
  double coarse_preconditioner_scale = 1.0;
};

MRPressureSystem3D buildMRPressureSystem3D(const MRMacGrid3D<4>& g, double dt);
MRPressureAggregation3D buildMRPressureAggregation3D(
  const MRPressureSystem3D& sys,
  const std::vector<int>& fineToCoarse);
MRPressureAggregation3D buildMRPressureLevel1Aggregation3D(
  const MRMacGrid3D<4>& g,
  const MRPressureSystem3D& sys);
void restrictMRPressureVolumeWeighted3D(
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& fineValues,
  std::vector<double>& coarseValues);
void prolongMRPressurePiecewiseConstant3D(
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& coarseValues,
  std::vector<double>& fineValues);
MRPressureSystem3D buildGalerkinCoarseSystem3D(
  const MRPressureSystem3D& fine,
  const MRPressureAggregation3D& aggregation);
void applyGalerkinCoarseCorrection3D(
  const MRPressureSystem3D& fine,
  const MRPressureAggregation3D& aggregation,
  const std::vector<double>& fineResidual,
  const MRPressureCoarseCorrectionConfig3D& config,
  std::vector<double>& fineCorrection,
  MRPressureCoarseCorrectionStats3D* stats = nullptr);
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
