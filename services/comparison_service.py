"""
Algorithm comparison service.

Provides utilities for comparing search algorithm results, selecting
the best algorithm for a given metric, and generating human-readable
summaries.
"""

try:
    import pandas as pd
except ImportError:
    class SimpleDataFrame(list):
        def __init__(self, rows):
            super().__init__(rows)
            self._rows = rows
        @property
        def empty(self):
            return len(self._rows) == 0
        def to_string(self):
            if not self._rows:
                return "Empty Table"
            keys = list(self._rows[0].keys())
            header = " | ".join(keys)
            sep = "-+-".join("-" * len(k) for k in keys)
            lines = [header, sep]
            for r in self._rows:
                lines.append(" | ".join(str(r.get(k, "")) for k in keys))
            return "\n".join(lines)
    pd = type("MockPandas", (), {"DataFrame": SimpleDataFrame})()



class ComparisonService:
    """Compare and summarise results from multiple search algorithms."""

    def __init__(self):
        """Initialize the ComparisonService."""
        pass

    # ------------------------------------------------------------------ #
    # DataFrame comparison
    # ------------------------------------------------------------------ #
    def compare_results(self, results_dict):
        """
        Build a comparison DataFrame from algorithm results.

        Args:
            results_dict: ``{algorithm_name: AlgorithmResult, ...}``

        Returns:
            pandas.DataFrame with columns:
                Algorithm, Status, Distance (m), Travel Time (s),
                Nodes Explored, Edges Traversed, Execution Time (ms).
        """
        rows = []
        for name, result in results_dict.items():
            status = "Found" if result.found else "Not Found"
            distance = round(result.total_distance, 2) if result.found else None
            travel_time = round(result.total_travel_time, 2) if result.found else None
            exec_ms = round(result.execution_time * 1000, 3)

            rows.append(
                {
                    "Algorithm": name,
                    "Status": status,
                    "Distance (m)": distance,
                    "Travel Time (s)": travel_time,
                    "Nodes Explored": result.nodes_explored,
                    "Edges Traversed": result.edges_traversed,
                    "Execution Time (ms)": exec_ms,
                }
            )

        df = pd.DataFrame(rows)
        return df

    # ------------------------------------------------------------------ #
    # Best algorithm selection
    # ------------------------------------------------------------------ #
    def get_best_algorithm(self, results_dict, metric="total_distance"):
        """
        Return the name of the algorithm with the best (lowest) value for
        *metric*, considering only algorithms that found a path.

        Supported metrics: ``total_distance``, ``total_travel_time``,
        ``nodes_explored``, ``edges_traversed``, ``execution_time``.

        Args:
            results_dict: ``{algorithm_name: AlgorithmResult, ...}``
            metric: Attribute name on AlgorithmResult to minimise.

        Returns:
            str | None: Algorithm name, or None if no algorithm found a path.
        """
        best_name = None
        best_value = float("inf")

        for name, result in results_dict.items():
            if not result.found:
                continue
            value = getattr(result, metric, None)
            if value is not None and value < best_value:
                best_value = value
                best_name = name

        return best_name

    # ------------------------------------------------------------------ #
    # Text summary
    # ------------------------------------------------------------------ #
    def generate_comparison_summary(self, results_dict):
        """
        Generate a human-readable text summary of algorithm comparison results.

        Args:
            results_dict: ``{algorithm_name: AlgorithmResult, ...}``

        Returns:
            str: Multi-line summary string.
        """
        lines = []
        lines.append("=" * 55)
        lines.append("  Algorithm Comparison Summary")
        lines.append("=" * 55)

        found_algos = {n: r for n, r in results_dict.items() if r.found}
        not_found = [n for n, r in results_dict.items() if not r.found]

        if not found_algos:
            lines.append("\nNo algorithm found a valid path.")
            if not_found:
                lines.append(f"Failed: {', '.join(not_found)}")
            return "\n".join(lines)

        # Per-algorithm details
        lines.append("")
        for name, result in found_algos.items():
            lines.append(f"  {name}:")
            lines.append(f"    Distance      : {result.total_distance:,.2f} m")
            lines.append(f"    Travel Time   : {result.total_travel_time:,.2f} s")
            lines.append(f"    Nodes Explored: {result.nodes_explored}")
            lines.append(f"    Edges Traversed: {result.edges_traversed}")
            lines.append(f"    Exec Time     : {result.execution_time * 1000:,.3f} ms")
            lines.append("")

        # Best-in-class
        best_dist = self.get_best_algorithm(results_dict, "total_distance")
        best_time = self.get_best_algorithm(results_dict, "total_travel_time")
        best_exec = self.get_best_algorithm(results_dict, "execution_time")
        best_nodes = self.get_best_algorithm(results_dict, "nodes_explored")

        lines.append("-" * 55)
        lines.append("  Winners:")
        if best_dist:
            lines.append(f"    Shortest Distance  : {best_dist}")
        if best_time:
            lines.append(f"    Fastest Travel Time: {best_time}")
        if best_exec:
            lines.append(f"    Quickest Execution : {best_exec}")
        if best_nodes:
            lines.append(f"    Fewest Nodes       : {best_nodes}")

        if not_found:
            lines.append(f"\n  Did not find a path: {', '.join(not_found)}")

        lines.append("=" * 55)
        return "\n".join(lines)
