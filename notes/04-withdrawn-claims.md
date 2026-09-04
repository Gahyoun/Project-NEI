# 철회한 주장과 그 이유

`2026-09-04`

고쳐 쓰지 않고 지운 것들이다. 각 claim의 premise와 `why it failed`를 남긴다.

## W1. `NEI 가 측정하는 분산은 inter-basin 이다`

두 전제 위에 서 있었다.

1. `종점은 local minimum 이다` — SMACOF terminal 의 $\eta_g$ 가 L-BFGS 보다 5 자릿수
   크다. terminal 은 stationary point 가 아니다.
2. `정지허용오차가 optimality gap 을 준다` — sklearn 의 `eps` 는 **상대 stress
   개선량**의 정지 허용오차이지 $\mathcal{F}(\hat X)-\mathcal{F}(X^\star)$ 의 상한이
   아니다. 따라서 $\lVert\hat X-X^\star\rVert=O(\sqrt{\varepsilon/\lambda_{\min}})$ 을
   좌표 오차 반경으로 읽을 근거가 없다.

둘 다 성립하지 않으므로 결론도 성립하지 않는다.
덧붙여 between/total 은 모든 run 이 singleton 이면 1, 전부 한 덩어리면 0 이 **데이터와
무관하게** 나오는 항등식이라 그 수치로 이 주장을 지지할 수 없다.

## W2. `0 이 아닌 NEI 는 multi-basin 구조의 관측량이다`

0 이 아닌 $\mathcal{I}$ 는 최소 네 가지와 양립한다.

- 분리된 다중 minimizer
- 평평한 방향을 가진 단일 minimizer
- metric automorphism orbit
- 미수렴 run 의 혼입

게다가 $\mathcal{I}$ 는 covariance operator 의 **trace** 이므로 앞의 둘을 **원리적으로**
구분하지 못한다. 하나를 지목하는 문장은 쓸 수 없다.

## W3. `NEI 는 위상 제약의 intrinsic 측도이다`

$\rho_0$ 가 point mass 이면 optimizer map 이 결정론적이므로 terminal ensemble 이 한
점으로 붕괴하고 $\mathcal{I}\equiv0$ 이 **알고리즘적으로 강제**된다. classical MDS 와
spectral layout 이 정확히 그 경우이다. NEI 는 (topology, sampling protocol) 쌍의
성질이며, 같은 소절이 열 줄 뒤에서 스스로 그렇게 적고 있었다.

## W4. `Eq.(inter_basin_variance) 가 $\mathcal{I}$ 를 알고리즘 불안정성에서 수학적으로 분리한다`

그 식은 바로 앞 문장의 조건 — `If each run terminates in the basin containing its
initialization` — 아래에서만 성립하는 $M\to\infty$ 극한이다. 알고리즘 불안정성이 사는
곳이 정확히 그 조건이므로 순환이다.

**측정으로도 무너진다.** 같은 $X^{(0)}$ 에서 SMACOF 와 L-BFGS 는 서로 다른 terminal 로
간다 (상대차 9–10%, 24개 중 일치 0개). $X^{(0)}\mapsto[X^\star]$ 사상이 optimizer 에
의존하므로 basin occupancy $P_\gamma$ 는 landscape 만의 성질이 아니다.

## W5. `random geometric graph 의 metric 은 구성상 Euclidean 이다`

Euclidean 인 것은 잠재 좌표이지 graph metric 이 아니다. → [02](02-representability-deficiency.md)

## W6. `세 관찰이 NEI 가 구조 정보를 잰다는 것을 확립한다`

세 번째 관찰(격자에서 $\mathcal{I}\approx0$)은 같은 원고가 protocol 의 convergence
control 로 쓰는 항목이다. 수렴 판정 기준으로 쓰는 관측을 동시에 측도 타당성의 독립
증거로 셀 수 없다. `independent` 와 `establish` 를 모두 내렸다.

## W7. `occupancy factor 의 최대는 $P=1/2$` (부분 정정)

$\sigma_{ij}^2=P(1-P)\Delta_{ij}^2$ 자체는 옳다. 그러나 $\mathcal{I}$ 의 피가수는
$r_{ij}=\sigma_{ij}^2/\overline{d}_{ij}^{\,2}$ 이고 분모
$\overline{d}_{ij}=Pa+(1-P)b$ 도 $P$ 에 의존한다. 따라서 $r_{ij}$ 의 최대는 $P=1/2$ 가
아니라 $P^\star=b/(a+b)$ 이고 그 값은 $(a-b)^2/(4ab)$ 이다.

## 기록: 내가 틀렸던 것

- $\beta_{\text{null}}=(K-1)/M$ 로 적었다. 옳은 값은 $(K-1)/(M-1)$ 이다.
  permutation 으로 확인했을 때 잔차가 남아 있었는데 `clustering 이 최적화되어서` 라고
  합리화했다. 무작위 permutation 이었으므로 최적화된 것이 없었다.
- occupancy × geometry 로 인수분해하고 최대가 $P=1/2$ 라고 적었다. 위 W7.
- $\mathcal{I}$ 가 유계가 아니라고 적었다. 유한 $M$ 에서는 $0\le r\le M-1$ 이며 한
  run 만 0 이 아닐 때 등호가 성립한다.
- $\mathcal{I}$ 와 $d_{\text{eff}}$ 가 독립이라고 적었다. 대용값 규격화의 인공물이었다.
  → [03](03-trace-vs-spectrum.md)
