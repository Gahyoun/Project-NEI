# Calibration null — protocol-specific numerical baseline

2026-09-05 · corrected rerun pending

## 1. why this control

1. **Target quantity**
   - Pair-standardized empirical NEI
     $$
     \widehat{\mathcal I}_M
     =\frac{1}{N_+}\sum_{a=1}^{N_+}
       \frac{\operatorname{Var}_m d_a^{(m)}}{\bar d_a^2},
     \qquad \bar d_a>0.
     $$
   - Primary policy: every off-diagonal pair included.
   - Any nonpositive empirical pair mean: undefined NEI and explicit failure, not silent pair removal.

2. **Calibration question**
   - Observed $\widehat{\mathcal I}_M>0$: resolved terminal spread or numerical residue.
   - Path graph $P_n$: exact-representability control for the declared all-pairs raw-stress problem.
   - Same implementation, initialization law, stopping rule and numerical environment: required comparison unit.

3. **Allowed role**
   - Path result: empirical baseline for the declared protocol and problem family.
   - Not a universal numerical floor for every graph, size, conditioning, optimizer or machine precision.

## 2. theorem and optimizer outcome

1. **Exact representability**
   - $\mathcal D_p=0$: target dissimilarity $\Delta$ has an exact realization in $\mathbb R^p$.
   - Positive weight on every off-diagonal pair:
     $$
     \mathcal D_p=0
     \quad\Longrightarrow\quad
     \min_X\mathcal F(X)=0.
     $$
   - Complete pair distances: zero-stress realization unique modulo $\mathrm E(p)$.

2. **Nonconvex optimization**
   - Exact global solution existence $\neq$ random-start optimizer success.
   - No implication of absent positive-stress local minima.
   - No implication of SMACOF or L-BFGS global convergence.
   - Calibration value valid only after terminal stationarity and admissibility checks.

3. **Interpretive boundary**
   - A small path-control value: numerical resolution demonstrated for that protocol instance.
   - A larger value on another graph: comparison target, not automatic proof of distinct minima or physical degeneracy.

## 3. Legacy raw output

Protocol recorded in the legacy run:

- $M=24$, $p=2$, RNG seed $11$.
- SMACOF: max_iter $=3000$, eps $=10^{-12}$.
- L-BFGS polish: maxiter $=40000$, ftol $=10^{-18}$, gtol $=10^{-14}$.
- Pair-standardized plug-in variance with divisor $M$.

The table below is preserved as an audit trail. $\mathcal D_2$ is a spectral diagnostic; the
$\widehat{\mathcal I}_M$ columns are legacy numerical outputs and are not corrected-rerun results.

| graph | $N$ | $\mathcal D_2$ | $\widehat{\mathcal I}_M$, SMACOF | $\widehat{\mathcal I}_M$, polish |
|---|---|---|---|---|
| path $P_{60}$ | 60 | **0.0000** | $9.97\times10^{-9}$ | $2.92\times10^{-16}$ |
| path $P_{120}$ | 120 | **0.0000** | $1.08\times10^{-8}$ | $8.87\times10^{-17}$ |
| cycle $C_{60}$ | 60 | 0.3913 | $4.12\times10^{-16}$ | $1.51\times10^{-22}$ |
| grid $8\times8$ | 64 | 0.3983 | $1.25\times10^{-12}$ | $2.69\times10^{-20}$ |
| grid $12\times12$ | 144 | 0.4045 | $1.81\times10^{-12}$ | $1.19\times10^{-19}$ |
| BA $n{=}120$ | 120 | 0.8468 | $7.60\times10^{-2}$ | $7.36\times10^{-2}$ |
| ER $n{=}120$ | 120 | 0.8956 | $1.01\times10^{-1}$ | $9.87\times10^{-2}$ |

## 4. Implementation audit

1. **Detected defect**
   - Declared objective:
     $$
     \mathcal F(X)
     =\frac12\sum_{i,j}r_{ij}^2
     =\sum_{i<j}r_{ij}^2,
     \qquad r_{ij}=d_{ij}-\Delta_{ij}.
     $$
   - Required gradient:
     $$
     \nabla_{x_i}\mathcal F
     =2\sum_{j\ne i}\frac{r_{ij}}{d_{ij}}(x_i-x_j).
     $$
   - Legacy calibration_null.py and floor_test.py: missing factor $2$ in the supplied gradient.
   - Consequence: same formal stationary set under exact arithmetic, but invalid objective–gradient pairing for line search, stopping status and reported gradient residual.

2. **Corrected code state**
   - calibration-null/corrected-gradient-v1.
   - Central finite-difference directional check.
   - Import guard and --gradient-check-only.
   - Explicit collision failure at nondifferentiable $d_{ij}\simeq0$.
   - Explicit failure for nonfinite distances or any $\bar d_a\le0$.

3. **Evidence state**
   - Derivative check: corrected implementation validation.
   - Calibration table: legacy output only.
   - Corrected calibration rerun: pending.
   - Physical-mechanism claim: unavailable from this control alone.

## 5. Finite-$M$ check

For nonnegative pair distances and divisor-$M$ empirical variance,
$$
0\le
\frac{\operatorname{Var}_m d_a^{(m)}}{\bar d_a^2}
\le M-1.
$$
Therefore
$$
0\le\widehat{\mathcal I}_M\le M-1.
$$
At $M=24$, the algebraic ceiling is $23$. This bound is a finite-sample sanity check, not a
confidence interval, population bound, state-count estimator or numerical-noise threshold.

## 6. Allowed reading of the contrast

1. **Current status**
   - Legacy pattern: ordered controls near the numerical floor; ER/BA at $O(10^{-1})$.
   - Status: hypothesis-generating diagnostic.

2. **Unavailable conclusions**
   - No measured “digit gap.”
   - No proof that $\mathcal D_p>0\not\Rightarrow\mathcal I>0$ at population level.
   - No proof that $\mathcal D_p$ magnitude is irrelevant.
   - No proof of distinct minima, equal-stress degeneracy, barrier or continuous minimizer family.

3. **Required comparison**
   - Corrected derivative-consistent rerun with stored optimizer status and stationarity residual.
   - Independent batches and larger $M$.
   - $\mathcal D_p$-matched or covariate-matched graph controls before a magnitude claim.
   - Connected random-regular and degree-preserving nulls before structural attribution.

## 7. Reproduction

Derivative validation:

    python3 code/calibration_null.py --gradient-check-only

Corrected calibration run:

```bash
python3 code/calibration_null.py
```
