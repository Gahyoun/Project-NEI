# 인수인계

`2026-09-04` · 다음 작업자(Codex 등)를 위한 문서.

## 30초 요약

- **주장** — 고정된 topology-to-geometry protocol 아래에서 네트워크의
  *representability* ($\mathcal{D}_p$, protocol 무관 · 닫힌 형태)와
  *identifiability* ($\mathcal{I}$, $d_{\text{eff}}$, protocol 조건부)를 잰다. 목표는 PRE.
- **최근 확정** — SMACOF terminal 을 L-BFGS 로 polish 하면 $\eta_g$ 가 5 자릿수
  내려가는데도 $\mathcal{I}$ 가 살아남고, terminal 이 전부 진짜 local minimizer 이며,
  $K$ 가 cutoff 6 자릿수에 불변이다. **NEI 는 landscape 의 real degeneracy 를 잰다.**
- **바로 할 일** — ① polish 를 전 표본에 적용 ② sweep 이 $X^{(m)}$, $S_\Delta$,
  $s_\Delta$, $\min d_{ij}$ 를 저장하게 수정 ③ $M$ 확대 ④ $\mathcal{D}_p$ 전 표본.
- **건드리기 전에** — [`notes/04`](notes/04-withdrawn-claims.md)(철회한 주장 7건)와
  아래 §4 함정 9가지를 먼저 볼 것.
- **하지 말 것** — `nei-verification` 저장소를 public 으로 바꾸지 말 것. 미출판 원고가
  히스토리에 있다.

---

## 1. 이 프로젝트가 주장하는 것

고정된 topology-to-geometry protocol 아래에서 네트워크의 두 성질을 정량화한다.

| | 무엇을 묻나 | protocol 의존 | 측정 |
|---|---|---|---|
| **representability** | graph metric $\delta_{ij}$ 가 $\mathbb{R}^p$ 에서 실현되는가 | **무관** (닫힌 형태) | Schoenberg 결손 $\mathcal{D}_p$ |
| **identifiability** | 그 실현이 결정되는가 | **의존** (명시적 조건부) | terminal ensemble + Hessian |

두 명사의 protocol 의존성이 서로 다르다는 것이 기여의 핵심이다. identifiability 는
표준 이론대로 local 비식별(Hessian 영방향 ⟹ floppy) / global 비식별(분리된 minimizer
다수 ⟹ 다중안정형) / 식별 가능(유일 ⟹ 강체형)으로 갈린다.

**목표 저널은 Physical Review E 이다.** PRE 2026 절단선은 `data/scope.json` 에 있고
웹 지도에 초록 점선 hyperedge 로 그려져 있다.

---

## 2. 지금 확정된 것 — 이것부터 읽어라

### 2.1 NEI 는 energy landscape 의 real degeneracy 를 잰다

가장 중요한 결과이다. 전문은 [`notes/01`](notes/01-nei-measures-real-degeneracy.md).

핵심 방법은 **polish and certify** 이다. SMACOF terminal 은 stationary point 가
아니다 — sklearn 의 stopping rule 이 상대 stress 개선량 기준이라, 무차원 지표
$\eta_g=\lVert g\rVert/\sqrt{S_\Delta}$ 가 L-BFGS 보다 4–5 자릿수 크다. 그래서 각
terminal 을 L-BFGS 로 밀어 넣은 뒤 다시 잰다.

```
eta_g   SMACOF 2.19e-03  ->  polish 2.00e-08
I       SMACOF 1.10e-01  ->  polish 7.66e-02
projected Hessian:  음의 eigenvalue 0/8,  lam_min/kappa+ 중앙 +1.63e-03
run 사이 최소 상대거리 7.9e-02,  K=24 가 cutoff 1e-8..1e-2 내내 불변
```

두 가지가 동시에 따라온다.
- $\mathcal{I}$ 가 5 자릿수의 수렴 개선을 거친 뒤에도 같은 크기로 남는다.
- **cutoff 보정 문제가 사라진다.** 지금까지 $K$ 를 못 정한 것은 landscape 때문이
  아니라 수렴을 안 했기 때문이었다. polish 후 minimizer 사이 거리는 $O(1)$,
  같은 minimizer 안 수치산포는 $O(10^{-9})$ 이다.

network 4개에서 $\mathcal{I}$ 가 optimizer 에 15% 안에서 무관하다.

| network | N | SMACOF 300 | SMACOF 10k | L-BFGS |
|---|---|---|---|---|
| bn-mouse-visual-cortex-2 | 193 | 0.1100 | 0.1104 | 0.0925 |
| ca-netscience | 379 | 0.0554 | 0.0461 | 0.0539 |
| rt-twitter-copen | 761 | 0.0723 | 0.0598 | 0.0634 |
| power-662-bus | 662 | 0.0465 | 0.0441 | 0.0456 |

**부수적으로 무너지는 것**: 같은 $X^{(0)}$ 에서 SMACOF 와 L-BFGS 가 서로 다른
terminal 로 간다(상대차 9–10%, 24개 중 일치 0). 즉 $X^{(0)}\mapsto[X^\star]$ 가
optimizer 에 의존하므로 **basin occupancy $P_\gamma$ 는 landscape 만의 성질이 아니다.**
원고의 basin occupancy 형식화는 이 사실과 양립하지 않는다.

### 2.2 $\mathcal{D}_p$ — protocol 이 개입하지 않는 축

$G=-\tfrac12 C\Delta^{(2)}C$ 의 eigenvalue $\mu_a$ 에 대해

$$\mathcal{D}_p=\frac{\sum_{a>p}\max\{\mu_a,0\}+\sum_a\max\{-\mu_a,0\}}{\sum_a|\mu_a|}\in[0,1]$$

Schoenberg 로 $\mathcal{D}_p=0$ 이 정확한 실현과 동치이다. 전문은 [`notes/02`](notes/02-representability-deficiency.md).

| 모형 | $\mathcal{D}_2$ | |
|---|---|---|
| 경로 $P_{200}$ | **0.000** | 정리로 뒷받침되는 protocol control |
| $\mathbb{R}^2$ 좌표 거리 | 0.000 | graph metric 이 아니라 좌표 거리 |
| 격자 14×14 | 0.406 | graph metric 이 $\ell_1$ 이라 0 이 아니다 |
| RGG $r{=}0.12$ | 0.464 | 격자보다 크다 |
| ER $p{=}0.02$ | 0.970 | |

**정리** — $\mathcal{D}_p=0$ 이면 $\min\mathcal{F}=0$ 이고 minimizer 가 $\Omega$ 에서
유일하다. 역은 거짓(격자가 반례). 따라서 $\mathcal{D}_p=0$ 인 그래프에서 관측되는
$\mathcal{I}>0$ 은 전부 protocol 의 실패이다. 경로 그래프 $P_n$ 이 격자보다 강한
control 인 이유이다.

### 2.3 벡터로 분해 — $\mathcal{I}$ 는 trace 이다

$\Delta_{mm'}$ 를 다시 이중중심화하면 run 구름의 Gram 행렬이 복원되고,
$\operatorname{tr}\mathbf{G}_{\text{run}}$ 이 곧 $\mathcal{I}$ 이다. 같은 연산자의
spectrum 이 $d_{\text{eff}}$ (participation ratio) 를 준다. **이미 저장된 $\Delta$ 만으로
계산되므로 재실행이 필요 없다.** 전문은 [`notes/03`](notes/03-trace-vs-spectrum.md).

실제 network 77개에서 $\rho(\mathcal{I},d_{\text{eff}})=+0.757$ 이나 순위분산의 43% 가
$d_{\text{eff}}$ 고유의 정보이다.

---

## 3. 어디에 무엇이 있는가

### 저장소

| | 공개 | 내용 |
|---|---|---|
| `Gahyoun/Project-NEI` | **public** + Pages | 이 저장소. 웹 지도, notes, code. 원고 없음 |
| `Gahyoun/nei-verification` | **private** | 원고(`tex/Project_NEI_v4.tex`, `v5.tex`), 결과 jsonl, 그림. **public 으로 바꾸지 말 것** — 미출판 원고가 히스토리에 있다 |

웹 지도: https://gahyoun.github.io/Project-NEI/

### 로컬 (Google Drive)

```
Project-HONE/
  nei-architecture/                 이 저장소
  Real_network_NEI/
    run_nei_unified.py              생산용 loader (공항망 버그 수정본)
    referee_round/                  sweep 코드. 4개 노드에 배포됨
      nei_core.py                   sklearn SMACOF ensemble
      hessian_spectrum.py           projected Hessian, soft mode
      basin_stats.py                run_dissimilarity (Gram 항등식으로 메모리 절약)
      run_referee_sweep.py          sweep driver
      representability.py           D_p
      landscape_vectors.py          run 구름 spectrum, d_eff
    note_sections/                  노트에 넣을 절과 아키텍처 그림
  prune_v2.py                       원고에서 틀린 주장 제거 (6건 적용 완료)
  delete_unsupported.py, fix_internal_logic.py, prune_errors.py
```

### 노트와 원고 (Downloads)

- `NEI_Method_Korean_Linear_Algebra_Note_Overleaf_v8.zip` — 방법 노트 (45쪽)
- `NEI_Architecture_v1.zip` — 아키텍처 문서 (6쪽). 노트에서 **분리**했다.
  노트가 TikZ 가 많아 Overleaf 무료 플랜의 컴파일 한도를 넘겼기 때문이다.
- `Project_NEI.tex` — 원고. `prune_v2.py --apply` 로 오류 6건 삭제 적용됨. `.bak` 있음

TikZ 그림은 전부 **PDF 로 미리 구워** `figures/*.pdf` 로 넣고 `\figpdf{name}` 으로
부른다. PDF 가 없으면 원본 TikZ 로 되돌아간다. 이 덕에 노트가 0.7초에 컴파일된다.

### 실험 서버

| 노드 | python | 비고 |
|---|---|---|
| node0 | `~/miniconda3/bin/python` | 유일하게 conda 가 남아 있음 |
| node1–3 | `~/nei-env/bin/python` | 이번에 venv 로 복구 (numpy 2.5.2, sklearn 1.9.0) |
| node26 | — | publickey 거부. 접속 불가 |

sweep 아티팩트는 4개 노드의 `~/Real_network_NEI/referee_round/artifacts/` 에 분산되어
있다(총 88개, 2.7 MB). 데이터셋은 `~/Real_network_NEI/h2networks/` 와
`~/Real_network_NEI/SHL network/`.

---

## 4. 함정 — 여기서 시간을 잃었다

1. **ssh 로 백그라운드 실행이 막힌다.** `nohup ... &` 를 ssh 명령에 직접 쓰면 채널이
   닫히지 않아 매달린다. 노드에 런처 스크립트를 두고 그 안에서
   `setsid ... >log 2>&1 </dev/null &` 로 띄운다.
2. **sklearn 의 `eps` 는 optimality gap 이 아니다.** 상대 stress 개선량의 정지
   허용오차이다. $\sqrt{\varepsilon/\lambda_{\min}}$ 를 좌표 오차 반경으로 읽으면 안 된다.
3. **기호 충돌.** 노트의 $\kappa_+$ 는 projected Hessian 의 positive spectral scale
   이다. Schoenberg 결손은 $\mathcal{D}_p$ 로 쓴다.
4. **$\beta_{\text{null}}=(K-1)/(M-1)$** 이다. $(K-1)/M$ 이 아니다.
5. **아티팩트에 없는 것** — terminal configuration $X^{(m)}$, $S_\Delta$, $s_\Delta$,
   run 별 $\min d_{ij}$. 앞의 셋이 없어 gate 를 사후 계산할 수 없고 L5·L6 이 막힌다.
   설계 실수이다. $X^{(m)}$ 은 network 당 약 1 MB 로 저장하지 않을 이유가 없었다.
6. **$d_{\text{eff}}$ 가 $M=100$ 에서 검열된다.** 상한이 $M-1=99$ 인데 관측 최댓값이
   98.98 이고 77개 중 27개가 $0.5(M-1)$ 을 넘는다.
7. **`SPECIAL_DIR_RULES` 가 절대경로를 쓴다.** 저장소를 다른 곳에 clone 하면
   road/power-grid/airport 가 조용히 `generic` 으로 떨어진다.
8. **Drive 경로에 한글이 있다.** 스크립트에서 인용부호를 빠뜨리면 깨진다.
9. **웹 지도의 hyperedge 는 볼록껍질이 아니다.** 원소가 여러 층에 흩어져 있으면
   볼록껍질이 비원소를 삼킨다. 층마다 원소를 왼쪽으로 안정 분할하고 계단형
   폴리곤으로 닫는다. `isPointInFill` 로 검증할 것.

---

## 5. 다음에 할 일 — 우선순위 순

### 필수 (PRE 2026 을 닫으려면)

1. **polish 를 전 표본에 적용한다.** 약 80개 network. 가장 큰 계산 항목이지만 단순
   반복이다. `code/polish_certify.py` 를 sweep driver 에 붙이면 된다. 이것이 끝나야
   `local minimizer 위에서 측정했다` 고 쓸 수 있다.
2. **sweep 이 $X^{(m)}$, $S_\Delta$, $s_\Delta$, run 별 $\min d_{ij}$ 를 저장하게 고친다.**
   `run_referee_sweep.py` 의 `np.savez_compressed` 호출에 필드를 추가한다.
3. **$M$ 을 키운다.** 층화 부표본에 $M=400$. $d_{\text{eff}}$ 의 검열을 없애고 $K$ 가
   $M$ 에 대해 포화하는지 본다(지금 $K=M=24$ 는 `적어도 24개` 라는 뜻이다).
4. **$\mathcal{D}_p$ 를 전 표본에 계산한다.** `code/representability.py`. eigendecomposition
   한 번씩이라 몇 분이면 끝난다.
5. **경로 그래프 control 을 싣는다.** $P_n$ 에서 $\mathcal{I}$ 를 재서 protocol 의 unit
   test 로 보고한다.
6. **비중복성을 보인다.** $\lambda_2$ · 평균 최단거리 · 차수 이질성과의 편상관.
   이전에 지운 $\lambda_2$ 분석을 복원한다. 이것이 없으면 심사자는 redundant 하다고
   가정한다.

### 권장

7. $\rho_0$ 강건성 — uniform / cMDS+noise / spectral+noise 의 순위상관. **$\rho_0$ 는
   반드시 비퇴화여야 한다.** 점질량이면 $\mathcal{I}\equiv0$ 이 강제된다.
8. 원고 갱신 — basin occupancy 형식화를 2.1 의 결과에 맞게 고친다.

### 선택 / 다음 논문

9. automorphism 벤치마크. 정리로 뒷받침되고 계산이 싸지만 범위를 늘린다.
10. **L6** — soft mode 가 사는 node 와 재현이 안 되는 node 의 정렬.
    $\operatorname{corr}(|v_{\text{soft},i}|^2, r_i)$. 가장 강한 물리 결과가 될 자리이고
    $X^{(m)}$ 저장이 전제이다.
11. **L7** — 장벽. 두 terminal 을 잇는 경로 위 stress 프로파일. `basin` 이라는 말을
    쓰려면 필요하다.
12. 좌절의 무질서도. 격자는 $\mathcal{D}_2=0.406$ 인데 $\mathcal{I}\approx0$ 이다.
    좌절의 크기만으로는 landscape 가 거칠어지지 않는다. 박사과정 주제.

---

## 6. 손대기 전에 읽을 것

- [`notes/04`](notes/04-withdrawn-claims.md) — 철회한 주장 7건과 그 이유.
  **되살리기 전에 왜 지웠는지 확인할 것.**
- [`notes/05`](notes/05-open.md) — 남은 물음.
- [`data/claims.json`](data/claims.json) — 23건이 정리/측정/미해결/철회로 분류되어 있다.
  새 주장을 쓰면 여기에 등록한다.
- [`data/scope.json`](data/scope.json) — PRE 2026 절단선.

## 7. 웹 지도를 고치려면

`data/` 의 JSON 만 고치면 지도·막대그림·표가 따라 바뀐다. 렌더러는 손댈 필요 없다.

```bash
python3 -m http.server 8000     # file:// 로 열면 fetch 가 막힌다
```

`graph.js` 는 계층형 DAG 렌더러이다. 위상 깊이로 층을 잡고 barycenter 로 층 안 순서를
정한 뒤, hyperedge 원소를 왼쪽으로 안정 분할한다. 휠 확대·축소, 끌어서 이동, 마디를
누르면 이웃만 남는다.
