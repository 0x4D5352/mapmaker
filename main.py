from random import choice, sample
from time import sleep
from os import system

map_tiles = {"land": "🟩", "water": "🟦", "desert": "🟨", "mountain": "🟫"}
tile_weightings = {"land": 0.3, "water": 0.4, "desert": 0.1, "mountain": 0.2}
x_mark = "❎"
fps = 60
framerate = 1 / fps


def grab_random_tile(tiles: dict, weights: dict = tile_weightings) -> str:
    weighted_tiles = [int(weight * 10) for weight in weights.values()]
    return tiles[choice(sample(list(tiles), k=1, counts=weighted_tiles))]


def find_neighbors(current_map: list, current_row: int, current_column: int) -> list:
    neighbors = []
    print(f"currently at: {current_row},{current_column}")
    if current_column != 0:
        neighbors.append(current_map[current_row][current_column - 1])
    if current_column != len(current_map) - 1:
        neighbors.append(current_map[current_row][current_column + 1])
    if current_row != 0:
        neighbors.append(current_map[current_row - 1][current_column])
    if current_row != len(current_map[0]) - 1:
        neighbors.append(current_map[current_row + 1][current_column])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = [neighbor for neighbor in neighbors if neighbor != x_mark]
    options.append(grab_random_tile(tiles))
    return choice(options)


def create_map(tiles: dict = map_tiles, rows: int = 0, columns: int = 0) -> list:
    rows = 5 if rows <= 0 else rows
    columns = rows if columns <= 0 else columns
    grid = [[x_mark for _ in range(rows)] for _ in range(columns)]
    for r_index, row in enumerate(grid):
        for c_index, _ in enumerate(row):
            if r_index == 0 and c_index == 0:
                grid[r_index][c_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(grid, r_index, c_index)
                grid[r_index][c_index] = select_neighbor(neighbors, tiles)
            print(print_map(grid))
            sleep(framerate)
            system("clear")
    return grid


def print_map(map: list) -> str:
    res = ""
    for row in map:
        for col in row:
            res += col
        res += "\n"
    return res


def get_map_dimensions() -> tuple:
    def get_dimension(dimension: str) -> int:
        try:
            value = int(input(f"How {dimension} do you want your map to be?\n> "))
        except:
            raise ValueError()
        return value

    rows = get_dimension("wide")
    columns = get_dimension("tall")
    return rows, columns


def main() -> None:
    rows, columns = get_map_dimensions()
    print(f"{print_map(create_map(map_tiles, rows, columns))}")
    print("\n")
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()
    print("thanks for playing! have a nice day 😄")
    exit(0)


if __name__ == "__main__":
    main()
