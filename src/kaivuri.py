from dictionary import Dictionary
from pysat.formula import CNF
from pysat.solvers import Solver
import dlx
import time


def custom_timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper


class Grid:
  def __init__(self, puzzle, rows=6, cols=5):
    assert len(puzzle) == rows * cols
    self.rows = rows
    self.cols = cols
    self.letters = puzzle.lower().strip().replace(" ", "").replace("\n", "")
    self.C = {(x,y) : self.letters[self.cols * y + x] for x in range(cols) for y in range(rows)}

  def get_word(self, path):
    return "".join([self.letters[self.cols * y + x] for x,y in path])

  
class Kaivuri:
  def __init__(self, puzzle, dictionary = Dictionary("finnish_dictionary.txt")):
    self.dictionary = dictionary
    self.grid = Grid(puzzle)
    self.init_W()


  def print_banner(self):
    words = set()
    for w in self.W.values():
      for wi in w:
        words.add(wi)

    print(f"""
┏┓      ┓   •      •
┗┓┏┓┏┓┏┓┃┏┏┓┓┓┏┓┏┏┓┓
┗┛┗┻┛┗┗┻┛┗┗┻┗┗┛┗┻┛ ┗
""")

    
    self.print_problem()
    print()
    print(f"""                     
Number of unique words: {len(words)}
Number of tiles       : {len(self.W)}""")

  def init_W(self):
    self.W = {}
    def init_W_inner(path):
      word = self.grid.get_word(path)

      if not self.dictionary.contains_prefix(word):
        return
      elif self.dictionary.contains(word):
        sorted_path = tuple(sorted(path))
        if sorted_path not in self.W:
          self.W[sorted_path] = set([word])
        else:
          self.W[sorted_path].add(word)

      x, y = path[-1]

      for dx in [-1,0,1]:
        for dy in [-1,0,1]:
          next = (x + dx, y + dy)
          if next in path or not next in self.grid.C:
            continue
          init_W_inner(path + [next])

    for ci in self.grid.C:
      init_W_inner([ci])


  def build_cnf(self):
    def vars():
      num = 1
      while True:
          yield num
          num += 1
    var_gen = vars()

    # Variables  
    w = { Wi : next(var_gen) for Wi in self.W }
    c = { Ci : next(var_gen) for Ci in self.grid.C }
    
    # Inverse mapping, needed later
    # self.c2C = { ci : Ci for Ci, ci in c.items() }
    self.w2W = { wi : Wi for Wi, wi in w.items() }

    # Clauses
    clauses = []

    # 1. Every cell is covered by some word
    for Ci in self.grid.C:
      clauses.append([c[Ci]]) # c1 & c2 & ... & c30

    # 2. If a word is in the solution, then all cells in that word must be covered
    for Wi in self.W:
      clauses.extend([[-w[Wi], c[Cj]] for Cj in Wi]) # (!wi | cx) & (!wi | cy) & (!wi | cz) & ...

    # 3. If a cell is covered, then at least one of the words containing that cell must be in the solution
    C2W = {Ci : [Wi for Wi in self.W if Ci in Wi] for Ci in self.grid.C}
    for Ci in self.grid.C:
      clauses.append([-c[Ci]] + [w[Wi] for Wi in C2W[Ci]]) # (!ci | wx | wy | wz | ...)

    # 4. No two words in the solution can intersect
    W2W = {Wi : [Wj for Wj in self.W if Wi != Wj and set(Wi) & set(Wj)] for Wi in self.W}
    for Wi in self.W:
      for Wj in W2W[Wi]:
        clauses.append([-w[Wi], -w[Wj]]) # (!wi | !wj)

    return CNF(from_clauses=clauses)


  def solve_all(self, solver):
    solutions = []
    for i, solution in enumerate(solver):
      print(f"Number of solutions   : {i + 1}\r", end='', flush=True)
      solutions.append(solution)
    print("")

    solutions = sorted(solutions, key=lambda solution: len(solution))

    return solutions


  def solve_any(self, solver):
    return [next(solver)]


  def solve_least_words(self, solver):
    return self.solve_all(solver)[:1]


  def solve_most_words(self, solver):
    return self.solve_all(solver)[-1:]


  def get_algx_solver(self):
    # Reduce to exact cover problem
    U = list(self.grid.C.keys())
    S = list(self.W.keys())

    # Solve ECP
    for ecp_solution in dlx.solve_algx(U, S):
      solution = {}
      for i in ecp_solution:
        solution[S[i]] = self.W[S[i]]
      yield solution


  def get_dlx_solver(self):
    # Reduce to exact cover problem
    U = list(self.grid.C.keys())
    S = list(self.W.keys())

    # Solve ECP
    for ecp_solution in dlx.solve_dlx(U, S):
      solution = {}
      for i in ecp_solution:
        solution[S[i]] = self.W[S[i]]
      yield solution


  def get_sat_solver(self):
    # Reduce to CNF-SAT
    cnf = self.build_cnf()

    # Solve SAT
    with Solver(bootstrap_with=cnf) as solver:
      solver.solve()
      for model in solver.enum_models():
        solution = {}
        for var in model:
          if var > 0 and var <= len(self.W):
            wi = var
            Wi = self.w2W[wi]
            solution[Wi] = self.W[Wi]
        yield solution


  def get_solver(self, solver_type):
    if solver_type == "algx":
      return self.get_algx_solver()
    if solver_type == "dlx":
      print("dlx selected")
      return self.get_dlx_solver()
    else:
      return self.get_sat_solver()


  @custom_timer
  def solve(self, solver_type="algx", mode="least_words"):
    solver = self.get_solver(solver_type)

    if mode == "all":
      return self.solve_all(solver)
    if mode == "any":
      # print("Solving for any solution...")
      return self.solve_any(solver)
    if mode == "least_words":
      # print("Solving for least words...")
      return self.solve_least_words(solver)
    if mode == "most_words":
      # print("Solving for most words...")
      return self.solve_most_words(solver)
    

  def print_problem(self):
    for y in range(self.grid.rows):
      print("   ", end="")
      for x in range(self.grid.cols):
        print(f'{self.grid.C[(x,y)].upper()}  ', end="")
      print("")


  def visualize(self, solutions):
    def buffer_Wi(Wi, i, buffer):
      for x, c in enumerate(', '.join(map(str,self.W[Wi]))):
        bx = i*(2*self.grid.cols + SPACING) + x
        if bx < len(buffer[0]):
          buffer[0][bx] = c

      for y in range(self.grid.rows):
        for x in range(self.grid.cols):
          Ci = (x,y)
          bx = i*(2*self.grid.cols + SPACING) + 2 * x
          by = y + 1
          if Ci in Wi:
            buffer[by][bx] = self.grid.C[Ci]
          else:
            buffer[by][bx] = '.'

    SPACING = 3
    for i, solution in enumerate(solutions):
      # print(f"Solution {i}")
      n_cols = 2 * len(solution) * 5 + (len(solution) - 1) * SPACING
      n_rows = self.grid.rows + 1
      buffer = [n_cols*[' '] for _ in range(n_rows)]
      for j,Wi in enumerate(solution):
        buffer_Wi(Wi,j,buffer)

      for row in buffer:
        for c in row:
          print(f'{c}', end="")
        print("")
      print("")