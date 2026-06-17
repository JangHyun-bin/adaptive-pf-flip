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

InterfaceDiagnostics3D diagnoseSparseInterface3D(const SparseMacGrid3D<4>& g,
                                                 const PhaseParams& phase);

InterfaceDiagnostics3D diagnoseMRInterface3D(const MRMacGrid3D<4>& g,
                                             const PhaseParams& phase);
