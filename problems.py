import itertools
import re
from collections.abc import Iterable
from typing import Any, Union

Number = Union[int, float]


class Problem:
    def __init__(self):
        """Initiates Problem space."""
        pass

    def expand(self, state) -> Iterable[tuple[Number, Any]]:
        """Given a state, returns all neighbour states."""
        pass

    def is_goal_state(self, state) -> bool:
        """True if given state is a goal state."""
        pass

    def canonical(self, state):
        """Returns a definitive version of the state."""
        pass


class TileProblem(Problem):
    def __init__(self, text: str):
        """Initiates a tile problem, such as an 8-tile or 15-tile problem.
        All tiles' goal locations and location adjacencies must be specified.
        States can contain adjacencies (adj), tile locations (at), and blanks.
        Internally, only locations are used - adjacencies stay constant.

        Args:
            text: The problem's goal state, with all adjacency and location
                predicates.
        """

        adjacencies = self.predicate_lists(text, "adj")
        locations = set(itertools.chain.from_iterable(adjacencies))

        self.adjacencies = {location: set() for location in locations}
        for first, second in adjacencies:
            self.adjacencies[first].add(second)

        self.as_string = self.canonical(text)
        self.distances = {} # Distances between given locations

    def remove_brackets(self, string: str) -> str:
        """Given a string with brackets, returns the brackets' contents."""
        opening_index = string.index("(")
        closing_index = string.index(")")
        return string[opening_index + 1:closing_index]

    def predicate_lists(self, string: str, predicate: str) -> list[list[str]]:
        """Given a string and a kind of predicate, returns a list of the
        contents of all predicates of that kind.

        Args:
            string: The string from which to extract predicates.
            predicate: The kind of predicate to extract.

        Returns:
            A list containing tuples representing the contents of all instances
            of the given kind of predicate. For example, 'at(8, e)' becomes
            ('8', 'e').
        """
        regex = predicate + r"\([^()]+\)"
        matches = re.findall(regex, string)
        split = []
        for match in matches:
            string = self.remove_brackets(match)
            split.append(string.split(","))
        return split

    def str_to_dict(self, state: str) -> dict[str, Any]:
        """Given a state string, returns a dict of all tile locations."""
        location_lists = self.predicate_lists(state, "at")
        locations = {location: None for location in self.adjacencies}
        for piece, location in location_lists:
            locations[location] = piece
        return locations

    def dict_to_str(self,
                    locations: dict[str, Any],
                    full: bool = False) -> str:
        """Given a dict of tile locations, returns a state string.
        Can contain only 'at' predicates (for compactness) or full description.

        Args:
            locations: Dictionary of tile locations.
            full: If True, returns a complete state description, with
                adjacencies, blanks, and a 'state' predicate encompassing the
                rest. If False, returns only 'at' predicates.

        Returns:
            A string describing the current state.
        """
        predicates = []

        if full:
            for first, seconds in self.adjacencies.items():
                for second in seconds:
                    predicates.append(f"adj({first},{second})")

        for location, piece in locations.items():
            if piece is not None:
                predicates.append(f"at({piece},{location})")
            elif full:
                predicates.append(f"blank({location})")

        predicates.sort()

        if full:
            predicate_string = ",".join(predicates)
            return "state([" + predicate_string + "])."
        return "".join(predicates)

    def canonical(self, state: str, full: bool = False) -> str:
        """Returns a definitive version of the state.
        Can return full description, but defaults to compact."""
        dictionary = self.str_to_dict(state)
        string = self.dict_to_str(dictionary, full)
        return string

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return self.as_string

    def __hash__(self):
        return hash(self.as_string)

    def is_goal_state(self, state: str) -> bool:
        """True if given state is a goal state."""
        state = self.canonical(state)
        return state == self.as_string

    def blanks(self, locations: dict[str, Any]) -> set[str]:
        """Given a location dict, returns a set of all blank locations."""
        return {
            location
            for location, piece in locations.items() if piece is None
        }

    def expand(self, state: str) -> set[tuple[int, str]]:
        """Given a state, returns all neighbour states."""
        next_states = set()
        locations = self.str_to_dict(state)
        blanks = self.blanks(locations)
        for blank in blanks:  # For our examples, only one blank
            for location, piece in locations.items():
                if blank in self.adjacencies[location]:
                    new_locations = locations.copy()
                    new_locations[blank] = piece
                    new_locations[location] = None
                    new_state = self.dict_to_str(new_locations)
                    next_states.add((1, new_state))
        return next_states

    def ensure_in_distance_dict(self, from_location, to_location):
        key = f"{from_location}->{to_location}"
        if key in self.distances:
            return
        current_nodes = {from_location}
        distance = 0
        explored_nodes = set()
        new_nodes = set()
        while key not in self.distances:
            for node in current_nodes:
                new_key = f"{from_location}->{node}"
                if new_key not in self.distances:
                    self.distances[new_key] = distance
                explored_nodes.add(node)
                new_nodes.update(self.adjacencies[node])
            current_nodes.update(new_nodes)
            current_nodes.difference_update(explored_nodes)
            distance += 1
                

    def manhattan_distance(self, state: str) -> Number:
        from_locations = self.str_to_dict(state)
        locations = self.str_to_dict(self.as_string)
        to_locations = {piece: location for location, piece in locations.items() if piece is not None}

        distance = 0

        for from_location, piece in from_locations.items():
            if piece is None:
                continue
            to_location = to_locations[piece]
            self.ensure_in_distance_dict(from_location, to_location)
            key = f"{from_location}->{to_location}"
            distance += self.distances[key]

        return distance
