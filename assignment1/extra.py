import ast
import os
import random
import statistics

import numpy
from matplotlib import pyplot as plt

import main as main_file


def main():
    """Attempts to plot the relationship between strength of heuristic and compression ratio."""
    random.seed(42)  # I used 42 for the experiments
    problem, states = main_file.a1_problems()
    puzzle_no = 8  # For the 8-puzzle, this is set to 8
    strengths = [8, 7, 6, 5, 4, 3, 2, 1]

    # Can't save pdbs to file; too big!
    # Next best thing: saving the results
    if os.path.isfile("results.txt"):
        with open("results.txt") as file:
            contents = file.read()
        results = ast.literal_eval(contents)
    else:
        results = main_file.run_experiments(states, problem, 8, strengths, [1])
        with open("results.txt", "w") as file:
            file.write(str(results))

    means = {strength: [] for strength in strengths}
    stdevs = {strength: [] for strength in strengths}
    for size, strength, problem_no, mean, stdev in results:
        means[strength].append(mean)
        stdevs[strength].append(stdev)

    for strength in strengths:
        means[strength] = statistics.mean(means[strengths])
        stdevs[strength] = statistics.mean(stdevs[strengths])

    mean_list = []
    stdev_list = []
    for i in range(1, 9):
        mean_list.append(means[i])
        stdev_list.append(stdev[i])

    plt.plot(numpy.linspace(0, puzzle_no, puzzle_no), mean_list, label="Means")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
