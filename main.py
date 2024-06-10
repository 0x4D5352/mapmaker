from random import choice, sample
from time import sleep
from datetime import date
from itertools import count
from os import system

map_tiles = {
    "land": "🟩",
    "water": "🟦",
    "desert": "🟨",
    "mountain": "🟫",
    "snow": "⬜️",
}
tile_weightings = {
    "land": 0.7,
    "water": 0.8,
    "desert": 0.2,
    "mountain": 0.2,
    "snow": 0.1,
}
x_mark = "❎"
active_cell = "🟪"
lock_framerate = False
fps = 120
framerate = 1 / fps
counter = count()


def grab_random_tile(tiles: dict, weights: dict = tile_weightings) -> str:
    weighted_tiles = [int(weight * 10) for weight in weights.values()]
    return tiles[choice(sample(list(tiles), k=1, counts=weighted_tiles))]


def find_neighbors(current_map: list, current_column: int, current_row: int) -> list:
    neighbors = []
    if current_column != 0:
        neighbors.append(current_map[current_column - 1][current_row])
    if current_column != len(current_map) - 1:
        neighbors.append(current_map[current_column + 1][current_row])
    if current_row != 0:
        neighbors.append(current_map[current_column][current_row - 1])
    if current_row != len(current_map[0]) - 1:
        neighbors.append(current_map[current_column][current_row + 1])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = [neighbor for neighbor in neighbors if neighbor != x_mark]
    options.append(grab_random_tile(tiles))
    return choice(options)


def generate_random_neighbor(tiles: dict, grid: list) -> list:
    for c_index, cols in enumerate(grid):
        for r_index, _ in enumerate(cols):
            if c_index == 0 and r_index == 0:
                grid[c_index][r_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(grid, c_index, r_index)
                grid[c_index][r_index] = select_neighbor(neighbors, tiles)
            print_running_map(grid)
    return grid


def grid_wrapper(x: int, table: list) -> int:
    return x % len(table)


def find_nearest_x(col: int, row: int, grid: list) -> tuple:
    x_col = col
    x_row = row

    while grid[x_col][x_row] != x_mark:
        x_col = grid_wrapper((x_col + choice([1, 0, -1])), grid)
        x_row = grid_wrapper((x_row + choice([1, 0, -1])), grid[0])
    return x_col, x_row


def generate_wandering_neighbor(tiles: dict, grid: list) -> list:
    new_grid = grid
    cardinality = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    current_column = choice(range(len(new_grid)))
    current_rows = choice(range(len(new_grid[0])))
    new_grid[current_column][current_rows] = grab_random_tile(tiles)
    visited = [(current_column, current_rows)]
    while any(x_mark in rows for rows in new_grid):
        current_cell = new_grid[current_column][current_rows]
        new_grid[current_column][current_rows] = active_cell
        print_running_map(new_grid, visited)
        # choose a direction
        options = [
            (
                grid_wrapper((current_column + x), new_grid),
                grid_wrapper((current_rows + y), new_grid[0]),
            )
            for x, y in cardinality
            if (
                grid_wrapper(current_column + x, new_grid),
                grid_wrapper(current_rows + y, new_grid[0]),
            )
            not in visited
        ]
        next_column, next_rows = (
            choice(options)
            if len(options) > 0
            else find_nearest_x(current_column, current_rows, new_grid)
        )
        if new_grid[next_column][next_rows] == x_mark:
            new_grid[current_column][current_rows] = current_cell
            new_grid[next_column][next_rows] = select_neighbor(
                find_neighbors(new_grid, next_column, next_rows), tiles
            )
            current_column, current_rows = next_column, next_rows
            visited.append((current_column, current_rows))
        print_running_map(new_grid, visited)
    return new_grid


def create_map(
    tiles: dict = map_tiles,
    columns: int = 0,
    rows: int = 0,
    strategy=generate_random_neighbor,
) -> list:
    columns = 5 if columns <= 0 else columns
    rows = columns if rows <= 0 else rows
    grid = [[x_mark for _ in range(columns)] for _ in range(rows)]
    grid = strategy(tiles, grid)
    return grid


def print_map(map: list) -> str:
    res = ""
    for col in map:
        res += "\n"
        for row in col:
            res += row
    res += "\n"
    return res


def print_running_map(grid: list, visited: list = []) -> None:
    area = len(grid) * len(grid[0])
    system("clear")
    print("completing map...")
    num_visited = len(visited)
    if num_visited > 0:
        # print(sorted(visited))
        print(f"currently at: {visited[-1][0]},{visited[-1][1]}")
        print(f"{num_visited} out of {area} seen")
        print(f"{(num_visited / area) * 100:.2f}% complete!")
    print(print_map(grid))
    if lock_framerate:
        sleep(framerate)


def get_map_dimensions() -> tuple:
    def get_dimension(dimension: str) -> int:
        try:
            value = int(input(f"How {dimension} do you want your map to be?\n> "))
        except:
            raise ValueError
        return value

    columns = get_dimension("wide")
    rows = get_dimension("tall")
    return columns, rows


def choose_strategy():
    strategies = [generate_random_neighbor, generate_wandering_neighbor]
    try:
        choice = strategies[
            int(
                input(
                    f"Select your map strategy:\n{", ".join([name.__str__().split(" ")[1] for name in strategies])}\n> "
                )
            )
            - 1
        ]
    except:
        raise ValueError
    return choice


def save_map(map) -> None:
    with open(
        f"{date.today()}_map_{next(counter)}.emoji", "w", encoding="utf-8"
    ) as image:
        image.write(map)
    print("saved!")


def main() -> None:
    strategy = choose_strategy()
    columns, rows = get_map_dimensions()
    map = print_map(create_map(map_tiles, columns, rows, strategy))
    system("clear")
    print("map completed!\nmap:")
    print(map)
    save = input("Save? Y/N\n>")
    if len(save) > 0:
        if "Y" in save.upper():
            save_map(map)
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()
    print("thanks for playing! have a nice day 😄")
    exit(0)


if __name__ == "__main__":
    main()
