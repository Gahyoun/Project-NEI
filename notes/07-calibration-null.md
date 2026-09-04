# Calibration null — $\mathcal D_p$의 크기는 multiplicity를 만들지 않는다

`2026-09-04`

## 왜 필요한가

$\widehat{\mathcal I}_M>0$을 보고할 때 "무엇에 비해 큰가"가 없으면 아무 말도 하지 못한다.
$\mathcal D_p=0$인 그래프는 minimizer가 $\Omega$에서 유일함이 정리이므로, 같은 protocol에서
잰 $\widehat{\mathcal I}_M$이 곧 **그 protocol의 수치 잡음 바닥**이다. 경로 그래프 $P_n$이
그런 그래프이다.

## 측정

쌍별 표준화 $\widehat{\mathcal I}_M=\frac1{N_+}\sum_a\operatorname{Var}_m d_a^{(m)}/\bar d_a^2$,
$M=24$, $p=2$. SMACOF(max_iter $3\times10^3$, eps $10^{-12}$) 후 L-BFGS polish.

| 그래프 | $N$ | $\mathcal D_2$ | $\mathcal I$ SMACOF | $\mathcal I$ polish |
|---|---|---|---|---|
| 경로 $P_{60}$ | 60 | **0.0000** | $9.97\times10^{-9}$ | $2.92\times10^{-16}$ |
| 경로 $P_{120}$ | 120 | **0.0000** | $1.08\times10^{-8}$ | $8.87\times10^{-17}$ |
| 링 $C_{60}$ | 60 | 0.3913 | $4.12\times10^{-16}$ | $1.51\times10^{-22}$ |
| 격자 $8\times8$ | 64 | 0.3983 | $1.25\times10^{-12}$ | $2.69\times10^{-20}$ |
| 격자 $12\times12$ | 144 | 0.4045 | $1.81\times10^{-12}$ | $1.19\times10^{-19}$ |
| BA $n{=}120$ | 120 | 0.8468 | $7.60\times10^{-2}$ | $7.36\times10^{-2}$ |
| ER $n{=}120$ | 120 | 0.8956 | $1.01\times10^{-1}$ | $9.87\times10^{-2}$ |

## 두 가지가 동시에 나온다

**(i) 비실현성의 크기는 multiplicity를 만들지 않는다.**
링과 격자는 $\mathcal D_2\approx0.39$–$0.40$으로 심하게 실현 불가인데
$\widehat{\mathcal I}_M$이 $10^{-19}$–$10^{-22}$이다. $\mathcal D_2$가 $0.40$에서 $0.85$로
두 배가 될 때 $\widehat{\mathcal I}_M$은 **17자릿수** 뛴다. 완만한 증가가 아니라 분리이다.
$\mathcal D_p$와 realized multiplicity는 서로 다른 축이며, 전자가 후자를 결정하지 않는다.

**(ii) 수치 잔여물과 구조적 spread가 polish로 갈린다.**
polish는 질서 구조에서 $\widehat{\mathcal I}_M$을 약 7자릿수 떨어뜨리지만
($10^{-12}\to10^{-20}$), ER·BA에서는 실질적으로 바꾸지 못한다
($1.01\times10^{-1}\to9.87\times10^{-2}$). stationarity를 높이면 사라지는 spread와
남는 spread가 이 대비로 구분된다.

## 무엇을 뜻하지 않는가

- polish 후 남은 spread가 **서로 다른 minimizer**에서 온다는 것을 뜻하지 않는다.
  그 판정에는 corrected quotient Hessian 인증과 class 재현성이 필요하다.
- $\mathcal D_p$가 multiplicity와 **무관**하다는 것을 뜻하지 않는다. 크기가 결정하지
  않는다는 것뿐이다. 무엇이 결정하는지는 열려 있다.
- 모형 그래프 7개의 관측이다. 실제 network 전 표본으로 확장하려면 corrected rerun이 필요하다.

## 다음 물음

격자는 $\mathcal D_2\approx0.40$으로 좌절되어 있는데 $\widehat{\mathcal I}_M$이 바닥이다.
좌절의 **크기**가 아니라 **무질서도**가 multiplicity를 지배하는 것으로 보인다. 측정 가능한
형태는 인증된 minimizer에서의 쌍별 잔차장 $r_a=\delta_a-d_a(X^\star)$의 공간적 상관구조이며,
격자에서 $r$은 질서적이고 ER에서는 무질서할 것으로 예상된다. 2차 일단락의 알맹이 후보이다.

## 재현

```bash
python3 code/calibration_null.py
```
