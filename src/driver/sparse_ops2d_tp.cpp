#include "driver/sparse_ops2d_tp.h"
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cmath>

// Eq.6 cubic kernel on squared distance; KR in cells (dense transfer2d_tp.cpp mirror)
static inline double kern(double d2, double r){ double q=d2/(r*r), t=1.0-q; return (t>0.0)? t*t*t : 0.0; }
static const double KR = 1.5;

// normalized 2-pass splat (partition of unity per particle) into u-field, ref()-activating writes
static void splatUK(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  const int W=g.nx+1, H=g.ny;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.u(ii,jj)+=(float)(w*mom); g.mu(ii,jj)+=(float)(w*m); }
}
// same for v-field
static void splatVK(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  const int W=g.nx, H=g.ny+1;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.v(ii,jj)+=(float)(w*mom); g.mv(ii,jj)+=(float)(w*m); }
}

void spP2G_tp(SparseMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp){
  g.uf.clear(); g.vf.clear(); g.muf.clear(); g.mvf.clear();
  for(size_t k=0;k<ps.size();++k){
    double rho=(ps.type[k]==0)? pp.rho_l : pp.rho_g; double mp=rho*Vp;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatUK(g, px, py-0.5, mp*ps.vel[k].x, mp);
    splatVK(g, px-0.5, py, mp*ps.vel[k].y, mp);
  }
  // normalize: face velocity = momentum / raw mass, over active mass blocks only
  for(int b: g.muf.activeBlocks()){ int bx,by; g.muf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>g.nx||j>=g.ny) continue;
      float m=g.gmu(i,j); if(m>0) g.u(i,j)=g.gu(i,j)/m; } }
  for(int b: g.mvf.activeBlocks()){ int bx,by; g.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=g.nx||j>g.ny) continue;
      float m=g.gmv(i,j); if(m>0) g.v(i,j)=g.gv(i,j)/m; } }
}

// clamped bilinear samplers on sparse fields (file-local; Phase A sparse_ops2d.cpp mirror)
static float sU(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5); double fx=px-i0,fy=(py-0.5)-j0;
  auto v=[&](int i,int j){ return g.gu(std::max(0,std::min(g.nx,i)),std::max(0,std::min(g.ny-1,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
static float sV(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py); double fx=(px-0.5)-i0,fy=py-j0;
  auto v=[&](int i,int j){ return g.gv(std::max(0,std::min(g.nx-1,i)),std::max(0,std::min(g.ny,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }

void spG2P_tp(const SparseMacGrid2D<8>& g, Particles2DTP& ps, const SparseMacGrid2D<8>& saved, double aL, double aG){
  for(size_t k=0;k<ps.size();++k){
    double a=(ps.type[k]==0)? aL : aG;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sU(g,px,py), vn=sV(g,px,py);
    double du=un-sU(saved,px,py), dv=vn-sV(saved,px,py);
    double pic_x=un, pic_y=vn, flip_x=ps.vel[k].x+du, flip_y=ps.vel[k].y+dv;
    ps.vel[k].x=a*flip_x+(1-a)*pic_x; ps.vel[k].y=a*flip_y+(1-a)*pic_y;
  }
}
void spAdvect_tp(Particles2DTP& ps, const SparseMacGrid2D<8>& g, double dt){
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(g,px,py),v1=sV(g,px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(g,mx/g.dx,my/g.dx),v2=sV(g,mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); }
}
