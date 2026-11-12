"""
Lightweight MultiDiGraph implementation used as a transparent fallback
when networkx is not yet installed in the environment.

Provides the subset of NetworkX MultiDiGraph methods required by the
emergency routing algorithms and simulation engine.
"""

from typing import Any, Dict, Iterator, List, Optional, Tuple
import copy


class SimpleMultiDiGraph:
    """A pure-Python MultiDiGraph compatible with NetworkX."""

    def __init__(self, crs: str = "EPSG:4326", name: str = "SimpleMultiDiGraph", **attr):
        self.graph = {"crs": crs, "name": name, **attr}
        self._nodes: Dict[Any, Dict[str, Any]] = {}
        self._succ: Dict[Any, Dict[Any, Dict[int, Dict[str, Any]]]] = {}
        self._pred: Dict[Any, Dict[Any, Dict[int, Dict[str, Any]]]] = {}

    @property
    def nodes(self) -> Dict[Any, Dict[str, Any]]:
        return self._nodes

    def add_node(self, node_for_adding: Any, **attr):
        if node_for_adding not in self._nodes:
            self._nodes[node_for_adding] = attr
            self._succ[node_for_adding] = {}
            self._pred[node_for_adding] = {}
        else:
            self._nodes[node_for_adding].update(attr)

    def add_edge(self, u_for_edge: Any, v_for_edge: Any, key: Optional[int] = None, **attr) -> int:
        u, v = u_for_edge, v_for_edge
        self.add_node(u)
        self.add_node(v)

        if key is None:
            key = len(self._succ[u].get(v, {}))

        if v not in self._succ[u]:
            self._succ[u][v] = {}
        if u not in self._pred[v]:
            self._pred[v][u] = {}

        self._succ[u][v][key] = attr
        self._pred[v][u][key] = attr
        return key

    def has_node(self, n: Any) -> bool:
        return n in self._nodes

    def has_edge(self, u: Any, v: Any, key: Optional[int] = None) -> bool:
        if u in self._succ and v in self._succ[u]:
            if key is None:
                return len(self._succ[u][v]) > 0
            return key in self._succ[u][v]
        return False

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return sum(len(kd) for nbrs in self._succ.values() for kd in nbrs.values())

    def degree(self, n: Any) -> int:
        out_deg = sum(len(kd) for kd in self._succ.get(n, {}).values())
        in_deg = sum(len(kd) for kd in self._pred.get(n, {}).values())
        return out_deg + in_deg

    def in_degree(self, n: Any) -> int:
        return sum(len(kd) for kd in self._pred.get(n, {}).values())

    def out_degree(self, n: Any) -> int:
        return sum(len(kd) for kd in self._succ.get(n, {}).values())

    def neighbors(self, n: Any) -> Iterator[Any]:
        if n not in self._succ:
            return iter([])
        return iter(list(self._succ[n].keys()))


    def get_edge_data(self, u: Any, v: Any, key: Optional[int] = None, default: Any = None) -> Any:
        try:
            if key is None:
                return self._succ[u][v]
            return self._succ[u][v][key]
        except KeyError:
            return default

    def __getitem__(self, n: Any) -> Dict[Any, Dict[int, Dict[str, Any]]]:
        return self._succ[n]

    def __contains__(self, n: Any) -> bool:
        return n in self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def edges(self, keys: bool = False, data: bool = False):
        edge_list = []
        for u, nbrs in self._succ.items():
            for v, keydict in nbrs.items():
                for key, datadict in keydict.items():
                    if keys and data:
                        edge_list.append((u, v, key, datadict))
                    elif keys:
                        edge_list.append((u, v, key))
                    elif data:
                        edge_list.append((u, v, datadict))
                    else:
                        edge_list.append((u, v))
        return edge_list

    def remove_edge(self, u: Any, v: Any, key: Optional[int] = None):
        if u in self._succ and v in self._succ[u]:
            if key is None:
                del self._succ[u][v]
                if u in self._pred[v]:
                    del self._pred[v][u]
            else:
                self._succ[u][v].pop(key, None)
                if not self._succ[u][v]:
                    del self._succ[u][v]
                if u in self._pred.get(v, {}):
                    self._pred[v][u].pop(key, None)
                    if not self._pred[v][u]:
                        del self._pred[v][u]

    def copy(self) -> "SimpleMultiDiGraph":
        g = SimpleMultiDiGraph(**self.graph)
        g._nodes = copy.deepcopy(self._nodes)
        g._succ = copy.deepcopy(self._succ)
        g._pred = copy.deepcopy(self._pred)
        return g
