#!/usr/bin/env python3
"""Publish a compact, privacy-safe view of one completed corrected study.

Input
-----
``STUDY/summary.json`` produced by ``summarize_corrected_study.py``.

Outputs
-------
* ``data/corrected-study.json`` (or ``--output``): compact web payload.
* ``STUDY/report.md`` (or ``--report``): Korean hierarchical audit report.

The publisher performs no scientific recomputation.  It selects the already
summarized estimand, withholds incomplete graph-null contrasts, aggregates
finite-time null diagnostics, and removes local paths and raw artifacts.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import tempfile
from typing import Any, Iterable, Mapping


PUBLIC_SCHEMA_VERSION = "corrected-study-public/v1"
FORBIDDEN_KEY_PARTS = (
    "coordinate",
    "source_labels",
    "target_coordinates",
    "artifact_path",
    "input_path",
)
LOCAL_PATH_PATTERN = re.compile(
    r"(?:file://|(?:^|[\s'\"])/(?:Users|home|private|var|tmp)(?:/|$)|[A-Za-z]:\\)"
)
WITHHELD_FIELDS = (
    "null_nei_mean",
    "available_null_nei_mean_descriptive",
    "null_nei_sd_between_graph_estimates",
    "contrast",
    "outer_graph_percentile95",
    "nested_resampling95_sensitivity",
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    block = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _atomic_json(path: Path, value: Any) -> None:
    encoded = json.dumps(
        value, ensure_ascii=False, indent=2, sort_keys=False, allow_nan=False
    ) + "\n"
    _atomic_text(path, encoded)


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _require_nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _finite_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _quantiles(values: Iterable[Any]) -> list[float] | None:
    numbers = sorted(
        number
        for value in values
        if (number := _finite_or_none(value)) is not None
    )
    if not numbers:
        return None
    return [numbers[0], float(statistics.median(numbers)), numbers[-1]]


def _copy_json(value: Any) -> Any:
    """Return a detached JSON-compatible copy without accepting NaN."""

    return json.loads(json.dumps(value, allow_nan=False))


def _validate_summary(summary: Mapping[str, Any]) -> None:
    required = {
        "study_id",
        "status",
        "config_sha256",
        "execution",
        "protocol",
        "null_design",
        "graph_count",
        "attempted_runs",
        "terminal_optimizations",
        "sources",
        "null_graphs",
        "graph_contrasts",
        "null_generation_failures",
        "scope",
        "outstanding",
        "interpretation_limits",
    }
    missing = sorted(required - set(summary))
    if missing:
        raise ValueError(f"summary.json missing keys: {', '.join(missing)}")
    for key in ("graph_count", "attempted_runs", "terminal_optimizations"):
        _require_nonnegative_int(summary[key], key)
    if not isinstance(summary["sources"], list):
        raise ValueError("sources must be a list")
    if not isinstance(summary["null_graphs"], list):
        raise ValueError("null_graphs must be a list")
    if len(summary["sources"]) + len(summary["null_graphs"]) != summary["graph_count"]:
        raise ValueError("graph_count does not match sources + null_graphs")
    if not isinstance(summary["graph_contrasts"], list):
        raise ValueError("graph_contrasts must be a list")
    if not isinstance(summary["null_generation_failures"], list):
        raise ValueError("null_generation_failures must be a list")
    config_hash = summary["config_sha256"]
    if not isinstance(config_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", config_hash):
        raise ValueError("config_sha256 must be a lowercase SHA-256 digest")
    execution = _require_mapping(summary["execution"], "execution")
    if execution.get("config_sha256") not in (None, config_hash):
        raise ValueError("execution and summary config_sha256 differ")
    protocol = _require_mapping(summary["protocol"], "protocol")
    M = _require_nonnegative_int(protocol.get("M"), "protocol.M")
    if summary["attempted_runs"] != summary["graph_count"] * M:
        raise ValueError("attempted_runs does not equal graph_count * protocol.M")
    expected_optimizations = 0
    for graph in [*summary["sources"], *summary["null_graphs"]]:
        graph = _require_mapping(graph, "graph summary")
        rungs = _require_mapping(graph.get("rungs"), f"{graph.get('id')}.rungs")
        expected_optimizations += len(rungs) * M
    if summary["terminal_optimizations"] != expected_optimizations:
        raise ValueError("terminal_optimizations does not match summarized rung counts")


def _published_primary(source: Mapping[str, Any]) -> dict[str, Any]:
    rungs = _require_mapping(source.get("rungs"), f"{source.get('id')}.rungs")
    primary = _require_mapping(rungs.get("primary"), f"{source.get('id')}.rungs.primary")
    attempted = primary.get("M_attempted")
    if attempted is not None:
        _require_nonnegative_int(attempted, f"{source.get('id')}.M_attempted")

    if bool(source.get("exact_control")):
        control = primary.get("exact_target_control")
        if not isinstance(control, Mapping):
            return {
                "selection": "exact_target_control",
                "M_attempted": attempted,
                "M_accepted": None,
                "alpha": None,
                "alpha_wilson95": None,
                "nei": None,
                "bootstrap_percentile95": None,
                "status": "withheld",
                "reason": "exact_target_control summary missing",
            }
        return {
            "selection": "exact_target_control",
            "definition": "numerical admissibility AND prespecified target-fit acceptance",
            "M_attempted": attempted,
            "M_accepted": control.get("M_accepted"),
            "alpha": control.get("alpha_control"),
            "alpha_wilson95": control.get("alpha_control_wilson95"),
            "target_fit_rejections": control.get("target_fit_rejections"),
            "nei": control.get("nei"),
            "bootstrap_percentile95": control.get("bootstrap_percentile95"),
            "status": "reported" if control.get("nei") is not None else "undefined",
            "reason": control.get("reason"),
        }

    return {
        "selection": "primary_numerically_admissible",
        "definition": "conditional law after the declared numerical admissibility gate",
        "M_attempted": attempted,
        "M_accepted": primary.get("M_accepted"),
        "alpha": primary.get("alpha"),
        "alpha_wilson95": primary.get("alpha_wilson95"),
        "nei": primary.get("nei"),
        "bootstrap_percentile95": primary.get("bootstrap_percentile95"),
        "status": "reported" if primary.get("nei") is not None else "undefined",
        "reason": primary.get("reason"),
    }


def _sanitize_source(source: Mapping[str, Any]) -> dict[str, Any]:
    """Whitelist non-null summary fields and add the public primary estimand."""

    allowed = (
        "id",
        "label",
        "kind",
        "n",
        "m",
        "exact_control",
        "null_anchor",
        "S_delta",
        "s_delta",
        "D2",
        "graph_sha256",
        "rungs",
        "recurrence",
        "rarefaction",
        "batch_estimates",
        "gate_sensitivity",
        "paired_rung_contrasts",
        "raw_smacof_nei_ungated",
        "rho_D_max_accepted",
        "preprocessing",
    )
    result = {key: _copy_json(source[key]) for key in allowed if key in source}
    if bool(source.get("exact_control")):
        # Preserve the summarizer output verbatim for the A_num/A_ctrl
        # distinction.  Only published_primary below selects the calibration
        # estimand; auxiliary source summaries remain explicitly labeled A_num.
        result["auxiliary_summary_selection"] = (
            "A_num (numerical admissibility), NOT A_ctrl (exact-target fit)"
        )
        result["exact_control_summary_note"] = (
            "Top-level rung NEI, recurrence, rarefaction, batch and paired-rung "
            "summaries use A_num. Calibration reporting uses exact_target_control (A_ctrl)."
        )
    provenance = source.get("source")
    if provenance is not None:
        provenance = _require_mapping(provenance, f"{source.get('id')}.source")
        result["source"] = {
            key: _copy_json(provenance[key])
            for key in ("id", "source_sha256", "weighted", "expected_n", "expected_e")
            if key in provenance
        }
    result["published_primary"] = _published_primary(source)
    return result


def _publish_contrast(row: Mapping[str, Any]) -> dict[str, Any]:
    published = _copy_json(dict(row))
    count_keys = ("generated_graphs", "estimable_graphs", "requested_graphs")
    counts_defined = all(
        isinstance(row.get(key), int) and not isinstance(row.get(key), bool)
        for key in count_keys
    )
    complete = (
        counts_defined
        and row["generated_graphs"] == row["requested_graphs"]
        and row["estimable_graphs"] == row["requested_graphs"]
        and row.get("complete_requested_ensemble") is True
    )
    inferential_fields_present = (
        row.get("contrast") is not None
        and row.get("outer_graph_percentile95") is not None
        and row.get("nested_resampling95_sensitivity") is not None
    )
    if not complete or not inferential_fields_present:
        for key in WITHHELD_FIELDS:
            published[key] = None
        published["publication_status"] = "withheld"
        if not counts_defined:
            reason = "null realization counts undefined"
        elif not complete:
            reason = (
                "incomplete requested null ensemble or at least one null graph has undefined NEI; "
                "selected-null mean and contrast withheld"
            )
        else:
            reason = "anchor/interval undefined under the declared finite-M analysis"
        published["withheld_reason"] = reason
    else:
        published["publication_status"] = "reported"
        published.pop("selection_warning", None)
    published["p_value"] = None
    return published


def _sanitize_failure(record: Mapping[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    safe = {
        "status": record.get("status"),
        "reason": record.get("reason"),
        "anchor_id": record.get("anchor_id"),
        "ensemble": record.get("ensemble"),
        "attribution_status": (
            "reported"
            if record.get("anchor_id") is not None and record.get("ensemble") is not None
            else "unavailable: summarizer did not preserve failure filename/anchor/ensemble"
        ),
    }
    if isinstance(metadata, Mapping):
        keys = (
            "method_version",
            "method",
            "n",
            "m",
            "requested_samples",
            "completed_samples",
            "failed_sample_index",
            "max_attempts_per_sample",
            "attempted",
            "rejected_disconnected",
            "largest_component_substitution_used",
        )
        safe["metadata"] = {
            key: _copy_json(metadata[key]) for key in keys if key in metadata
        }
    return safe


def _null_meta_group_from_name(name: str) -> tuple[str, str] | None:
    match = re.match(r"^(.*)--(degree_long|degree|gnm)-\d+\.json$", name)
    return (match.group(1), match.group(2)) if match else None


def _null_diagnostics(
    study: Path,
    null_graphs: list[Mapping[str, Any]],
    published_contrasts: list[Mapping[str, Any]],
    null_design: Mapping[str, Any],
) -> dict[str, Any]:
    metadata_groups: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    directory = study / "null_meta"
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            if path.name.endswith("failed.json"):
                continue
            group = _null_meta_group_from_name(path.name)
            if group is None:
                continue
            value = _read_json(path)
            if isinstance(value, Mapping):
                metadata_groups.setdefault(group, []).append(value)

    graph_groups: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for graph in null_graphs:
        anchor = graph.get("anchor_id")
        ensemble = graph.get("ensemble")
        if isinstance(anchor, str) and isinstance(ensemble, str):
            graph_groups.setdefault((anchor, ensemble), []).append(graph)

    requested_by_ensemble = {
        "degree": null_design.get("B_degree"),
        "degree_long": null_design.get("B_degree_long"),
        "gnm": null_design.get("B_gnm"),
    }
    groups = []
    for key in sorted(set(metadata_groups) | set(graph_groups)):
        anchor, ensemble = key
        metas = metadata_groups.get(key, [])
        graphs = graph_groups.get(key, [])
        attempted = [meta.get("attempted") for meta in metas]
        accepted = [meta.get("accepted") for meta in metas]
        rates = [meta.get("acceptance_rate") for meta in metas]
        overlaps = []
        for meta in metas:
            for sample in meta.get("sample_records", []):
                if isinstance(sample, Mapping) and "edge_overlap_fraction" in sample:
                    overlaps.append(sample.get("edge_overlap_fraction"))
        duplicate_count = sum(bool(graph.get("duplicate_of_input")) for graph in graphs)
        requested = requested_by_ensemble.get(ensemble)
        generated = len(graphs)
        groups.append(
            {
                "anchor_id": anchor,
                "ensemble": ensemble,
                "requested_graphs": requested,
                "generated_graphs": generated,
                "complete_requested_ensemble": (
                    isinstance(requested, int) and generated == requested
                ),
                "metadata_records": len(metas),
                "attempted_moves_or_draws_sum": (
                    int(sum(value for value in attempted if isinstance(value, int)))
                    if attempted
                    else None
                ),
                "accepted_moves_or_draws_sum": (
                    int(sum(value for value in accepted if isinstance(value, int)))
                    if accepted
                    else None
                ),
                "accepted_per_record_min_median_max": _quantiles(accepted),
                "acceptance_rate_min_median_max": _quantiles(rates),
                "final_edge_overlap_min_median_max": _quantiles(overlaps),
                "duplicate_of_input_count": duplicate_count,
                "duplicate_of_input_fraction": (
                    duplicate_count / generated if generated else None
                ),
                "diagnostic_scope": (
                    "finite-time trace only; stationarity, reachability and uniform mixing not certified"
                    if ensemble.startswith("degree")
                    else "independent exact G(n,m) proposals retained conditional on connectivity"
                ),
            }
        )

    by_key = {
        (row.get("anchor_id"), row.get("ensemble")): row
        for row in published_contrasts
    }
    burnin = []
    anchors = sorted(
        anchor
        for anchor, ensemble in by_key
        if isinstance(anchor, str) and ensemble == "degree"
    )
    for anchor in anchors:
        ordinary = by_key.get((anchor, "degree"), {})
        long = by_key.get((anchor, "degree_long"), {})
        usable = (
            ordinary.get("publication_status") == "reported"
            and long.get("publication_status") == "reported"
        )
        burnin.append(
            {
                "anchor_id": anchor,
                "degree_contrast": ordinary.get("contrast") if usable else None,
                "degree_long_contrast": long.get("contrast") if usable else None,
                "degree_long_minus_degree": (
                    long["contrast"] - ordinary["contrast"] if usable else None
                ),
                "status": "descriptive" if usable else "withheld",
                "note": (
                    "comparison of two declared finite-time kernels; not a mixing certificate"
                ),
            }
        )

    gnm_contrasts = [
        row for row in published_contrasts if row.get("ensemble") == "gnm"
    ]
    return {
        "groups": groups,
        "burnin_sensitivity": burnin,
        "finite_time_degree_mixing_certified": False,
        "gnm_incomplete_any_anchor": (
            not gnm_contrasts
            or any(row.get("publication_status") != "reported" for row in gnm_contrasts)
        ),
        "trace_interpretation": (
            "Edge overlap, accepted attempts, triangles and assortativity are diagnostics; "
            "they do not certify finite-time uniformity or state-space mixing."
        ),
    }


def _execution_hashes(summary: Mapping[str, Any], study: Path) -> dict[str, Any]:
    execution = _require_mapping(summary["execution"], "execution")
    result = {
        "config_sha256": summary["config_sha256"],
        "scientific_code_sha256": _copy_json(execution.get("code_sha256", {})),
    }
    execution_path = study / "execution.json"
    summary_path = study / "summary.json"
    if execution_path.exists():
        result["execution_record_sha256"] = _sha256(execution_path)
    if summary_path.exists():
        result["input_summary_sha256"] = _sha256(summary_path)
    publisher_path = Path(__file__).resolve()
    summarizer_path = publisher_path.with_name("summarize_corrected_study.py")
    result["publisher_sha256"] = _sha256(publisher_path)
    if summarizer_path.exists():
        result["summarizer_sha256"] = _sha256(summarizer_path)
    return result


def build_public_payload(summary: Mapping[str, Any], study: Path) -> dict[str, Any]:
    _validate_summary(summary)
    sources = [_sanitize_source(_require_mapping(row, "source row")) for row in summary["sources"]]
    contrasts = [
        _publish_contrast(_require_mapping(row, "graph contrast row"))
        for row in summary["graph_contrasts"]
    ]
    null_design = _copy_json(summary["null_design"])
    payload = {
        "schema_version": PUBLIC_SCHEMA_VERSION,
        "study_id": summary["study_id"],
        "status": summary["status"],
        "counts": {
            "graphs": summary["graph_count"],
            "attempted_runs": summary["attempted_runs"],
            "terminal_optimizations": summary["terminal_optimizations"],
        },
        "config_sha256": summary["config_sha256"],
        "protocol": _copy_json(summary["protocol"]),
        "null_design": null_design,
        "sources": sources,
        "graph_contrasts": contrasts,
        "null_generation_failures": [
            _sanitize_failure(_require_mapping(row, "null failure row"))
            for row in summary["null_generation_failures"]
        ],
        "interpretation_limits": _copy_json(summary["interpretation_limits"])
        + [
            "This payload contains newly calculated corrected-study summaries only. Legacy values are neither pooled nor silently replaced.",
            "Exact-target controls use target-fit acceptance in addition to the numerical gate.",
            "A missing or undefined requested null realization causes the selected-null mean, contrast and intervals to be withheld.",
            "Graph contrasts are exploratory and not multiplicity-adjusted; bootstrap intervals are not confirmatory tests.",
            "No prespecified numerical equivalence margin in this bounded run: tolerance equality is descriptive, not an equivalence-test verdict.",
        ],
        "outstanding": _copy_json(summary["outstanding"]),
        "scope": _copy_json(summary["scope"]),
        "execution_hashes": _execution_hashes(summary, study),
    }
    payload["null_diagnostics_summary"] = _null_diagnostics(
        study,
        [_require_mapping(row, "null graph row") for row in summary["null_graphs"]],
        contrasts,
        _require_mapping(summary["null_design"], "null_design"),
    )
    audit_path = study / "artifact_audit.json"
    if audit_path.exists():
        audit = _read_json(audit_path)
        if audit.get("config_sha256") != summary["config_sha256"] or audit.get("status") != "pass":
            raise ValueError("artifact audit does not certify this frozen protocol")
        payload["artifact_audit"] = _copy_json(audit)
    validate_public_payload(payload)
    return payload


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def validate_public_payload(payload: Mapping[str, Any]) -> None:
    required = {
        "study_id",
        "status",
        "counts",
        "config_sha256",
        "protocol",
        "null_design",
        "sources",
        "graph_contrasts",
        "null_generation_failures",
        "interpretation_limits",
        "outstanding",
        "execution_hashes",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"public payload missing keys: {', '.join(missing)}")
    counts = _require_mapping(payload["counts"], "counts")
    for key in ("graphs", "attempted_runs", "terminal_optimizations"):
        _require_nonnegative_int(counts.get(key), f"counts.{key}")
    for path, value in _walk(payload):
        leaf = path.rsplit(".", 1)[-1].lower()
        if any(part in leaf for part in FORBIDDEN_KEY_PARTS):
            raise ValueError(f"forbidden public field: {path}")
        if isinstance(value, str) and LOCAL_PATH_PATTERN.search(value):
            raise ValueError(f"local path leaked into public payload: {path}")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"nonfinite public number: {path}")
    for source in payload["sources"]:
        if bool(source.get("exact_control")):
            selected = source.get("published_primary", {})
            if selected.get("selection") != "exact_target_control":
                raise ValueError("exact control published from numerical gate alone")
    for row in payload["graph_contrasts"]:
        if row.get("publication_status") == "withheld":
            if any(row.get(key) is not None for key in WITHHELD_FIELDS):
                raise ValueError("withheld contrast retains selected-null statistics")
    json.dumps(payload, ensure_ascii=False, allow_nan=False)


def _fmt(value: Any, digits: int = 4) -> str:
    number = _finite_or_none(value)
    if number is None:
        return "—"
    if number == 0:
        return "0"
    if abs(number) < 1e-3 or abs(number) >= 1e4:
        return f"{number:.{digits - 1}e}"
    return f"{number:.{digits}g}"


def _fmt_interval(value: Any) -> str:
    if not isinstance(value, list) or len(value) != 2:
        return "—"
    return f"[{_fmt(value[0])}, {_fmt(value[1])}]"


def _as_lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def render_report(payload: Mapping[str, Any]) -> str:
    counts = payload["counts"]
    protocol = payload["protocol"]
    lines = [
        "# Corrected bounded study — evidence report",
        "",
        f"- Study ID: `{payload['study_id']}`",
        f"- Status: {payload['status']}",
        f"- Config SHA-256: `{payload['config_sha256']}`",
        f"- Graphs: {counts['graphs']}",
        f"- Attempted run vectors: {counts['attempted_runs']}",
        f"- Terminal optimizations: {counts['terminal_optimizations']}",
        "",
        "> 이 문서의 값은 corrected implementation에서 새로 계산한 bounded-study summary. "
        "Legacy table과의 pooling·자동 대체·연속성 가정 없음.",
        "",
        "## 1. Declared protocol",
        "",
        f"1. Target dimension: $p={protocol.get('p', '—')}$.",
        f"2. Attempted initializations per graph: $M={protocol.get('M', '—')}$; "
        f"independent batches: {protocol.get('independent_batches', '—')}.",
        f"3. Initialization: {protocol.get('initialization', '—')}.",
        f"4. Numerical acceptance: {protocol.get('policy', '—')}.",
        f"5. Exact-target control acceptance: {protocol.get('control_policy', '—')}.",
        "6. Reported interval: whole-run percentile bootstrap 95% summary; exact coverage, "
        "unseen-class correction 및 small-sample guarantee 없음.",
        "",
        "## 2. Source-level primary estimates",
        "",
        r"Exact-target control의 $M_{\rm accept}$와 $\mathcal I_{\rm primary}$는 "
        "numerical gate만이 아니라 `exact_target_control`에서 선택. 나머지는 declared "
        "numerically admissible conditional law에서 선택.",
        "Exact-control source의 원래 rung·recurrence·rarefaction·batch·paired-rung "
        "summary는 A_num auxiliary diagnostics로 원값 보존; calibration 판정과 표의 "
        "primary estimate는 A_ctrl만 사용.",
        "",
        r"| source | kind | $N$ | $E$ | selection | $M_{\rm accept}/M$ | $\alpha$ | $\mathcal I_{\rm primary}$ | bootstrap 95% |",
        "|---|---|---:|---:|---|---:|---:|---:|---|",
    ]
    for source in payload["sources"]:
        selected = source["published_primary"]
        accepted = selected.get("M_accepted")
        attempted = selected.get("M_attempted")
        count = f"{accepted}/{attempted}" if accepted is not None and attempted is not None else "—"
        lines.append(
            "| {label} | {kind} | {n} | {m} | `{selection}` | {count} | {alpha} | {nei} | {interval} |".format(
                label=source.get("label", source.get("id", "—")),
                kind=source.get("kind", "—"),
                n=source.get("n", "—"),
                m=source.get("m", "—"),
                selection=selected.get("selection", "—"),
                count=count,
                alpha=_fmt(selected.get("alpha")),
                nei=_fmt(selected.get("nei")),
                interval=_fmt_interval(selected.get("bootstrap_percentile95")),
            )
        )

    lines.extend(
        [
            "",
            "## 3. Graph-realization null contrasts",
            "",
            r"Contrast definition: $\delta_g=\widehat{\mathcal I}_g-"
            r"\overline{\widehat{\mathcal I}}_{g,{\rm null}}$. Graph realization은 outer unit, "
            "restart vector는 within-graph unit. Requested null graph 중 생성 실패 또는 undefined "
            "NEI가 하나라도 존재하면 selected-null mean, contrast와 interval 전부 withheld.",
            "Outer interval은 anchor point estimate를 고정한 null-graph-only resampling. "
            "Nested sensitivity는 anchor run, null graph와 within-null run resampling을 함께 포함. "
            "두 interval은 uncertainty의 범위가 다르며 confirmatory test 또는 multiplicity-adjusted interval이 아님.",
            "",
            r"| anchor | ensemble | estimable/requested | status | anchor $\mathcal I$ | null mean | $\delta_g$ | outer 95% | nested 95% sensitivity |",
            "|---|---|---:|---|---:|---:|---:|---|---|",
        ]
    )
    for row in payload["graph_contrasts"]:
        estimable = row.get("estimable_graphs")
        requested = row.get("requested_graphs")
        count = f"{estimable}/{requested}" if estimable is not None and requested is not None else "—"
        lines.append(
            "| {anchor} | {ensemble} | {count} | {status} | {anchor_nei} | {null_mean} | {contrast} | {outer} | {nested} |".format(
                anchor=row.get("anchor_id", "—"),
                ensemble=row.get("ensemble", "—"),
                count=count,
                status=row.get("publication_status", "—"),
                anchor_nei=_fmt(row.get("anchor_nei")),
                null_mean=_fmt(row.get("null_nei_mean")),
                contrast=_fmt(row.get("contrast")),
                outer=_fmt_interval(row.get("outer_graph_percentile95")),
                nested=_fmt_interval(row.get("nested_resampling95_sensitivity")),
            )
        )

    diagnostics = payload["null_diagnostics_summary"]
    lines.extend(
        [
            "",
            "## 4. Null-generation diagnostics",
            "",
            "Degree-preserving null의 edge overlap·accepted attempts·triangle·assortativity trace는 "
            "finite-time diagnostic. Stationarity, reachability 및 uniform mixing의 certificate 아님.",
            f"Connected G(n,m) incomplete anchor 존재: "
            f"`{str(diagnostics['gnm_incomplete_any_anchor']).lower()}`.",
            "",
            "| anchor | ensemble | generated/requested | accepted attempts/draws | acceptance rate | final edge overlap | duplicate-input fraction |",
            "|---|---|---:|---:|---|---|---:|",
        ]
    )
    for group in diagnostics["groups"]:
        generated = group.get("generated_graphs")
        requested = group.get("requested_graphs")
        count = f"{generated}/{requested}" if requested is not None else str(generated)
        lines.append(
            "| {anchor} | {ensemble} | {count} | {accepted} | {rate} | {overlap} | {duplicate} |".format(
                anchor=group.get("anchor_id", "—"),
                ensemble=group.get("ensemble", "—"),
                count=count,
                accepted=group.get("accepted_moves_or_draws_sum", "—"),
                rate=(
                    "/".join(_fmt(value) for value in group["acceptance_rate_min_median_max"])
                    if group.get("acceptance_rate_min_median_max")
                    else "—"
                ),
                overlap=(
                    "/".join(_fmt(value) for value in group["final_edge_overlap_min_median_max"])
                    if group.get("final_edge_overlap_min_median_max")
                    else "—"
                ),
                duplicate=_fmt(group.get("duplicate_of_input_fraction")),
            )
        )

    lines.extend(["", "### 4.1 Burn-in-length sensitivity", ""])
    for row in diagnostics["burnin_sensitivity"]:
        lines.append(
            "- `{anchor}`: degree-long minus degree contrast = {difference}; status = `{status}`. "
            "Descriptive finite-time-kernel comparison, mixing certificate 아님.".format(
                anchor=row["anchor_id"],
                difference=_fmt(row.get("degree_long_minus_degree")),
                status=row["status"],
            )
        )
    if not diagnostics["burnin_sensitivity"]:
        lines.append("- Available paired degree/degree-long summary 없음.")

    lines.extend(["", "## 5. Null-generation failures", ""])
    failures = payload["null_generation_failures"]
    if failures:
        for failure in failures:
            meta = failure.get("metadata", {})
            lines.append(
                f"- `{failure.get('status', 'failure')}`: {failure.get('reason', 'reason unavailable')} "
                f"(completed/requested={meta.get('completed_samples', '—')}/"
                f"{meta.get('requested_samples', '—')}; attribution="
                f"{failure.get('attribution_status', 'unavailable')})."
            )
    else:
        lines.append("- Recorded null-generation failure 없음.")

    lines.extend(["", "## 6. Interpretation limits", ""])
    for item in payload["interpretation_limits"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 7. Outstanding", ""])
    for item in _as_lines(payload["outstanding"]):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 8. Provenance",
            "",
            f"- Input summary SHA-256: `{payload['execution_hashes'].get('input_summary_sha256', 'unavailable')}`",
            f"- Execution record SHA-256: `{payload['execution_hashes'].get('execution_record_sha256', 'unavailable')}`",
            "- Raw source paths, raw coordinates, terminal coordinates 및 graph edge lists: public payload 미포함.",
            "",
        ]
    )
    return "\n".join(lines)


def _self_test() -> None:
    digest = "a" * 64
    primary = {
        "M_attempted": 4,
        "M_accepted": 3,
        "alpha": 0.75,
        "alpha_wilson95": [0.3, 0.95],
        "nei": 0.1,
        "bootstrap_percentile95": [0.05, 0.15],
        "exact_target_control": {
            "M_accepted": 2,
            "nei": 1e-12,
            "bootstrap_percentile95": [0.0, 2e-12],
            "alpha_control": 0.5,
            "alpha_control_wilson95": [0.15, 0.85],
            "target_fit_rejections": 1,
        },
    }
    source = {
        "id": "path",
        "label": "Path control",
        "kind": "synthetic",
        "n": 4,
        "m": 3,
        "exact_control": True,
        "null_anchor": False,
        "rungs": {"primary": primary},
    }
    real = {
        "id": "real",
        "label": "Real graph",
        "kind": "real",
        "n": 5,
        "m": 6,
        "exact_control": False,
        "null_anchor": True,
        "rungs": {"primary": {key: value for key, value in primary.items() if key != "exact_target_control"}},
        "source": {"id": "real", "source_sha256": "b" * 64, "weighted": False, "expected_n": 5, "expected_e": 6},
        "preprocessing": {"columns_used": [0, 1], "weight": None},
    }
    incomplete = {
        "anchor_id": "real",
        "ensemble": "gnm",
        "generated_graphs": 1,
        "estimable_graphs": 1,
        "requested_graphs": 2,
        "complete_requested_ensemble": False,
        "anchor_nei": 0.1,
        "anchor_alpha": 0.75,
        "null_nei_mean": 0.2,
        "null_nei_sd_between_graph_estimates": None,
        "contrast": -0.1,
        "outer_graph_percentile95": [-0.2, 0.0],
        "nested_resampling95_sensitivity": [-0.2, 0.0],
        "p_value": None,
    }
    summary = {
        "study_id": "synthetic-publisher-test",
        "status": "complete",
        "config_sha256": digest,
        "execution": {"code_sha256": {"runner.py": "c" * 64}},
        "protocol": {"p": 2, "M": 4, "independent_batches": 2, "initialization": "fixed", "policy": "declared", "control_policy": "target fit"},
        "null_design": {"B_degree": 0, "B_degree_long": 0, "B_gnm": 2, "uniform_mixing_certified": False},
        "graph_count": 3,
        "attempted_runs": 12,
        "terminal_optimizations": 12,
        "sources": [source, real],
        "null_graphs": [{
            "id": "real--gnm-000",
            "anchor_id": "real",
            "ensemble": "gnm",
            "duplicate_of_input": False,
            "rungs": {"primary": primary},
        }],
        "graph_contrasts": [incomplete],
        "null_generation_failures": [],
        "scope": "synthetic test",
        "outstanding": "none",
        "interpretation_limits": ["test only"],
    }
    with tempfile.TemporaryDirectory() as directory_name:
        directory = Path(directory_name)
        summary["execution"]["config_sha256"] = digest
        (directory / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False), encoding="utf-8"
        )
        (directory / "execution.json").write_text(
            json.dumps(summary["execution"]), encoding="utf-8"
        )
        payload = build_public_payload(summary, directory)
        assert payload["sources"][0]["published_primary"]["nei"] == 1e-12
        assert payload["sources"][0]["rungs"]["primary"]["nei"] == 0.1
        assert payload["sources"][0]["auxiliary_summary_selection"].startswith("A_num")
        assert payload["graph_contrasts"][0]["publication_status"] == "withheld"
        assert payload["graph_contrasts"][0]["contrast"] is None
        report = render_report(payload)
        assert "exact_target_control" in report
        validate_public_payload(payload)
        _atomic_json(directory / "public.json", payload)
        _atomic_text(directory / "report.md", report)
        validate_public_payload(_read_json(directory / "public.json"))
    print("SELF-TEST OK: schema, exact-control selection, withholding and privacy guard")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path, nargs="?", help="completed local study directory")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "corrected-study.json",
        help="public JSON payload",
    )
    parser.add_argument("--report", type=Path, default=None, help="Markdown report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if args.study is None:
        parser.error("STUDY is required unless --self-test is used")
    summary_path = args.study / "summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"missing summarized study: {summary_path}")
    summary = _require_mapping(_read_json(summary_path), "summary.json")
    payload = build_public_payload(summary, args.study)
    report_path = args.report or (args.study / "report.md")
    _atomic_json(args.output, payload)
    _atomic_text(report_path, render_report(payload))
    print(
        f"PUBLISHED study={payload['study_id']} sources={len(payload['sources'])} "
        f"contrasts={len(payload['graph_contrasts'])} withheld="
        f"{sum(row['publication_status']=='withheld' for row in payload['graph_contrasts'])}"
    )


if __name__ == "__main__":
    main()
