# Research lineage: inheritance and transfer boundaries

- Scope.
  - Selected research lineage, not an exhaustive publication catalogue.
  - Node authorship and edge provenance are independent attributes.
  - Historical influence is not inferred from chronology, coauthorship, or thematic similarity.

## Relation types

1. **Documented extension:** explicit original citation plus actual reuse/extension of a definition or method.
   - Kim 2015 → Kim & Lee 2019: Sec. II A, Ref. [13], Eqs. (1)–(2).
   - Kim & Lee 2019 → Lee et al. 2021: Sec. II C, Eqs. (6)–(7), Ref. [15]; Sec. III A3, Fig. 5 compares CoI and MeI.
   - Lee, Cucuringu & Porter 2014 → Lee 2016: Sec. II B, Eqs. (2)–(5), Ref. [17]; reuse and adaptation of core-score calculation.
   - Kim, Lee & Holme 2016 → Kim et al. 2018: introduction, Sec. 3.2, Ref. [21]; analysis of mechanisms underlying nonmonotonic basin-stability profiles.
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
- CoI, PaI/MeI, and NEI have distinct constructions.
  - The CoI–NEI connection is aggregation of relational variance, with different observables, normalization, and sampling laws.
  - PaI and MeI incorporate similarities between solutions or memberships. They complement CoI rather than universally replacing it.
  - With partition frequencies q_alpha and element-centric similarities S_alpha,beta (unit diagonal), PaI is the reciprocal of sum(q_alpha q_beta S_alpha,beta).
  - If distinct partitions have zero similarity, the definition reduces algebraically to 1/sum(q_alpha^2); equal frequencies then give the number of represented partitions.
  - NEI measures mean-normalized geometric dispersion. Occupancy and separation supply complementary information.
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
  - Lee (2016), Sec. III B and IV, provides a methodological precedent through degree-preserving randomization of nestedness and coreness.
  - Degree sequence constrains attainable structural patterns; randomization need not weaken the observed descriptor.
  - The transfer to NEI specifies a comparison design, not the sign of an NEI contrast.
- Spectral realizability, the chosen deficiency diagnostic, and raw-stress optimization are distinct.
  - Schoenberg and de Leeuw supply separate foundations for NEI: realizability criteria and stress majorization, respectively. The map does not posit an algorithmic dependency between them.
- Protocol variation and repeated runs at fixed protocol answer different questions.
  - Bernenko et al. (2023, semi-nested communities) motivate examination of reorganization across community resolutions.
  - Community resolution gamma changes the objective; epsilon_D classifies a fixed set of terminal outputs.
  - Changing only the classification threshold can change occupancy summaries while leaving pair-distance NEI unchanged.

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
- Borg & Leutner (1985).
  - *Measuring the Similarity of MDS Configurations*.
  - DOI: https://doi.org/10.1207/s15327906mbr2003_6
  - Corresponding interpoint distances were already used to compare configurations without coordinate alignment. This is a precedent for the comparison object, not the NEI estimator.
- Lee (2016).
  - *Network nestedness as generalized core-periphery structures*.
  - DOI: https://doi.org/10.1103/PhysRevE.93.022306
- Bernenko, Lee, Stenberg & Lizana (2023).
  - *Mapping the semi-nested community structure of 3D chromosome contact networks*.
  - DOI: https://doi.org/10.1371/journal.pcbi.1011185
  - Separate bibliographic record from *Exploring 3D community inconsistency in human chromosome contact networks*.

## Contribution and presentation

- Position NEI relative to relational variance, configurational comparison, and degree-conditioned graph ensembles.
- Define the admissible terminal law before interpreting mean squared pair-distance coefficients of variation.
- Information beyond stress and degree sequence remains an empirical question requiring controlled comparisons; the lineage does not establish nonredundancy.
- Remove the weak K-SAT → core–periphery analogy from the map. The K-SAT paper remains available as background on size-dependent observables.
- Separate bibliographic authorship from intellectual relations and use neutral research prose throughout the additions.

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
  - Scope checks prevent explicitly excluded literature from reappearing in the rendered lineage or references.
- Existing C41/C42 text and numerical values retained.
  - Missing schema fields restored as empirical_result / legacy.
  - No numerical rerun or promotion of evidence.
- Boundaries.
  - These checks are schema, finite-identity, and rendering regressions, not universal scientific certification.
  - Unrelated pre-existing sections have mobile-wide content; the mobile-width assertion is scoped to the lineage section.
  - No new empirical network results produced by this edit.
