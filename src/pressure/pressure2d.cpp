#include "pressure/pressure2d.h"
#include "grid/uniform_grid2d.h"
#include <cmath>
#include <algorithm>

std::vector<double> divergence(const UniformGrid2D& g) {
  UniformGrid2D& gm = const_cast<UniformGrid2D&>(g);
  std::vector<double> d(g.nx*g.ny, 0.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    double du = gm.u(i+1,j) - gm.u(i,j);
    double dv = gm.v(i,j+1) - gm.v(i,j);
    d[i + g.nx*j] = (du + dv)/g.dx;
  }
  return d;
}

namespace {
inline bool isFluid(UniformGrid2D& g, int i, int j) {
  return g.inBounds(i,j) && g.cell(i,j) == Cell::FLUID;
}
inline bool isSolid(UniformGrid2D& g, int i, int j) {
  return !g.inBounds(i,j) || g.cell(i,j) == Cell::SOLID;
}
void applyA(UniformGrid2D& g, double scale,
            const std::vector<double>& x, std::vector<double>& out) {
  const int di[4]={1,-1,0,0}, dj[4]={0,0,1,-1};
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    int c = i + g.nx*j; out[c] = 0.0;
    if (!isFluid(g,i,j)) continue;
    double diag=0.0, off=0.0;
    for (int n=0;n<4;++n){
      int ni=i+di[n], nj=j+dj[n];
      if (isSolid(g,ni,nj)) continue;
      diag += 1.0;
      if (isFluid(g,ni,nj)) off += x[ni + g.nx*nj];
    }
    out[c] = scale*(diag*x[c] - off);
  }
}
double diagOf(UniformGrid2D& g, double scale, int i, int j) {
  const int di[4]={1,-1,0,0}, dj[4]={0,0,1,-1}; double d=0.0;
  for (int n=0;n<4;++n) if (!isSolid(g,i+di[n],j+dj[n])) d+=1.0;
  return scale*d;
}
} // namespace

double solvePressure(UniformGrid2D& g, const std::vector<double>& div,
                     double dt, double rho, int max_iter, double tol) {
  int N = g.nx*g.ny;
  double scale = dt/(rho*g.dx*g.dx);
  std::vector<double> x(N,0.0), r(N,0.0), z(N,0.0), pdir(N,0.0), Ap(N,0.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    int c=i+g.nx*j; r[c] = isFluid(g,i,j) ? -div[c] : 0.0;
  }
  auto precond = [&](const std::vector<double>& in, std::vector<double>& outv){
    for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i){
      int c=i+g.nx*j; double d = isFluid(g,i,j)? diagOf(g,scale,i,j):0.0;
      outv[c] = (d>0.0)? in[c]/d : 0.0; } };
  auto dotp = [&](const std::vector<double>& a, const std::vector<double>& b){
    double s=0.0; for (int k=0;k<N;++k) s+=a[k]*b[k]; return s; };

  double res0 = 0.0; for (int k=0;k<N;++k) res0 = std::max(res0, std::abs(r[k]));
  if (res0 < tol) { g.pfield = x; return res0; }
  precond(r, z); pdir = z;
  double rz = dotp(r, z), res = res0;
  for (int it=0; it<max_iter; ++it) {
    applyA(g, scale, pdir, Ap);
    double pAp = dotp(pdir, Ap);
    if (std::abs(pAp) < 1e-30) break;
    double alpha = rz/pAp;
    for (int k=0;k<N;++k){ x[k]+=alpha*pdir[k]; r[k]-=alpha*Ap[k]; }
    res=0.0; for (int k=0;k<N;++k) res=std::max(res,std::abs(r[k]));
    if (res < tol) break;
    precond(r, z);
    double rz_new = dotp(r, z), beta = rz_new/rz; rz = rz_new;
    for (int k=0;k<N;++k) pdir[k] = z[k] + beta*pdir[k];
  }
  g.pfield = x; return res;
}

void project(UniformGrid2D& g, double dt, double rho) {
  double scale = dt/(rho*g.dx);
  for (int j=0;j<g.ny;++j) for (int i=1;i<g.nx;++i) {
    if (isSolid(g,i-1,j) || isSolid(g,i,j)) { g.u(i,j)=0.0; continue; }
    bool lf=isFluid(g,i-1,j), rf=isFluid(g,i,j);
    if (lf||rf) {
      double pl = lf? g.p(i-1,j):0.0, pr = rf? g.p(i,j):0.0;
      g.u(i,j) -= scale*(pr-pl);
    }
  }
  for (int j=1;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    if (isSolid(g,i,j-1) || isSolid(g,i,j)) { g.v(i,j)=0.0; continue; }
    bool bf=isFluid(g,i,j-1), tf=isFluid(g,i,j);
    if (bf||tf) {
      double pb = bf? g.p(i,j-1):0.0, pt = tf? g.p(i,j):0.0;
      g.v(i,j) -= scale*(pt-pb);
    }
  }
}
