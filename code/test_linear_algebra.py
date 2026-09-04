#!/usr/bin/env python3
"""핵심 선형대수 항등식과 반례의 작은 regression test."""
from __future__ import annotations

import numpy as np

import polish_certify as pc
import representability as rp


def test_derivatives() -> None:
    rng = np.random.default_rng(7)
    n, p = 5, 2
    x = rng.normal(size=n * p)
    target_x = rng.normal(size=(n, p))
    Delta, _ = pc._dist(target_x)
    v = rng.normal(size=x.size)
    v /= np.linalg.norm(v)
    h = 1e-5

    _, g = pc.fg(x, Delta, n, p)
    fd = (
        pc.fg(x + h * v, Delta, n, p)[0]
        - pc.fg(x - h * v, Delta, n, p)[0]
    ) / (2 * h)
    np.testing.assert_allclose(g @ v, fd, rtol=1e-7, atol=1e-8)

    H = pc.hessian(x.reshape(n, p), Delta)
    hv = (
        pc.fg(x + h * v, Delta, n, p)[1]
        - pc.fg(x - h * v, Delta, n, p)[1]
    ) / (2 * h)
    np.testing.assert_allclose(H @ v, hv, rtol=1e-7, atol=1e-8)


def test_nei_trace_identity() -> None:
    rng = np.random.default_rng(11)
    M, q = 13, 9
    D = np.exp(rng.normal(size=(M, q)))
    mean = D.mean(axis=0)
    Z = D / (mean * np.sqrt(q))
    C = np.eye(M) - np.ones((M, M)) / M
    Bz = C @ Z @ Z.T @ C
    nei = np.mean(np.var(D, axis=0, ddof=0) / mean**2)
    np.testing.assert_allclose(nei, np.trace(Bz) / M, rtol=1e-12, atol=1e-12)

    # For the empirical law, rho_mu is the pair-mean-standardized Euclidean
    # metric.  Averaging over two iid draws gives exactly twice the variance.
    rho2 = np.sum((Z[:, None, :] - Z[None, :, :]) ** 2, axis=2)
    np.testing.assert_allclose(nei, 0.5 * np.mean(rho2), rtol=1e-12, atol=1e-12)

    point_mass = np.repeat(D[:1], M, axis=0)
    np.testing.assert_allclose(
        np.mean(np.var(point_mass, axis=0, ddof=0) / point_mass.mean(axis=0) ** 2),
        0.0,
        atol=1e-15,
    )

    raw = np.sum(np.var(D, axis=0, ddof=0)) / np.sum(mean**2)
    if np.isclose(nei, raw, rtol=1e-5, atol=1e-8):
        raise AssertionError("test data failed to distinguish raw and standardized traces")


def test_path_zero_modes_do_not_imply_continuum() -> None:
    n, p = 6, 2
    X = np.column_stack((np.arange(n, dtype=float), np.zeros(n)))
    Delta, _ = pc._dist(X)
    B = rp.gram_cmds(Delta)
    mu = np.linalg.eigvalsh(B)[::-1]
    np.testing.assert_allclose(rp.deficiency(mu, p), 0.0, atol=1e-12)

    w, _, q_gauge = pc.projected_spectrum(X, Delta, k=n * p)
    zero_count = int(np.sum(np.abs(w) < 1e-10))
    if q_gauge != 3:
        raise AssertionError(f"collinear E(2) orbit rank should be 3, got {q_gauge}")
    if zero_count < n - 2:
        raise AssertionError(f"expected transverse quartic zero modes, got {zero_count}")

    # A nonrigid transverse direction raises exact-fit stress at quartic order.
    v = np.linspace(-1.0, 1.0, n)
    ts = np.array([1e-2, 2e-2, 4e-2])
    Fs = []
    for t in ts:
        Xt = X.copy()
        Xt[:, 1] = t * v**2
        Fs.append(pc.fg(Xt.ravel(), Delta, n, p)[0])
    slope = np.polyfit(np.log(ts), np.log(Fs), 1)[0]
    if not 3.8 < slope < 4.2:
        raise AssertionError(f"path transverse stress should be quartic, slope={slope}")


def main() -> int:
    test_derivatives()
    test_nei_trace_identity()
    test_path_zero_modes_do_not_imply_continuum()
    print("OK: derivatives, NEI trace/pair-distance identities, path quartic counterexample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
