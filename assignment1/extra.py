import random

import main


def main():
    """Attempts to plot the relationship between strength of heuristic and compression ratio."""
    random.seed(42)  # I used 42 for the experiments
    problem, states = main.a1_problems()
    puzzle_no = 8  # For the 8-puzzle, this is set to 8
    strengths = [8, 7, 6, 5, 4, 3, 2, 1]

    main.get_pdbs("BIG_PDBS.txt", puzzle_no, strengths, problem)


if __name__ == "__main__":
    main()
