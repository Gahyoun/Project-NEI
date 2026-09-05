# Corrected rerun and graph-null — research decision note

## 1. Result and scope

- **Bounded execution complete; full-corpus validation incomplete.**
  - 14 source graph/metric instances와 316 generated null graphs.
  - Graph/metric instance당 attempted $M=100$, independent batches 50+50.
  - 33,000 initialization attempts, 40,000 polished terminal records.
  - Source 14개에만 six-rung paired tolerance comparison; null graph에는 primary rung 적용.
  - Real inputs: ca-sandi-auths $(81,119)$, enzymes-g295 $(123,139)$, eco-foodweb-baywet $(128,2075)$.
  - 세 real input 모두 unweighted. Weighted corpus, 전체 역사적 표본, $M=200,400$ 확장은 미실행.
- Provenance.
  - Protocol SHA-256: `d64740163f3f6d1391263b82f001bcff40379117f1d79052ac73fab833eb39be`.
  - Input hashes, implementation hashes, seeds, versions와 모든 rejected outcomes 보존.
  - [Public result](../data/corrected-study.json), [input audit](09-input-audit.md), [execution code](../code/corrected_evidence.py).
  - 좌표·pair vectors·raw graphs는 local study에 보존; 이 repository에는 공개 summary만 포함.
  - Synthetic realization·initialization·sample size가 legacy test와 동일한 paired intervention은 아님. Legacy와의 차이 전부를 gradient correction 하나에 귀속하지 않음.

## 2. What was corrected and independently checked

- Derivative consistency.
  - $\mathcal F(X)=\sum_{i<j}(d_{ij}-\delta_{ij})^2$에 맞는 gradient와 Hessian 사용.
  - Central finite-difference regression, quotient projection과 covariance identity regression 적용.
- Input consistency.
  - Headerless edge list의 첫 edge 보존. ca-sandi-auths의 $E=119$ 복원.
  - Numeric third column을 자동 weight로 승격하지 않음.
  - Connected simple graph의 $N,E$ 고정; null에 largest-component substitute 미사용.
  - Degree-null의 labeled degree vector, connectedness, simplicity를 모든 생성 graph에서 검증.
- Artifact reconstruction.
  - 40,000 terminal의 좌표에서 pair distance·stress와 독립 Laplacian-form gradient 재계산.
  - 최대 pair-distance 오차: 0.
  - 최대 stress 오차 $|F_{\rm reconstructed}-F_{\rm saved}|/\max(1,F_{\rm reconstructed})$: $4.78\times10^{-15}$.
  - 최대 $\eta_g$ 절대 차이: $1.04\times10^{-15}$ 미만.
  - Stored quotient spectrum의 inertia와 acceptance 판정 전수 대조.
  - Hessian derivative는 별도 deterministic tests로 검증. 모든 terminal에서 독립 eigendecomposition을 이중 수행했다는 의미는 아님.
- Acceptance.
  - $A_{\rm num}$: optimizer success, finite diagnostics, $\eta_g\le10^{-9}$, $\chi_{\rm coll}\ge10^{-8}$, normalized quotient curvature에서 negative mode 없음.
  - Exact-target control만 $A_{\rm ctrl}=A_{\rm num}\cap\{\phi\le10^{-6}\}$ 추가.
  - $\eta_g=\|\nabla\mathcal F\|_2/\sqrt{S_\Delta}$, $\phi=\sqrt{\mathcal F/S_\Delta}$, $S_\Delta=\sum_{i<j}\delta_{ij}^2$.
  - $\chi_{\rm coll}=\min_{i<j}d_{ij}/\sqrt{S_\Delta/N_+}$.
  - Negative-mode cutoff: $-10^{-9}\kappa_+$; tiny signed eigenvalues를 analytic zero로 인증하지 않음.
  - $M_{\rm adm}<2$는 이번 inference report에서 NEI estimate 보류. $M_{\rm adm}=1$에서 algebraic plug-in 값이 0이라는 항등식과 구분.

## 3. Calibration does not imply global convergence

| Target/control | Selection | Accepted / attempted | Conditional NEI |
|---|---|---:|---:|
| Path $P_{60}$ | $A_{\rm ctrl}$ | 100/100 | $1.07\times10^{-17}$ |
| Path $P_{120}$ | $A_{\rm ctrl}$ | 100/100 | $9.26\times10^{-18}$ |
| Full-rank Euclidean target, $N=20$ | $A_{\rm ctrl}$ | 80/100 | $1.21\times10^{-23}$ |
| Same Euclidean target | $A_{\rm num}$ only | 88/100 | $2.60\times10^{-3}$ |

- Full-rank target의 target-fit rejected numerical terminals: 8개.
  - Exact Euclidean representability는 zero-stress global realization의 uniqueness modulo isometry와 정합.
  - Nonglobal terminal candidates의 부재 또는 arbitrary-start global convergence는 보장하지 않음.
  - $A_{\rm num}$-only spread를 numerical floor라고 부르면 optimization outcome과 calibration error의 혼합 발생.
- 위 작은 값은 해당 target·size·protocol의 numerical baseline.
  - $10^{-17}$과 $10^{-23}$의 차이를 물리적 separation으로 해석하지 않음.
  - 모든 network에 적용 가능한 universal NEI floor의 인증 아님.

## 4. Rare terminal in the 8×8 lattice

- Primary numerical acceptance: 84/100; $\widehat{\mathcal I}_{\rm adm}=0.0042093$.
  - Dominant geometry 83개, 다른 geometry 1개.
  - Discovery occupancy $(40,1)$; independent validation matches $(43,0)$.
  - $\varepsilon_D=10^{-5}$에서 discovery classes 2개, recurrent class 1개.
- Rare terminal: `grid8/run-0026`, primary rung.
  - $\mathcal F/S_\Delta=0.10051655$; observed lower-stress terminal의 $0.01076095$보다 높음.
  - $\eta_g=1.73199\times10^{-13}$, $\chi_{\rm coll}=0.07432$.
  - $\lambda_{\min}(H_\perp)/\kappa_+=0.18178$; signed inertia $(0,0,125)$.
  - 낮은 residual-gradient와 positive pointwise curvature를 가진 고-stress terminal candidate.
- Interpretation.
  - Rare terminal을 사후 삭제하지 않음. 현재 protocol은 lowest-stress selection이 아님.
  - “Regular lattice이면 모든 initialization에서 NEI≈0”이라는 보편적 서술 불가.
  - 다만 rare class는 validation에서 미관측. Recurrent two-class structure, exact local-minimum existence 또는 population occupancy의 인증 아님.
  - Whole-run bootstrap이 rare observation을 놓치는 replicate를 포함. NEI interval의 lower end가 floor에 가까운 이유이며 rare-state coverage를 보장하지 않음.

## 5. Graph-null results

- Null design.
  - Degree: independent fresh chain 20개, 각 $100E$ attempted lazy switches.
  - Degree-long: independent fresh chain 8개, 각 $500E$ attempted lazy switches.
  - $G(n,m)$: exact proposals를 connectedness에 조건부로 rejection sampling, requested 20개.
  - Switch의 symmetry와 rejection accounting은 확인; finite-time uniformity와 mixing time의 인증은 아님.
  - Degree-long은 다른 finite-time kernel의 sensitivity check. 같은 law에서 mixing이 완료됐다는 보증 아님.
- Primary contrast: $\delta_g=\widehat{\mathcal I}_g-\operatorname{mean}_b\widehat{\mathcal I}_{g,b}^{\rm null}$.
  - Graph realization: outer experimental unit.
  - Whole embedding run vector: within-graph unit.
  - Outer interval: anchor point estimate를 고정하고 null graph point estimates만 resampling.
  - Nested interval: anchor run bootstrap + outer graph bootstrap + within-null run bootstrap.
  - 999회 percentile resampling. Small-sample coverage, unseen-class correction 또는 confirmatory inference의 보증 없음.

| Real anchor | Null | $\delta_g$ | Nested 95% sensitivity interval | Reading |
|---|---|---:|---|---|
| ca-sandi-auths | degree, $100E$ | −0.01778 | [−0.03683, −0.00315] | Lower conditional spread |
| ca-sandi-auths | degree-long, $500E$ | −0.02966 | [−0.04915, −0.01318] | Same direction in this kernel sensitivity |
| ca-sandi-auths | connected $G(n,m)$ | −0.02238 | [−0.04162, −0.00686] | Lower conditional spread |
| enzymes-g295 | degree, $100E$ | +0.00014 | [−0.00807, +0.00815] | Direction unresolved |
| enzymes-g295 | degree-long, $500E$ | −0.01251 | [−0.02025, −0.00212] | Kernel/sample sensitivity; primary conclusion not replaced |
| enzymes-g295 | connected $G(n,m)$ | withheld | unavailable | 10,000 proposals 모두 disconnected |
| eco-foodweb-baywet | all three ensembles | withheld | unavailable | Requested ensemble에 undefined-NEI null 포함 |

- Acceptance is part of the result.
  - Real $A_{\rm num}$: ca-sandi 21/100, ENZYMES 42/100, eco-baywet 9/100.
  - eco-baywet null median acceptance: degree 4/100, degree-long 5/100, $G(n,m)$ 0/100.
  - Requested null 가운데 inference-eligible count는 각각 19/20, 7/8, 4/20.
  - Ineligible null을 0으로 치환하거나 estimable subset만으로 전체 ensemble contrast를 보고하지 않음.
- Allowed conclusion.
  - ca-sandi-auths에서 declared finite-time kernels에 대한 exploratory conditional association 관측.
  - “모든 real network의 NEI가 null보다 작음”은 이번 결과로 지지되지 않음.
  - 21 contrast는 multiplicity-adjusted confirmatory tests가 아님. Uniform null, structural novelty, physical mechanism의 확인과 구분.
  - Finite-$M_{\rm adm}$ plug-in bias는 graph별로 다를 수 있음. Between-graph point-estimate variance는 within-graph estimation noise를 이미 포함; nested bootstrap은 이를 완전히 분리한 variance-component estimator가 아니라 sensitivity summary.
  - [Prespecified gate-sensitivity artifact](../data/corrected-gate-sensitivity.json): 7 anchors × 3 null ensembles × 4 gates.
    - ca-sandi-auths의 degree contrast는 네 gate에서 모두 음수: −0.01801, −0.01778, −0.01064, −0.00673.
    - ENZYMES의 같은 대비는 +0.00028, +0.00014, +0.00012, −0.00175. 부호의 안정성 없음.
    - eco-baywet은 느슨한 gate에서 contrast 계산 가능하나 primary withheld 판정을 대체하지 않음.
    - 이 sensitivity에는 CI·p-value 미산출. 각 gate는 서로 다른 conditional estimand.

## 6. Tolerance plateau is not achieved convergence

- ER100: $\widehat{\mathcal I}_{\rm adm}=0.10664$, acceptance 16/100.
- BA100: $\widehat{\mathcal I}_{\rm adm}=0.06285$, acceptance 16/100.
  - 두 graph에서 $\mathrm{gtol}=10^{-10},10^{-14},10^{-18}$의 conditional NEI 유지.
  - Primary 100개 run 모두 `REL_REDUCTION_OF_F_<=_FACTR*EPSMCH` criterion으로 종료.
  - 같은 function-reduction stopping이 requested gradient tolerance보다 먼저 작동할 수 있음.
  - 따라서 identical gtol-ladder outputs는 optimizer endpoint plateau의 관측이지, achieved stationarity를 계속 개선해도 physical signal이 유지된다는 증명은 아님.
- $\varepsilon_D=10^{-5}$의 recurrence.
  - ER100: discovery accepted 9, validation accepted 7, recurrent class 0.
  - BA100: discovery accepted 8, validation accepted 8, recurrent class 0.
  - Nonzero spread는 관측되지만 recurrent class catalog의 검증은 미완료.
- Protocol sensitivity.
  - Fixed $\mathrm{gtol}$ 아래 $\mathrm{ftol}$을 변경한 비교와 fixed $\mathrm{ftol}$의 gtol ladder 분리.
  - Stationarity gate sensitivity는 다른 conditional law의 비교. Primary gate를 사후 완화한 결과로 대체하지 않음.
  - Numerical equivalence margin은 이번 실행에서 미선언. Formal equivalence-test verdict 미보고.
  - Absolute $U[0,1]$ initialization 사용. Observable의 scale invariance만으로 implemented protocol의 input-scale equivariance 주장 불가.

## 7. Next decision

- 1차 일단락에 사용 가능한 내용.
  - Corrected measurement code, artifact provenance, run-level gate, exact-target calibration, graph-level conditional comparisons.
  - Failure, rare terminal, null-generation cap와 nonrecurrence를 포함한 재현 가능한 empirical record.
- 추가 검증 전 유보.
  - Low-acceptance graph의 stable conditional estimate와 unseen-class coverage.
  - Weighted preprocessing/null repair와 full-corpus sweep.
  - Kernel-length effect와 graph-realization sampling variance의 분리.
  - Local stationarity를 개선하는 별도 solver protocol의 사전 선언·독립 재검증.
  - Equal-energy degeneracy, continuous minimizer family, thermodynamic mechanism.
- 현재의 결론은 “NEI 가설의 전면 검증 완료”가 아니라 **corrected bounded measurement 완료, structural interpretation 일부 지지·일부 미해결**.

## 8. Reproduction procedure

- Environment versions는 공개 payload의 scientific provenance와 local execution record에서 확인.
  - NumPy 1.26.4, SciPy 1.12.0, scikit-learn 1.4.1.post1, NetworkX 3.2.1.
  - BLAS thread 수 1, independent process workers 4.
- 새 output directory와 원본 파일을 지정한 input manifest 필요.
  - [Input template](../code/corrected_inputs.template.json)의 세 파일 SHA-256 일치 확인.
  - 아래 명령은 repository root 기준. `study-output`은 아직 존재하지 않는 새 directory.

```bash
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
python3 code/prepare_corrected_study.py study-output --inputs inputs.json --workers 4
python3 code/corrected_evidence.py study-output --workers 4
python3 code/validate_corrected_artifacts.py study-output
python3 code/summarize_corrected_study.py study-output
python3 code/publish_corrected_summary.py study-output --output study-output/public-summary.json
```

- Same-version/same-platform numerical reproduction을 목표로 한 절차. 다른 BLAS/platform의 bitwise equality 보장 아님.
- Protocol과 input/implementation hashes가 다르면 기존 run을 resume하지 않도록 검사.
- 연구용 전수 원자료의 local 보존과 공개 summary의 privacy audit 분리.
