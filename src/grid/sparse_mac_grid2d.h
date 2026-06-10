#pragma once
#include "grid/sparse_block_grid2d.h"
#include <vector>
// MAC grid backed by sparse block fields. Single-phase scalar.
template<int B>
struct SparseMacGrid2D {
  int nx, ny; double dx, ox=0.0, oy=0.0;
  SparseBlockGrid2D<B> uf, vf, muf, mvf, pf, mkf;   // u(nx+1,ny) v(nx,ny+1) masses, p & marker(nx,ny)
  SparseMacGrid2D(int nx_,int ny_,double dx_)
    : nx(nx_), ny(ny_), dx(dx_),
      uf(nx_+1,ny_,dx_), vf(nx_,ny_+1,dx_),
      muf(nx_+1,ny_,dx_), mvf(nx_,ny_+1,dx_),
      pf(nx_,ny_,dx_), mkf(nx_,ny_,dx_) {}
  float& u(int i,int j){ return uf.ref(i,j); }
  float& v(int i,int j){ return vf.ref(i,j); }
  float& mu(int i,int j){ return muf.ref(i,j); }
  float& mv(int i,int j){ return mvf.ref(i,j); }
  float& p(int i,int j){ return pf.ref(i,j); }
  float gu(int i,int j) const { return uf.get(i,j); }
  float gv(int i,int j) const { return vf.get(i,j); }
  float gmu(int i,int j) const { return muf.get(i,j); }
  float gmv(int i,int j) const { return mvf.get(i,j); }
  float gp(int i,int j) const { return pf.get(i,j); }
  void setCell(int i,int j,int c){ mkf.ref(i,j)=(float)c; }
  int cell(int i,int j) const { return (int)(mkf.get(i,j)+0.5f); }   // inactive -> 0 (AIR)
  bool inBounds(int i,int j) const { return i>=0&&i<nx&&j>=0&&j<ny; }
  void clearAll(){ uf.clear(); vf.clear(); muf.clear(); mvf.clear(); pf.clear(); mkf.clear(); }
  size_t activeCellBlocks() const { return pf.activeBlockCount(); }
  size_t totalCellBlocks()  const { return pf.totalBlocks(); }
};
