"""
Main program to run all uninformed search algorithms on the Milk and Water Jug Problem.

Compares Breadth First Search (BFS), Depth First Search (DFS), and 
Iterative Deepening Depth First Search (IDDFS).
"""

from problem.jug import JugProblem
from bfs.bfs import bfs
from dfs.dfs import dfs
from iddfs.iddfs import iddfs


def print_solution(algorithm_name, solution, nodes_explored):
    """Print the solution in a formatted way."""
    print(f"\n{'='*60}")
    print(f"{algorithm_name}")
    print(f"{'='*60}")
    
    if solution is None:
        print("No solution found")
        print(f"Nodes explored: {nodes_explored}")
        return
    
    print("Solution found!")
    print("\nState sequence:")
    for i, state in enumerate(solution):
        print(f"  {i}: {state}")
    
    print(f"\nSolution length: {len(solution) - 1} steps")
    print(f"Nodes explored: {nodes_explored}")


def print_comparison_table(results):
    """Print a comparison table of all algorithms."""
    print(f"\n{'='*60}")
    print("ALGORITHM COMPARISON")
    print(f"{'='*60}")
    
    print(f"{'Algorithm':<15} {'Solution Length':<20} {'Nodes Explored':<20}")
    print("-" * 55)
    
    for name, solution, nodes in results:
        sol_len = len(solution) - 1 if solution else "N/A"
        print(f"{name:<15} {str(sol_len):<20} {nodes:<20}")


def main():
    """Run all search algorithms and compare results."""
    print("\n" + "="*60)
    print("UNINFORMED SEARCH ALGORITHMS")
    print("Milk and Water Jug Problem")
    print("="*60)
    print("\nProblem Setup:")
    print("  Jug 1 capacity: 4 liters")
    print("  Jug 2 capacity: 3 liters")
    print("  Initial state: (0, 0)")
    print("  Goal: Measure exactly 2 liters in one jug")
    
    # Create problem instance
    problem = JugProblem()
    results = []
    
    # Run BFS
    print("\n\nRunning BFS...")
    solution_bfs, nodes_bfs = bfs(problem)
    print_solution("BREADTH FIRST SEARCH (BFS)", solution_bfs, nodes_bfs)
    results.append(("BFS", solution_bfs, nodes_bfs))
    
    # Run DFS
    print("\n\nRunning DFS...")
    solution_dfs, nodes_dfs = dfs(problem)
    print_solution("DEPTH FIRST SEARCH (DFS)", solution_dfs, nodes_dfs)
    results.append(("DFS", solution_dfs, nodes_dfs))
    
    # Run IDDFS
    print("\n\nRunning IDDFS...")
    solution_iddfs, nodes_iddfs = iddfs(problem)
    print_solution("ITERATIVE DEEPENING DFS (IDDFS)", solution_iddfs, nodes_iddfs)
    results.append(("IDDFS", solution_iddfs, nodes_iddfs))
    
    # Print comparison
    print_comparison_table(results)
    
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    print("""
BFS:
  - Explores level by level
  - Guarantees shortest path
  - Requires more memory

DFS:
  - Explores deep paths first
  - Uses minimal memory
  - May not find optimal solution

IDDFS:
  - Combines BFS and DFS advantages
  - Finds optimal depth with low memory
  - Re-explores nodes multiple times
    """)


if __name__ == "__main__":
    main()
