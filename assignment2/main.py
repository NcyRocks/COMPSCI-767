import math
import os
import statistics
import string
import sys
from typing import Any, Union
import matplotlib.pyplot as plt

import openpyxl

sys.path.append(os.path.relpath("../"))
import problems
import search

Number = Union[int, float]

c_stars = [10, 15, 20]
weights = [4, 8, 16, 24]


def rho(bound1, bound2, cost, c_star):
    try:
        numerator = math.log(bound1) - math.log(cost/c_star)
        denominator = math.log(bound2) - math.log(cost/c_star)
        return numerator / denominator
    except ZeroDivisionError:
        return 1


def main():
    """Performs data generation for Assignment 2.
    Assumes GoalState.txt and Problems[C*].txt are in the same directory,
    in the form they were provided on Canvas.
    """

    with open("GoalState.txt") as file:
        goal = file.read().strip()
    problem = problems.TileProblem(goal)
    h = problem.manhattan_distance

    Side = openpyxl.styles.borders.Side
    border_style = openpyxl.styles.borders.Border(right=Side(style="medium"),
                                                  bottom=Side(style="medium"))
    headings = [
        "Problem", "C", "C/C*", "F/Iter", "g_min/Iter", "FBound", "XBound",
        "FB/XB", "Exceptn"
    ]

    for c_star in c_stars:
        with open(f"Problems{c_star}.txt") as file:
            contents = file.readlines()
        states = [state.strip() for state in contents]
        for w in weights:
            print(f"Analysing problems with C*={c_star} using W={w}")
            filename = f"Results{c_star}.{w:02}.xlsx"

            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Sheet1"

            for index, heading in enumerate(headings):
                letter = string.ascii_uppercase[index]
                sheet[f"{letter}1"] = heading
                sheet[f"{letter}1"].border = border_style
                if index not in [3, 4, 8]:
                    sheet[f"{letter}27"] = f"=AVERAGE({letter}2:{letter}26)"
                    sheet[f"{letter}28"] = f"=STDEVPA({letter}2:{letter}26)"

            sheet["A27"] = "mean"
            sheet["A28"] = "SD"

            for problem_number, state in enumerate(states):
                results = search.weighted_a_star_with_bounds(
                    state, problem, h, w)
                C, _, F, f_iter, g_min, g_iter, f_bound, x_bound = results
                inputs = [
                    problem_number + 1, C, C / c_star, f"{F}/{f_iter}",
                    f"{g_min}/{g_iter}", f_bound, x_bound, f_bound / x_bound
                ]

                for index, cell_contents in enumerate(inputs):
                    letter = string.ascii_uppercase[index]
                    sheet[f"{letter}{problem_number + 2}"] = cell_contents
                if f_bound < x_bound:
                    sheet[f"I{problem_number + 2}"] = "XXX"

            workbook.save(filename)


if __name__ == "__main__":
    main()
