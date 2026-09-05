# NEI — research discussion note

[Interactive architecture and discussion](https://gahyoun.github.io/Project-NEI/)

## 1. Reading rule

- Definition → assumptions → identity → diagnostic → empirical evidence → allowed conclusion.
  - Edge: dependency or named relation. Causality 아님.
  - NEI: fully specified protocol 아래 terminal geometry의 spread.
  - Representability: fixed graph metric과 target dimension의 spectral property.
  - 서로 다른 estimand라는 사실과 statistical independence는 별개.
- Terminology.
  - 1차 일단락: definition, numerical admissibility, finite-protocol evidence.
  - 2차 일단락 대상: controlled mechanism analysis, path/barrier evidence, size-dependent theory.
  - Korean nominal statements와 English technical terms 사용.

## 2. Review status — 2026-09-05

- Numerical audit.
  - floor_test.py와 calibration_null.py에서 stress–gradient coefficient mismatch 확인.
    - Declared stress: $\mathcal F=\sum_{i<j}(d_{ij}-\delta_{ij})^2$.
    - Required gradient: $2\sum_{j\ne i}(1-\delta_{ij}/d_{ij})(x_i-x_j)$.
    - Legacy implementation: required gradient의 1/2.
  - 두 script 수정 및 central finite-difference checks 통과.
    - Floor relative error: $2.017\times10^{-10}$.
    - Calibration relative error: $1.449\times10^{-10}$.
  - Existing result table은 legacy snapshot으로 보존. Corrected full rerun 미실행.
    - Legacy residual의 단순 배율 수정으로 optimizer trajectory·termination 재검증을 대체할 수 없음.
    - Nominal gtol과 achieved gradient 구분. gtol과 ftol을 함께 바꾼 coupled tolerance test.
    - gtol이 machine epsilon보다 작다는 사실만으로 “double precision 범위 밖”이라는 해석 불가.
- Sampling-frame audit.
  - 현재 선택된 48-network subset의 spectral result 보존.
  - CSV 48행의 decomposition, range, monotonicity, leading-eigenvalue identities 확인.
  - CSV와 불일치한 D1 summary만 [0.1474060562, 0.6907260504, 0.9924955280]으로 갱신. Raw spectrum 재계산 아님.
  - WL hash 일치 ≠ graph isomorphism certificate. [NetworkX API](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash.html)의 attribute policy와 version 기록 필요.
  - Unweighted edge hash 일치 ≠ weighted metric 동일성.
  - Rounded $\mathcal D_2$에 따른 exclusion은 outcome-dependent selection.
  - Large absolute eigenvalue 또는 low rank만으로 numerical failure 확정 불가.
  - Weighted equivalence, loader provenance, exclusion sensitivity 확인 전까지 “확정 표본” 표현 유보.
- Source traceability.
  - Main red / SI green / Note blue 유지.
  - Inspector에는 raw manuscript filename 미표시. Provenance metadata는 보존.
  - Direct/partial card에는 첨부 원문의 실제 문장·수식 발췌. 원문 자체의 교정 없음.
  - LaTeX 원문, 원문 행 위치와 source SHA-256 보존. Citation·cross-reference는 원문 key로 표시.
  - 기존 요약은 접힌 Coverage note로 분리. 원문 인용과 현재 해석을 구분.
  - 핵심 node에 assumptions / interpretation boundary / discriminating check 추가.
  - 기존 manuscript snapshot과 현재 page additions를 구분.
  - Source audit pending ≠ manuscript에 미서술.

## 3. Primary mathematical object

- Fixed input.
  - Graph metric $\Delta(G)$, target dimension $p$, pair weights $W$.
  - Primary geometry: all off-diagonal pair distances with positive weights.
  - Euclidean isometries, including reflection, quotient 처리. Vertex labels 유지.
- Fully specified protocol $\Pi$.
  - Initialization, algorithmic randomness, optimizer, stopping rule, gate, geometric resolution 선언.
  - Terminal map $T_\Pi$와 input law의 pushforward로 $\mu_{G,\Pi}$ 정의.
  - Gate event $A_{\mathrm{num}}$와 acceptance $\alpha_{G,\Pi}>0$ 아래 admissible conditional law 정의.
  - $\alpha_{G,\Pi}$와 rejected-run fraction을 NEI와 함께 보고.
- Kernel formulation.
  - $K_\Pi(\Delta,\mathcal B)$: input metric에서 terminal-geometry event의 probability로 가는 kernel.
  - Measurability와 conditional normalization은 definition의 요건.
  - Input perturbation에 대한 continuity, robustness는 별도 성질.
  - Kernel/pushforward 자체의 최초 제안 주장 없음.
  - Failure atom을 포함한 augmented kernel과 accepted conditional law 구분.
  - Acceptance가 0이면 conditional NEI는 undefined이며 zero spread로 처리하지 않음.
- Zero-set identity.
  - Fixed finite pair set, $0<\mathbb E D_a<\infty$, finite second moments 가정.
  - $\mathcal I=N_+^{-1}\sum_a\operatorname{Var}(D_a)/(\mathbb E D_a)^2$.
  - $\mathcal I=\tfrac12\mathbb E[\rho_\mu^2(D,D')]$ for independent copies.
    - All-pairs primary law에서 $\mathcal I=0$ iff point mass.
    - Partial pair set에서는 projected law의 point mass만 보장.
    - $\mathcal I>0$만으로 prespecified $\rho_D$-resolution 초과 여부 판정 불가.
- Metric calibration.
  - Positive finite pair weights 아래 $\rho_D$와 $\rho_\mu$는 norm-equivalent.
  - 동일한 numerical threshold의 자동 교환은 불가.
  - Page의 “NEI identity and resolution”에서 equivalence constants와 sufficient threshold 유도.
  - 별도 mass-resolution proposition에서 $\beta$-mass separated regions의 detection power와
    NEI lower bound 유도. Population mass assumption과 finite-sample occupancy inference 구분.
  - Target-fit calibration에서는 $A_{\rm ctrl}=A_{\rm num}\cap\{\phi\le\tau_\phi\}$와
    $\alpha_{\rm ctrl}$를 함께 보고. Non-target-fit terminal을 numerical floor로 집계하지 않음.

## 4. Degeneracy: object별 구분

- Conic/SDP degeneracy.
  - Slater failure, facial structure, conditioning의 문제.
  - Multiple terminal geometries와 동일한 개념 아님.
- Exact distance-geometry realization.
  - Complete exact Euclidean distance matrix는 centered Gram matrix를 유일하게 결정.
  - Realization은 Euclidean isometry까지 동일.
  - 이 정리는 nonconvex stress의 nonglobal local minima를 배제하지 않음.
- Hessian degeneracy.
  - Symmetry 제거 후 zero mode 또는 near-zero curvature.
  - Quartic isolated minimum에서도 발생 가능. Continuous family의 증거로 불충분.
- Energy degeneracy.
  - Distinct states의 equal-energy 조건.
  - NEI 단독으로 판정 불가.
- Realized geometric degeneracy.
  - Declared protocol·gate·resolution 아래 terminal law의 nonconcentration.
  - Geometry-weighted spread와 state count는 별개.
  - Large NEI만으로 many minima, barriers, metastability 또는 exact continuum 주장 불가.
- Analytic continuum.
  - 별도 existence proof 필요.
  - Morse–Bott는 smooth critical manifold와 transverse quadratic stability를 갖는 sufficient route.
  - Necessary condition 아님: $\mathcal F(x,y)=y^4$의 minimizer line은 non-Morse–Bott.

## 5. What is exact, and what remains empirical?

- Exact finite-sample algebra.
  - Accepted sample $M=M_{\mathrm{adm}}$.
  - $z_{ma}=d_a^{(m)}/(\sqrt{N_+}\bar d_a)$.
  - $B_z=C_MZZ^\mathsf TC_M$.
  - $\widehat{\mathcal I}_M=\operatorname{tr}(B_z)/M$.
  - $d_{\mathrm{eff}}=(\operatorname{tr}B_z)^2/\operatorname{tr}(B_z^2)$ when the denominator is positive.
  - $d_{\mathrm{eff}}$는 covariance directions의 participation ratio. Basin count 아님.
- Exact-convergence decomposition.
  - Isolated minimizer classes로 exact convergence 시 within-class variance 0.
  - NEI는 occupancies와 class geometry로 표현 가능.
  - Hessian은 식의 explicit term이 아니지만 basin structure·occupancy를 통해 간접 영향 가능.
- Empirical validation.
  - Achieved stationarity, collision margin, quotient curvature, recurrence, resolution sensitivity 확인.
  - Scalar stability는 terminal support 일치나 optimizer independence의 증명 아님.
  - Batches는 Monte Carlo replication; graph mechanisms 비교의 experimental unit은 graph.
- Mechanism hypothesis.
  - Signed residual / prestress organization과 terminal multiplicity의 관계.
  - $H=2R^\mathsf TWR+H_{\mathrm{pre}}$의 quotient-projected comparison.
  - Degree-preserving ring rewiring의 null은 random-regular ensemble. ER과 동일하지 않음.
  - Fixed-landscape path continuation과 parameter continuation 구분.

## 6. Meeting decisions

- [Decision sheet](notes/08-decision-sheet.md): 1차 claim과 required evidence 선택.
- [Primary definition](notes/01-nei-measures-real-degeneracy.md).
- [Representability diagnostic](notes/02-representability-deficiency.md).
- [Trace and covariance spectrum](notes/03-trace-vs-spectrum.md).
- [Withdrawn and restricted claims](notes/04-withdrawn-claims.md).
- [Open questions](notes/05-open.md).
- [Realized geometric degeneracy](notes/06-real-degeneracy-definition.md).
- [Calibration controls](notes/07-calibration-null.md).

## 7. References and scope

- [Drusvyatskiy–Wolkowicz (2017)](https://doi.org/10.1561/2400000011): conic degeneracy, Slater failure, facial reduction.
- [Stillinger–Weber (1982)](https://doi.org/10.1103/PhysRevA.25.978): quenched inherent-structure description.
- [Menck et al. (2013)](https://doi.org/10.1038/nphys2516): initialization-measure-dependent basin stability.
- [Borg–Mair (2017)](https://doi.org/10.17713/ajs.v46i2.561): MDS solution differences, multistart comparison and interpretation.
- 각 문헌은 해당 mathematical context의 근거. NEI의 novelty 또는 현재 측정값을 보증하는 근거 아님.
- 전체 bibliography와 DOI는 page reference section 및 data/refs.json에 수록.

## 8. Reproducibility

- Page content: index.html, data/*.json.
- Offline bundle: node code/build_offline_data.mjs.
- Structural validation: python3 code/validate_architecture.py.
- Algebra regression: python3 code/test_linear_algebra.py.
- Reported spectrum consistency: python3 code/audit_reported_spectrum.py.
- Static formula rendering: node code/validate_research_math.cjs.
- Source excerpt rendering: node code/validate_source_excerpts.cjs.
  - 원문 파일과의 exact-match 검증: 위 명령에 --originals <원문 디렉터리> 추가.
  - 67개 source card, 111개 excerpt. 원문 전체 SHA-256 및 line/offset slice 대조.
- Gradient checks: python3 code/floor_test.py --gradient-check-only 및 python3 code/calibration_null.py --gradient-check-only.
- Full sweep는 별도 실행. 구조·derivative 검산 통과를 전체 empirical result 인증으로 표현하지 않음.
