import argparse

from mainari import Mainari
import util

def parse_puzzle(puzzle_string):
  parts = puzzle_string.split(".")
  if len(parts) == 3:
    try:
       return util.fetch_sanalouhos(puzzle_string)
    except Exception as e:
      print("An error occurred:", e)
  return puzzle_string

def main():
  parser = argparse.ArgumentParser(description="Sanamainari is automatic solver for the word puzzle Sanalouhos published daily by Helsingin Sanomat.")
  parser.add_argument("puzzle", help="Puzzle string (i.e. \"ktatmauaiaajveloaatlrasaameakk\") or date (i.e. \"11.4.2024\").")
  parser.add_argument("--solve-mode", choices=["all", "any", "least_words", "most_words"], default="least_words", help="Solve mode")

  args = parser.parse_args()

  puzzle = parse_puzzle(args.puzzle)

  mainari = Mainari(puzzle)
  print("Puzzle:")
  mainari.print_problem()
  print()

  solutions = mainari.solve(args.solve_mode)

  print()
  mainari.visualize(solutions)

if __name__ == "__main__":
    main()