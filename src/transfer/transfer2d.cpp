#include "transfer/transfer2d.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include <algorithm>
#include <cmath>

static void splat(std::vector<double>& field, std::vector<double>& mass,
                  int stride_w, int w, int h, double gx, double gy,
                  double mom, double m) {
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx - i0, fy = gy - j0;
  double wgt[2][2] = {{(1-fx)*(1-fy), fx*(1-fy)}, {(1-fx)*fy, fx*fy}};
  for (int dj = 0; dj < 2; ++dj)
    for (int di = 0; di < 2; ++di) {
      int ii = i0+di, jj = j0+dj;
      if (ii < 0 || ii >= w || jj < 0 || jj >= h) continue;
      int idx = ii + stride_w*jj;
      field[idx] += wgt[dj][di]*mom;
      mass[idx]  += wgt[dj][di]*m;
    }
}

void p2g(UniformGrid2D& g, const Particles2D& ps) {
  std::fill(g.ufield.begin(), g.ufield.end(), 0.0);
  std::fill(g.vfield.begin(), g.vfield.end(), 0.0);
  std::fill(g.mu.begin(), g.mu.end(), 0.0);
  std::fill(g.mv.begin(), g.mv.end(), 0.0);
  const double m_p = 1.0;
  for (size_t k = 0; k < ps.size(); ++k) {
    double px = (ps.pos[k].x - g.ox)/g.dx;
    double py = (ps.pos[k].y - g.oy)/g.dx;
    splat(g.ufield, g.mu, g.nx+1, g.nx+1, g.ny, px, py-0.5, m_p*ps.vel[k].x, m_p);
    splat(g.vfield, g.mv, g.nx,   g.nx,   g.ny+1, px-0.5, py, m_p*ps.vel[k].y, m_p);
  }
  for (size_t i = 0; i < g.ufield.size(); ++i) if (g.mu[i] > 0.0) g.ufield[i] /= g.mu[i];
  for (size_t i = 0; i < g.vfield.size(); ++i) if (g.mv[i] > 0.0) g.vfield[i] /= g.mv[i];
}

double sampleU(const UniformGrid2D& g, double px, double py) {
  const std::vector<double>& f = g.ufield;
  int w = g.nx+1, h = g.ny, stride = g.nx+1;
  double gx = px, gy = py - 0.5;
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx-i0, fy = gy-j0;
  auto get = [&](int ii, int jj)->double {
    ii = std::max(0, std::min(w-1, ii)); jj = std::max(0, std::min(h-1, jj));
    return f[ii + stride*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0) + fx*(1-fy)*get(i0+1,j0)
       + (1-fx)*fy*get(i0,j0+1) + fx*fy*get(i0+1,j0+1);
}

double sampleV(const UniformGrid2D& g, double px, double py) {
  const std::vector<double>& f = g.vfield;
  int w = g.nx, h = g.ny+1, stride = g.nx;
  double gx = px - 0.5, gy = py;
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx-i0, fy = gy-j0;
  auto get = [&](int ii, int jj)->double {
    ii = std::max(0, std::min(w-1, ii)); jj = std::max(0, std::min(h-1, jj));
    return f[ii + stride*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0) + fx*(1-fy)*get(i0+1,j0)
       + (1-fx)*fy*get(i0,j0+1) + fx*fy*get(i0+1,j0+1);
}

void g2p(const UniformGrid2D& g, Particles2D& ps,
         const UniformGrid2D& saved, double alpha) {
  for (size_t k = 0; k < ps.size(); ++k) {
    double px = (ps.pos[k].x - g.ox)/g.dx;
    double py = (ps.pos[k].y - g.oy)/g.dx;
    double u_new = sampleU(g, px, py), v_new = sampleV(g, px, py);
    double du = u_new - sampleU(saved, px, py);
    double dv = v_new - sampleV(saved, px, py);
    Vec2 pic{u_new, v_new};
    Vec2 flip{ps.vel[k].x + du, ps.vel[k].y + dv};
    ps.vel[k] = flip*alpha + pic*(1.0 - alpha);
  }
}
