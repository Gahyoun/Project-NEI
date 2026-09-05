#!/usr/bin/env python3
"""Deterministic, bounded tests for connected graph-null generators."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import networkx as nx

import graph_null_ensemble as nulls


def edge_signature(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(tuple(sorted(edge)) for edge in graph.edges()))


class DegreePreservingConnectedNullTest(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = nx.watts_strogatz_graph(14, 4, 0.25, seed=11)
        self.assertTrue(nx.is_connected(self.graph))

    def generate(self) -> dict:
        return nulls.degree_preserving_connected_null(
            self.graph,
            n_samples=4,
            burnin_attempts=80,
            thinning_attempts=30,
            seed=1729,
            trace_every=25,
        )

    def test_exact_invariants_and_input_immutability(self) -> None:
        input_edges = edge_signature(self.graph)
        input_degrees = dict(self.graph.degree())
        result = self.generate()

        self.assertEqual(edge_signature(self.graph), input_edges)
        for graph in result["graphs"]:
            self.assertIs(type(graph), nx.Graph)
            self.assertEqual(graph.number_of_nodes(), self.graph.number_of_nodes())
            self.assertEqual(graph.number_of_edges(), self.graph.number_of_edges())
            self.assertEqual(dict(graph.degree()), input_degrees)
            self.assertTrue(nx.is_connected(graph))
            self.assertEqual(nx.number_of_selfloops(graph), 0)
            self.assertTrue(all(not data for _, _, data in graph.edges(data=True)))

    def test_attempt_clock_accounting_and_diagnostic_scope(self) -> None:
        result = self.generate()
        metadata = result["metadata"]
        expected_attempts = 80 + 3 * 30
        self.assertEqual(metadata["attempted"], expected_attempts)
        self.assertEqual(
            metadata["attempted"],
            metadata["accepted"] + sum(metadata["rejection_counts"].values()),
        )
        self.assertEqual(metadata["rejected"], sum(metadata["rejection_counts"].values()))
        diagnostics = metadata["mixing_diagnostics"]
        self.assertFalse(diagnostics["finite_run_uniformity_certified"])
        self.assertFalse(diagnostics["mixing_certified"])
        self.assertFalse(diagnostics["state_space_reachability_certified"])
        trace = diagnostics["trace"]
        self.assertTrue(trace)
        for record in trace:
            self.assertIn("edge_overlap_fraction", record)
            self.assertIn("triangles", record)
            self.assertIn("degree_assortativity", record)
            self.assertLessEqual(record["attempt"], expected_attempts)

    def test_seed_reproducibility(self) -> None:
        first = self.generate()
        second = self.generate()
        self.assertEqual(
            [edge_signature(graph) for graph in first["graphs"]],
            [edge_signature(graph) for graph in second["graphs"]],
        )
        self.assertEqual(first["metadata"], second["metadata"])

    def test_zero_burnin_merges_same_clock_trace_events(self) -> None:
        result = nulls.degree_preserving_connected_null(
            self.graph,
            n_samples=1,
            burnin_attempts=0,
            thinning_attempts=0,
            seed=9,
            trace_every=1,
        )
        trace = result["metadata"]["mixing_diagnostics"]["trace"]
        self.assertEqual(len(trace), 1)
        self.assertEqual(
            trace[0]["events"], ["initial", "post_burnin", "sample_0"]
        )

    def test_rejects_wrong_input_state_space(self) -> None:
        disconnected = nx.Graph([(0, 1), (2, 3)])
        with self.assertRaisesRegex(ValueError, "already be connected"):
            nulls.degree_preserving_connected_null(
                disconnected,
                n_samples=1,
                burnin_attempts=0,
                thinning_attempts=0,
                seed=1,
            )

        weighted = nx.path_graph(4)
        weighted[0][1]["weight"] = 2.0
        with self.assertRaisesRegex(ValueError, "unweighted"):
            nulls.degree_preserving_connected_null(
                weighted,
                n_samples=1,
                burnin_attempts=0,
                thinning_attempts=0,
                seed=1,
            )


class ConnectedGnmNullTest(unittest.TestCase):
    def generate(self) -> dict:
        return nulls.connected_gnm_null(
            12,
            20,
            n_samples=3,
            seed=20260905,
            max_attempts_per_sample=200,
        )

    def test_exact_ne_and_connectivity(self) -> None:
        result = self.generate()
        for graph in result["graphs"]:
            self.assertEqual(graph.number_of_nodes(), 12)
            self.assertEqual(graph.number_of_edges(), 20)
            self.assertTrue(nx.is_connected(graph))
            self.assertEqual(nx.number_of_selfloops(graph), 0)
        metadata = result["metadata"]
        self.assertEqual(metadata["accepted"], 3)
        self.assertEqual(
            metadata["attempted"], metadata["accepted"] + metadata["rejected"]
        )
        self.assertFalse(metadata["largest_component_substitution_used"])

    def test_seed_reproducibility(self) -> None:
        first = self.generate()
        second = self.generate()
        self.assertEqual(
            [edge_signature(graph) for graph in first["graphs"]],
            [edge_signature(graph) for graph in second["graphs"]],
        )
        self.assertEqual(first["metadata"], second["metadata"])

    def test_impossible_connected_parameters_fail_before_sampling(self) -> None:
        with self.assertRaisesRegex(ValueError, "no connected simple graph"):
            nulls.connected_gnm_null(
                8,
                5,
                n_samples=1,
                seed=3,
                max_attempts_per_sample=10,
            )

    def test_attempt_cap_never_substitutes_largest_component(self) -> None:
        disconnected_exact_nm = nx.Graph()
        disconnected_exact_nm.add_nodes_from(range(6))
        disconnected_exact_nm.add_edges_from(
            [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5)]
        )
        self.assertEqual(disconnected_exact_nm.number_of_edges(), 5)
        self.assertFalse(nx.is_connected(disconnected_exact_nm))

        with mock.patch.object(
            nulls.nx, "gnm_random_graph", return_value=disconnected_exact_nm
        ) as generator:
            with self.assertRaises(nulls.ConnectedGnmSamplingError) as caught:
                nulls.connected_gnm_null(
                    6,
                    5,
                    n_samples=1,
                    seed=4,
                    max_attempts_per_sample=3,
                )
        self.assertEqual(generator.call_count, 3)
        self.assertEqual(caught.exception.metadata["attempted"], 3)
        self.assertEqual(caught.exception.metadata["completed_samples"], 0)
        self.assertFalse(
            caught.exception.metadata["largest_component_substitution_used"]
        )


class SerializationTest(unittest.TestCase):
    def test_edge_overlap_and_strict_json_save(self) -> None:
        graph = nx.cycle_graph(6)
        result = nulls.degree_preserving_connected_null(
            graph,
            n_samples=2,
            burnin_attempts=10,
            thinning_attempts=5,
            seed=7,
            trace_every=4,
        )
        self.assertEqual(nulls.edge_overlap_fraction(graph, graph), 1.0)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "null.json"
            returned = nulls.save_null_ensemble(path, result)
            self.assertEqual(returned, path)
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["metadata"], result["metadata"])
        self.assertEqual(len(payload["graphs"]), 2)
        self.assertEqual(len(payload["graphs"][0]["edges"]), graph.number_of_edges())

    def test_tuple_labels_are_type_tagged(self) -> None:
        graph = nx.grid_2d_graph(2, 2)
        payload = nulls.serialize_graph_edges(graph)
        self.assertEqual(len(payload["nodes"]), 4)
        self.assertTrue(
            all(record["label"]["type"] == "tuple" for record in payload["nodes"])
        )


if __name__ == "__main__":
    unittest.main()
