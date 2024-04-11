def compare(list1, list2, n=None):
    if n is None:
       n = max(len(list1), len(list2))

    l1 = list1[:n]
    l2 = list2[:n]

    # Iterate over elements pairwise and compare
    for x, y in zip(l1, l2):
        if x < y:
            return -1
        elif x > y:
            return 1
    # If all elements are equal, compare based on length
    if len(l1) < len(l2):
        return -1
    elif len(l1) > len(l2):
        return 1
    else:
        return 0


class Dictionary:
  def __init__(self, filename):
    self.dictionary = []
    with open(filename, 'r', encoding='utf-8') as file:
      for line in file.readlines():
        line = line.strip()
        self.dictionary.append(line)


  def contains(self, word):
    l = 0
    r = len(self.dictionary) - 1

    while l <= r:
      m = (l + r) // 2
      cmp = compare(word, self.dictionary[m])
      if cmp == 1:
        l = m + 1
      elif cmp == -1:
        r = m - 1
      else:
        return True
    return False


  def contains_prefix(self, prefix):
    l = 0
    r = len(self.dictionary) - 1

    while l <= r:
      m = (l + r) // 2
      cmp = compare(prefix, self.dictionary[m], n = len(prefix))
      if cmp == 1:
        l = m + 1
      elif cmp == -1:
        r = m - 1
      else:
        return True
    return False