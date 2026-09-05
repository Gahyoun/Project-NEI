# Terminal geometry의 trace와 spectrum — 표준화 정정

2026-09-04 · P0 correction

## 결론

NEI는 **pairwise standardized terminal vectors**의 covariance trace다. 기존 artifact에
저장된 global-Frobenius-scale run distance는 다른 raw-distance covariance를 복원한다.
따라서 기존 $d_{\rm eff}$와 NEI가 같은 operator에서 나온다는 주장은 철회하고,
standardized vectors를 저장한 뒤 다시 계산한다.

## 정확한 선형대수

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

에 비례한다. global scalar rescaling은 participation ratio를 바꾸지 않지만 pairwise
whitening은 covariance eigenvalue ratios를 바꾼다. 따라서 기존 77-network
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

## finite-$M$ 해상도

$d_a^{(m)}\ge0$, $\bar d_a>0$이고 divisor $M$ empirical variance를 쓰면 pair별
coefficient of variation squared가 $M-1$ 이하이므로

$$
0\le\widehat{\mathcal I}_M\le M-1.
$$

이는 algebraic finite-sample bound이며 confidence interval, state count 또는 population
upper bound가 아니다.

$d_{\rm eff}\le M-1$은 정확하다. 그러나 $d_{\rm eff}>0.5(M-1)$를 모두 censored라고
분류하는 것은 heuristic이다. Marchenko–Pastur law도 iid isotropic random matrix
가정이 없는 constrained terminal cloud에 자동 적용되지 않는다.

필요한 보고는

- $M=25,50,100,200,400$ rarefaction
- independent seed batches
- $d_{\rm eff}(M)$과 leading spectral fractions의 CI
- eigenvalue threshold sensitivity
- standardized와 raw covariance의 직접 비교

이다.
