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
        f_value, state = heapq.heappop(opened)
        cost = g_values[state]

        if problem.is_goal_state(state):
            return cost, reconstruct_path(state, parents)

        neighbours = problem.expand(state)
        for distance, neighbour in neighbours:
            g = cost + distance
            h_cost = h(neighbour)
            f = g + h_cost
            old_g = g_values.get(neighbour, infinity)
            if g < old_g:
                if old_g != infinity:
                    remove_if_in_heap(opened, (old_g + h_cost, neighbour))
                g_values[neighbour] = g
                f_values[neighbour] = f
                heapq.heappush(opened, (f, neighbour))
                parents[neighbour] = state

    return infinity, [None]


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


def weighted_a_star_with_bounds(start,
                                problem: Problem,
                                h: Callable[Any, Number] = null_heuristic,
                                w: Number = 1) -> tuple[float, Any]:
    """Weighted A* that also returns values needed to calculate F and X bounds.

    Args:
        start: The beginning state.
        problem: The problem space.
        h: A heuristic function taking a state and returning a number.
        w: The weight placed on the heuristic function. The solution
            cost is guaranteed to be no more than the true cost multiplied
            by this weight.

    Returns:
        A tuple of the form (cost, path, F, f_iter, g_min, g_iter, f_bound, x_bound).
    """

    Wh = weighted_heuristic(h, w)

    start = problem.canonical(start)

    opened = [(Wh(start), start)]
    parents = {}
    g_values = {start: 0}
    f_values = {start: Wh(start)}
    F = float("-inf")
    g_min = infinity
    g_heap = [(0, start)]
    f_iter = -1
    g_iter = -1

    iteration = 0
    while opened:
        iteration += 1
        f_w_min, current = heapq.heappop(opened)
        cost = g_values[current]

        if f_w_min > F:
            F = f_w_min
            f_iter = iteration
            g_min = g_heap[0][0]
            g_iter = iteration
        elif f_w_min == F:
            lowest_g = g_heap[0][0]
            if lowest_g < g_min:
                g_min = lowest_g
                g_iter = iteration

        if problem.is_goal_state(current):
            unweighted_f_values = [g + h(state) for g, state in g_heap]
            min_f = min(unweighted_f_values)  # Not largest!
            f_bound = (cost * w) / (F + (w - 1) * g_min)
            x_bound = cost / min_f
            path = reconstruct_path(current, parents)

            return cost, path, F, f_iter, g_min, g_iter, f_bound, x_bound

        remove_from_heap(g_heap, (cost, current))

        neighbours = problem.expand(current)
        for distance, neighbour in neighbours:
            g = cost + distance
            Wh_cost = Wh(neighbour)
            f = g + Wh_cost
            old_g = g_values.get(neighbour, infinity)
            if g < old_g:
                if old_g != infinity:
                    remove_if_in_heap(opened, (old_g + Wh_cost, neighbour))
                    remove_if_in_heap(g_heap, (old_g, neighbour))
                g_values[neighbour] = g
                f_values[neighbour] = f
                heapq.heappush(opened, (f, neighbour))
                heapq.heappush(g_heap, (g, neighbour))
                parents[neighbour] = current

    # This doesn't include all values but I don't expect to run into this situation soon
    return infinity, [None]
