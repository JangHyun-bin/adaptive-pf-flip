# SPEC-1 — Adaptive PF-FLIP (2025) 충실 코어 재현

> 상태: **설계 승인됨 (사용자 리뷰 대기)**
> 작성일: 2026-06-09
> 대상 논문: B. Braun, J. Bender, N. Thuerey, *"Adaptive Phase-Field-FLIP for Very Large Scale Two-Phase Fluid Simulation"*, ACM TOG 44(4), Article 42 (SIGGRAPH 2025). DOI 10.1145/3730854. 로컬: `ref/3730854.pdf`
> 구현 전략(사용자 확정): **처음부터 C++ on 오픈 MSBG** (`github.com/tum-pbs/MSBG`, Apache-2.0)
> 환경: AMD Threadripper 7970X 32C/64T, RAM 128GB, RTX 4080S 16GB

---

## 1. 목표와 범위

### 1.1 목표
논문의 **핵심 알고리즘을 "방법적으로 동일(algorithmically identical)"하게** 재현한다 — 같은 수식, 같은 알고리즘 구조, 같은 자료구조(MSBG). 최종 산출물은 **표면 재구성 없이 동작하는 phase-field 2상 FLIP 시뮬레이터**(검증된 데모 수준).

### 1.2 "identical"의 계약 (이 스펙의 핵심)
| 의미 | 목표 |
|---|---|
| 알고리즘적 동일 (수식·구조·자료구조) | ✅ **본 스펙의 목표** |
| 결과 동일 (Table/Fig CPU시간·스케일 bit 재현) | ❌ **명시적 비목표** (사유: 솔버 코어 비공개, 미명시 상수, 하드웨어 절반) |

### 1.3 범위 (In / Out)
**In (SPEC-1 = Phase 0~3):**
- 균일 MAC 격자 위 FLIP/PIC 코어 (P2G/G2P, 이류, 점성)
- Phase-field 2상: raw 밀도 → φ 변환(Eq.7), 가변계수 압력투영(Eq.8–10)
- escaped particle → droplet/bubble 분기 (기본형)
- 오픈 MSBG 자료구조 통합 (균일 → 희소·다해상도 격자 교체)
- 검증 하니스 (Fig.6/7/8, Table 4, Rayleigh-Taylor)

**Out (후속 SPEC):**
- 이중 입자-격자 적응성·확률적 조대화 → **SPEC-2**
- 적응형 Poisson 솔버(§6: Galerkin MG + adaptive relaxation + flexible CG) → **SPEC-3** (SPEC-1은 표준 MGPCG로 대체)
- 스프레이 물리·증발·고해상도 래스터화·체적 렌더 → **SPEC-4**
- 플래그십 스케일(30억 입자), Table 5/6 정량 CPU시간 동치

### 1.4 다중 스펙 로드맵
```
SPEC-1 (본 문서)  충실 코어: 2D→3D 단상→phase-field 2상→MSBG 통합
   └─ SPEC-2  이중 적응성 + 확률적 조대화
        └─ SPEC-3  적응형 Poisson 솔버 (§6)
             └─ SPEC-4  스프레이 + VDB export + 렌더
```

---

## 2. 충실도 계약 (컴포넌트별)

| 컴포넌트 | 목표 충실도 | 검증 체크포인트 | 분류 |
|---|---|---|---|
| Eq.7 위상장 변환 | 비트 단위 | Fig.7 1D ρ̃↔φ 곡선 | 🟢 identical |
| P2G/G2P 커널 (Eq.3–6) | 알고리즘 동일 | 질량보존 단위테스트 | 🟢 identical |
| FLIP/PIC 혼합·점성 (Eq.12–13) | 알고리즘 동일 | ν=(1−α)Δx²/6Δt 수치확인 | 🟢 identical |
| 가변계수 Poisson 조립 (Eq.8–10) | 알고리즘 동일 | 결정론적 수렴 | 🟢 identical |
| Galerkin/전이상수 (σ_CF=1/3, σ_FC=2/3, ω=6/7) | 비트 단위 (닫힌형) | 직접 조립 수치 일치 | 🟢 identical |
| escaped particle 처리 | 근사 (판정 타이밍 미명시) | splash 정성 | 🟡 approx |
| 압력 솔버 | 방법 대체 (표준 MGPCG; §6는 SPEC-3) | 수렴+발산<tol | 🟡 approx |
| 미명시 상수 (c_div, ρ̃_0, δ_φ…) | 역설계 튜닝 | 정성 거동 | 🟡 approx |
| 초대규모 스케일 | 비목표 (128GB) | — | 🔴 non-goal |

---

## 3. 표기와 핵심 방정식 (구현 대상)

MAC staggered 격자: 압력 `p` = 셀 중심, 속도 `u` = 셀 면. 입자 위치 `x_p`, 속도 `u_p`, 타입 `t_p ∈ {liquid, gas}`(시뮬레이션 내내 고정).

**지배식**
- (Eq.1) `∂u/∂t = −(u·∇)u − (1/ρ)∇p + ν∇²u + f/ρ`
- (Eq.2) `∇·u = 0`
- 밀도/점성 보간: `ρ(x) = φ·ρ_l + (1−φ)·ρ_g` (φ=1 액체, φ=0 기체), `ρ_l/ρ_g ≈ 1000`

**P2G (셀 면 a∈{x,y,z}, 면 인덱스 i)**
- (Eq.5) `m_p = ρ_{t_p}·V_p`
- (Eq.6) 커널 `w_{a,i,p} = (max(1 − (‖x_i + e_a/2 − x_p‖ / r_p)², 0))³`  ← 제곱거리 cubic, √ 회피
- (Eq.3) 질량 `m_{a,i} = Σ_p w_{a,i,p}·m_p`
- (Eq.4) 운동량 `P_{a,i} = Σ_p w_{a,i,p}·m_p·u_p`
- 예비 면속도 `ũ*_{a,i} = P_{a,i} / m_{a,i}`
- **raw 밀도** `ρ̃_{a,i} = m_{a,i}` (면 위 — 후속 β 계수 위치와 동일)

**위상장 (Eq.7)**
```
φ(ρ̃) = 0,                                                if ρ̃ < ρ̃_min
        min( sqrt( max(ρ̃ − ρ̃_min, 0) / (α_φ · ρ̃_0 · ρ_l) ), 1 ),  otherwise
```
- `ρ̃_min = η_φ · ρ_g · ρ̃_0`,  `η_φ = log(ρ_l/ρ_g)`
- `α_φ` 기본 1 (노이즈↔강성 노브), 계면 두께 `ε_φ = r_0 = Δx`
- `ρ̃_0` = 목표 입자 밀도 (셀당 입자 수 기반, 역설계 대상)

**압력투영 (Eq.8–10)**
- 면 계수 `β_{a,i} = 1/ρ_{a,i}`,  `ρ_{a,i} = φ_{a,i}ρ_l + (1−φ_{a,i})ρ_g`  ← φ는 면 위 raw 밀도에서 직접 (보간/외삽 불필요)
- (Eq.8) `Δt · ∇·(β ∇p) = ∇·u* + c_div`
- `c_div` = 부피보존 발산 보정항(목표 밀도 ρ̃_0 유지 — 역설계 대상)
- 투영 `u = u* − Δt · β · ∇p`
- 라플라시안 `L` = SPD 7점 스텐실. **SPEC-1 솔버 = 표준 MGPCG** (대각/MIC 전처리). §6 적응 솔버는 SPEC-3.

**G2P·점성 (Eq.11–13)**
- (Eq.11) `Δu = u − ũ*`
- (Eq.12) `u_p^new = α(u_p^old + I(Δu, x_p)) + (1−α)·I(u, x_p)` (I = trilinear 보간)
- (Eq.13) `ν = (1−α)·Δx² / (6Δt)` → **타입별 α 설정으로 상별 점성** (액체 α≈0.985, 기체 α≈0.96)
- 이류: 액체 속도를 기체 상으로 수 셀 외삽 후 RK3, locally adaptive time stepping

**escaped particle (§3.4)**: 계면 잘못된 쪽 입자 — `φ(x_p) < 1/2 − δ_φ` → droplet(라그랑주 점질량), `φ(x_p) > 1/2 + δ_φ` → bubble(SPEC-1에선 삭제). `δ_φ` 기본 0.2.

---

## 4. 아키텍처 (모듈 / 인터페이스)

```
┌─ M5 Driver ───────────────────────────────────────────┐
│  타임스텝 루프, 씬/경계조건/외력, CFL adaptive dt       │
└───────┬───────────────────────────────────────────────┘
        │ 호출
┌───────▼──────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ M1 Particles │ │ M2 PhaseField│ │ M3 Pressure  │ │ M4 Advect    │
│ P2G/G2P,타입 │ │ Eq.7, β=1/ρ  │ │ Eq.8 조립+   │ │ FLIP/PIC,점성│
│ (Eq.3–6,11–13)│ │              │ │ MGPCG        │ │ RK3          │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       └────────────────┴─── M0 Grid ────┴────────────────┘
                  균일 MAC (Phase 0–2) → 오픈 MSBG (Phase 3)
┌──────────────┐ ┌──────────────┐
│ M6 Validate  │ │ M7 IO        │  (검증 하니스 / 상태·VDB export)
└──────────────┘ └──────────────┘
```

**모듈 인터페이스 (요지)**
- `M0 Grid`: 면/셀 채널 할당·접근, 이웃 스텐실, (Phase3) 희소·다해상도. 추상 인터페이스 `IGrid`로 균일↔MSBG 교체 가능하게.
- `M1 Particles`: `splatP2G(grid, particles) → (m_face, P_face)`, `gatherG2P(grid, particles)`, 입자 풀(타입 고정·재시딩 불필요).
- `M2 PhaseField`: `rawDensityToPhi(m_face) → φ_face` (Eq.7), `faceBeta(φ_face) → β_face`.
- `M3 Pressure`: `assemble(β, divU*, c_div) → (L, b)`, `solve(L, b) → p` (MGPCG), `project(u*, p, β) → u`.
- `M4 Advect`: `blendVelocity(u, ũ*, particles, α)` (Eq.12), `advectRK3(particles, u, dt)`, 속도 외삽.
- `M6 Validate`: 체크포인트 자동 비교 (수치 출력 → 논문 Fig/Table와 대조 리포트).

---

## 5. 빌드 단계 (각 단계 = 검증 게이트)

| Phase | 산출물 | 검증 게이트 (PASS 조건) | 중단 가능? |
|---|---|---|---|
| **0. 2D 코어** | 균일 2D MAC, P2G/G2P, 표준 PCG, FLIP/PIC | 2D dam-break·단일와류 안정·질량보존 오차 < 1% | 기반 |
| **1. 3D 단상** | 3D 확장, 점성(Eq.13), RK3 이류 | 단상 dam-break 정성, ν 수치 일치 | △ |
| **2. ★phase-field 2상** | Eq.7, 가변계수 Poisson(Eq.8–10), escaped 분기 | **(a) Fig.7 1D 곡선 일치, (b) Fig.6 2D φ 슬라이스, (c) shear-flow advection 상대 L2 오차 ≈ 0.03 수준(Table 4), (d) Rayleigh-Taylor A=0.9 spike-tip 거동(Fig.16b)** | ✅ **권장 정지선** |
| **3. MSBG 통합** | `IGrid`를 오픈 MSBG로 교체, refinement map(균일레벨) | **Fig.8 오버헤드 곡선 재계산 일치**, 동일 씬 결과 동등 | ✅ |

> **권장 1차 정지선 = Phase 2 완료** = "논문 핵심(표면재구성 없는 2상 phase-field FLIP)을 보여주는 검증된 데모". 여기서 멈춰도 완결된 산출물.

---

## 6. 기술 스택 / 빌드 (사용자 확정: C++ on MSBG)

### 6.1 오픈 MSBG 실태 (확인됨)
- 라이선스 **Apache-2.0**. 언어 C++11/C. 빌드 `../mk` (Make 기반, CMake 없음). 의존성 **TBB** + **VectorClass**(번들). 일부 **ISPC 커널**(`kernels_ispc.h`).
- 핵심 소스: `msbg.h`(104KB, 메인 API)·`msbg.cpp`(176KB)·`msbg2/3/4.cpp`·`msbgcell.h`, `sbg.h`(128KB)·`sbg.cpp`(희소 블록 격자), `blockpool.*`(블록 메모리풀), `halo.*`(경계 교환), `thread.*`(TBB), `vectorclass_util.h`(SIMD), `visualizeSlices.cpp`/`render.*`(시각화).
- **포함**: MSBG 자료구조 + 8-color lockless splatting + 범용 sparse PDE 커널(평균곡률흐름 `applyChannelPdeFast()`) + halo + SIMD.
- **미포함(백지 구현 대상)**: PF-FLIP 2상 솔버, 압력투영, 입자 시뮬레이션 본체, phase-field 항.

### 6.2 결정 사항
- **D1. Phase 0–2는 자체 균일 MAC 격자**로 시작(MSBG 결합 전 알고리즘 검증). `IGrid` 추상화로 Phase 3에서 MSBG 교체.
- **D2. 압력 솔버**: SPEC-1은 자체 또는 검증된 MGPCG. MSBG의 sparse PDE 커널(`applyChannelPdeFast`)을 Poisson용으로 전용(轉用)할 여지는 SPEC-3에서 평가.
- **D3. 빌드**: MSBG의 `../mk` 흐름에 맞추되, 우리 코드는 분리 디렉토리 + 자체 Makefile, MSBG를 정적 라이브러리로 링크. (CMake 도입은 선택.)
- **D4. 검증 우선**: 성능 최적화(AVX 핫패스)는 정확성 게이트 통과 후. SPEC-1의 목표는 충실도이지 논문 CPU시간이 아님.

### 6.3 오픈 질문 (Phase 3 진입 시 해소)
- Q1. `msbg.h`/`sbg.h`의 실제 채널 생성·면 접근·이웃 스텐실 API 시그니처 (소스 직접 독해 필요 — 문서 없음).
- Q2. MSBG splatting 커널이 면(staggered) 위치 P2G를 직접 지원하는지 vs 셀 중심만인지.
- Q3. MSBG halo 교환이 가변계수 7점 라플라시안에 그대로 쓰이는지.

---

## 7. 검증 전략 (M6 하니스)

| 검증 | 방법 | 기대치 | 출처 |
|---|---|---|---|
| Eq.7 변환 | 1D ρ̃ 스윕 → φ(ρ̃) 플롯 | 곡선 형태 일치 | Fig.7 |
| 질량보존 | 타입 고정 P2G 총합 추적 | 드리프트 ≈ 0 | §3.2 |
| 점성 | α↔ν 매핑 측정 | ν=(1−α)Δx²/6Δt | Eq.13 |
| 2D φ 슬라이스 | 정적/낙하 물방울 | Fig.6 유사 | Fig.6 |
| shear-flow advection | 표준 전단류 이류 테스트 | 상대 L2 ≈ 0.03대 | Table 4 |
| Rayleigh-Taylor | A=0.9, 256×64×64 | spike-tip 위치 거동 | Fig.16b |
| MSBG 오버헤드 | 1−O(n^2.5)/n³ 재계산 | Fig.8 곡선 일치 | Fig.8 |

> 자동화: 각 검증을 회귀 테스트로 코드에 내장. PASS/FAIL + 수치 리포트 출력. (이 하니스 자체가 후속 SPEC과 잠재적 오픈소스 기여의 토대 — 연구 경로 T1-3.)

---

## 8. 비목표 (명시적 스코프 컷)
- ❌ 논문 Table 5·6 정량 CPU시간/반복수 동치 (알고리즘·수렴 *차수*만)
- ❌ 플래그십 스케일(30억 입자, 3072³) — 128GB 한계, ~절반 규모가 상한
- ❌ §6 적응형 Poisson 솔버 (SPEC-3)
- ❌ 스프레이 물리·증발·체적 렌더 룩 매칭 (SPEC-4, 그것도 대체 렌더러)
- ❌ 표면장력(소규모 전용) — 대규모 목표상 SPEC-1 생략

---

## 9. 리스크와 완화
| 리스크 | 영향 | 완화 |
|---|---|---|
| 미명시 상수(c_div, ρ̃_0) 역설계 실패 | 2상 분리 임계 어긋남 | Eq.7 단위검증(Fig.7) 먼저 고정, 상수 스윕 하니스화 (→ T1-2 문서화 자산) |
| MSBG API 미문서 | Phase 3 통합 지연 | Phase 0–2를 자체 균일 격자로 분리, `IGrid` 추상화로 결합 위험 격리 |
| MSBG "research code" 결합 버그 | 빌드/링크 마찰 | 정적 링크 + 최소 표면적 사용, 데모(`msbg_demo`) 먼저 빌드 검증 |
| 압력 솔버 수렴(고밀도비 ill-conditioned) | 발산/느림 | SPEC-1은 표준 MGPCG로 충분(소규모), §6은 SPEC-3로 분리 |
| 1인 공수 초과 | 일정 지연 | Phase 2 정지선을 1차 완결 목표로, 이후는 선택 |

## 10. 공수 (참고, 1인+AI)
- Phase 0–2 (권장 정지선): **약 2~4개월**
- Phase 0–3 (MSBG 통합까지): **약 4~6개월**
- (전체 트랙 B = SPEC-1~4: 5~8개월 데모급 / 정량 동치는 비목표)

---

## 부록 A. 디렉토리 구조 (제안)
```
lsfs/
  ref/3730854.pdf            # 원논문
  external/MSBG/             # 오픈 MSBG (서브모듈/클론)
  src/
    grid/      # M0 IGrid: uniform_grid, msbg_grid
    particles/ # M1 P2G/G2P
    phasefield/# M2 Eq.7, beta
    pressure/  # M3 assemble + MGPCG + project
    advect/    # M4 FLIP/PIC, RK3
    driver/    # M5 sim loop, scenes, BC
    validate/  # M6 검증 하니스
    io/        # M7 state/VDB
  tests/       # 회귀 테스트 (검증 게이트)
  docs/superpowers/specs/    # 본 스펙 + 후속
```
