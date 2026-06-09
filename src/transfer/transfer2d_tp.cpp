#include "transfer/transfer2d_tp.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>
#include <vector>

static inline double kernel(double dx2_cells, double r){
  double q = dx2_cells/(r*r); double t = 1.0 - q; return (t>0.0) ? t*t*t : 0.0;
}

// Normalized splat: weights are divided by their sum so partition-of-unity holds.
// This guarantees sum_nodes(w_i) == 1 per particle -> exact momentum conservation.
static void splatK(std::vector<double>& field, std::vector<double>& mass,
                   int sw,int W,int H, double gx,double gy, double mom,double m, double r){
  int rad=(int)std::ceil(r); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  // Two-pass: first accumulate weights, then splat normalized.
  double wsum = 0.0;
  for(int dj=-rad; dj<=rad+1; ++dj) for(int di=-rad; di<=rad+1; ++di){
    int ii=i0+di, jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double ddx=(gx-ii), ddy=(gy-jj); double d2=ddx*ddx+ddy*ddy;
    wsum += kernel(d2,r);
  }
  if(wsum <= 0.0) return;
  for(int dj=-rad; dj<=rad+1; ++dj) for(int di=-rad; di<=rad+1; ++di){
    int ii=i0+di, jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double ddx=(gx-ii), ddy=(gy-jj); double d2=ddx*ddx+ddy*ddy;
    double w=kernel(d2,r)/wsum; if(w<=0.0) continue;
    int idx=ii+sw*jj; field[idx]+=w*mom; mass[idx]+=w*m;
  }
}
static const double KR = 1.5;   // kernel support radius (cells)

double calibrateRhoTilde0(const PhaseParams& pp, double Vp){
  UniformGrid2D g(8,8,1.0);
  double mp = pp.rho_l*Vp;
  for(int j=0;j<8;++j) for(int i=0;i<8;++i) for(int s=0;s<4;++s){
    double x=i+0.25+0.5*(s%2), y=j+0.25+0.5*(s/2);
    splatK(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny, x, y-0.5, 0.0, mp, KR);
  }
  double raw = g.mu[4+(g.nx+1)*4];
  return (raw>0)? raw/pp.rho_l : 1.0;
}
void p2g_tp(UniformGrid2D& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0); std::fill(g.vfield.begin(),g.vfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0); std::fill(g.mv.begin(),g.mv.end(),0.0);
  for(size_t k=0;k<ps.size();++k){
    double rho=(ps.type[k]==0)? pp.rho_l : pp.rho_g; double mp=rho*Vp;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatK(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny, px, py-0.5, mp*ps.vel[k].x, mp, KR);
    splatK(g.vfield,g.mv, g.nx,  g.nx,g.ny+1, px-0.5, py, mp*ps.vel[k].y, mp, KR);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0.0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0.0) g.vfield[i]/=g.mv[i];
}
static double triF(const std::vector<double>& f,int sw,int W,int H,double gx,double gy){
  int i0=(int)std::floor(gx),j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  auto get=[&](int ii,int jj){ ii=std::max(0,std::min(W-1,ii)); jj=std::max(0,std::min(H-1,jj)); return f[ii+sw*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0)+fx*(1-fy)*get(i0+1,j0)+(1-fx)*fy*get(i0,j0+1)+fx*fy*get(i0+1,j0+1);
}
static double sU(const UniformGrid2D& g,double px,double py){ return triF(g.ufield,g.nx+1,g.nx+1,g.ny,px,py-0.5); }
static double sV(const UniformGrid2D& g,double px,double py){ return triF(g.vfield,g.nx,g.nx,g.ny+1,px-0.5,py); }
void g2p_tp(const UniformGrid2D& g, Particles2DTP& ps, const UniformGrid2D& saved, double aL, double aG){
  for(size_t k=0;k<ps.size();++k){
    double a=(ps.type[k]==0)? aL : aG;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sU(g,px,py), vn=sV(g,px,py);
    double du=un-sU(saved,px,py), dv=vn-sV(saved,px,py);
    Vec2 pic{un,vn}; Vec2 flip{ps.vel[k].x+du, ps.vel[k].y+dv};
    ps.vel[k]=flip*a + pic*(1.0-a);
  }
}
