"""Run and compare BFS, DFS, and IDDFS on the Jug Problem."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from problem.jug import JugProblem
from bfs.bfs import bfs
from dfs.dfs import dfs
from iddfs.iddfs import iddfs


def print_solution(algorithm_name, solution, nodes_explored):
    """Display solution and statistics."""
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
    """Compare performance of all algorithms."""
    print(f"\n{'='*60}")
    print("ALGORITHM COMPARISON")
    print(f"{'='*60}")
    
    print(f"{'Algorithm':<15} {'Solution Length':<20} {'Nodes Explored':<20}")
    print("-" * 55)
    
    for name, solution, nodes in results:
        sol_len = len(solution) - 1 if solution else "N/A"
        print(f"{name:<15} {str(sol_len):<20} {nodes:<20}")


def main():
    """Run and compare BFS, DFS, and IDDFS on the Jug Problem."""
    print("\n" + "="*60)
    print("UNINFORMED SEARCH ALGORITHMS")
    print("Milk and Water Jug Problem")
    print("="*60)
    print("\nProblem Setup:")
    print("  Jug 1 capacity: 4 liters")
    print("  Jug 2 capacity: 3 liters")
    print("  Initial state: (0, 0)")
    print("  Goal: Measure exactly 2 liters in one jug")
    
    print("\n" + "="*60)
    print("SELECT ALGORITHM")
    print("="*60)
    print("1. BFS (Breadth First Search)")
    print("2. DFS (Depth First Search)")
    print("3. IDDFS (Iterative Deepening DFS)")
    print("4. Run All Algorithms")
    print("="*60)
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    problem = JugProblem()
    results = []
    
    if choice == "1" or choice == "4":
        print("\n\nRunning BFS...")
        solution_bfs, nodes_bfs = bfs(problem)
        print_solution("BREADTH FIRST SEARCH (BFS)", solution_bfs, nodes_bfs)
        results.append(("BFS", solution_bfs, nodes_bfs))
    
    if choice == "2" or choice == "4":
        print("\n\nRunning DFS...")
        solution_dfs, nodes_dfs = dfs(problem)
        print_solution("DEPTH FIRST SEARCH (DFS)", solution_dfs, nodes_dfs)
        results.append(("DFS", solution_dfs, nodes_dfs))
    
    if choice == "3" or choice == "4":
        print("\n\nRunning IDDFS...")
        solution_iddfs, nodes_iddfs = iddfs(problem)
        print_solution("ITERATIVE DEEPENING DFS (IDDFS)", solution_iddfs, nodes_iddfs)
        results.append(("IDDFS", solution_iddfs, nodes_iddfs))
    
    if not results:
        print("Invalid choice. Please enter 1-4.")
        return
    
    if len(results) > 1:
        print_comparison_table(results)



if __name__ == "__main__":
    main()
