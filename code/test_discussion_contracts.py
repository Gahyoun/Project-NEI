"""Finite examples for the discussion-note bounds; not an empirical NEI sweep."""
from __future__ import annotations

import math
import numpy as np


def test_mass_resolution() -> None:
    # Three valid triangle distance vectors: a finite law on full pair space.
    D = np.array([[1.0, 1.2, 1.4], [3.0, 2.5, 3.7], [1.8, 1.9, 2.1]])
    w = np.array([1.0, 2.0, 0.5])
    target = np.array([2.0, 2.0, 2.0])
    scale = np.sum(w * target**2)
    for beta in (0.01, 0.1, 0.3, 0.5):
        p = np.array([beta, beta, 1 - 2 * beta])
        mean = p @ D
        var = p @ (D - mean)**2
        nei = np.mean(var / mean**2)
        delta = D[:, None, :] - D[None, :, :]
        rho_d2 = np.sum(w * delta**2, axis=2) / scale
        rho_mu2 = np.mean(delta**2 / mean**2, axis=2)
        c_minus2 = scale / D.shape[1] * np.min(1 / (w * mean**2))
        c_plus2 = scale / D.shape[1] * np.max(1 / (w * mean**2))
        assert np.all(rho_mu2 + 1e-13 >= c_minus2 * rho_d2)
        assert np.all(rho_mu2 <= c_plus2 * rho_d2 + 1e-13)
        np.testing.assert_allclose(nei, 0.5 * p @ rho_mu2 @ p)
        epsilon2 = 0.99 * rho_d2[0, 1]
        assert nei + 1e-13 >= c_minus2 * beta**2 * epsilon2

        for M in (2, 10, 100, 400):
            exact_detection = 1 - 2 * (1 - beta)**M + (1 - 2 * beta)**M
            union_bound = 1 - 2 * (1 - beta)**M
            assert exact_detection + 1e-13 >= union_bound
        for zeta in (0.05, 0.01):
            needed = math.ceil(math.log(zeta / 2) / math.log1p(-beta))
            assert 2 * (1 - beta)**needed <= zeta + 1e-13


def test_acceptance_representation() -> None:
    conditional = np.array([0.2, 0.3, 0.5])
    for alpha in (0.01, 0.5, 1.0):
        augmented = np.append(alpha * conditional, 1 - alpha)
        np.testing.assert_allclose(augmented.sum(), 1)
        np.testing.assert_allclose(1 - augmented[-1], alpha)
        np.testing.assert_allclose(augmented[:-1] / alpha, conditional)
    # At alpha=0 there is no conditional distribution to normalize.
    all_failed = np.array([0.0, 0.0, 0.0, 1.0])
    assert 1 - all_failed[-1] == 0


def test_control_fit_identity() -> None:
    D = np.array([1.0, 1.2, 1.4])
    target = np.array([2.0, 2.0, 2.0])
    w = np.array([1.0, 2.0, 0.5])
    phi = np.sum(w * (D - target)**2) / np.sum(w * target**2)
    for scale in (1e-6, 1.0, 1e6):
        rho2 = np.sum(w * (scale * D - scale * target)**2)
        rho2 /= np.sum(w * (scale * target)**2)
        np.testing.assert_allclose(rho2, phi)


if __name__ == "__main__":
    test_mass_resolution()
    test_acceptance_representation()
    test_control_fit_identity()
    print("OK: mass/separation bounds, detection power, acceptance normalization, target-fit scaling")
