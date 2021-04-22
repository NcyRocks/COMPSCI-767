import ast
import itertools
import os
import random
import statistics
import string
import sys
from typing import Any, Union

import openpyxl

sys.path.append(os.path.relpath("../"))
import problems
import search

Number = Union[int, float]

sizes = [0.25, 0.5, 0.75, 1]


def excel_cell_A1(size: int, strength: int, problem: int,
                  is_stdev: bool) -> str:
    """Given a problem number, sample size and heuristic strength, outputs
    the correct cell for that data point.

    Specific to COMPSCI 767 S1 2021 Assignment 1.
    """
    column = 10 - strength + is_stdev
    column = string.ascii_uppercase[column - 1]

    row = problem + 2
    section = sizes.index(size)
    row += section * 27
    row = str(row)

    return column + row


def abstractify(state: str, ids: tuple[int]) -> str:
    """Given a tuple, creates an abstracted version of a TileProblem state."""
    ids = [str(num) for num in ids]
    for num in ids:
        state = state.replace(num, ids[0])
    return state


def choose_n(total, sample_size):
    """Given a number of items N and a sample size S, returns all possible
    unordered S-tuples of integers up to N."""
    return list(itertools.combinations(range(1, total + 1), sample_size))


def main():
    """Completes data generation for Assignment 1.
    Assumes GoalState.txt, Problems.txt, and ExperimentalData.xlsx are in the
    same directory, in the form they were provided on Canvas.
    Takes a few minutes at best - you might want to put the kettle on.
    """

    random.seed(42)  # I used 42 for the experiments
    with open("GoalState.txt") as file:
        goal = file.read().strip()
    problem = problems.TileProblem(goal)

    with open("Problems.txt") as file:
        contents = file.readlines()
    initial_states = [state.strip() for state in contents]

    puzzle_num = 8  # For the 8-puzzle, this is set to 8
    strengths = [7, 5, 3]
    patterns = {
        strength: choose_n(puzzle_num, strength)
        for strength in strengths
    }

    # WARNING: This will use up hundreds of megabytes with default settings.
    # It will save a few minutes execution next time, however.
    # Choose wisely.
    use_file = True
    pdb_location = "PDBs.txt"

    if use_file and os.path.isfile(pdb_location):
        with open(pdb_location) as file:
            print("Reading existing PDB file...")
            pdbs_string = file.read()
        print("Loading PDBs (this may take a few minutes)...")
        pdbs = ast.literal_eval(pdbs_string)
        print("PDBs loaded.")

    else:
        print("Generating PDBs from scratch - this will take a wee while.")
        pdbs = {}
        for strength in strengths:
            pdbs[strength] = {}
            for pattern in patterns[strength]:
                print(f"Constructing PDB by merging these tile IDs: {pattern}")
                new_goal = abstractify(goal, pattern)
                pdbs[strength][pattern] = search.make_pdb(new_goal, problem)
        print("All PDBs constructed.")
        if use_file:
            print("Writing PDBs to file for later...")
            with open(pdb_location, "w") as file:
                file.write(str(pdbs))

    address = "ExperimentalData.xlsx"
    ExperimentalData = openpyxl.load_workbook(address)
    Sheet1 = ExperimentalData["Sheet1"]

    runs = 100
    print("Running experiments...")
    for strength in strengths:
        for size in sizes:
            sample_size = int(len(patterns[strength]) * size)
            for index, state in enumerate(initial_states):
                averages = []
                stdevs = []
                for _ in range(runs):
                    h_values = []
                    sample = random.sample(patterns[strength], sample_size)
                    for pattern in sample:
                        abstract_state = abstractify(state, pattern)
                        abstract_state = problem.canonical(abstract_state)
                        pdb = pdbs[strength][pattern]
                        h_values.append(pdb[abstract_state])
                    averages.append(statistics.mean(h_values))
                    stdevs.append(statistics.stdev(h_values))

                mean_cell = excel_cell_A1(size, strength, index, False)
                stdev_cell = excel_cell_A1(size, strength, index, True)
                Sheet1[mean_cell] = statistics.mean(averages)
                Sheet1[stdev_cell] = statistics.mean(stdevs)

    print("Experiments finished. Adding final touches...")

    for col in "CDEFGH":
        row = 27
        for _ in range(len(sizes)):
            Sheet1[col + str(row)] = f"=AVERAGE({col}{row-25}:{col}{row-1})"
            row += 27

    for col in "CEG":
        row = 28
        for _ in range(len(sizes)):
            Sheet1[col + str(row)] = f"={col}{row-1}/20"
            row += 27

    ExperimentalData.save(address)

    print("Done!")


if __name__ == "__main__":
    main()
