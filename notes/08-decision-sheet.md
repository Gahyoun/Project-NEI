# 9/17 결정 시트

`2026-09-05` · 한 장. 읽는 데 3분.

## 정할 것은 하나다

**1차 논문의 실증 주장을 어디서 끊는가.** 정의와 정리는 이미 닫혀 있으므로 논쟁 대상이
아니다. 남은 것은 "어떤 측정까지 논문에 넣는가" 하나다.

## 지금 준비된 것 — 추가 비용 0

| | 상태 |
|---|---|
| $\mathcal D_p$ 정의와 정리 ($\mathcal D_p=0\iff$ exact realizability) | 완료 |
| 표본 정의 (후보 83 → 대표 56 → 근사중복·병리 제외 → 분석 표본 **48**) | 완료 |
| $\mathcal D_p$ 전 표본 측정 (48개 전수) | 완료 |
| NEI를 kernel $K_\Pi$의 functional로 정의 | 완료 |
| 유한표본 항등식 $\widehat{\mathcal I}_M=\operatorname{tr}(B_z)/M$ | 완료 |
| floor 대 signal 판별 설계 + 모형망 결과 | 완료 |

여기까지로 말할 수 있는 것: *representability는 protocol 없이 재고, terminal spread는
protocol 조건부로 재며, 둘은 서로를 결정하지 않는다. 모형망에서 질서 구조는 point mass로부터
unresolved이고 ER·BA는 tolerance-stable하다. 실제 network 48개에서 $\mathcal D_2$가
$0.108$–$0.986$에 걸치고 유형별로 단조 정렬되며, 분해가 공항망과 사회망을 가른다.*

## 추가로 드는 것

| | 무엇 | 비용 |
|---|---|---|
| **P0** | corrected rerun — polish, $X^{(m)}$ 저장, 독립 batch | 4노드 **1–3일** |
| **P2** | configuration model null, $z_{\mathcal I}$ | +**2–3일** |
| **P3** | class 재현성 (2 batch × 2 optimizer) | +**2일** |

## 세 절단선

| | 넣는 것 | 사는 것 | 잃는 것 |
|---|---|---|---|
| **A** | 지금 있는 것만 | 즉시 착수 가능 | 실증이 모형망 수준. 기여가 얇다 |
| **B** | A + P0 | "실제망에서도 signal" | null이 없어 심사에서 반드시 지적된다 |
| **C** | B + P2 + P3 | "새 관측량"까지 주장 가능 | 2주 |

## 권고 — B로 끊고 null은 revision에서

C가 과학적으로 완결이지만, **null 없이 투고하고 revision에서 대응하는 것이 현실적**이다.
심사자가 configuration model을 요구할 것은 거의 확실하나, 그때 P2는 2–3일이면 된다.
A는 권하지 않는다 — 실제망 측정이 없으면 "네트워크의 성질"이라는 말을 쓸 수 없다.

## 원고 기준 매핑

`Project_NEI.tex`를 중심으로 볼 때:

**넣는다** — $\mathcal D_p$ 절(신규), 표본 정의 절(신규, 짧게), floor/signal 판별(신규),
kernel 정의로 estimand 절 교체.

**뺀다** — basin occupancy 형식화 전체(측정과 양립하지 않음), $d_{\rm eff}$(현재 값은
raw-distance 연산자의 것), "many minima" 어휘, intrinsic 어휘.

**다시 쓴다** — 결론 절. "새 불변량"이 아니라 "두 축의 분리와 그 독립성"으로.

## 이 문서가 짧은 이유

깊이는 박사과정 분량이 맞다. 그러나 1차 논문이 그 깊이를 해소할 필요는 없다.
[`data/agenda.json`](../data/agenda.json)에 열린 문제를 A1–A3로 적어두었고, 그것들은
**의도적으로 논문 밖**이다. 아키텍처 작업의 목적은 깊이 파는 것이 아니라 어디서 끊을지를
보이게 만드는 것이었다.
