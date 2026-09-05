#!/usr/bin/env python3
"""Connected graph-null generators with explicit finite-run provenance.

degree_preserving_connected_null implements a rejection-lazy, symmetric
double-edge-switch Markov chain on connected simple labeled graphs with the
input degree sequence. Every clock tick is counted, including deliberate holds
and invalid proposals. Symmetry makes the Metropolis ratio one for an
admissible switch, but neither reachability nor finite-run mixing is certified.

connected_gnm_null generates independent exact G(n,m) draws and retains only
connected draws. Exceeding the declared attempt cap raises an error. A largest
connected component is never substituted because that changes N, E, and the
sampling law.

Both functions return {"graphs": [...], "metadata": {...}}. The save helper
writes an audit-oriented JSON representation of edge sets and metadata.
"""

from __future__ import annotations

from collections import Counter
import json
import math
import numbers
from pathlib import Path
import random
from typing import Any, Hashable, Mapping
import warnings

import networkx as nx


METHOD_VERSION = "graph-null-ensemble/v1"
_REJECTION_REASONS = (
    "lazy_hold",
    "insufficient_edges",
    "self_loop",
    "duplicate_candidate",
    "no_change",
    "multiedge",
    "disconnected",
)


class ConnectedGnmSamplingError(RuntimeError):
    """Connected G(n,m) rejection sampling exceeded its declared cap."""

    def __init__(self, message: str, *, metadata: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.metadata = dict(metadata)


def _require_int(name: str, value: Any, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise TypeError(f"{name} must be an integer")
    result = int(value)
    if result < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return result


def _require_seed(seed: Any) -> int:
    if isinstance(seed, bool) or not isinstance(seed, numbers.Integral):
        raise TypeError("seed must be an explicitly declared integer")
    return int(seed)


def _as_simple_connected_unweighted(graph: nx.Graph) -> nx.Graph:
    """Validate the conditioning event and return an edge-attribute-free copy."""

    if graph.is_directed():
        raise TypeError("graph must be undirected")
    if graph.is_multigraph():
        raise TypeError("graph must be simple, not a MultiGraph")
    if graph.number_of_nodes() < 1:
        raise ValueError("graph must contain at least one node")
    if nx.number_of_selfloops(graph):
        raise ValueError("graph must not contain self-loops")
    if not nx.is_connected(graph):
        raise ValueError(
            "graph must already be connected; largest-component replacement "
            "would define a different null problem"
        )
    for _, _, data in graph.edges(data=True):
        if "weight" in data and float(data["weight"]) != 1.0:
            raise ValueError("degree-preserving null requires an unweighted graph")

    clean = nx.Graph()
    clean.graph.update(graph.graph)
    clean.add_nodes_from((node, dict(data)) for node, data in graph.nodes(data=True))
    clean.add_edges_from(graph.edges())
    return clean


def _ranked_edge(
    u: Hashable, v: Hashable, node_rank: Mapping[Hashable, int]
) -> tuple[Hashable, Hashable]:
    return (u, v) if node_rank[u] < node_rank[v] else (v, u)


def _ranked_edges(
    graph: nx.Graph, node_rank: Mapping[Hashable, int]
) -> list[tuple[Hashable, Hashable]]:
    return sorted(
        (_ranked_edge(u, v, node_rank) for u, v in graph.edges()),
        key=lambda edge: (node_rank[edge[0]], node_rank[edge[1]]),
    )


def _edge_frozensets(graph: nx.Graph) -> set[frozenset[Hashable]]:
    return {frozenset((u, v)) for u, v in graph.edges()}


def edge_overlap_fraction(reference: nx.Graph, graph: nx.Graph) -> float:
    """Return |E(reference) intersection E(graph)| / |E(reference)|."""

    reference_edges = _edge_frozensets(reference)
    candidate_edges = _edge_frozensets(graph)
    if not reference_edges:
        return 1.0 if not candidate_edges else 0.0
    return len(reference_edges & candidate_edges) / len(reference_edges)


def _degree_assortativity_or_none(graph: nx.Graph) -> float | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            value = float(nx.degree_assortativity_coefficient(graph))
        except (FloatingPointError, ZeroDivisionError):
            return None
    return value if math.isfinite(value) else None


def graph_diagnostics(
    graph: nx.Graph, *, reference: nx.Graph | None = None
) -> dict[str, Any]:
    """Return edge overlap, triangle count, and assortativity diagnostics."""

    triangles = sum(nx.triangles(graph).values()) // 3
    result: dict[str, Any] = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "connected": bool(nx.is_connected(graph)),
        "triangles": int(triangles),
        "degree_assortativity": _degree_assortativity_or_none(graph),
    }
    if reference is not None:
        result["edge_overlap_fraction"] = edge_overlap_fraction(reference, graph)
    return result


def _attempt_connected_switch(
    graph: nx.Graph,
    *,
    edges: list[tuple[Hashable, Hashable]],
    rng: random.Random,
    node_rank: Mapping[Hashable, int],
    hold_probability: float,
) -> tuple[bool, str | None]:
    """Perform one attempted symmetric switch; rejection retains the state."""

    if rng.random() < hold_probability:
        return False, "lazy_hold"

    if len(edges) < 2:
        return False, "insufficient_edges"
    left_index, right_index = sorted(rng.sample(range(len(edges)), 2))
    (a, b), (c, d) = edges[left_index], edges[right_index]

    if rng.randrange(2) == 0:
        raw_candidates = ((a, c), (b, d))
    else:
        raw_candidates = ((a, d), (b, c))
    if any(u == v for u, v in raw_candidates):
        return False, "self_loop"
    candidates = tuple(
        _ranked_edge(u, v, node_rank) for u, v in raw_candidates
    )
    if candidates[0] == candidates[1]:
        return False, "duplicate_candidate"

    old_edges = (edges[left_index], edges[right_index])
    if frozenset(candidates) == frozenset(old_edges):
        return False, "no_change"

    graph.remove_edges_from(old_edges)
    if any(graph.has_edge(u, v) for u, v in candidates):
        graph.add_edges_from(old_edges)
        return False, "multiedge"
    graph.add_edges_from(candidates)
    if not nx.is_connected(graph):
        graph.remove_edges_from(candidates)
        graph.add_edges_from(old_edges)
        return False, "disconnected"
    # Keep a persistent uniform edge-index table. Its order is immaterial:
    # choosing two distinct indices samples an unordered edge pair uniformly.
    edges[left_index], edges[right_index] = candidates
    return True, None


def degree_preserving_connected_null(
    graph: nx.Graph,
    *,
    n_samples: int,
    burnin_attempts: int,
    thinning_attempts: int,
    seed: int,
    trace_every: int = 100,
    hold_probability: float = 0.5,
) -> dict[str, Any]:
    """Sample a finite-time connected degree-preserving switch chain.

    The first sample is recorded immediately after burn-in; later samples
    follow the declared number of attempted clock ticks. Trace quantities are
    diagnostics only, not mixing or finite-run uniformity certificates.
    """

    n_samples = _require_int("n_samples", n_samples, minimum=1)
    burnin_attempts = _require_int("burnin_attempts", burnin_attempts, minimum=0)
    thinning_attempts = _require_int(
        "thinning_attempts", thinning_attempts, minimum=0
    )
    trace_every = _require_int("trace_every", trace_every, minimum=1)
    seed = _require_seed(seed)
    if not isinstance(hold_probability, numbers.Real):
        raise TypeError("hold_probability must be a real number")
    hold_probability = float(hold_probability)
    if not 0.0 <= hold_probability < 1.0:
        raise ValueError("hold_probability must lie in [0,1)")

    work = _as_simple_connected_unweighted(graph)
    reference = work.copy()
    node_rank = {node: index for index, node in enumerate(work.nodes())}
    edges = _ranked_edges(work, node_rank)
    reference_degrees = dict(reference.degree())
    rng = random.Random(seed)
    attempted = 0
    accepted = 0
    rejection_counts: Counter[str] = Counter()
    trace: list[dict[str, Any]] = []

    def record_trace(event: str) -> None:
        diagnostic = {
            "attempt": attempted,
            "accepted_moves": accepted,
            "event": event,
            **graph_diagnostics(work, reference=reference),
        }
        if trace and trace[-1]["attempt"] == attempted:
            previous = trace[-1]
            if "events" in previous:
                previous["events"].append(event)
            else:
                previous["events"] = [previous.pop("event"), event]
        else:
            trace.append(diagnostic)

    def advance(number_of_attempts: int) -> None:
        nonlocal attempted, accepted
        for _ in range(number_of_attempts):
            moved, reason = _attempt_connected_switch(
                work,
                edges=edges,
                rng=rng,
                node_rank=node_rank,
                hold_probability=hold_probability,
            )
            attempted += 1
            if moved:
                accepted += 1
            else:
                if reason not in _REJECTION_REASONS:
                    raise AssertionError(f"unknown rejection reason: {reason}")
                rejection_counts[reason] += 1
            if attempted % trace_every == 0:
                record_trace("periodic")

    record_trace("initial")
    advance(burnin_attempts)
    record_trace("post_burnin")

    samples: list[nx.Graph] = []
    sample_records: list[dict[str, Any]] = []
    for sample_index in range(n_samples):
        if sample_index:
            advance(thinning_attempts)
        sample = work.copy()
        samples.append(sample)
        sample_records.append(
            {
                "sample_index": sample_index,
                "attempt": attempted,
                "accepted_moves": accepted,
                **graph_diagnostics(sample, reference=reference),
            }
        )
        record_trace(f"sample_{sample_index}")

    if dict(work.degree()) != reference_degrees:
        raise AssertionError("internal error: degree sequence changed")
    if len(edges) != work.number_of_edges() or set(edges) != set(
        _ranked_edges(work, node_rank)
    ):
        raise AssertionError("internal error: persistent edge table diverged")
    if not nx.is_connected(work):
        raise AssertionError("internal error: chain left the connected state space")

    rejected = attempted - accepted
    rejection_record = {
        reason: int(rejection_counts.get(reason, 0))
        for reason in _REJECTION_REASONS
    }
    if sum(rejection_record.values()) != rejected:
        raise AssertionError("internal error: attempted-move accounting mismatch")
    active_attempts = attempted - rejection_record["lazy_hold"]

    metadata = {
        "method_version": METHOD_VERSION,
        "method": "symmetric_rejection_lazy_connected_double_edge_switch_mh",
        "conditioning": {
            "simple": True,
            "unweighted": True,
            "connected": True,
            "degree_sequence_fixed": True,
            "labeled_nodes": True,
        },
        "seed": seed,
        "configuration": {
            "n_samples": n_samples,
            "burnin_attempts": burnin_attempts,
            "thinning_attempts": thinning_attempts,
            "trace_every_attempts": trace_every,
            "hold_probability": hold_probability,
            "first_sample": "immediately after burn-in",
        },
        "proposal": {
            "edge_pair": "uniform unordered pair of distinct present edges",
            "endpoint_pairing": "one of two alternative pairings with probability 1/2",
            "metropolis_probability_for_admissible_switch": 1.0,
            "invalid_or_disconnected_proposal": "retain current state",
        },
        "input": {
            **graph_diagnostics(reference),
            "degree_sequence": sorted(dict(reference.degree()).values()),
        },
        "attempted": attempted,
        "accepted": accepted,
        "rejected": rejected,
        "acceptance_rate": accepted / attempted if attempted else None,
        "active_proposal_acceptance_rate": (
            accepted / active_attempts if active_attempts else None
        ),
        "rejection_counts": rejection_record,
        "sample_records": sample_records,
        "mixing_diagnostics": {
            "trace": trace,
            "edge_overlap_definition": "|E_t intersection E_0| / |E_0|",
            "finite_run_uniformity_certified": False,
            "state_space_reachability_certified": False,
            "mixing_certified": False,
            "note": (
                "Burn-in, thinning, acceptance, edge-overlap, triangle, and "
                "assortativity traces are diagnostics, not proof of stationarity "
                "or finite-run uniformity."
            ),
        },
    }
    return {"graphs": samples, "metadata": metadata}


def connected_gnm_null(
    n: int,
    m: int,
    *,
    n_samples: int,
    seed: int,
    max_attempts_per_sample: int,
) -> dict[str, Any]:
    """Return independent exact G(n,m) draws conditioned on connectivity."""

    n = _require_int("n", n, minimum=1)
    m = _require_int("m", m, minimum=0)
    n_samples = _require_int("n_samples", n_samples, minimum=1)
    max_attempts_per_sample = _require_int(
        "max_attempts_per_sample", max_attempts_per_sample, minimum=1
    )
    seed = _require_seed(seed)
    maximum_edges = n * (n - 1) // 2
    if m > maximum_edges:
        raise ValueError(f"m must not exceed n(n-1)/2={maximum_edges}")
    if (n == 1 and m != 0) or (n > 1 and m < n - 1):
        raise ValueError("no connected simple graph exists for the declared n,m")

    rng = random.Random(seed)
    samples: list[nx.Graph] = []
    sample_records: list[dict[str, Any]] = []
    attempted = 0
    rejected_disconnected = 0

    for sample_index in range(n_samples):
        for within_sample_attempt in range(1, max_attempts_per_sample + 1):
            draw_seed = rng.randrange(0, 2**63)
            candidate = nx.gnm_random_graph(n, m, seed=draw_seed, directed=False)
            attempted += 1
            if nx.is_connected(candidate):
                samples.append(candidate)
                sample_records.append(
                    {
                        "sample_index": sample_index,
                        "attempts_for_sample": within_sample_attempt,
                        "cumulative_attempts": attempted,
                        "accepted_draw_seed": draw_seed,
                        **graph_diagnostics(candidate),
                    }
                )
                break
            rejected_disconnected += 1
        else:
            failure_metadata = {
                "method_version": METHOD_VERSION,
                "method": "independent_gnm_rejection_conditioned_connected",
                "n": n,
                "m": m,
                "seed": seed,
                "requested_samples": n_samples,
                "completed_samples": len(samples),
                "failed_sample_index": sample_index,
                "max_attempts_per_sample": max_attempts_per_sample,
                "attempted": attempted,
                "rejected_disconnected": rejected_disconnected,
                "largest_component_substitution_used": False,
            }
            raise ConnectedGnmSamplingError(
                "connected G(n,m) rejection sampler reached "
                f"max_attempts_per_sample={max_attempts_per_sample} at "
                f"sample_index={sample_index}; no largest-component substitute "
                "was returned",
                metadata=failure_metadata,
            )

    metadata = {
        "method_version": METHOD_VERSION,
        "method": "independent_gnm_rejection_conditioned_connected",
        "conditioning": {
            "simple": True,
            "unweighted": True,
            "connected": True,
            "n_fixed": n,
            "m_fixed": m,
        },
        "seed": seed,
        "configuration": {
            "n_samples": n_samples,
            "max_attempts_per_sample": max_attempts_per_sample,
        },
        "attempted": attempted,
        "accepted": n_samples,
        "rejected": rejected_disconnected,
        "acceptance_rate": n_samples / attempted,
        "rejection_counts": {"disconnected": rejected_disconnected},
        "sample_records": sample_records,
        "largest_component_substitution_used": False,
        "sampling_note": (
            "Each proposal is an exact G(n,m) draw. Retained samples have the "
            "G(n,m) law conditional on connectivity. The cap causes explicit "
            "failure rather than a change of graph size."
        ),
    }
    return {"graphs": samples, "metadata": metadata}


def _json_node_label(node: Hashable) -> dict[str, Any]:
    """Encode common immutable node labels without conflating their types."""

    if node is None:
        return {"type": "none", "value": None}
    if isinstance(node, bool):
        return {"type": "bool", "value": node}
    if isinstance(node, numbers.Integral):
        return {"type": "int", "value": int(node)}
    if isinstance(node, numbers.Real):
        value = float(node)
        if not math.isfinite(value):
            raise TypeError("nonfinite float node labels are not JSON serializable")
        return {"type": "float", "value": value}
    if isinstance(node, str):
        return {"type": "str", "value": node}
    if isinstance(node, tuple):
        return {"type": "tuple", "value": [_json_node_label(x) for x in node]}
    raise TypeError(
        "save_null_ensemble supports None/bool/int/finite-float/str/tuple "
        f"node labels, not {type(node).__name__}"
    )


def serialize_graph_edges(graph: nx.Graph) -> dict[str, Any]:
    """Create a deterministic node table and integer-indexed undirected edges."""

    encoded = [(_json_node_label(node), node) for node in graph.nodes()]
    encoded.sort(
        key=lambda item: json.dumps(
            item[0], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    )
    node_order = [node for _, node in encoded]
    node_index = {node: index for index, node in enumerate(node_order)}
    edges = sorted(
        (min(node_index[u], node_index[v]), max(node_index[u], node_index[v]))
        for u, v in graph.edges()
    )
    return {
        "nodes": [
            {"index": index, "label": label}
            for index, (label, _) in enumerate(encoded)
        ],
        "edges": [list(edge) for edge in edges],
    }


def null_ensemble_payload(result: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a result into an audit-oriented JSON payload."""

    graphs = result.get("graphs")
    metadata = result.get("metadata")
    if not isinstance(graphs, list) or not isinstance(metadata, Mapping):
        raise TypeError("result must contain list 'graphs' and mapping 'metadata'")
    if not all(isinstance(graph, nx.Graph) for graph in graphs):
        raise TypeError("every result graph must be a networkx Graph")
    return {
        "metadata": dict(metadata),
        "graphs": [
            {"sample_index": index, **serialize_graph_edges(graph)}
            for index, graph in enumerate(graphs)
        ],
    }


def save_null_ensemble(path: str | Path, result: Mapping[str, Any]) -> Path:
    """Write graph edges and metadata as strict JSON."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = null_ensemble_payload(result)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        handle.write("\n")
    return output


__all__ = [
    "ConnectedGnmSamplingError",
    "METHOD_VERSION",
    "connected_gnm_null",
    "degree_preserving_connected_null",
    "edge_overlap_fraction",
    "graph_diagnostics",
    "null_ensemble_payload",
    "save_null_ensemble",
    "serialize_graph_edges",
]
