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
> .\kaivuri.bat 1.4.2024

Puzzle:
T A T L E 
M Y L E T
P I P T T
I E Y Ä Ä
K U P I H
A A T A I

Solving for least words...
3 solutions found...

tympeyttää   tallete      piikata      hiipua
t . . . .    . a t l e    . . . . .    . . . . .
m y . . .    . . l e t    . . . . .    . . . . .
p . . t t    . . . . .    . i p . .    . . . . .
. e y ä ä    . . . . .    i . . . .    . . . . .
. . . . .    . . . . .    k . . . .    . u p i h
. . . . .    . . . . .    . a t a .    a . . . i
```
The app will fetch the puzzle from the Helsingin Sanomat api and solve the puzzle. By default it will find the solution with the least amount of words. 

Alternatively the puzzle letters can be given as a string to the solver:
```
> .\kaivuri.bat PELLEHÄLLIYHÄETIKMYTTUTÄMYKSET
Puzzle:
P E L L E 
H Ä L L I
Y H Ä E T
I K M Y T
T U T Ä M
Y K S E T

Solving for least words...
4 solutions found...

pelleillä    hyhmettyä    kituset      mätky
p e l l e    . . . . .    . . . . .    . . . . . 
. ä l l i    h . . . .    . . . . .    . . . . .
. . . . .    y h ä e t    . . . . .    . . . . .
. . . . .    . . m y t    i k . . .    . . . . .
. . . . .    . . . . .    t u . . .    . . t ä m
. . . . .    . . . . .    . . s e t    y k . . .
```

The supported solve modes are `least_words`, `most_words`, `any` and `all`. The desired solve mode can be defined using the `--solve-mode` parameter:
```
kaivuri.bat 11.4.2024 --solve-mode=all
```

## Model
Each grid cell is assigned a unique id from $C = \{ 1,2,\ldots,30 \}$. Then, each word $W_i \subseteq C$ present in the grid can be represented as a subset  of the cell ids. $W = \{W_1, W_2, \ldots, W_N\}$ is the set of all possible words in the grid. Notice that the we don't care about the letters, only about the cells belonging to a word. Generation of $W$ is discussed later.

A solution $S \subseteq W$ to the puzzle is then a subset of words that 1) don't overlap and 2) cover each cell in the grid. In other words, the intersection of words $W_i \in S$ is empty and the union of words $W_i \in S$ is equal to $C$:
$$
\bigcap_{S_i \in S} S_i = \varnothing \text{ and }
\bigcup_{S_i \in S} S_i = C
$$

The problem can be modeled as a [Boolean satisfiability problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem) (SAT).

### SAT
Variables $w_1,w_2,\ldots,w_N$ and $c_1,c_2,\ldots,c_{30}$ are introduced for the SAT problem. Here, $w_i$ stands for "$W_i$ is present in the solution", and $c_i$ stands for "cell $i$ is covered by some word". The following clauses should be satisfied in order to find a solution:

1. Every cell is covered by some word:
$$
  \bigwedge_{i \in C} c_i
$$

2. If a word is in the solution, then all cells in that word must be covered:
$$
  \bigwedge_{i \in [1,N]} (w_i \rightarrow \bigwedge_{j \in W_i}c_j)
$$

3. If a cell is covered, then at least one of the words containing that cell must be in the solution:
$$
  \bigwedge_{i \in C} (c_i \rightarrow  \bigvee_{\{ j \text{ : } C_i \in W_j \}} w_j )
$$

4. No two words in the solution can intersect:
$$
\bigwedge_{i \in [1,N]} (w_i \rightarrow \bigwedge_{\{ j \text{ : } W_j \cap W_i \neq \varnothing, i \neq j \}} \neg w_j)
$$

Final step is to define the clauses in [conjunctive normal form](https://en.wikipedia.org/wiki/Conjunctive_normal_form) (CNF). The formula in CNF form is then fed to a SAT-solver. I'm using [PySAT](https://pysathq.github.io/) for solving the puzzle.
