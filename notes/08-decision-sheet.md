# 2026-09-17 · Research discussion decisions

## 1. Primary question

- 1차 일단락에서 어떤 empirical claim까지 제시할 것인가?
  - Definition, identity, numerical diagnostic, mechanism의 evidence 요건을 분리.
  - “두 축의 구분”과 statistical independence를 혼동하지 않음.
  - 연구 depth가 아니라 현재 확보된 evidence에 맞춰 claim 범위 결정.

## 2. Current status — 2026-09-05 audit

- Definition and algebra.
  - Fixed metric representability와 protocol-conditioned terminal spread 구분.
  - Primary all-pairs NEI와 finite-sample trace identity 명시.
  - Partial pairs에서는 projected geometry만 식별.
  - Kernel formulation은 standard mathematical construct를 사용한 연구 대상의 명료화. Kernel 자체의 신규성 주장 없음.
- Numerical evidence.
  - Floor/calibration script의 stress–gradient factor 2 오류 수정.
  - Derivative checks 통과. Corrected full rerun pending.
  - 기존 floor와 ER/BA table은 legacy evidence로 보존.
  - Tolerance stability만으로 exact minima, equal-energy degeneracy 또는 physical mechanism 확정 불가.
- Sampling frame.
  - 선택된 48-network subset의 spectral computation 완료.
  - Weighted duplicate audit, loader provenance, outcome-conditioned exclusion sensitivity 미완료.
  - “계산 완료”와 “확정 표본”은 별개.

## 3. Decisions required for 1차 일단락

1. Primary estimand.
   - All-pairs geometry, vertex labels 유지, Euclidean isometries 제거.
   - Protocol, acceptance event, $\alpha_{G,\Pi}$, resolution 선언.
   - NEI는 spread. State count나 barrier의 대용량 아님.
2. Numerical evidence.
   - Corrected gradient, achieved residual, stopping reason.
   - Collision margin과 quotient-curvature diagnostic.
   - Independent batches와 terminal-class recurrence.
   - Raw terminal configurations와 normalization scales 저장.
3. Comparison claim.
   - “이 protocol에서 recurrent geometric spread 관측”: terminal-level validation 필요.
   - “Degree로 설명되지 않는 정보”: degree-preserving null과 matched comparison 필요.
   - “새 physical mechanism”: controlled ensemble와 competing explanation 분리 필요.
4. Sample membership.
   - WL 및 unweighted hash는 screening.
   - Merge/exclude decision의 provenance와 sensitivity 공개.
   - Existing 48개 table은 selection audit와 함께 해석.
5. Scope.
   - 미충족 evidence를 사후 보완할 것으로 가정한 claim 선행 금지.
   - 해당 claim을 유보하거나 필요한 검증을 1차 범위에 포함.

## 4. Candidate outcomes

- A · Certified finite-protocol result.
  - Requirements.
    - Corrected evidence, sample audit, resolution and recurrence.
    - Beyond-descriptor claim이 있으면 해당 null 포함.
  - Allowed conclusion.
    - Declared protocol 아래의 admissible terminal-geometry spread.
  - Not implied.
    - Global completeness, optimizer-free invariant, exact continuum.
- B · Definitions with exploratory evidence.
  - Requirements.
    - Identity와 diagnostic 설명, legacy provenance, outstanding tests 공개.
  - Allowed conclusion.
    - 검증 가능한 framework와 preliminary observations.
  - Not implied.
    - Corrected empirical confirmation.
- C · Mechanism extension.
  - 2차 일단락 대상.
    - Signed residual/prestress organization.
    - Connected random-regular controls와 degree-heterogeneous ER 비교.
    - Fixed-landscape paths, barrier evidence, 필요 시 size scaling.
  - No preselected outcome.
    - Residual disorder가 multiplicity를 만든다는 가설 자체가 test 대상.

## 5. Manuscript mapping rule

- Main / SI / Note의 실제 source location과 현재 page additions를 구분.
  - Main: concise definition, protocol, supported observations.
  - SI: derivations, numerical checks, sensitivity analyses.
  - Note: alternative explanations, mathematical extensions, meeting decisions.
- Source audit pending을 “미서술”로 계산하지 않음.
- Basin occupancy는 exact algorithmic basin이 정의된 경우 유효한 formal object.
  - 현재 측정이 terminal clustering이면 basin certificate로 과장하지 않음.
- Covariance participation ratio는 올바른 pair-standardized matrix에서 계산.
  - 기존 raw-distance statistic과 NEI-normalized statistic 구분.
