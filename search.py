import heapq
from collections.abc import Callable
from typing import Any, Union

from problems import Problem

Number = Union[int, float]
infinity = float("inf")


def null_heuristic(state) -> int:
    """Heuristic that only returns 0."""
    return 0


def weighted_heuristic(heuristic: Callable[Any, Number],
                       weight: Number) -> Callable[Any, Number]:
    """Given a heuristic, weights it with a specified weight."""
    return lambda x: heuristic(x) * weight


def remove_if_in_heap(heap: list, to_remove):
    """If an item is in the heap, removes it."""
    if to_remove in heap:
        remove_from_heap(heap, to_remove)


def remove_from_heap(heap: list, to_remove):
    """Removes a given item from the given heap."""
    heap.remove(to_remove)
    heapq.heapify(heap)


def reconstruct_path(state, parents: dict) -> list:
    """Reconstructs a path to a state.

    Args:
        state: The final state in the path.
        parents: A dict of the form [child, parent].

    Returns:
        A list representing the path from the origin to the given state.
    """
    path = [state]
    while state in parents:
        state = parents[state]
        path.append(state)
    path.reverse()
    return path


def a_star(
        start,
        problem: Problem,
        h: Callable[Any, Number] = null_heuristic) -> tuple[float, list[Any]]:
    """A simple implementation of A*. Finds the shortest path to a goal node.

    Args:
        start: The beginning state.
        problem: The problem space.
        h: A heuristic function taking a state and returning a number.
            Must be admissible for optimal solution.

    Returns:
        A tuple of the form (cost, path).
    """
    start = problem.canonical(start)

    opened = [(0, start)]
    parents = {}
    g_values = {start: 0}
    f_values = {start: h(start)}

    while opened:
        cost, state = heapq.heappop(opened)

        if problem.is_goal_state(state):
            return cost, reconstruct_path(state, parents)

        neighbours = problem.expand(state)
        for distance, neighbour in neighbours:
            g = cost + distance
            f = g + h(neighbour)
            old_g = g_values.get(neighbour, infinity)
            if g < old_g:
                if old_g != infinity:
                    remove_if_in_heap(opened, (old_g, neighbour))
                g_values[neighbour] = g
                f_values[neighbour] = f
                heapq.heappush(opened, (g, neighbour))
                parents[neighbour] = state

    return float("inf"), [None]


def weighted_a_star(start,
                    problem: Problem,
                    h: Callable[Any, Number] = null_heuristic,
                    weight: Number = 1) -> tuple[float, Any]:
    """A simple implementation of weighted A*. Faster but suboptimal.

    Args:
        start: The beginning state.
        problem: The problem space.
        h: A heuristic function taking a state and returning a number.
            Must be admissible for optimal solution.
        weight: The weight placed on the heuristic function. The solution
            cost is guaranteed to be no more than the true cost multiplied
            by this weight.

    Returns:
        A tuple of the form (cost, path).
    """

    h = weighted_heuristic(h, weight)
    return a_star(start, problem, h)


def make_pdb(start, problem: Problem) -> dict[Any, Number]:
    """Uses a simple Dijkstra search to compute the distance from a state to
    all other reachable states. Has no need for a heuristic, and so does not
    use one.

    Args:
        start: The initial state. All distances will be from this state.
        problem: The problem space.

    Returns:
        A dictionary of the form {state: distance}.
    """
    start = problem.canonical(start)

    opened = [(0, start)]
    g_values = {start: 0}

    while opened:
        cost, state = heapq.heappop(opened)
        neighbours = problem.expand(state)
        for distance, neighbour in neighbours:
            g = cost + distance
            old_g = g_values.get(neighbour, infinity)
            if g < old_g:
                if old_g != infinity:
                    remove_if_in_heap(opened, (old_g, neighbour))
                g_values[neighbour] = g
                heapq.heappush(opened, (g, neighbour))

    return g_values
