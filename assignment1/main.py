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


def a1_problems(goal_file="GoalState.txt", problem_file="Problems.txt"):
    """Returns the default problems for Assignment 1."""
    with open("GoalState.txt") as file:
        goal = file.read().strip()
    problem = problems.TileProblem(goal)

    with open("Problems.txt") as file:
        contents = file.readlines()
    states = [state.strip() for state in contents]

    return problem, states


def make_pdbs(
        puzzle_no: int, strengths: list[int],
        problem: problems.Problem) -> dict[int:dict[tuple[int]:dict[str:int]]]:
    """Constructs abstracted PDBs for a problem space."""
    pdbs = {}
    goal = str(problem)
    for strength in strengths:
        pdbs[strength] = {}
        for pattern in choose_n(puzzle_no, strength):
            print(f"Constructing PDB by merging these tile IDs: {pattern}")
            new_goal = abstractify(goal, pattern)
            pdbs[strength][pattern] = search.make_pdb(new_goal, problem)
    return pdbs


def get_pdbs(
        filename: str, puzzle_no: int, strengths: list[int],
        problem: problems.Problem) -> dict[int:dict[tuple[int]:dict[str:int]]]:
    """Attempts to retrieve PDB file. If not found, makes from scratch."""
    goal = str(problem)
    if os.path.isfile(filename):
        with open(filename) as file:
            print("Reading existing PDB file...")
            pdbs_string = file.read()
        print("Loading PDBs (this may take a few minutes)...")
        pdbs = ast.literal_eval(pdbs_string)
        print("PDBs loaded.")

    else:
        print("Generating PDBs from scratch - this will take a wee while.")
        pdbs = make_pdbs(puzzle_no, strengths, problem)
        print("All PDBs constructed.")
        print("Writing PDBs to file for later...")
        with open(filename, "w") as file:
            file.write(str(pdbs))


def run_experiments(initial_states,
                    problem,
                    puzzle_no,
                    strengths,
                    sizes,
                    pdbs=None,
                    runs=100):
    """Runs experiments for Assignment 1."""
    if pdbs == None:
        pdbs = make_pdbs(puzzle_no, strengths, problem)
    patterns = {
        strength: choose_n(puzzle_no, strength)
        for strength in strengths
    }
    results = []

    for strength in strengths:
        for size in sizes:
            sample_size = int(len(patterns[strength]) * size)
            for problem_no, state in enumerate(initial_states):
                means = []
                stdevs = []
                for _ in range(runs):
                    h_values = []
                    for pattern in random.sample(patterns[strength],
                                                 sample_size):
                        pdb = pdbs[strength][pattern]
                        abstract_state = abstractify(state, pattern)
                        abstract_state = problem.canonical(abstract_state)
                        h_values.append(pdb[abstract_state])
                    means.append(statistics.mean(h_values))
                    stdevs.append(statistics.stdev(h_values))
                mean = statistics.mean(means)
                mean_stdev = statistics.mean(stdevs)
                results.append((size, strength, problem_no, mean, mean_stdev))

    return results


def write_to_excel(results, filename, sheetname):
    """Writes Assignment 1 results to an Excel sheet."""
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook[sheetname]

    for size, strength, problem_no, mean, stdev in results:
        mean_cell = excel_cell_A1(size, strength, problem_no, False)
        stdev_cell = excel_cell_A1(size, strength, problem_no, True)
        sheet[mean_cell] = mean
        sheet[stdev_cell] = stdev

    for col in "CDEFGH":
        row = 27
        for _ in range(len(sizes)):
            sheet[col + str(row)] = f"=AVERAGE({col}{row-25}:{col}{row-1})"
            row += 27
    for col in "CEG":
        row = 28
        for _ in range(len(sizes)):
            sheet[col + str(row)] = f"={col}{row-1}/20"
            row += 27

    workbook.save(filename)


def main(use_file=True):
    """Completes data generation for Assignment 1.
    Assumes GoalState.txt, Problems.txt, and ExperimentalData.xlsx are in the
    same directory, in the form they were provided on Canvas.
    Takes a few minutes at best - you might want to put the kettle on.
    """
    random.seed(42)  # I used 42 for the experiments
    problem, states = a1_problems()
    puzzle_no = 8  # For the 8-puzzle, this is set to 8
    strengths = [7, 5, 3]

    # WARNING: This will use up hundreds of megabytes with default settings.
    # It will save a couple of minutes' execution next time, however.
    # Choose wisely.
    if use_file:
        pdbs = get_pdbs("PDBs.txt", puzzle_no, strengths, problem)
    else:
        pdbs = make_pdbs(puzzle_no, strengths, problem)

    print("Running experiments...")
    results = run_experiments(states, problem, puzzle_no, strengths, sizes,
                              pdbs)
    print("Experiments finished. Recording results...")
    write_to_excel(results, "ExperimentalData.xlsx", "Sheet1")
    print("Done!")


if __name__ == "__main__":
    main()
