"""Deterministic tests of the local residual bound; no network-sweep certification."""
from __future__ import annotations

import numpy as np


def test_exact_two_node_raw_stress_bound() -> None:
    # x* = (-ell/2, ell/2), Q = (-1,1)/sqrt(2).
    # d(u) = ell + sqrt(2)u and F(u) = 2u^2 on the noncollision chart.
    ell = 2.0
    u = np.array([-0.2, -0.1, 0.1, 0.2])
    d = ell + np.sqrt(2.0) * u
    g = 4.0 * u
    kappa = 4.0
    assert np.all(d > 0)
    mean = d.mean()
    nei = d.var() / mean**2
    bound = (2 / mean**2) * np.mean(g**2) / kappa**2
    # Equality for this symmetric law: the distance is affine and E[u]=0.
    np.testing.assert_allclose(nei, bound, rtol=1e-12)
    for scale in (1e-5, 1.0, 1e5):
        scaled_bound = (2 / (scale * mean)**2) * np.mean((scale * g)**2) / kappa**2
        np.testing.assert_allclose(scaled_bound, bound, rtol=1e-12)

    shifted_u = u + 0.07
    shifted_d = ell + np.sqrt(2.0) * shifted_u
    shifted_bound = (2 / shifted_d.mean()**2) * np.mean((4 * shifted_u)**2) / kappa**2
    assert shifted_d.var() / shifted_d.mean()**2 < shifted_bound


def test_endpoint_curvature_is_not_uniform_curvature() -> None:
    # Toy local objective f(u)=u^4, NOT a new empirical raw-stress example.
    # Positive curvature at the two sampled endpoints cannot certify the interval.
    a = 0.1
    u = np.array([-a, a])
    d = 2.0 + np.sqrt(2.0) * u
    g = 4 * u**3
    endpoint_curvature = 12 * a**2
    invalid_bound = (2 / d.mean()**2) * np.mean(g**2) / endpoint_curvature**2
    nei = d.var() / d.mean()**2
    assert nei > invalid_bound
    np.testing.assert_allclose(nei, 9 * invalid_bound, rtol=1e-12)


if __name__ == "__main__":
    test_exact_two_node_raw_stress_bound()
    test_endpoint_curvature_is_not_uniform_curvature()
    print("OK: exact local raw-stress bound, scale invariance, nonuniform-curvature counterexample")
