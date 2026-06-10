#include "driver/sparse_ops2d.h"
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d.h"
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cmath>

static void splatU(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  double w[2][2]={{(1-fx)*(1-fy),fx*(1-fy)},{(1-fx)*fy,fx*fy}};
  for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){ int ii=i0+di,jj=j0+dj;
    if(ii<0||ii>g.nx||jj<0||jj>=g.ny) continue; g.u(ii,jj)+=(float)(w[dj][di]*mom); g.mu(ii,jj)+=(float)(w[dj][di]*m); } }
static void splatV(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  double w[2][2]={{(1-fx)*(1-fy),fx*(1-fy)},{(1-fx)*fy,fx*fy}};
  for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){ int ii=i0+di,jj=j0+dj;
    if(ii<0||ii>=g.nx||jj<0||jj>g.ny) continue; g.v(ii,jj)+=(float)(w[dj][di]*mom); g.mv(ii,jj)+=(float)(w[dj][di]*m); } }

void spP2G(SparseMacGrid2D<8>& g, const Particles2D& ps){
  g.uf.clear(); g.vf.clear(); g.muf.clear(); g.mvf.clear();
  const double mp=1.0;
  for(size_t k=0;k<ps.size();++k){ double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatU(g,px,py-0.5,mp*ps.vel[k].x,mp); splatV(g,px-0.5,py,mp*ps.vel[k].y,mp); }
  // normalize: iterate active u/v mass blocks
  for(int b: g.muf.activeBlocks()){ int bx,by; g.muf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>g.nx||j>=g.ny) continue;
      float m=g.gmu(i,j); if(m>0) g.u(i,j)=g.gu(i,j)/m; } }
  for(int b: g.mvf.activeBlocks()){ int bx,by; g.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=g.nx||j>g.ny) continue;
      float m=g.gmv(i,j); if(m>0) g.v(i,j)=g.gv(i,j)/m; } }
}

static std::vector<int> fluidCells(const SparseMacGrid2D<8>& g){
  std::vector<int> cells;
  for(int b: g.mkf.activeBlocks()){ int bx,by; g.mkf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly;
      if(g.inBounds(i,j) && g.cell(i,j)==1) cells.push_back(i + g.nx*j); } }
  return cells;
}
void spProjectStep(SparseMacGrid2D<8>& g, double dt, int cg_iters, double cg_tol){
  auto cells = fluidCells(g);
  int N=(int)cells.size(); if(N==0) return;
  std::unordered_map<int,int> idx; idx.reserve(N*2);
  for(int t=0;t<N;++t) idx[cells[t]]=t;
  auto isFluid=[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==1; };
  auto isSolid=[&](int i,int j){ return !g.inBounds(i,j) || g.cell(i,j)==2; };
  double scale=dt/(g.dx*g.dx);
  // rhs b = -divergence at fluid cells
  std::vector<double> bvec(N), x(N,0),r(N),z(N),pd(N),Ap(N);
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx, j=cells[t]/g.nx;
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j))/g.dx; bvec[t]=-d; r[t]=bvec[t]; }
  auto diagOf=[&](int i,int j){ double d=0; const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int n=0;n<4;++n) if(!isSolid(i+di[n],j+dj[n])) d+=1.0; return scale*d; };
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; double diag=0,off=0;
      for(int n=0;n<4;++n){ int ni=i+di[n],nj=j+dj[n]; if(isSolid(ni,nj)) continue; diag+=1.0;
        if(isFluid(ni,nj)) off+=xx[idx[ni+g.nx*nj]]; }
      out[t]=scale*(diag*xx[t]-off); } };
  auto prec=[&](const std::vector<double>& in,std::vector<double>& o){ for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; double d=diagOf(i,j); o[t]=(d>0)?in[t]/d:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<cg_tol) return;
  prec(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<cg_iters;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<cg_tol) break;
    prec(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  // write pressure into sparse p-field
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; g.p(i,j)=(float)x[t]; }
  // project: update each u and v face exactly once (mirror of uniform project())
  double s=dt/g.dx;
  // u faces: face u(i,j) is between cell (i-1,j) and cell (i,j). i ranges 1..nx-1
  // Only update if at least one adjacent cell is fluid (and neither is solid)
  // Use a separate pass over the active uf blocks to find candidate faces
  for(int j=0;j<g.ny;++j) for(int i=1;i<g.nx;++i){
    bool lf=isFluid(i-1,j), rf=isFluid(i,j);
    if(!lf&&!rf) continue;
    if(isSolid(i-1,j)||isSolid(i,j)){ g.u(i,j)=0.0f; continue; }
    double pl=lf?g.gp(i-1,j):0.0, pr=rf?g.gp(i,j):0.0;
    g.u(i,j)=g.gu(i,j)-(float)(s*(pr-pl));
  }
  // v faces: face v(i,j) is between cell (i,j-1) and cell (i,j). j ranges 1..ny-1
  for(int j=1;j<g.ny;++j) for(int i=0;i<g.nx;++i){
    bool bf=isFluid(i,j-1), tf=isFluid(i,j);
    if(!bf&&!tf) continue;
    if(isSolid(i,j-1)||isSolid(i,j)){ g.v(i,j)=0.0f; continue; }
    double pb=bf?g.gp(i,j-1):0.0, pt=tf?g.gp(i,j):0.0;
    g.v(i,j)=g.gv(i,j)-(float)(s*(pt-pb));
  }
}
// g2p/advect (Phase 0 mirror, sparse get sampling)
static float sU(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5); double fx=px-i0,fy=(py-0.5)-j0;
  auto v=[&](int i,int j){ return g.gu(std::max(0,std::min(g.nx,i)),std::max(0,std::min(g.ny-1,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
static float sV(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py); double fx=(px-0.5)-i0,fy=py-j0;
  auto v=[&](int i,int j){ return g.gv(std::max(0,std::min(g.nx-1,i)),std::max(0,std::min(g.ny,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
void spG2P(const SparseMacGrid2D<8>& g, Particles2D& ps, const SparseMacGrid2D<8>& saved, double alpha){
  for(size_t k=0;k<ps.size();++k){ double px=(ps.pos[k].x-g.ox)/g.dx,py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sU(g,px,py),vn=sV(g,px,py); double du=un-sU(saved,px,py),dv=vn-sV(saved,px,py);
    double pic_x=un,pic_y=vn, flip_x=ps.vel[k].x+du, flip_y=ps.vel[k].y+dv;
    ps.vel[k].x=alpha*flip_x+(1-alpha)*pic_x; ps.vel[k].y=alpha*flip_y+(1-alpha)*pic_y; } }
void spAdvect(Particles2D& ps, const SparseMacGrid2D<8>& g, double dt){
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(g,px,py),v1=sV(g,px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(g,mx/g.dx,my/g.dx),v2=sV(g,mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); } }
