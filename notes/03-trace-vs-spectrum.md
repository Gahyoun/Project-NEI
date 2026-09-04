# $\mathcal{I}$ 는 trace 이다 — 스칼라가 놓치는 것

`2026-09-04`

## 관찰

저장된 run 사이 거리
$\Delta_{mm'}=\lVert D^{(m)}-D^{(m')}\rVert_F/\text{scale}$ 는 쌍공간
$\mathbb{R}^{N_+}$ 의 **Euclidean** 거리이므로, 한 번 더 이중중심화하면 run 구름의
Gram 행렬이 정확히 복원된다.

$$\mathbf{G}_{\text{run}}=-\tfrac12 C_M\Delta^{\circ2}C_M,\qquad
\operatorname{tr}\mathbf{G}_{\text{run}}=\frac{1}{\text{scale}^2}\sum_{i<j}\sigma_{ij}^2$$

즉 **$\mathcal{I}$ 는 terminal covariance operator 의 trace 이다.** trace 는 크기만
말하고 모양을 말하지 않는다. 분산이 한 방향에 갇혔는지(다중안정형) 여러 방향으로
퍼졌는지(floppy) 는 eigenvalue spectrum 에만 들어 있다.

$$d_{\text{eff}}=\frac{(\sum_a\nu_a)^2}{\sum_a\nu_a^2}$$

**이 값은 이미 저장된 $\Delta$ 만으로 계산된다. 재실행이 필요 없다.**

## 측정 (실제 network 77개)

- Spearman $\rho(\mathcal{I},d_{\text{eff}})=+0.757$ — 강하게 상관한다.
- 그러나 **순위분산의 43% 가 설명되지 않는다** (해상 가능 부표본만 보면 56%).
- $\mathcal{I}$ 5분위 안에서 $d_{\text{eff}}$ 가 **3–77배** 벌어진다.

| $\mathcal{I}$ 분위 | n | $d_{\text{eff}}$ 범위 |
|---|---|---|
| 1 | 16 | 1.00 – 42.53 |
| 2 | 15 | 1.12 – 86.89 |
| 3 | 15 | 5.75 – 84.72 |
| 4 | 15 | 5.02 – 87.82 |
| 5 | 16 | 30.54 – 98.98 |

극단적인 예: `bn-mouse-visual-cortex-2` ($\mathcal{I}=0.0966$, $d_{\text{eff}}=5.0$) 와
`socfb-Mich67` ($\mathcal{I}=0.0970$, $d_{\text{eff}}=52.9$) 는 $\mathcal{I}$ 가 소수점
셋째 자리까지 같은데 차원이 10배 다르다.

올바른 진술은 `독립` 이 아니라 **`결정되지 않는다`** 이다.

## 설계상의 문제: $M=100$ 으로는 해상되지 않는다

$d_{\text{eff}}\le M-1=99$ 인데 관측 최댓값이 **98.98** 이다.

| | 개수 |
|---|---|
| $d_{\text{eff}}<0.5(M-1)$ | 50 / 77 |
| $0.5$–$0.9\,(M-1)$ | 23 / 77 |
| $>0.9\,(M-1)$ | 4 / 77 |

표본공분산의 Marchenko–Pastur 편향까지 감안하면 $0.5(M-1)$ 을 넘는 27개는 측정된
것이 아니라 상한에 붙은 것이다. **$M$ 을 키우지 않으면 이 축을 보고할 수 없다.**

## 초기 오류 하나 (기록용)

처음에 대용값 $\operatorname{tr}\mathbf{G}/N_+$ 로 계산해 $\rho=+0.169$ (유의하지 않음)
를 얻고 `두 양은 독립` 이라고 적었다. 이는 $N_+\sim N^2$ 로 나눈 데서 온 인공물이었다
(대용값 대 $N$ 의 상관이 $-0.764$, 진짜 $\mathcal{I}$ 대 $N$ 은 $+0.080$). 진짜
$\mathcal{I}$ 로 다시 계산해 $+0.757$ 로 정정했다.
