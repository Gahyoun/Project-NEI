# Terminal geometry의 trace와 spectrum — 표준화 정정

2026-09-04 · P0 correction

## 결론

NEI는 **pairwise standardized terminal vectors**의 covariance trace다. 기존 artifact에
저장된 global-Frobenius-scale run distance는 다른 raw-distance covariance를 복원한다.
따라서 기존 $d_{\rm eff}$와 NEI가 같은 operator에서 나온다는 주장은 철회하고,
standardized vectors를 저장한 뒤 다시 계산한다.

## 정확한 선형대수

$G$와 $\Pi$를 고정하고 $\alpha_{G,\Pi}>0$이라 가정한다. 이 절의 $M$은 attempted
run 수가 아니라 admissibility gate를 통과한 $M_{\rm adm}$의 약칭이며,
$D^{(1)},\ldots,D^{(M)}$는 $\mu_{G,\Pi}^{\rm adm}$에서 얻은 complete run-vectors다.
attempted-run failure rate는 $\widehat\alpha=M_{\rm adm}/M_{\rm try}$로 별도 보고한다.

$a=(i,j)$, $a=1,\dots,N_+$라 하고

$$
z_{ma}=\frac{d_a^{(m)}}{\bar d_a\sqrt{N_+}},\qquad
Z_c=C_MZ,\qquad C_M=I_M-\frac1M\mathbf1\mathbf1^{\mathsf T}.
$$

empirical variance divisor $M$을 쓰면

$$
\widehat{\mathcal I}_M
=\frac1{N_+}\sum_a
\frac{M^{-1}\sum_m(d_a^{(m)}-\bar d_a)^2}{\bar d_a^2}
=\frac1M\|Z_c\|_F^2.
$$

표준화된 run 사이 거리

$$
\Delta^{(z)}_{mm'}=\|z_m-z_{m'}\|_2
$$

를 double-center하면

$$
B_z=-\frac12C_M(\Delta^{(z)})^{\circ2}C_M
=Z_cZ_c^{\mathsf T},
$$

따라서

$$
\boxed{\widehat{\mathcal I}_M=\operatorname{tr}B_z/M}.
$$

이는 finite-sample plug-in identity이지 population NEI의 unbiasedness statement가 아니다.
모든 empirical mean $\bar d_a$가 positive여야 하며, 하나라도 0이면 primary NEI는
undefined다. sample variance convention이면 분모는 $M-1$이다. full symmetric distance matrix의
Frobenius norm을 쓰면 upper-triangle pair가 두 번 들어가므로 factor 2도 명시해야 한다.

$B_z$는 run-space Gram이고

$$
C_z=\frac1MZ_c^{\mathsf T}Z_c
$$

는 pair-feature covariance다. 두 행렬은 같은 행렬은 아니지만 nonzero eigenvalues가
$M$배 관계로 대응한다.

## 기존 artifact가 주는 연산자

기존 저장량은

$$
\Delta^{(\rm raw)}_{mm'}
=\frac{\|D^{(m)}-D^{(m')}\|_F}
{\sqrt{\sum_a\bar d_a^2}}
$$

형태로 single global scale을 쓴다. 이로부터 얻는 trace는 pair별
$1/\bar d_a^2$ 가중치를 갖는 NEI가 아니라

$$
\frac{\sum_a\operatorname{Var}(d_a)}
{\sum_a\bar d_a^2}
$$

에 비례한다. Global scalar rescaling은 participation ratio를 보존하지만 pairwise
mean normalization은 covariance eigenvalue ratios를 변경할 수 있음. 이 diagonal rescaling은
covariance를 identity로 만드는 whitening과 다른 연산. 따라서 기존 77-network
$d_{\rm eff}$는 raw-cloud effective rank로만 보존하고, NEI와 같은 operator의 spectrum은
재실행 후 새 이름으로 보고한다.

두 operator 또는 두 estimand가 다르다는 사실은 statistical independence나
nonredundancy를 뜻하지 않는다. 그 결론에는 같은 sampling frame에서의 joint analysis와
covariate-conditioned null comparison이 별도로 필요하다.

## $d_{\rm eff}$의 정확한 해석

$C_z$의 고유값을 $\nu_a\ge0$라 하면

$$
d_{\rm eff}=\frac{(\sum_a\nu_a)^2}{\sum_a\nu_a^2}.
$$

이는 linear covariance의 effective rank다.

- physical zero-mode 개수가 아니다.
- minimizer manifold의 topological dimension이 아니다.
- discrete states와 continuous support를 단독으로 구분하지 못한다.
- curved one-dimensional manifold가 여러 principal components를 점유할 수 있다.
- 여러 discrete states도 high-rank covariance를 만들 수 있다.

특히 1D toy landscape의 terminal coordinate를 그대로 쓰면 nonzero covariance rank는
항상 1이다. histogram bin의 $1/\sum_b p_b^2$는 occupancy Hill number이지
$d_{\rm eff}$가 아니다. 웹 demo에서는 두 양을 분리한다.

## 기존 77-network 결과의 지위

관측된

$$
\rho_S(\mathcal I,d_{\rm eff}^{\rm raw})=0.757
$$

은 raw-cloud exploratory association이다. $1-\rho_S^2=0.43$을 고유 정보량 또는
순위분산 decomposition으로 해석하지 않는다. 허용되는 말은 다음이다.

> NEI and the raw-cloud effective rank showed a substantial but nonperfect monotone
> association in the exploratory sample.

같은 standardized operator의 $d_{\rm eff}$를 재계산한 뒤에도 paired scatter,
within-NEI conditional spread와 bootstrap uncertainty를 다시 보고해야 한다.

## Population consistency와 asymptotic inference

$D=(D_a)_{a\in\mathcal P}\sim\mu_{G,\Pi}^{\rm adm}$에 대해

$$
m_a=\mathbb E[D_a]>0,\qquad
s_a=\mathbb E[D_a^2],\qquad
v_a=s_a-m_a^2
$$

로 둔다. $N_+$가 fixed이고 모든 $s_a<\infty$이면 SLLN과 continuous mapping
theorem으로

$$
\widehat{\mathcal I}_M
=\frac1{N_+}\sum_a\left(
\frac{M^{-1}\sum_m(D_a^{(m)})^2}{\bar D_a^2}-1\right)
\xrightarrow{\rm a.s.}
\frac1{N_+}\sum_a\frac{v_a}{m_a^2}
=\mathcal I.
$$

이는 fixed conditional law에 대한 consistency다. $\Pi$, gate, pair set 또는
resolution을 $M$과 함께 바꾸는 triangular-array claim이 아니다. accepted sample을
attempted runs에서 얻는 경우에는 $\alpha_{G,\Pi}>0$과 $M_{\rm adm}\to\infty$도 필요하다.

모든 $\mathbb E[D_a^4]<\infty$이면 multivariate CLT와 delta method로

$$
\sqrt M(\widehat{\mathcal I}_M-\mathcal I)
\Rightarrow\mathcal N(0,V),
\qquad V=\operatorname{Var}[\psi(D)],
$$

여기서 mean-zero influence function의 raw-moment form은

$$
\psi_{\rm raw}(d)=\frac1{N_+}\sum_a\left[
\frac{d_a^2-s_a}{m_a^2}
-\frac{2s_a(d_a-m_a)}{m_a^3}
\right]
$$

이고, 같은 함수의 centered-moment form은

$$
\psi_{\rm ctr}(d)=\frac1{N_+}\sum_a\left[
\frac{(d_a-m_a)^2-v_a}{m_a^2}
-\frac{2v_a(d_a-m_a)}{m_a^3}
\right].
$$

$s_a=v_a+m_a^2$를 대입하면 $\psi_{\rm raw}=\psi_{\rm ctr}$가 pointwise로 성립한다.
regular Wald interval에는 추가로 $0<V<\infty$가 필요하다. bootstrap은 pair 좌표를
독립 재표집하지 않고 complete run-vector를 재표집하며, replicate마다 $\bar D_a$와
$\widehat{\mathcal I}_M$을 다시 계산한다. 이 방식이 한 run 안의 cross-pair dependence를
보존한다.

## finite-$M$ algebraic bound와 rank ceiling

$d_a^{(m)}\ge0$, $\bar d_a>0$이고 divisor $M$ empirical variance를 쓰면 pair별
coefficient of variation squared는

$$
\widehat r_a
=M\frac{\sum_{m=1}^M(d_a^{(m)})^2}
{(\sum_{m=1}^M d_a^{(m)})^2}-1.
$$

$d_a^{(m)}\ge0$에서
$(\sum_m d_a^{(m)})^2/M\le\sum_m(d_a^{(m)})^2
\le(\sum_m d_a^{(m)})^2$이므로

$$
0\le\widehat r_a\le M-1,
\qquad
\boxed{0\le\widehat{\mathcal I}_M\le M-1}.
$$

lower equality는 해당 pair-distance가 모든 run에서 같을 때, upper equality는 정확히
한 run에서만 positive일 때 성립한다. NEI upper equality에는 모든 prespecified pair가
이 조건을 만족해야 한다. divisor $M-1$의 unbiased sample variance를 쓰면 $M\ge2$에서
upper bound는 $M$이다. 이는 algebraic finite-sample bound이며 confidence interval,
state count 또는 population upper bound가 아니다. 특히 divisor $M$ convention에서
$\widehat{\mathcal I}_1=0$은 identity일 뿐 population point mass의 evidence가 아니다.

$C_z$의 positive eigenvalue 수를 $r$라 하면 $\operatorname{tr}C_z>0$에서

$$
1\le d_{\rm eff}
=\frac{(\sum_{k=1}^r\nu_k)^2}{\sum_{k=1}^r\nu_k^2}
\le r\le\min(N_+,M-1).
$$

첫 부등식은 $\nu_k\ge0$, 둘째 부등식은 Cauchy--Schwarz, 마지막 부등식은
$\operatorname{rank}(C_M)=M-1$에서 나온다. $d_{\rm eff}=1$은 rank-one spectrum,
$d_{\rm eff}=r$은 $r$개 positive eigenvalue가 모두 같은 경우다. $\operatorname{tr}C_z=0$
이면 ratio는 $0/0$이므로 $d_{\rm eff}$를 0으로 대입하지 않고 undefined로 보고한다.
$d_{\rm eff}>0.5(M-1)$를 모두 censored라고 분류하는 것은 heuristic이다.
Marchenko--Pastur law도 iid isotropic random matrix 가정이 없는 constrained terminal
cloud에 자동 적용되지 않는다.

## Variance와 resolution의 분리

population $\mathcal I>0$은 projected law가 point mass가 아님을 뜻하지만,
$\rho_D$-diameter가 predeclared $\varepsilon_D$를 넘는다는 뜻은 아니다. 예를 들어 두
support points의 거리가 $\varepsilon_D/2$이면 nonzero variance와 unresolved support가
동시에 가능하다. 반대로
$(1-\eta)\delta_{d_0}+\eta\delta_{d_1}$에서
$\rho_D(d_0,d_1)>\varepsilon_D$를 고정하고 $\eta\downarrow0$로 보내면, means가 0에서
떨어져 있는 한 $\mathcal I=O(\eta)$로 arbitrarily small이지만 support separation은
유지된다. 따라서 NEI magnitude와 finite-resolution multiplicity는 서로 대체할 수 없는
질문이다.

empirical diameter $\le\varepsilon_D$ 또는 $\widehat{\mathcal I}_M=0$은 finite-$M$
non-detection이다. unseen rare support를 배제하는 population certificate가 아니다.
minimum class mass, missing-mass bound 또는 별도 sampling assumption 없이
“terminal law가 한 점으로 collapse”라는 결론으로 올리지 않는다.

필요한 보고는

- $M=25,50,100,200,400$ rarefaction
- independent seed batches
- $d_{\rm eff}(M)$과 leading spectral fractions의 CI
- eigenvalue threshold sensitivity
- standardized와 raw covariance의 직접 비교

이다.
