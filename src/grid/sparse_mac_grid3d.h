#pragma once
#include "grid/sparse_block_grid3d.h"

// 3D MAC grid backed by sparse block fields.
template<int B>
struct SparseMacGrid3D {
  int nx, ny, nz;
  double dx, ox=0.0, oy=0.0, oz=0.0;
  SparseBlockGrid3D<B> uf, vf, wf;
  SparseBlockGrid3D<B> muf, mvf, mwf;
  SparseBlockGrid3D<B> pf, mkf;

  SparseMacGrid3D(int nx_, int ny_, int nz_, double dx_)
    : nx(nx_), ny(ny_), nz(nz_), dx(dx_),
      uf(nx_+1,ny_,nz_,dx_), vf(nx_,ny_+1,nz_,dx_), wf(nx_,ny_,nz_+1,dx_),
      muf(nx_+1,ny_,nz_,dx_), mvf(nx_,ny_+1,nz_,dx_), mwf(nx_,ny_,nz_+1,dx_),
      pf(nx_,ny_,nz_,dx_), mkf(nx_,ny_,nz_,dx_) {}

  float& u(int i,int j,int k){ return uf.ref(i,j,k); }
  float& v(int i,int j,int k){ return vf.ref(i,j,k); }
  float& w(int i,int j,int k){ return wf.ref(i,j,k); }
  float& mu(int i,int j,int k){ return muf.ref(i,j,k); }
  float& mv(int i,int j,int k){ return mvf.ref(i,j,k); }
  float& mw(int i,int j,int k){ return mwf.ref(i,j,k); }
  float& p(int i,int j,int k){ return pf.ref(i,j,k); }

  float gu(int i,int j,int k) const { return uf.get(i,j,k); }
  float gv(int i,int j,int k) const { return vf.get(i,j,k); }
  float gw(int i,int j,int k) const { return wf.get(i,j,k); }
  float gmu(int i,int j,int k) const { return muf.get(i,j,k); }
  float gmv(int i,int j,int k) const { return mvf.get(i,j,k); }
  float gmw(int i,int j,int k) const { return mwf.get(i,j,k); }
  float gp(int i,int j,int k) const { return pf.get(i,j,k); }

  void setCell(int i,int j,int k,int c){ mkf.ref(i,j,k)=(float)c; }
  int cell(int i,int j,int k) const { return (int)(mkf.get(i,j,k)+0.5f); }
  bool inBounds(int i,int j,int k) const {
    return i>=0&&i<nx&&j>=0&&j<ny&&k>=0&&k<nz;
  }
  void clearAll(){
    uf.clear(); vf.clear(); wf.clear();
    muf.clear(); mvf.clear(); mwf.clear();
    pf.clear(); mkf.clear();
  }
  size_t activeCellBlocks() const { return pf.activeBlockCount(); }
  size_t totalCellBlocks() const { return pf.totalBlocks(); }
};
