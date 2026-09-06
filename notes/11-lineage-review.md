# Research lineage: inheritance and transfer boundaries

- Scope.
  - Selected research lineage, not an exhaustive publication catalogue.
  - Node authorship and edge provenance are independent attributes.
  - Historical influence is not inferred from chronology, coauthorship, or thematic similarity.

## Relation types

1. **Documented extension:** explicit original citation plus actual reuse/extension of a definition or method.
   - Kim 2015 → Kim & Lee 2019: Sec. II A, Ref. [13], Eqs. (1)–(2).
   - Lee 2021 → Bernenko 2023: Methods, Sec. III A/C, Ref. [14].
   - Menck 2013 → Schultz 2017: basin-stability definition and numerical estimation analysis.
2. **Methodological transfer:** an identified sampling or observable-construction component.
   - A proposed transfer in this note, not a claim that estimators or dynamics are identical.
3. **Mathematical foundation:** an actually used theorem or algorithm, with its assumptions.
4. **Conceptual analogy:** an explicitly bounded comparison of questions.
   - No historical-priority, causal, or mathematical-implication claim.

## Mathematical corrections

- CoI is **companionship inconsistency** in Kim & Lee (2019).
  - Binary co-membership variance identity; empirical variance uses divisor M.
  - The 2015 measure was already node-level.
  - Fixed-ensemble pair aggregation and deletion/re-embedding intervention are different operations.
- SMACOF is a discrete majorization algorithm.
  - Monotone stress descent is not proof of terminal multiplicity.
  - The full output law and its acceptance-conditioned law are distinct.
- Consistency landscape is a resolution-dependent profile.
  - It is not an energy-surface or barrier reconstruction.
- Basin probability is relative to a declared perturbation law.
  - It is normalized geometric volume only for the corresponding uniform law.
  - Attractor recovery and NEI geometry-weighted spread are different observables.
- Rare-class sampling.
  - Miss probability: (1 − p)^M; occupancy SE: sqrt[p(1 − p)/M].
  - If the true p = 1/500, M = 1497 suffices for at least 95% detection probability.
  - Occupancy SE is not automatically the SE of the nonlinear NEI estimator.
  - Fixed-graph Monte Carlo convergence and graph-size non-self-averaging are different limits.
- Inherent structures.
  - Minimization quench is not synonymous with quenched random disorder.
  - Deterministic pushforward does not exclude a thermal input law.
- Degree-conditioned null contrast is not a unique causal decomposition.
- Spectral realizability, the chosen deficiency diagnostic, and raw-stress optimization are distinct.

## Bibliographic separation

- Schultz, Menck, Heitzig & Kurths (2017).
  - *Potentials and Limits to Basin Stability Estimation*.
  - DOI: https://doi.org/10.1088/1367-2630/aa5a7b
  - Numerical estimation; Heetae Kim is not an author.
- Kim, Lee, Davidsen & Son (2018).
  - Power-grid multistability; DOI: https://doi.org/10.1088/1367-2630/aae8eb
- Kim, Mi Jin Lee, Sang Hoon Lee & Son (2019).
  - Integrated basin instability; DOI: https://doi.org/10.1063/1.5115532
- Borg & Mair (2017).
  - Multistart MDS fit/configuration comparison; DOI: https://doi.org/10.17713/ajs.v46i2.561
  - Direct prior-work boundary; the ordinal-MDS examples are not raw-stress NEI evidence.

## Validation and maintenance

- Data source: data/lineage.json.
  - Every edge has type, inherited component, boundary, and evidence locator.
  - Every paper has original object, randomness, transfer boundary, and source.
- Rebuild the local-file bundle after data changes:
  - node code/build_offline_data.mjs
- Checks:
  - node code/validate_lineage.cjs
  - node code/validate_research_math.cjs
  - python3 code/validate_architecture.py
  - node code/validate_source_excerpts.cjs
  - node code/validate_lineage.cjs --browser
    - Requires Playwright and Chromium; NEI_BROWSER_CHANNEL=chrome selects installed Chrome.
    - Tests every lineage node/link, four filters, math, HTTP and file loading, and lineage mobile width.
- Existing C41/C42 text and numerical values retained.
  - Missing schema fields restored as empirical_result / legacy.
  - No numerical rerun or promotion of evidence.
- Boundaries.
  - These checks are schema, finite-identity, and rendering regressions, not universal scientific certification.
  - Unrelated pre-existing sections have mobile-wide content; the mobile-width assertion is scoped to the lineage section.
  - No new empirical network results produced by this edit.
