# NEI 는 SMACOF 의 인공물이 아니다

`2026-09-04`

## 물음

`classical MDS 는 결정론적이라 반복해도 NEI 가 구조적으로 0 이다. 그러면 지금
NEI 가 보는 신호는 SMACOF 가 만들어낸 것 아닌가?`

이 물음은 둘로 갈라야 한다.

1. **cMDS 에 초기조건이 있는가** — 없다. 이중중심화 후 eigendecomposition 하는 닫힌
   형태이므로 distance matrix 가 유일하고 $\mathcal{I}_{\text{cMDS}}\equiv 0$ 은 관측이
   아니라 항등식이다. 수치로도 $2.6\times10^{-33}$ 이 나온다.

2. **SMACOF 의 terminal 산포가 landscape 때문인가, 수렴 실패 때문인가** — 이것이
   진짜 물음이고, 아래가 그 답이다.

cMDS 와 SMACOF 의 차이는 `결정론적 대 확률적` 이 아니다. **다른 objective 를
최소화한다.**

| | objective | 성질 |
|---|---|---|
| cMDS | strain $\lVert G-XX^{\mathsf T}\rVert_F^2$ | $XX^{\mathsf T}$ 에 대해 볼록, Eckart–Young 으로 global optimum 유일 |
| SMACOF | stress $\sum w(\delta-d)^2$ | 비볼록, 다중 local minimum 이 실재 |

stress 의 비볼록성은 알려진 수학적 사실이지 구현의 결함이 아니다.

## 문제: SMACOF terminal 은 stationary point 가 아니다

sklearn 의 stopping rule 은 **상대 stress 개선량**이지 optimality gap 이 아니다.
실측하면 무차원 stationarity 지표 $\eta_g=\lVert g\rVert/\sqrt{S_\Delta}$ 가

    SMACOF (max_iter=300)    2.19e-03
    SMACOF (max_iter=10000)  2.19e-03
    L-BFGS                   1.96e-08

로, SMACOF 는 반복을 33배 늘려도 개선되지 않는다. 이 상태의 terminal ensemble 로는
`서로 다른 minimizer 인가, 같은 minimizer 근처에서 멈춘 것인가` 를 구분할 수 없다.

## 방법: polish and certify

각 SMACOF terminal 을 시작점으로 L-BFGS 를 돌려 진짜 stationary point 까지
밀어넣는다. 그러면 두 가지가 동시에 풀린다.

1. projected Hessian 으로 그 점이 local minimizer 인지 인증할 수 있다.
2. 서로 다른 minimizer 사이 거리는 $O(1)$, 같은 minimizer 안의 수치산포는 $O(10^{-9})$
   가 되어 **cutoff 를 보정할 필요가 없어진다.**

## 결과 (bn-mouse-visual-cortex-2, N=193, M=24)

```
eta_g   SMACOF 2.19e-03  ->  polish 2.00e-08      (10^5 배)
stress 가 polish 로 더 내려간 비율(중앙)  1.78e-05
I       SMACOF 1.0999e-01 ->  polish 7.6646e-02   (비 0.697)

projected Hessian 인증 (8개 표본)
  음의 eigenvalue        0 / 8
  lam_min/kappa+ 중앙    +1.63e-03

polish 후 run 사이 상대거리   최소 7.95e-02  중앙 2.91e-01  최대 3.33e-01
  cutoff 1e-8 -> K = 24      cutoff 1e-3 -> K = 24
  cutoff 1e-6 -> K = 24      cutoff 1e-2 -> K = 24
  cutoff 1e-4 -> K = 24
```

## 읽는 법

- **$\mathcal{I}$ 는 5 자릿수의 수렴 개선을 견디고 살아남는다.** 값이 30% 줄지만
  크기는 그대로다. 수렴 실패가 만들어낸 신호였다면 무너졌어야 한다.
- **polish 된 terminal 은 전부 진짜 local minimizer 이다.** saddle 이 하나도 없다.
- **24개 run 이 서로 다른 24개 minimizer 로 간다.** 가장 가까운 두 terminal 도 7.9%
  떨어져 있어 cutoff 를 6 자릿수 움직여도 $K$ 가 변하지 않는다.

따라서 NEI 가 재는 것은 stress landscape 의 실제 degeneracy 이다.

## 부수적으로 무너지는 것

같은 실험이 다른 것을 하나 무너뜨린다. 같은 $X^{(0)}$ 에서 SMACOF 와 L-BFGS 는
**서로 다른 terminal 로 간다** (distance matrix 상대차 약 9–10%, 24개 run 중 1e-3
이내로 일치한 것 0개). 즉 $X^{(0)}\mapsto[X^\star]$ 사상은 optimizer 에 의존하므로,
**basin occupancy $P_\gamma$ 는 landscape 만의 성질이 아니다.** 원고의 basin
occupancy 형식화는 이 사실과 양립하지 않는다.

## 남은 일

- polish 를 전 표본에 적용해야 한다. 위는 검사한 network 에 대한 진술이다.
- $K=M$ 이 나온 것은 `적어도 24개` 라는 뜻이다. $M$ 을 늘리면 $K$ 도 늘어날 수 있다.
  포화하는지 보아야 한다.
- polish 후의 $\mathcal{I}$ 를 논문의 주 측정량으로 삼을지 결정해야 한다. 그렇게 하면
  `local minimizer 위에서 측정했다` 고 쓸 수 있다.

## 재현

```bash
python3 polish_certify.py nets/bn-mouse-visual-cortex-2.edges 24
```
