#pragma once
#include <vector>
#include <cstddef>
#include <algorithm>
enum class Cell3 : unsigned char { AIR=0, FLUID=1, SOLID=2 };
struct UniformGrid3D {
  int nx, ny, nz;
  double dx, ox=0.0, oy=0.0, oz=0.0;
  std::vector<double> ufield, vfield, wfield;
  std::vector<double> mu, mv, mw;
  std::vector<double> bu, bv, bw;
  std::vector<double> pfield;
  std::vector<Cell3> marker;
  UniformGrid3D(int nx_,int ny_,int nz_,double dx_)
    : nx(nx_),ny(ny_),nz(nz_),dx(dx_),
      ufield((nx_+1)*ny_*nz_,0.0), vfield(nx_*(ny_+1)*nz_,0.0), wfield(nx_*ny_*(nz_+1),0.0),
      mu((nx_+1)*ny_*nz_,0.0), mv(nx_*(ny_+1)*nz_,0.0), mw(nx_*ny_*(nz_+1),0.0),
      bu((nx_+1)*ny_*nz_,1.0), bv(nx_*(ny_+1)*nz_,1.0), bw(nx_*ny_*(nz_+1),1.0),
      pfield(nx_*ny_*nz_,0.0), marker(nx_*ny_*nz_,Cell3::AIR) {}
  size_t u_size() const { return ufield.size(); }
  size_t v_size() const { return vfield.size(); }
  size_t w_size() const { return wfield.size(); }
  size_t cell_size() const { return pfield.size(); }
  int uidx(int i,int j,int k) const { return i + (nx+1)*(j + ny*k); }
  int vidx(int i,int j,int k) const { return i + nx*(j + (ny+1)*k); }
  int widx(int i,int j,int k) const { return i + nx*(j + ny*k); }
  int cidx(int i,int j,int k) const { return i + nx*(j + ny*k); }
  double& u(int i,int j,int k){ return ufield[uidx(i,j,k)]; }
  double& v(int i,int j,int k){ return vfield[vidx(i,j,k)]; }
  double& w(int i,int j,int k){ return wfield[widx(i,j,k)]; }
  double& p(int i,int j,int k){ return pfield[cidx(i,j,k)]; }
  Cell3& cell(int i,int j,int k){ return marker[cidx(i,j,k)]; }
  const double& u(int i,int j,int k) const { return ufield[uidx(i,j,k)]; }
  const double& v(int i,int j,int k) const { return vfield[vidx(i,j,k)]; }
  const double& w(int i,int j,int k) const { return wfield[widx(i,j,k)]; }
  const double& p(int i,int j,int k) const { return pfield[cidx(i,j,k)]; }
  const Cell3& cell(int i,int j,int k) const { return marker[cidx(i,j,k)]; }
  bool inBounds(int i,int j,int k) const { return i>=0&&i<nx&&j>=0&&j<ny&&k>=0&&k<nz; }
  void clear(){
    std::fill(ufield.begin(),ufield.end(),0.0); std::fill(vfield.begin(),vfield.end(),0.0);
    std::fill(wfield.begin(),wfield.end(),0.0); std::fill(mu.begin(),mu.end(),0.0);
    std::fill(mv.begin(),mv.end(),0.0); std::fill(mw.begin(),mw.end(),0.0);
    std::fill(pfield.begin(),pfield.end(),0.0);
  }
};
