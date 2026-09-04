# 남은 물음

`2026-09-04`

## 지금 답할 수 있는 것과 없는 것

energy landscape 를 캐는 사다리로 적으면 이렇다.

| 층 | 무엇을 묻나 | 상태 |
|---|---|---|
| L0 | 이 terminal 은 얼마나 깊은가 (stress) | 측정 |
| L1 | 그 점이 얼마나 평평한가 ($\widetilde\lambda_{\text{soft}}$) | 부분 — 100개 run 중 8개만 |
| L2 | terminal 들이 얼마나 흩어졌나 ($\mathcal{I}$) | 측정 |
| L3 | 그 비유일성이 **몇 개**의 자유도인가 ($d_{\text{eff}}$) | 측정, 다만 $M=100$ 에서 검열 |
| L4 | 그 자유도가 **이산**인가 **연속**인가 ($K$) | polish 하면 결정된다 |
| L5 | 비유일성이 **어디에** 사는가 ($r_i$, $r_{ij}$ 장) | 미측정 |
| L6 | 평평한 방향과 재현 안 되는 방향이 **같은가** | 미측정 |
| L7 | 두 terminal 사이에 **장벽**이 있는가 | 미측정 |

## 설계상의 실수 하나

아티팩트에 `Delta` (run 사이 거리, $M\times M$) 만 저장하고 **terminal configuration
$X^{(m)}$ 을 저장하지 않았다.** 그 결과

- $\eta_g$ 를 무차원화할 $S_\Delta$ 가 없어 gate 를 사후 계산할 수 없다
- $\chi_{\text{coll}}=\min d_{ij}/s_\Delta$ 를 아예 계산할 수 없다
- L5, L6 이 원천 봉쇄된다

$X^{(m)}$ 은 network 당 약 1 MB 이다. 저장하지 않을 이유가 없었다.

## L6 — 가장 강한 물리 결과가 될 자리

Hessian 의 soft mode 가 사는 node 와 재현이 안 되는 node 가 일치하는지를 보는 것이다.
일치하면 `위상이 만든 평평한 방향이 곧 기하적 비유일성의 원인` 이라는 인과 서술이
가능하다. 지금은 $\lambda_{\min}$ (스칼라)과 $\mathcal{I}$ (스칼라)뿐이라 이 문장을 쓸
수단이 없다.

측정할 것: $\operatorname{corr}(|v_{\text{soft},i}|^2,\ r_i)$, 그리고 무작위 방향에
대한 널.

## L7 — `basin` 이라는 말을 쓰려면

terminal 분포의 gap 은 장벽의 **정황**이지 증거가 아니다. $\Gamma=X-\tfrac12
V^{+}\nabla\mathcal{F}$ 는 정확한 gradient flow 가 아니므로 $\Gamma$ 의 끌림영역
경계와 $\mathcal{F}$ 안장점의 안정다양체는 근사적으로만 일치한다. 두 terminal 을 잇는
경로 위 stress 프로파일이 필요하다.

## 좌절의 무질서도

격자는 $\mathcal{D}_2=0.406$ 으로 좌절되어 있는데도 $\mathcal{I}\approx0$ 이다. 좌절의
**크기**만으로는 landscape 가 거칠어지지 않는다. 무엇이 더 필요한가 — 좌절의
공간적 무질서도로 보이지만 아직 정량화하지 못했다.

## protocol 강건성

$\mathcal{I}$ 가 $\Pi$ 에 의존한다는 사실은 약점이 아니라 명시할 조건이다. 다만
`네트워크의 성질` 이라고 부르려면 조건 너머로 살아남는 것이 있어야 한다. 요구할 것은
값의 일치가 아니라 **순위의 안정성**이다.

- $\rho_0\in\{$uniform, cMDS+noise, spectral+noise$\}$ — 셋 다 비퇴화여야 한다
- optimizer $\in\{$SMACOF, stress 에 대한 L-BFGS$\}$
- 보고량: protocol 쌍마다 $\mathcal{I}$ 와 $d_{\text{eff}}$ 의 Spearman 순위상관

## 비중복성

`또 다른 성질` 이라는 주장의 심사 기준은 비중복성이다. 표준 기술자(spectral gap,
평균 최단거리, 차수 이질성)와의 상관을 **보이고**, 그것들로 회귀한 뒤 남는 잔차분산이
있음을 보여야 한다. 지운 $\lambda_2$ 상관 분석은 복원해서 편상관 형태로 넣어야 한다.
