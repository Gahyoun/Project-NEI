# 벡터로 energy landscape 를 분해한다 — trace 와 spectrum

`2026-09-04`

## 관찰

저장된 run 사이 거리
$\Delta_{mm'}=\lVert D^{(m)}-D^{(m')}\rVert_F/\text{scale}$ 는 쌍공간
$\mathbb{R}^{N_+}$ 의 **Euclidean** 거리이므로, 한 번 더 이중중심화하면 run 구름의
Gram 행렬이 정확히 복원된다.

$$\mathbf{G}_{\text{run}}=-\tfrac12 C_M\Delta^{\circ2}C_M,\qquad
\operatorname{tr}\mathbf{G}_{\text{run}}=\frac{1}{\text{scale}^2}\sum_{i<j}\sigma_{ij}^2$$

즉 **$\mathcal{I}$ 는 terminal covariance operator 의 trace 이고, 같은 연산자의
eigenvalue spectrum 이 그 모양을 담는다.** trace 는 degeneracy 의 크기를 주고,
spectrum 은 degeneracy 가 몇 개의 자유도를 차지하는지를 준다 — 한 방향에 갇힌
다중안정형과 여러 방향으로 퍼진 floppy 가 여기서 갈린다.

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

정확한 진술은 **`$d_{\text{eff}}$ 가 $\mathcal{I}$ 와 독립한 정보를 담는다`** 이다.

## $d_{\text{eff}}$ 의 해상에는 더 큰 $M$ 이 필요하다

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
