#include "pressure/pressure2d_vc.h"
#include "grid/uniform_grid2d.h"
#include <cmath>
#include <algorithm>

// Helpers (file scope, but keep in anonymous namespace for ODR safety)
namespace {

inline bool isFluid(UniformGrid2D& g,int i,int j){ return g.inBounds(i,j)&&g.cell(i,j)==Cell::FLUID; }
inline bool isSolid(UniformGrid2D& g,int i,int j){ return !g.inBounds(i,j)||g.cell(i,j)==Cell::SOLID; }
inline bool isAir(UniformGrid2D& g,int i,int j){ return g.inBounds(i,j)&&g.cell(i,j)==Cell::AIR; }
inline double bU(UniformGrid2D& g,int i,int j){ return g.bu[i+(g.nx+1)*j]; }
inline double bV(UniformGrid2D& g,int i,int j){ return g.bv[i+g.nx*j]; }

// Returns index of a cell to pin for pure-Neumann systems.
// Returns -1 if any fluid cell has an AIR neighbor (Dirichlet BC exists).
int findPinCell(UniformGrid2D& g) {
  const int di[4]={1,-1,0,0}, dj[4]={0,0,1,-1};
  int firstFluid = -1;
  for(int j=0;j<g.ny;++j) for(int i=0;i<g.nx;++i) {
    if(!isFluid(g,i,j)) continue;
    if(firstFluid<0) firstFluid = i+g.nx*j;
    for(int n=0;n<4;++n) {
      int ni=i+di[n], nj=j+dj[n];
      if(isAir(g,ni,nj)) return -1; // Dirichlet BC found, no pin needed
    }
  }
  return firstFluid; // pure Neumann: pin the first fluid cell
}

void applyA(UniformGrid2D& g, double scale, const std::vector<double>& x,
            std::vector<double>& out, int pinCell) {
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=i+g.nx*j; out[c]=0.0;
    if(!isFluid(g,i,j)) continue;
    if(c==pinCell){ out[c]=x[c]; continue; } // pinned: A*e_pin = e_pin
    double diag=0,off=0;
    struct F{int ni,nj; double b;};
    F fs[4]={ {i+1,j,bU(g,i+1,j)}, {i-1,j,bU(g,i,j)}, {i,j+1,bV(g,i,j+1)}, {i,j-1,bV(g,i,j)} };
    for(auto& f: fs){
      if(isSolid(g,f.ni,f.nj)) continue;
      diag+=f.b;
      int nc=f.ni+g.nx*f.nj;
      // AIR neighbor or pinned neighbor: Dirichlet p=0, only diagonal contribution
      if(isFluid(g,f.ni,f.nj) && nc!=pinCell) off+=f.b*x[nc];
    }
    out[c]=scale*(diag*x[c]-off);
  }
}

double diagOf(UniformGrid2D& g, double scale, int i, int j, int pinCell){
  int c=i+g.nx*j;
  if(c==pinCell) return 1.0;
  double d=0;
  struct F{int ni,nj;double b;};
  F fs[4]={ {i+1,j,bU(g,i+1,j)},{i-1,j,bU(g,i,j)},{i,j+1,bV(g,i,j+1)},{i,j-1,bV(g,i,j)} };
  for(auto& f:fs) if(!isSolid(g,f.ni,f.nj)) d+=f.b;
  return scale*d;
}

} // namespace

// Divergence: respects solid BCs — solid-adjacent face velocities are treated as 0
// because projectVC will zero them anyway.
std::vector<double> divergenceVC(const UniformGrid2D& g){
  std::vector<double> d(g.nx*g.ny,0.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(g.cell(i,j)!=Cell::FLUID) continue;
    // u-faces: left = (i, j) in ufield, right = (i+1, j)
    // If the neighboring cell is SOLID (or OOB), that face velocity is 0 (solid BC)
    auto solidLeft  = (!g.inBounds(i-1,j) || g.cell(i-1,j)==Cell::SOLID);
    auto solidRight = (!g.inBounds(i+1,j) || g.cell(i+1,j)==Cell::SOLID);
    auto solidBot   = (!g.inBounds(i,j-1) || g.cell(i,j-1)==Cell::SOLID);
    auto solidTop   = (!g.inBounds(i,j+1) || g.cell(i,j+1)==Cell::SOLID);

    double uR = solidRight ? 0.0 : g.u(i+1,j);
    double uL = solidLeft  ? 0.0 : g.u(i,  j);
    double vT = solidTop   ? 0.0 : g.v(i,j+1);
    double vB = solidBot   ? 0.0 : g.v(i,  j);

    d[i+g.nx*j] = ((uR-uL) + (vT-vB)) / g.dx;
  }
  return d;
}

double solvePressureVC(UniformGrid2D& g, const std::vector<double>& div,
                       double dt, int max_iter, double tol){
  int N=g.nx*g.ny;
  double scale=dt/(g.dx*g.dx);
  int pinCell = findPinCell(g);

  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pd(N,0.0),Ap(N,0.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=i+g.nx*j;
    if(!isFluid(g,i,j)) { r[c]=0.0; continue; }
    r[c] = (c==pinCell) ? 0.0 : -div[c];
  }

  auto precond=[&](const std::vector<double>& in, std::vector<double>& o){
    for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
      int c=i+g.nx*j;
      double d=isFluid(g,i,j)?diagOf(g,scale,i,j,pinCell):0.0;
      o[c]=(d>0.0)?in[c]/d:0.0;
    }
  };
  auto dotp=[&](const std::vector<double>& a, const std::vector<double>& b){
    double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s;
  };

  double res0=0;
  for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t]));
  if(res0<tol){ g.pfield=x; return res0; }

  precond(r,z); pd=z;
  double rz=dotp(r,z), res=res0;

  for(int it=0;it<max_iter;++it){
    applyA(g,scale,pd,Ap,pinCell);
    double pAp=dotp(pd,Ap);
    if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp;
    for(int t=0;t<N;++t){ x[t]+=al*pd[t]; r[t]-=al*Ap[t]; }
    res=0;
    for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t]));
    if(res<tol) break;
    precond(r,z);
    double rzn=dotp(r,z), be=rzn/rz;
    rz=rzn;
    for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t];
  }
  g.pfield=x;
  return res;
}

void projectVC(UniformGrid2D& g, double dt){
  double s=dt/g.dx;
  for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){
    if(isSolid(g,i-1,j)||isSolid(g,i,j)){ g.u(i,j)=0; continue; }
    bool a=isFluid(g,i-1,j), b=isFluid(g,i,j);
    if(a||b){
      double pl=a?g.p(i-1,j):0.0, pr=b?g.p(i,j):0.0;
      g.u(i,j)-=s*bU(g,i,j)*(pr-pl);
    }
  }
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(isSolid(g,i,j-1)||isSolid(g,i,j)){ g.v(i,j)=0; continue; }
    bool a=isFluid(g,i,j-1), b=isFluid(g,i,j);
    if(a||b){
      double pb=a?g.p(i,j-1):0.0, pt=b?g.p(i,j):0.0;
      g.v(i,j)-=s*bV(g,i,j)*(pt-pb);
    }
  }
}
