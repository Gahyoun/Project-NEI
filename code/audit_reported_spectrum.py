#!/usr/bin/env python3
"""Audit algebraic invariants in the reported representability spectrum.

This script deliberately uses only the reported CSV aggregates.  It can detect
internal contradictions and stale JSON summaries, but it cannot certify the
underlying graph loader, edge weights, distance matrix, or eigendecomposition
without their raw artifacts.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path


P_LIST = (1, 2, 3, 5, 10)
DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def close(a: float, b: float, tol: float) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def number(row: dict[str, str], field: str) -> float:
    raw = row.get(field, "")
    if raw is None or not str(raw).strip():
        raise ValueError(f"missing {field}")
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"nonfinite {field}={raw!r}")
    return value


def audit_rows(rows: list[dict[str, str]], tol: float) -> tuple[list[str], int]:
    issues: list[str] = []
    checked = 0
    for csv_line, row in enumerate(rows, start=2):
        if row.get("status") != "ok":
            continue
        checked += 1
        name = row.get("stem") or row.get("path") or f"line {csv_line}"
        prefix = f"CSV line {csv_line} ({name})"
        try:
            n = int(float(row["N"]))
            rank_eps = int(float(row["rank_eps"]))
            total = number(row, "mu_abs_sum")
            mu_max = number(row, "mu_max")
            mu_min = number(row, "mu_min")
            dneg = number(row, "D_neg")
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(f"{prefix}: {exc}")
            continue

        if total <= 0.0:
            issues.append(f"{prefix}: mu_abs_sum={total} must be positive")
            continue
        if not (0 <= rank_eps <= n):
            issues.append(f"{prefix}: rank_eps={rank_eps} outside [0,N={n}]")
        if mu_max <= 0.0:
            issues.append(f"{prefix}: mu_max={mu_max} must be positive for a nonzero EDM")
        if mu_max < mu_min - tol:
            issues.append(f"{prefix}: mu_max={mu_max} smaller than mu_min={mu_min}")
        if abs(mu_max) > total * (1.0 + tol):
            issues.append(f"{prefix}: |mu_max| exceeds mu_abs_sum")
        if abs(mu_min) > total * (1.0 + tol):
            issues.append(f"{prefix}: |mu_min| exceeds mu_abs_sum")

        # For B=-C Delta^{\circ 2} C/2 with hollow nonnegative Delta,
        # tr(B)=sum_{ij} Delta_ij^2/(2N)>=0, hence negative mass <= 1/2.
        if not (-tol <= dneg <= 0.5 + tol):
            issues.append(f"{prefix}: D_neg={dneg} outside the EDM mass range [0,1/2]")

        previous_d = None
        previous_dim = None
        previous_expl = None
        for p in P_LIST:
            if p >= n or not str(row.get(f"D{p}", "")).strip():
                continue
            try:
                dim = number(row, f"D{p}_dim")
                dp = number(row, f"D{p}")
                expl = number(row, f"expl{p}")
            except ValueError as exc:
                issues.append(f"{prefix}: {exc}")
                continue

            if not (-tol <= dim <= 1.0 + tol):
                issues.append(f"{prefix}: D{p}_dim={dim} outside [0,1]")
            if not (-tol <= dp <= 1.0 + tol):
                issues.append(f"{prefix}: D{p}={dp} outside [0,1]")
            if not (-tol <= expl <= 1.0 + tol):
                issues.append(f"{prefix}: expl{p}={expl} outside [0,1]")
            if not close(dp, dim + dneg, tol):
                issues.append(
                    f"{prefix}: D{p}={dp} != D{p}_dim+D_neg={dim + dneg}"
                )
            if dim > 1.0 - dneg + tol:
                issues.append(
                    f"{prefix}: D{p}_dim={dim} exceeds positive mass 1-D_neg={1-dneg}"
                )

            positive_fraction = 1.0 - dneg
            if positive_fraction <= 0.0:
                issues.append(f"{prefix}: nonpositive reported positive spectral mass")
            else:
                expected_expl = 1.0 - dim / positive_fraction
                if not close(expl, expected_expl, tol):
                    issues.append(
                        f"{prefix}: expl{p}={expl} != 1-D{p}_dim/(1-D_neg)="
                        f"{expected_expl}"
                    )

            if previous_d is not None and dp > previous_d + tol:
                issues.append(f"{prefix}: D{p}={dp} increases from {previous_d}")
            if previous_dim is not None and dim > previous_dim + tol:
                issues.append(f"{prefix}: D{p}_dim={dim} increases from {previous_dim}")
            if previous_expl is not None and expl < previous_expl - tol:
                issues.append(f"{prefix}: expl{p}={expl} decreases from {previous_expl}")
            previous_d, previous_dim, previous_expl = dp, dim, expl

        try:
            d1 = number(row, "D1")
            d1_dim = number(row, "D1_dim")
            expected_d1 = 1.0 - mu_max / total
            expected_d1_dim = 1.0 - dneg - mu_max / total
            if not close(d1, expected_d1, tol):
                issues.append(f"{prefix}: D1={d1} != 1-mu_max/mu_abs_sum={expected_d1}")
            if not close(d1_dim, expected_d1_dim, tol):
                issues.append(
                    f"{prefix}: D1_dim={d1_dim} != 1-D_neg-mu_max/mu_abs_sum="
                    f"{expected_d1_dim}"
                )
        except ValueError as exc:
            issues.append(f"{prefix}: {exc}")

        weighted = str(row.get("weighted", "")).strip().lower()
        if weighted not in {"true", "false"}:
            issues.append(f"{prefix}: weighted flag is not boolean: {row.get('weighted')!r}")
        if weighted == "true" and not str(row.get("weight_def", "")).strip():
            issues.append(f"{prefix}: weighted row has no weight_def")

    return issues, checked


def audit_quantiles(
    rows: list[dict[str, str]], measurements_path: Path, tol: float
) -> list[str]:
    with measurements_path.open(encoding="utf-8") as handle:
        measurements = json.load(handle)
    reported = {
        item["k"]: item["v"] for item in measurements["repr_full"]["quantiles"]
    }
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    expected_fields = {
        "$\\mathcal D_1$": "D1",
        "$\\mathcal D_2$": "D2",
        "$\\mathcal D^{\\rm neg}$": "D_neg",
    }
    issues: list[str] = []
    labels = ("min", "median", "max")
    for key, field in expected_fields.items():
        values = [number(row, field) for row in ok_rows]
        expected = [min(values), statistics.median(values), max(values)]
        actual = reported.get(key)
        if not isinstance(actual, list) or len(actual) != 3:
            issues.append(f"JSON repr_full.quantiles[{key!r}] is missing or malformed")
            continue
        for label, got, want in zip(labels, actual, expected):
            got_float = float(got)
            if not close(got_float, want, tol):
                issues.append(
                    f"JSON repr_full.quantiles[{key!r}].{label}={got_float} "
                    f"but CSV gives {want}"
                )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv", type=Path, default=DEFAULT_ROOT / "data" / "repr_full_sample.csv"
    )
    parser.add_argument(
        "--measurements",
        type=Path,
        default=DEFAULT_ROOT / "data" / "measurements.json",
    )
    parser.add_argument("--csv-only", action="store_true")
    parser.add_argument("--tol", type=float, default=1e-10)
    args = parser.parse_args()

    with args.csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    row_issues, checked = audit_rows(rows, args.tol)
    summary_issues = [] if args.csv_only else audit_quantiles(
        rows, args.measurements, args.tol
    )

    print(f"reported rows checked: {checked}")
    print(f"row-level algebraic issues: {len(row_issues)}")
    for issue in row_issues:
        print(f"ERROR {issue}")
    print(f"summary issues: {len(summary_issues)}")
    for issue in summary_issues:
        print(f"ERROR {issue}")
    print(
        "LIMITATION raw eigenvalues, input distances, and edge weights are absent; "
        "their provenance and sign cannot be certified from this CSV"
    )
    return 1 if row_issues or summary_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
