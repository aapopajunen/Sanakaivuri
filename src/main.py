import argparse


from kaivuri import Kaivuri
import util

def get_puzzle(puzzle_string):
  parts = puzzle_string.split(".")
  if len(parts) == 3:
    try:
       return util.fetch_sanalouhos(puzzle_string)
    except Exception as e:
      print("An error occurred:", e)
  return puzzle_string

def get_solution_string(solve_mode):
   if solve_mode == "all":
      return "All solutions:"
   if solve_mode == "any":
      return "First solution found:"
   if solve_mode == "least_words":
      return "Solution with least words:"
   if solve_mode == "most_words":
      return "Solution with most words:"

def main():
  parser = argparse.ArgumentParser(description="Sanakaivuri is automatic solver for the word puzzle Sanalouhos published daily by Helsingin Sanomat.")
  parser.add_argument("puzzle", help="Puzzle string (i.e. \"ktatmauaiaajveloaatlrasaameakk\") or date (i.e. \"11.4.2024\").")
  parser.add_argument("--solve-mode", choices=["all", "any", "least_words", "most_words"], default="least_words", help="Solve mode")
  parser.add_argument("--solver", choices=["sat", "dlx", "algx", "cdlx"], default="algx", help="Solve mode")

  args = parser.parse_args()

  puzzle = get_puzzle(args.puzzle)

  kaivuri = Kaivuri(puzzle)
  kaivuri.print_banner()
  

  solutions, t = kaivuri.solve(args.solver, args.solve_mode)

  print(f'Solve time            : {1000 * t:.2f} ms\n\n')

  print(get_solution_string(args.solve_mode))
  kaivuri.visualize(solutions)
  print()

if __name__ == "__main__":
    main()