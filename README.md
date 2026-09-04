# Project&nbsp;NEI — 아키텍처

고정된 topology-to-geometry protocol 아래에서 네트워크의 **geometric
representability** 와 **embedding identifiability** 를 정량화한다.

**웹 지도 → https://gahyoun.github.io/Project-NEI/**

두 명사는 서로 다른 질문이고, 결정적으로 protocol 의존성이 서로 다르다.

| | 무엇을 묻나 | protocol 의존 | 측정 |
|---|---|---|---|
| representability | $\delta_{ij}$ 가 $\mathbb{R}^p$ 에서 실현되는가 | **무관** (닫힌 형태) | Schoenberg 결손 $\mathcal{D}_p$ |
| identifiability | 그 실현이 결정되는가 | **의존** (명시적 조건부) | terminal ensemble + Hessian |

identifiability 는 표준 이론대로 두 갈래로 쪼개진다.

- **local 비식별** — projected Hessian 이 $\mathrm{E}(p)$ zero mode 너머로 영방향을
  가짐 ⟹ 연속족 ⟹ *floppy*
- **global 비식별** — 비길 만한 stress 의 분리된 minimizer 다수 ⟹ 이산 ⟹ *다중안정형*
- **식별 가능** — 유일 ⟹ *강체형*

## 지금까지 확정된 것

- **NEI 는 energy landscape 의 real degeneracy 를 잰다.** SMACOF terminal 을 L-BFGS 로 polish 해
  $\eta_g$ 를 $2.19\times10^{-3}\to2.00\times10^{-8}$ 로 내려도 $\mathcal{I}$ 가
  $0.110\to0.0767$ 로 살아남는다. polish 된 terminal 은 전부 진짜 local minimizer
  이고(음의 eigenvalue 0/8), 24개 run 이 서로 다른 24개 minimizer 로 가며 $K$ 는
  cutoff 를 6 자릿수 움직여도 변하지 않는다. → [notes/01](notes/01-nei-measures-real-degeneracy.md)
- **$\mathcal{D}_p$ 는 protocol 없이 계산되는 축이다.** 경로 그래프는 $0.000$ (정리로
  뒷받침되는 control), 격자는 $0.406$, RGG 는 $0.464$ — RGG 의 graph metric 은
  Euclidean 이 아니다. → [notes/02](notes/02-representability-deficiency.md)
- **$\mathcal{I}$ 는 terminal covariance 의 trace 이다.** trace 는 크기만 말한다.
  실제 network 77개에서 $\rho(\mathcal{I},d_{\text{eff}})=+0.757$ 이지만 순위분산의
  43% 가 설명되지 않는다. → [notes/03](notes/03-trace-vs-spectrum.md)

철회한 주장은 [notes/04](notes/04-withdrawn-claims.md), 남은 물음은
[notes/05](notes/05-open.md) 에 있다.

## PRE 2026 절단선

지도 위에 **초록 점선 hyperedge** 로 두른 22개 중 16개가 2026년에 일단락할 범위이다.
쌍별 간선이 아니라 hyperedge 로 묶은 이유는, 이 범위가 몇 개의 연결이 아니라 마디의
집합 하나로 닫히기 때문이다.

**주장 네 개.**

1. $\mathcal{D}_p$ 는 protocol 이 개입하지 않는 representability 축이다.
   $\mathcal{D}_p=0$ 이 정확한 실현과 동치이고(Schoenberg), 경로 그래프가 정리로
   뒷받침되는 control 을 준다.
2. 인증된 local minimizer 위에서도 terminal ensemble 은 축퇴되어 있다.
3. $\mathcal{I}$ 는 terminal covariance 의 trace 이고, 같은 연산자의 spectrum 이
   $d_{\text{eff}}$ 를 준다.
4. 두 축은 서로를 결정하지 않는다.

**닫으려면 필요한 것** — polish 전면 적용, $M$ 확대, $S_\Delta\cdot s_\Delta\cdot\min d_{ij}$
저장, $\mathcal{D}_p$ 전 표본, 경로 그래프 control, 표준 기술자와의 편상관.

**hyperedge 바깥** — soft mode 와 $r_i$ 의 정렬(L6), 장벽·continuation(L7), 좌절의
무질서도. 앞의 둘은 다음 논문, 마지막은 박사과정 주제이다.

자세한 것은 웹 지도의 `PRE 2026 절단선` 절과 [`data/scope.json`](data/scope.json) 에 있다.

다음 작업자는 [HANDOVER.md](HANDOVER.md) 부터 읽는다.

## 구성

```
index.html  krds.css  app.js      줌·팬 되는 계층형 지도 (KRDS 디자인 시스템 참조)
graph.js                          계층형 DAG 렌더러 (줌·팬, hyperedge)
data/                             지도·표·참고문헌의 원본 JSON
  nodes.json  edges.json          개념과 연결
  connectors.json                 연결을 지탱하는 다섯 장치
  claims.json                     정리 / 측정 / 미해결 / 철회
  refs.json                       참고문헌 43건
  measurements.json               막대그림이 읽는 수치
  scope.json                      PRE 2026 절단선 hyperedge
notes/                            중간에 확정한 것들
code/                             재현 코드
```

`data/` 의 JSON 을 고치면 웹 지도가 그대로 따라 바뀐다.

## 로컬에서 보기

```bash
python3 -m http.server 8000
```

`file://` 로 직접 열면 브라우저가 `fetch` 를 막는다.

## 기호 주의

방법 노트의 $\kappa_+$ 는 projected Hessian 의 positive spectral scale 이다.
Schoenberg 결손에는 $\mathcal{D}_p$ 를 쓴다. 혼동하지 말 것.
