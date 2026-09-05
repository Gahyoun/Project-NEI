#!/usr/bin/env python3
"""Deterministic regression tests for the NEI inference identities.

The tests use synthetic nonnegative pair-distance vectors only.  They verify
algebraic identities and regularity calculations; they do not validate any
reported network measurement.
"""

from __future__ import annotations

import unittest

import numpy as np


def plugin_nei(samples: np.ndarray, *, ddof: int = 0) -> float:
    """Return the plug-in NEI, averaging coordinate-wise squared CVs."""

    values = np.asarray(samples, dtype=float)
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] < 1:
        raise ValueError("samples must have shape (M, N_plus) with M,N_plus >= 1")
    if np.any(values < 0.0):
        raise ValueError("pair distances must be nonnegative")
    if ddof not in (0, 1):
        raise ValueError("only divisor-M (ddof=0) and divisor-(M-1) are tested")
    if values.shape[0] - ddof <= 0:
        raise ValueError("the requested variance divisor is undefined")

    means = values.mean(axis=0)
    if np.any(means <= 0.0):
        raise ValueError("NEI is undefined when an empirical pair mean is zero")
    return float(np.mean(values.var(axis=0, ddof=ddof) / means**2))


def spectral_participation_ratio(samples: np.ndarray) -> tuple[float, int]:
    """Return covariance participation ratio and numerical positive rank."""

    values = np.asarray(samples, dtype=float)
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] < 1:
        raise ValueError("samples must be a nonempty matrix")
    centered = values - values.mean(axis=0, keepdims=True)
    covariance = centered.T @ centered / values.shape[0]
    eigenvalues = np.linalg.eigvalsh(covariance)
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    tolerance = 100.0 * np.finfo(float).eps * max(values.shape) * scale
    positive = eigenvalues[eigenvalues > tolerance]
    rank = int(positive.size)
    if rank == 0:
        return float("nan"), 0
    ratio = float(positive.sum() ** 2 / np.dot(positive, positive))
    return ratio, rank


def population_moments(
    support: np.ndarray, probabilities: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Return NEI and coordinate-wise mean, raw second moment, and variance."""

    points = np.asarray(support, dtype=float)
    probs = np.asarray(probabilities, dtype=float)
    if points.ndim != 2 or probs.shape != (points.shape[0],):
        raise ValueError("support/probability shapes do not agree")
    if np.any(points < 0.0) or np.any(probs < 0.0):
        raise ValueError("support and probabilities must be nonnegative")
    if not np.isclose(probs.sum(), 1.0, rtol=0.0, atol=1e-14):
        raise ValueError("probabilities must sum to one")
    means = probs @ points
    if np.any(means <= 0.0):
        raise ValueError("population NEI requires positive coordinate means")
    seconds = probs @ (points**2)
    variances = seconds - means**2
    nei = float(np.mean(variances / means**2))
    return nei, means, seconds, variances


def influence_raw(
    point: np.ndarray, means: np.ndarray, seconds: np.ndarray
) -> float:
    """Raw-moment form of the NEI influence function."""

    d = np.asarray(point, dtype=float)
    terms = (d**2 - seconds) / means**2 - 2.0 * seconds * (d - means) / means**3
    return float(np.mean(terms))


def influence_centered(
    point: np.ndarray, means: np.ndarray, variances: np.ndarray
) -> float:
    """Centered-moment form of the same NEI influence function."""

    d = np.asarray(point, dtype=float)
    terms = ((d - means) ** 2 - variances) / means**2
    terms -= 2.0 * variances * (d - means) / means**3
    return float(np.mean(terms))


class FiniteSampleBoundsTest(unittest.TestCase):
    def test_divisor_m_bounds_and_upper_equality(self) -> None:
        samples = np.array(
            [
                [0.2, 1.1, 4.0],
                [1.3, 2.0, 0.0],
                [2.1, 0.4, 1.2],
                [0.0, 3.2, 2.8],
                [4.4, 1.8, 0.7],
            ]
        )
        estimate = plugin_nei(samples)
        self.assertGreaterEqual(estimate, 0.0)
        self.assertLessEqual(estimate, samples.shape[0] - 1.0 + 1e-14)

        # Every coordinate has exactly one positive observation.  The positive
        # observation need not occur in the same run for every coordinate.
        equality_samples = np.array(
            [
                [2.0, 0.0, 0.0],
                [0.0, 7.0, 0.0],
                [0.0, 0.0, 1.5],
                [0.0, 0.0, 0.0],
            ]
        )
        m = equality_samples.shape[0]
        self.assertAlmostEqual(plugin_nei(equality_samples), m - 1.0)
        self.assertAlmostEqual(plugin_nei(equality_samples, ddof=1), float(m))

    def test_m_one_identity_and_sample_variance_undefined(self) -> None:
        # This numerical zero is an algebraic identity, not evidence that the
        # population terminal law is a point mass.
        self.assertEqual(plugin_nei(np.array([[1.0, 2.0, 3.0]])), 0.0)
        with self.assertRaises(ValueError):
            plugin_nei(np.array([[1.0, 2.0, 3.0]]), ddof=1)


class ParticipationRatioTest(unittest.TestCase):
    def test_rank_bounds_and_equality_cases(self) -> None:
        rank_one = np.outer(
            np.array([-2.0, -1.0, 0.0, 1.0, 2.0]),
            np.array([1.0, -3.0, 2.0]),
        )
        ratio, rank = spectral_participation_ratio(rank_one)
        self.assertEqual(rank, 1)
        self.assertAlmostEqual(ratio, 1.0)

        # Columns spanning the centered subspace have equal positive covariance
        # eigenvalues, and therefore attain d_eff = rank = M-1.
        m = 5
        centering = np.eye(m) - np.ones((m, m)) / m
        eigenvalues, eigenvectors = np.linalg.eigh(centering)
        isotropic = eigenvectors[:, eigenvalues > 0.5]
        ratio, rank = spectral_participation_ratio(isotropic)
        self.assertEqual(rank, m - 1)
        self.assertAlmostEqual(ratio, float(rank), places=12)

        generic = np.array(
            [
                [0.0, 1.0, 4.0, 2.0, 8.0, 3.0],
                [1.0, 1.5, 3.0, 3.0, 5.0, 4.0],
                [2.0, 0.5, 2.0, 5.0, 3.0, 2.0],
                [4.0, 2.5, 1.0, 7.0, 2.0, 6.0],
            ]
        )
        ratio, rank = spectral_participation_ratio(generic)
        self.assertGreaterEqual(ratio, 1.0 - 1e-12)
        self.assertLessEqual(ratio, rank + 1e-12)
        self.assertLessEqual(rank, min(generic.shape[1], generic.shape[0] - 1))


class InfluenceFunctionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.support = np.array(
            [
                [1.0, 2.0, 3.0],
                [2.0, 1.5, 4.0],
                [4.0, 3.0, 1.0],
            ]
        )
        self.probabilities = np.array([0.2, 0.5, 0.3])
        self.nei, self.means, self.seconds, self.variances = population_moments(
            self.support, self.probabilities
        )

    def test_raw_and_centered_forms_are_pointwise_equal(self) -> None:
        test_points = np.vstack((self.support, np.array([[3.4, 0.8, 5.2]])))
        for point in test_points:
            raw = influence_raw(point, self.means, self.seconds)
            centered = influence_centered(point, self.means, self.variances)
            self.assertAlmostEqual(raw, centered, places=13)

        expected_influence = sum(
            probability * influence_raw(point, self.means, self.seconds)
            for probability, point in zip(self.probabilities, self.support)
        )
        self.assertAlmostEqual(expected_influence, 0.0, places=13)

    def test_contamination_derivative(self) -> None:
        contaminating_point = np.array([3.4, 0.8, 5.2])
        epsilon = 1e-7
        contaminated_support = np.vstack((self.support, contaminating_point))
        contaminated_probabilities = np.concatenate(
            ((1.0 - epsilon) * self.probabilities, np.array([epsilon]))
        )
        contaminated_nei, *_ = population_moments(
            contaminated_support, contaminated_probabilities
        )
        finite_difference = (contaminated_nei - self.nei) / epsilon
        analytic = influence_raw(contaminating_point, self.means, self.seconds)
        self.assertAlmostEqual(finite_difference, analytic, places=5)

    def test_pairwise_scale_invariance(self) -> None:
        sample = np.array(
            [
                [1.0, 2.0, 3.0],
                [2.0, 1.5, 4.0],
                [4.0, 3.0, 1.0],
                [3.0, 0.7, 2.5],
            ]
        )
        scales = np.array([3.0, 0.2, 10.0])
        self.assertAlmostEqual(plugin_nei(sample), plugin_nei(sample * scales), places=14)

        scaled_nei, scaled_means, scaled_seconds, scaled_variances = population_moments(
            self.support * scales, self.probabilities
        )
        self.assertAlmostEqual(self.nei, scaled_nei, places=14)

        point = np.array([3.4, 0.8, 5.2])
        raw = influence_raw(point, self.means, self.seconds)
        scaled_raw = influence_raw(point * scales, scaled_means, scaled_seconds)
        centered = influence_centered(point, self.means, self.variances)
        scaled_centered = influence_centered(
            point * scales, scaled_means, scaled_variances
        )
        self.assertAlmostEqual(raw, scaled_raw, places=13)
        self.assertAlmostEqual(centered, scaled_centered, places=13)


if __name__ == "__main__":
    unittest.main()
