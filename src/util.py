import requests

def export_solutions(puzzle, solutions, filename):
  f = open(filename, "w")

  f.write(f'{puzzle}\n')
  for solution in solutions:
    strs = [f'{",".join(map(str,selection))} {",".join(map(str,words))}' for selection, words in solution]
    f.write("|".join(map(str, strs)))
    f.write("\n")

  f.close()


def import_solutions(filename):
  puzzle = ""
  solutions = []

  with open(filename) as f:
    puzzle = f.readline().strip()

    for line in f.readlines():
      line = line.strip()
      parts = line.split("|")
      solution = []
      for part in parts:
        cells, words = part.split(" ")
        cells = [int(i) for i in cells.split(",")]
        words = words.split(",")
        solution.append((cells, words))
      solutions.append(solution)
  f.close()

  return puzzle, solutions


def fetch_sanalouhos(date):
    try:
      url = f'https://sanalouhos.datadesk.hs.fi/api/game/{date}'
      response = requests.get(url)
      response.raise_for_status()
      json_data = response.json()
      return "".join(json_data['item']['gameCharArray'])
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None