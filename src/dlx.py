# Implementation of dancing links
import numpy as np


class Node(object):
    pass


def link_horizontally(nodes):
  prev = None
  for n in nodes:
    if prev:
      n.L = prev
      prev.R = n
    prev = n
  nodes[0].L = prev
  prev.R = nodes[0]


def link_vertically(nodes):
  prev = None
  for n in nodes:
    if prev:
      n.U = prev
      prev.D = n
    prev = n
  nodes[0].U = prev
  prev.D = nodes[0]


def build_dlx(U,S):
  M = np.array([[ui in set(si) for ui in U] for si in S])
  M = M.astype(bool)

  m, n = M.shape # rows, cols

  # Root node h
  h = Node()

  # Header nodes
  header = [Node() for _ in range(n)]

  # Data nodes
  data = [[Node() if M[r, c] else None for c in range(n)] for r in range(m)]

  # Create header meta data
  for i, node in enumerate(header):
    node.S = sum([1 if data[row][i] else 0 for row in range(m)])
    node.C = node
    node.N = i

  # Link header
  link_horizontally([h] + header)

  # Vertical links
  for ci, node in enumerate(header):
    column_nodes = [node] + [data[row][ci] for row in range(m) if data[row][ci]]
    link_vertically(column_nodes)

   # Link to header
  for ci, node in enumerate(header):
    for row in range(m):
      if data[row][ci]:
        data[row][ci].C = node
        data[row][ci].ID = row

  # Horizontal links
  for row in data:
    row_nodes = [node for node in row if node]
    link_horizontally(row_nodes)

  return h


def cover(c):
  c.R.L = c.L
  c.L.R = c.R
  i = c.D
  while i != c:
    j = i.R
    while j != i:
      j.D.U = j.U
      j.U.D = j.D
      j.C.S = j.C.S - 1
      j = j.R
    i = i.D


def uncover(c):
  i = c.U
  while i != c:
    j = i.L
    while j != i:
      j.C.S = j.C.S + 1
      j.D.U = j
      j.U.D = j
      j = j.L
    i = i.U
  c.R.L = c
  c.L.R = c

# A horrible implementation of Dancing Links
# Implementation mirrors quite slavisly the syntax
# of the paper... Terrible for memory I would assume.
# This probably would work better on really sparse matrices.
# Better than SAT atleast.
def solve_dlx(U, S):
  # Root node
  h = build_dlx(U, S)

  def search(res = []):
    if h.R == h:
      yield res
      return
    
    # Select c
    j = h.R
    s = j.S
    c = j
    while j != h:
      if j.S < s:
        c = j
        s = j.S
      j = j.R

    # Cover c
    cover(c) # Should be fine

    r = c.D
    while r != c:
      # Cover
      j = r.R
      while j != r:
        cover(j.C)
        j = j.R
      
      # Recurse
      yield from search(res + [r.ID])
      c = r.C

      # Uncover
      j = r.L
      while j != r:
        uncover(j.C)
        j = j.L
      r = r.D
    uncover(c)

  return search()


# Naive implementation of Knuth's Algorithm X
def solve_algx(U, S):
  """
  U: universe
  S: subsets of U
  """

  M = np.array([[ui in set(si) for ui in U] for si in S])
  M = M.astype(bool)

  def search(m, labels, path = []):
    if m.shape[1] == 0:
      yield path
      return
    
    # Counts of 1s in columns
    counts = np.sum(m, axis=0)

    # Column with lowers number of 1s
    c = np.argmin(counts)

    if counts[c] == 0:
      return False

    # Rows with 1 at col c
    rs = np.where(m[:, c])[0]

    for r in rs:
      cols_to_remove = m[r, :]
      rows_to_remove = np.any(m[:,cols_to_remove], axis=1)

      # Specify rows to keep
      cols_to_keep = np.logical_not(cols_to_remove)
      rows_to_keep = np.logical_not(rows_to_remove)

      # Recurse
      m_next = m[rows_to_keep,:][:,cols_to_keep]
      yield from search(m_next, labels[rows_to_keep], path + [labels[r]])

  return search(M, np.arange(M.shape[0]))