# AI Search Algorithms & Theoretical Foundations
## Classical Pathfinding Algorithms for Emergency Route Planning

This document details the theory, pseudocode, asymptotic complexity, and empirical behavior of the four classical search algorithms implemented in the **Intelligent Emergency Route Planner**.

The algorithms are independent implementations in `algorithms/`; route geometry is handled after search by the visualization layer. Search results contain node sequences and metrics, while `MapVisualizer` reconstructs the displayed route from the stored geometry of each traversed edge. Traffic-adjusted costs and closures are applied to a working graph copy before search, so closed edges are unavailable to every algorithm.

---

## 1. Breadth-First Search (BFS)

### 1.1 Overview & Theoretical Basis
Breadth-First Search is an uninformed (blind) graph traversal algorithm. It systematically explores all neighbor vertices at the present depth level before moving on to vertices at the next depth level.

- **Data Structure**: First-In-First-Out (FIFO) queue (`collections.deque`).
- **Completeness**: Complete if the branching factor $b$ is finite.
- **Optimality**: Optimal **only** for unweighted graphs (or graphs where all edges have identical positive weights). BFS guarantees finding the path with the **minimum number of edges (hops)**, but it does **not** guarantee minimum physical distance or travel time on weighted road networks.

### 1.2 Pseudocode
```
function BFS(Graph, Start, Goal):
    if Start == Goal:
        return [Start]
    
    Frontier = Queue([Start])
    Visited = Set([Start])
    ParentMap = {}
    NodesExplored = 0
    EdgesTraversed = 0
    
    while Frontier is not empty:
        Current = Frontier.pop_left()
        NodesExplored += 1
        
        for Neighbor in Graph.neighbors(Current):
            EdgesTraversed += 1
            if Neighbor == Goal:
                ParentMap[Goal] = Current
                return ReconstructPath(ParentMap, Start, Goal)
                
            if Neighbor not in Visited:
                Visited.add(Neighbor)
                ParentMap[Neighbor] = Current
                Frontier.push_right(Neighbor)
                
    return Failure (No path exists)
```

### 1.3 Asymptotic Complexity
- **Time Complexity**: $\mathcal{O}(V + E)$, where $V$ is the number of vertices and $E$ is the number of edges.
- **Space Complexity**: $\mathcal{O}(V)$ to maintain the queue and the visited set.

---

## 2. Depth-First Search (DFS)

### 2.1 Overview & Theoretical Basis
Depth-First Search explores as deep as possible along each branch before backtracking. 

- **Data Structure**: Last-In-First-Out (LIFO) stack (`list` in Python) or recursive call stack.
- **Completeness**: Complete on finite graphs when cycle checking (visited set) is enforced.
- **Optimality**: **Non-optimal**. DFS can find highly convoluted paths that loop through distant sections of the graph before stumbling upon the destination.
- **Emergency Utility**: Strongly ill-suited for physical emergency vehicle routing, but provides an essential baseline for comparing uninformed search strategies.

### 2.2 Pseudocode
```
function DFS(Graph, Start, Goal):
    if Start == Goal:
        return [Start]
        
    Frontier = Stack([Start])
    Visited = Set([Start])
    ParentMap = {}
    NodesExplored = 0
    EdgesTraversed = 0
    
    while Frontier is not empty:
        Current = Frontier.pop()
        NodesExplored += 1
        
        if Current == Goal:
            return ReconstructPath(ParentMap, Start, Goal)
            
        for Neighbor in Graph.neighbors(Current):
            EdgesTraversed += 1
            if Neighbor not in Visited:
                Visited.add(Neighbor)
                ParentMap[Neighbor] = Current
                Frontier.push(Neighbor)
                
    return Failure (No path exists)
```

### 2.3 Asymptotic Complexity
- **Time Complexity**: $\mathcal{O}(V + E)$ in finite graphs with visited tracking.
- **Space Complexity**: $\mathcal{O}(V)$ for storing stack elements and parent pointers.

---

## 3. Greedy Best-First Search

### 3.1 Overview & Theoretical Basis
Greedy Best-First Search is an informed (heuristic) search algorithm. It expands the node that appears closest to the goal according to a heuristic function $h(n)$:

$$f(n) = h(n)$$

In this system, $h(n)$ is the great-circle Haversine straight-line distance from the coordinates of node $n$ to the destination coordinates:

$$h(n) = 2 R \arcsin \left( \sqrt{ \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right) } \right)$$

- **Data Structure**: Priority queue (min-heap via Python `heapq`).
- **Completeness**: Incomplete on infinite graphs; complete in finite graphs with cycle detection.
- **Optimality**: **Non-optimal**. Because it evaluates only remaining distance and ignores past accumulated cost $g(n)$, it can be led into dead ends or costly detours.
- **Strength**: Often expands very few nodes compared to uninformed algorithms, executing quickly.

### 3.2 Pseudocode
```
function GREEDY_BEST_FIRST(Graph, Start, Goal):
    if Start == Goal:
        return [Start]
        
    Frontier = MinPriorityQueue()
    Frontier.push(priority=Heuristic(Start, Goal), node=Start)
    Visited = Set([Start])
    ParentMap = {}
    NodesExplored = 0
    EdgesTraversed = 0
    
    while Frontier is not empty:
        Current = Frontier.pop_min()
        NodesExplored += 1
        
        if Current == Goal:
            return ReconstructPath(ParentMap, Start, Goal)
            
        for Neighbor in Graph.neighbors(Current):
            EdgesTraversed += 1
            if Neighbor not in Visited:
                Visited.add(Neighbor)
                ParentMap[Neighbor] = Current
                h_val = Heuristic(Neighbor, Goal)
                Frontier.push(priority=h_val, node=Neighbor)
                
    return Failure (No path exists)
```

### 3.3 Asymptotic Complexity
- **Time Complexity**: $\mathcal{O}(E \log V)$ in the worst case where every edge is considered in the priority queue.
- **Space Complexity**: $\mathcal{O}(V)$ for the priority queue and parent map.

---

## 4. A* Search Algorithm

### 4.1 Overview & Theoretical Basis
A* Search evaluates candidate paths by combining the actual cost incurred from the start node $g(n)$ and the estimated cost to reach the goal $h(n)$:

$$f(n) = g(n) + h(n)$$

Where:
- $g(n)$: Exact accumulated cost from the start node to node $n$ along the evaluated path.
- $h(n)$: Admissible, consistent heuristic estimating the remaining cost to the goal.

### 4.2 Heuristic Admissibility & Consistency
1. **Admissibility**: A heuristic is admissible if it never overestimates the true cost to reach the goal:
   $$\forall n, \quad 0 \leq h(n) \leq h^*(n)$$
   - *Distance Optimization*: Straight-line Haversine distance is the shortest possible path between two points on Earth; road distance can never be shorter.
   - *Travel Time Optimization*: $h_{time}(n) = \frac{h_{dist}(n)}{v_{max}}$, where $v_{max}$ is the theoretical maximum speed across the network ($120\text{ km/h} \approx 33.33\text{ m/s}$). Since no vehicle can exceed $v_{max}$, actual travel time is strictly $\geq h_{time}(n)$.
2. **Consistency (Monotonicity)**: For any node $n$ and neighbor $n'$ generated by action $a$:
   $$h(n) \leq c(n, a, n') + h(n')$$
   Because the Haversine metric satisfies the triangle inequality on a spherical manifold, the heuristic is consistent, guaranteeing that the first time a node is expanded, the path to it is optimal.

### 4.3 Pseudocode
```
function A_STAR(Graph, Start, Goal, WeightAttr):
    if Start == Goal:
        return [Start]
        
    Frontier = MinPriorityQueue()
    g_score = {node: infinity for node in Graph.nodes}
    g_score[Start] = 0.0
    
    f_start = g_score[Start] + Heuristic(Start, Goal)
    Frontier.push(priority=f_start, node=Start)
    
    ParentMap = {}
    NodesExplored = 0
    EdgesTraversed = 0
    ClosedSet = Set()
    
    while Frontier is not empty:
        Current = Frontier.pop_min()
        
        if Current in ClosedSet:
            continue
        ClosedSet.add(Current)
        NodesExplored += 1
        
        if Current == Goal:
            return ReconstructPath(ParentMap, Start, Goal)
            
        for Neighbor in Graph.neighbors(Current):
            EdgesTraversed += 1
            EdgeCost = GetEdgeCost(Graph, Current, Neighbor, WeightAttr)
            TentativeG = g_score[Current] + EdgeCost
            
            if TentativeG < g_score[Neighbor]:
                g_score[Neighbor] = TentativeG
                ParentMap[Neighbor] = Current
                f_score = TentativeG + Heuristic(Neighbor, Goal)
                Frontier.push(priority=f_score, node=Neighbor)
                
    return Failure (No path exists)
```

### 4.4 Asymptotic Complexity
- **Time Complexity**: $\mathcal{O}(E \log V)$ with a binary heap priority queue.
- **Space Complexity**: $\mathcal{O}(V)$ for storing priority queue entries, g-scores, and closed set.

---

## 5. Comparative Algorithmic Summary

| Algorithm | Strategy | Complete? | Optimal? | Time Complexity | Space Complexity | Best Use Case |
|---|---|---|---|---|---|---|
| **BFS** | FIFO Queue (Layer by Layer) | Yes | Yes (Unweighted only) | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Minimum-hop routing on unweighted graphs |
| **DFS** | LIFO Stack (Deep Traversal) | Yes (Finite) | No | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Topological sorting, maze solving |
| **Greedy** | Min-Heap ($f = h$) | Yes (Finite) | No | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V)$ | Fast heuristic exploration when speed > optimality |
| **A\*** | Min-Heap ($f = g + h$) | Yes | **Yes** (Admissible $h$) | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V)$ | Optimal pathfinding on weighted road networks |

