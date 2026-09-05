#!/usr/bin/env python3
"""Publish bounded graph-null point contrasts across prespecified tau_g gates.

This script reads already-computed per-graph gate_sensitivity summaries. It does
not reopen run vectors, refit embeddings, or change the frozen study. Each
tau_g value defines a different acceptance-conditioned empirical law, so rows
are descriptive sensitivity analyses rather than repeated estimates of one
fixed estimand. No confidence interval, p-value, mixing claim, or full-corpus
claim is produced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


SCHEMA_VERSION = "corrected-gate-sensitivity-public/v1"
ENSEMBLES = ("degree", "gnm", "degree_long")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requested_count(null_design: dict[str, Any], ensemble: str) -> int:
    key = {
        "degree": "B_degree",
        "gnm": "B_gnm",
        "degree_long": "B_degree_long",
    }[ensemble]
    value = null_design[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"invalid requested graph count {key}={value!r}")
    return value


def three_number_summary(values: list[int]) -> list[float] | None:
    if not values:
        return None
    array = np.asarray(values, dtype=float)
    return np.quantile(array, [0.0, 0.5, 1.0]).tolist()


def same_optional_number(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-14)


def build_gate_sensitivity(
    summary: dict[str, Any],
    published_primary: dict[str, Any],
    *,
    summary_sha256: str,
    published_primary_sha256: str,
    script_sha256: str,
) -> dict[str, Any]:
    if summary["study_id"] != published_primary["study_id"]:
        raise ValueError("study id differs between local and published summaries")
    if summary["config_sha256"] != published_primary["config_sha256"]:
        raise ValueError("config hash differs between local and published summaries")

    protocol = summary["protocol"]
    attempted = int(protocol["M"])
    tau_values = [float(value) for value in protocol["tau_g_sensitivity"]]
    if not tau_values or any(value <= 0 or not math.isfinite(value) for value in tau_values):
        raise ValueError("tau_g_sensitivity must contain finite positive values")
    if len(set(tau_values)) != len(tau_values):
        raise ValueError("tau_g_sensitivity contains duplicates")

    anchors = [graph for graph in summary["sources"] if graph["null_anchor"]]
    null_graphs = summary["null_graphs"]
    null_design = summary["null_design"]
    primary_rows = {
        (row["anchor_id"], row["ensemble"]): row
        for row in published_primary["graph_contrasts"]
    }
    rows: list[dict[str, Any]] = []

    for anchor in sorted(anchors, key=lambda graph: graph["id"]):
        for ensemble in ENSEMBLES:
            group = sorted(
                (
                    graph
                    for graph in null_graphs
                    if graph.get("anchor_id") == anchor["id"]
                    and graph.get("ensemble") == ensemble
                ),
                key=lambda graph: graph["id"],
            )
            requested = requested_count(null_design, ensemble)
            for tau_g in tau_values:
                tau_key = str(tau_g)
                try:
                    anchor_gate = anchor["gate_sensitivity"][tau_key]
                    null_gates = [graph["gate_sensitivity"][tau_key] for graph in group]
                except KeyError as error:
                    raise ValueError(
                        f"missing gate_sensitivity value {tau_key} for "
                        f"{anchor['id']} {ensemble}"
                    ) from error

                anchor_accepted = int(anchor_gate["accepted"])
                anchor_nei = anchor_gate["nei"]
                null_accepted = [int(gate["accepted"]) for gate in null_gates]
                available_nei = [
                    float(gate["nei"])
                    for gate in null_gates
                    if gate["nei"] is not None
                ]
                estimable = len(available_nei)
                null_complete = len(group) == requested and estimable == requested
                complete_for_contrast = null_complete and anchor_nei is not None
                null_mean = (
                    float(np.mean(available_nei)) if null_complete else None
                )
                contrast = (
                    float(anchor_nei) - null_mean
                    if complete_for_contrast and null_mean is not None
                    else None
                )
                count_summary = three_number_summary(null_accepted)
                rate_summary = (
                    [value / attempted for value in count_summary]
                    if count_summary is not None
                    else None
                )
                rows.append(
                    {
                        "anchor_id": anchor["id"],
                        "anchor_label": anchor["label"],
                        "anchor_kind": anchor["kind"],
                        "ensemble": ensemble,
                        "tau_g": tau_g,
                        "M_attempted_per_graph": attempted,
                        "anchor_accepted": anchor_accepted,
                        "anchor_alpha": anchor_accepted / attempted,
                        "anchor_nei_conditional": (
                            float(anchor_nei) if anchor_nei is not None else None
                        ),
                        "null_acceptance_count_min_median_max": count_summary,
                        "null_acceptance_rate_min_median_max": rate_summary,
                        "generated_graphs": len(group),
                        "estimable_graphs": estimable,
                        "requested_graphs": requested,
                        "complete_requested_ensemble": null_complete,
                        "null_nei_mean": null_mean,
                        "point_contrast_anchor_minus_null_mean": contrast,
                        "incomplete_reason": (
                            None
                            if complete_for_contrast
                            else (
                                "anchor NEI undefined at this gate"
                                if anchor_nei is None and null_complete
                                else "requested null ensemble missing or not fully estimable"
                            )
                        ),
                        "confidence_interval": None,
                        "p_value": None,
                    }
                )

    primary_tau = float(protocol["tau_g"])
    matching_tau = [value for value in tau_values if value == primary_tau]
    if len(matching_tau) != 1:
        raise ValueError("primary tau_g must occur exactly once in sensitivity ladder")
    checked = 0
    for row in rows:
        if row["tau_g"] != primary_tau:
            continue
        key = (row["anchor_id"], row["ensemble"])
        if key not in primary_rows:
            raise ValueError(f"published primary contrast missing row {key}")
        reported = primary_rows[key]["contrast"]
        computed = row["point_contrast_anchor_minus_null_mean"]
        if not same_optional_number(computed, reported):
            raise ValueError(
                f"primary contrast mismatch for {key}: "
                f"gate sensitivity={computed!r}, published={reported!r}"
            )
        checked += 1

    expected_rows = len(anchors) * len(ENSEMBLES) * len(tau_values)
    if len(rows) != expected_rows:
        raise AssertionError("internal error: incomplete sensitivity row product")

    return {
        "schema_version": SCHEMA_VERSION,
        "study_id": summary["study_id"],
        "status": "bounded descriptive gate sensitivity; full corpus pending",
        "config_sha256": summary["config_sha256"],
        "source_summary_sha256": summary_sha256,
        "published_primary_sha256": published_primary_sha256,
        "summarizer_sha256": script_sha256,
        "scope": (
            "Same bounded corrected study, including three unweighted real "
            "networks and declared synthetic controls; not a full-corpus validation."
        ),
        "definition": (
            "For each tau_g, recompute the point contrast as anchor conditional "
            "NEI minus the mean conditional NEI across the complete requested "
            "graph-null ensemble. All other numerical gates remain fixed."
        ),
        "estimand_warning": (
            "Changing tau_g changes the acceptance event and therefore the "
            "conditional terminal law. Rows are descriptive sensitivity analyses, "
            "not repeated estimates of one common estimand."
        ),
        "inference": {
            "confidence_intervals": None,
            "p_values": None,
            "finite_time_degree_null_uniformity_certified": False,
            "missing_or_nonestimable_null_policy": (
                "Report counts and acceptance summaries; withhold null mean and "
                "point contrast unless every requested graph is estimable."
            ),
        },
        "primary_crosscheck": {
            "tau_g": primary_tau,
            "checked_anchor_ensemble_rows": checked,
            "matches_corrected_study_reported_contrast": True,
            "withheld_primary_contrasts_required_to_remain_null": True,
        },
        "counts": {
            "anchors": len(anchors),
            "ensembles_per_anchor": len(ENSEMBLES),
            "tau_g_values": len(tau_values),
            "rows": len(rows),
        },
        "tau_g_values": tau_values,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument(
        "--published-primary",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "corrected-study.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "data"
        / "corrected-gate-sensitivity.json",
    )
    args = parser.parse_args()

    summary_path = args.study / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    published = json.loads(args.published_primary.read_text(encoding="utf-8"))
    result = build_gate_sensitivity(
        summary,
        published,
        summary_sha256=sha256(summary_path),
        published_primary_sha256=sha256(args.published_primary),
        script_sha256=sha256(Path(__file__)),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".partial")
    temporary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(args.output)
    print(
        f"WROTE {args.output} rows={result['counts']['rows']} "
        f"primary_checks={result['primary_crosscheck']['checked_anchor_ensemble_rows']}"
    )


if __name__ == "__main__":
    main()
