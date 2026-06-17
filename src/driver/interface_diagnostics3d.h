#pragma once

#include "grid/multires_mac_grid3d.h"
#include "grid/sparse_mac_grid3d.h"
#include "physics/phasefield.h"

struct InterfaceDiagnostics3D {
  int sample_cells = 0;
  int interface_cells = 0;
  int finite = 1;
  int surface_tension_candidate = 0;
  double phi_min = 0.0;
  double phi_max = 0.0;
  double phi_mean = 0.0;
  double grad_mean = 0.0;
  double grad_max = 0.0;
  double curvature_abs_mean = 0.0;
  double curvature_abs_max = 0.0;
};

struct SurfaceTensionStats3D {
  int enabled = 0;
  int applied_cells = 0;
  int finite = 1;
  double strength = 0.0;
  double max_delta_speed_limit = 0.0;
  double mean_delta_speed = 0.0;
  double max_delta_speed = 0.0;
};

InterfaceDiagnostics3D diagnoseSparseInterface3D(const SparseMacGrid3D<4>& g,
                                                 const PhaseParams& phase);

InterfaceDiagnostics3D diagnoseMRInterface3D(const MRMacGrid3D<4>& g,
                                             const PhaseParams& phase);

SurfaceTensionStats3D applySparseSurfaceTension3D(SparseMacGrid3D<4>& g,
                                                  const PhaseParams& phase,
                                                  double dt,
                                                  double strength,
                                                  double maxDeltaSpeed);

SurfaceTensionStats3D applyMRSurfaceTension3D(MRMacGrid3D<4>& g,
                                              const PhaseParams& phase,
                                              double dt,
                                              double strength,
                                              double maxDeltaSpeed);
