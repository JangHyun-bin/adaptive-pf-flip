#pragma once
#include <vector>
#include <cstddef>
#include <algorithm>

enum class Cell : unsigned char { AIR = 0, FLUID = 1, SOLID = 2 };

struct UniformGrid2D {
  int nx, ny;
  double dx;
  double ox = 0.0, oy = 0.0;

  std::vector<double> ufield, vfield;   // face velocities
  std::vector<double> mu, mv;           // face masses
  std::vector<double> pfield;           // cell pressure
  std::vector<Cell> marker;             // cell type

  UniformGrid2D(int nx_, int ny_, double dx_)
      : nx(nx_), ny(ny_), dx(dx_),
        ufield((nx_+1)*ny_, 0.0), vfield(nx_*(ny_+1), 0.0),
        mu((nx_+1)*ny_, 0.0), mv(nx_*(ny_+1), 0.0),
        pfield(nx_*ny_, 0.0), marker(nx_*ny_, Cell::AIR) {}

  size_t u_size() const { return ufield.size(); }
  size_t v_size() const { return vfield.size(); }
  size_t cell_size() const { return pfield.size(); }

  double& u(int i, int j) { return ufield[i + (nx+1)*j]; }
  double& v(int i, int j) { return vfield[i + nx*j]; }
  double& p(int i, int j) { return pfield[i + nx*j]; }
  Cell& cell(int i, int j) { return marker[i + nx*j]; }

  const double& u(int i, int j) const { return ufield[i + (nx+1)*j]; }
  const double& v(int i, int j) const { return vfield[i + nx*j]; }
  const double& p(int i, int j) const { return pfield[i + nx*j]; }
  const Cell& cell(int i, int j) const { return marker[i + nx*j]; }

  bool inBounds(int i, int j) const { return i>=0 && i<nx && j>=0 && j<ny; }

  void clear() {
    std::fill(ufield.begin(), ufield.end(), 0.0);
    std::fill(vfield.begin(), vfield.end(), 0.0);
    std::fill(mu.begin(), mu.end(), 0.0);
    std::fill(mv.begin(), mv.end(), 0.0);
    std::fill(pfield.begin(), pfield.end(), 0.0);
  }
};
