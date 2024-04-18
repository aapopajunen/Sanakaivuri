# Sanakaivuri
*Ruining the fun of puzzle solving!*

Sanakaivuri is a solver for the puzzle [**Sanalouhos**](https://sanalouhos.datadesk.hs.fi/) published daily by [Helsingin Sanomat](https://hs.fi).


In Sanalouhos you're given 6x5 grid of letters. The task is to connect cells and find words in the grid. Words can be formed by connecting cells either diagonally, vertically or horizontally. Below is a puzzle and an example solution.

```
Puzzle    | siirtyä   | odottaa   | ala       | pitää     | osittain 
----------|-----------|-----------|-----------|-----------|----------
S I I Y Ä | S I I Y Ä | . . . . . | . . . . . | . . . . . | . . . . .
O O T R T | . . . R T | O O T . . | . . . . . | . . . . . | . . . . .
D A T Ä T | . . . . . | D A T . . | . . . . . | . . . Ä T | . . . . .
A A P I Ä | . . . . . | . A . . . | A . . . . | . . P I Ä | . . . . .
L A T T A | . . . . . | . . . . . | L A . . . | . . . . . | . . T T A
O S I N I | . . . . . | . . . . . | . . . . . | . . . . . | O S I N I
```

## Usage
### Solving a puzzle
```
> .\kaivuri.bat 18.4.2024

┏┓      ┓   •      •
┗┓┏┓┏┓┏┓┃┏┏┓┓┓┏┓┏┏┓┓
┗┛┗┻┛┗┗┻┛┗┗┻┗┗┛┗┻┛ ┗

   T  M  S  I  I
   O  U  L  K  N
   I  E  K  I  A
   I  T  T  A  O
   N  T  T  I  M
   A  A  O  T  I


Number of unique words: 311
Number of tiles       : 735
Number of solutions   : 662
Solve time            : 368.72 ms


Solution with least words:
ilmoittaa    oikein       tuskin       mitoittaa
. m . i .    . . . . .    t . s . i    . . . . .
o . l . .    . . . . .    . u . k n    . . . . .
i . . . .    . e k i .    . . . . .    . . . . a
. t . . .    i . . . o    . . . . .    . . t a .
. t . . .    n . . . .    . . . . .    . . t i m
a a . . .    . . . . .    . . . . .    . . o t i
```
The app will fetch the puzzle from the Helsingin Sanomat api and solve the puzzle. By default it will find the solution with the least amount of words. 

Alternatively the puzzle letters can be given as a string to the solver:
```
> .\kaivuri.bat PELLEHÄLLIYHÄETIKMYTTUTÄMYKSET

┏┓      ┓   •      •
┗┓┏┓┏┓┏┓┃┏┏┓┓┓┏┓┏┏┓┓
┗┛┗┻┛┗┗┻┛┗┗┻┗┗┛┗┻┛ ┗

   P  E  L  L  E
   H  Ä  L  L  I
   Y  H  Ä  E  T
   I  K  M  Y  T
   T  U  T  Ä  M
   Y  K  S  E  T


Number of unique words: 92
Number of tiles       : 231
Number of solutions   : 4
Solve time            : 6.00 ms


Solution with least words:
mätky        kituset      hyhmettyä    pelleillä
. . . . .    . . . . .    . . . . .    p e l l e
. . . . .    . . . . .    h . . . .    . ä l l i
. . . . .    . . . . .    y h ä e t    . . . . .
. . . . .    i k . . .    . . m y t    . . . . .
. . t ä m    t u . . .    . . . . .    . . . . .
y k . . .    . . s e t    . . . . .    . . . . .
```

The supported solve modes are `least_words`, `most_words`, `any` and `all`. Additionally, the tool provides three different solvers: `algx`, `dlg` and `sat`. The desired solve mode and solver can be defined using the `--solve-mode` and `--solver` parameters:

The tool supports four solve modes: `least_words`, `most_words`, `any`, and `all`. Additionally, it
offers three solvers: `algx`, `dlg`, and `sat`. You can specify the desired solve mode and solver
using the `--solve-mode` and `--solver` parameters, like this:
```
kaivuri.bat 11.4.2024 --solve-mode=all --solver=sat
```
By default, `least_words` and `algx` are used for solve mode and solver, respectively.


## Problem
Each grid cell is assigned a unique ID from the set $`C = \{ 1, 2, \ldots, 30 \}`$. Then, each word $W_i \subseteq C$
found within the grid can be represented as a subset of cell IDs. Let $`W = \{ W_1, W_2, \ldots, W_N \}`$ denote the
set of all words present in the grid. It's worth noting that during solving, we're solely concerned with the
spatial arrangement of cells, disregarding the letters forming each word.

A solution $S \subseteq W$ to the puzzle consists of a subset of words that satisfy two conditions: 1) they don't
overlap, and 2) they collectively cover each cell in the grid. In other words, the intersection of words $W_i \in S$
should be empty, and the union of words $W_i \in S$ should equal $C$:
```math
\bigcap_{W_i \in S} W_i = \varnothing \text{ and }
\bigcup_{W_i \in S} W_i = C
```
Hence, the problem is equivalent to the [Exact cover problem](https://en.wikipedia.org/wiki/Exact_cover).

The solvers `algx` and `dlx` directly solve the exact cover problem. In contrast, the `sat` solver first
transforms the problem into a Boolean satisfiability problem [Boolean satisfiability problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem) (SAT)
before solving it. Details of this transformation are discussed below.

### Reduction to SAT
Variables $w_1,w_2,\ldots,w_N$ and $c_1,c_2,\ldots,c_{30}$ are introduced for the SAT problem. Here, $w_i$
stands for "word $W_i$ is present in the solution", and $c_i$ stands for "cell $i$ is covered by some word".
A solution to the puzzle satisfies the following clauses:

1. Every cell is covered by some word:
```math
  \bigwedge_{i \in C} c_i
```

2. If a word is in the solution, then all cells in that word must be covered:
```math
  \bigwedge_{i \in [1,N]} (w_i \rightarrow \bigwedge_{j \in W_i}c_j)
```

3. If a cell is covered, then at least one of the words containing that cell must be in the solution:
```math
  \bigwedge_{i \in C} (c_i \rightarrow  \bigvee_{\{ j \text{ : } C_i \in W_j \}} w_j )
```

4. No two words in the solution can intersect:
```math
\bigwedge_{i \in [1,N]} (w_i \rightarrow \bigwedge_{\{ j \text{ : } W_j \cap W_i \neq \varnothing, i \neq j \}} \neg w_j)
```

Final step is to define the clauses in [conjunctive normal form](https://en.wikipedia.org/wiki/Conjunctive_normal_form) (CNF).
The formula in CNF form is then fed to a SAT-solver. I'm using [PySAT](https://pysathq.github.io/) for solving the puzzle.