# Real-network pilot input audit

2026-09-05 · local raw corpus confirmed · corrected rerun input freeze

## 1. Scope

1. **Purpose**
   - Corrected numerical gate와 graph-realization null workflow의 end-to-end pilot.
   - 세 empirical graph의 결과는 loader·gate·nested resampling의 재현성 검증 대상.
   - 전체 corpus, network family 또는 population-level structural effect의 대표 표본이라는 해석 금지.

2. **Access state**
   - Raw files: local Google Drive corpus에서 확인.
   - Public repository: raw files와 개인별 absolute path 미포함.
   - Executable manifest: repository 밖 local run directory에 고정.

## 2. Frozen pilot inputs

모든 수치는 raw text를 headerless edge list로 읽고, endpoint integer labels를 정렬한 뒤
0-based contiguous labels로 relabeling하고, simple undirected graph로 축약하여 독립적으로
검산한 값이다. Self-loop 제거와 repeated/reciprocal row collapse 뒤 세 graph 모두 connected.

| id | corpus-relative path | raw active rows | $N$ | $E$ | metric policy | SHA-256 |
|---|---|---:|---:|---:|---|---|
| `ca-sandi-auths` | `Real_network_NEI/network repository/Collaboration Networks/ca-sandi_auths.edges` | 124 | 81 | 119 | unweighted, $\ell_{uv}=1$ | `b205caf6ef3ca94ee832f4dc8ca1f3c888ab8ef45c40d06fa64de0b2e160c517` |
| `enzymes-g295` | `Real network/2026하반기/networks/Chemistry/ENZYMES-g295.edges` | 278 | 123 | 139 | unweighted, $\ell_{uv}=1$ | `ec4d18400d8d83a78eb5e96f72170c349c7d3eb44a5c7cbe2b483ac0fa5499b4` |
| `eco-foodweb-baywet` | `Real network/2026하반기/networks/Ecology/eco-foodweb-baywet.edges` | 2106 | 128 | 2075 | unweighted, third-column flux ignored | `f80e74718832f7e613684609ae4ec5c77f403aa879bb4a36f4416d2c38553319` |

Source attribution: Network Data Repository for all three inputs. Per-file download records are present
for `ENZYMES-g295` and `eco-foodweb-baywet`; the local corpus contains no per-file download record for
`ca-sandi_auths`. `ENZYMES-g295` is associated with the manuscript citation key
`borgwardt2005protein`.

## 3. Parser contract

1. **Header policy**
   - `ca-sandi_auths.edges`: no header; line 1, `28 0`, is data.
   - `ENZYMES-g295.edges`: no header; line 1, `7 2`, is data.
   - `eco-foodweb-baywet.edges`: leading `%` lines are metadata; data begin on line 3.
   - Automatic header inference 금지.

2. **Graph construction**
   - First two active columns: integer endpoints.
   - All endpoint vertices retained before connectivity validation.
   - Integer-label sort followed by deterministic 0-based relabeling.
   - Undirected projection, self-loop removal and duplicate/reciprocal edge collapse.
   - Expected $(N,E)$ mismatch: hard failure.

3. **Metric construction**
   - Three inputs 모두 $\ell_{uv}=1$.
   - `eco-foodweb-baywet` third field: carbon flux; edge length 또는 interaction-strength transform으로 사용 금지.
   - GCC extraction 불필요: frozen raw graphs 자체가 connected.
   - Pair vector: 0-based labels의 lexicographic unordered all-pair order.
   - Terminal comparison: labeled pair-distance vector; graph-isomorphism quotient 적용 금지.

## 4. Loader audit

1. **Host-specific dispatch**
   - `run_nei_unified.py:27--45`: default roots와 `SPECIAL_DIR_RULES`의 `/home/hedgehog` absolute prefix.
   - `run_nei_unified.py:140--145`: prefix mismatch 시 unconditional `generic` fallback.
   - Local Drive path의 road·repository network에 대한 intended specialized loader 미선택.

2. **Header loss**
   - `run_nei_unified.py:148--176`: `header=0` 성공값을 `header=None`보다 먼저 반환.
   - Headerless `ca-sandi_auths.edges` line 1의 edge 누락: legacy load $(81,118)$, corrected parse $(81,119)$.
   - Headerless `bn-mouse-visual-cortex-2.edges`에서도 동일한 one-edge loss 확인: legacy $E=213$, corrected $E=214$.
   - 자동 header inference에 기초한 legacy $(N,E)$와 hash의 corrected evidence 재사용 금지.

3. **Third-column ambiguity**
   - `run_nei_unified.py:418--432`: generic numeric third column을 무조건 shortest-path weight로 사용.
   - `run_referee_sweep.py:44--58`: 2026H2 자료에서 다섯 filename exception 외 전부 unweighted로 되돌리는 path-dependent override.
   - Override는 local variable `w`만 `None`으로 바꾸고 `meta["weighted"]`는 갱신하지 않으므로, output flag와 실제 shortest-path metric의 불일치 가능.
   - Pilot manifest의 per-file metric policy가 loader inference보다 우선.

4. **Weighted-null mismatch**
   - `run_nei_unified.py:583--589`: real graph에는 declared weight key를 사용하지만 ER과 degree-preserving null에는 `None` 전달.
   - Manuscript의 “same multiset of edge lengths” 조건을 구현하는 weight assignment 없음.
   - 현재 graph-null pilot의 unweighted input 제한.
   - Weighted structural comparison: edge-length reassignment rule과 sensitivity analysis 구현 전 보류.

5. **Null-generation safeguards**
   - `run_nei_unified.py:465--487`: matched-ER 후보 탐색은 단일 first exact GCC를 반환하는 utility이며 독립 graph-realization ensemble 자체가 아님.
   - `run_nei_unified.py:490--504`: connected double-edge swap 실패 시 unchanged parent graph를 경고 없이 반환.
   - Corrected runner의 graph seed, realized $(N,E)$, connectivity, degree equality, changed-edge fraction,
     retry/failure reason 및 null-realization identity 저장 필요.

## 5. Existing manifest boundary

1. `data/sample_manifest.json:2--5`: 83 files, 56 representatives, 15 duplicates, 12 exclusions의 legacy inventory.
2. `data/sample_manifest.json:44--71`: 동일 raw/derived `ca-sandi_auths`가 각각 $E=118$과 $E=119$로 서로 다른 representative 처리.
3. `data/sample_paths.txt:1--12`: host-specific `/home/hedgehog` absolute paths.
4. `build_manifest.py` default-root scan: 별도 2026H2 corpus 미포함.
5. Local 2026H2 raw corpus: 69 files (`.mtx` 35, `.edges` 34); `download_log.csv`의 69개 `ok` 행은 download provenance이며 checksum·parser·GCC·weight policy manifest가 아님.
6. 결론: legacy manifest는 provenance audit trail이며 corrected full-scope sampling frame 또는 pilot executable manifest가 아님.

## 6. Duplicate exclusion

`eco-florida.edges`와 `eco-foodweb-baywet.edges`는 각각 $(N,E)=(128,2075)$이고
unweighted topology에서 isomorphic임을 확인하였다. Pilot의 독립 graph unit은
`eco-foodweb-baywet` 하나만 사용. 이 제외는 현재 three-graph stage에만 적용되며 전체
corpus의 complete isomorphism audit를 대신하지 않는다.

## 7. Allowed evidence role

1. **Permitted**
   - Corrected parser와 run-level numerical gate의 end-to-end 실행 확인.
   - 각 parent graph 아래 independent ER 및 degree-preserving realizations의 nested inference 확인.
   - Raw hash, parser decision, graph realization, initialization 및 terminal failure의 provenance 확인.

2. **Not permitted**
   - Three-graph 평균의 population estimate 해석.
   - Network family effect 또는 universal real-vs-null ordering 주장.
   - Weighted network comparison으로의 일반화.
   - Legacy table 수치의 corrected result 승격.
