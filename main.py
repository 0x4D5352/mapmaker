from random import choice, sample
from time import sleep
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
    "snow": 0.2,
}
x_mark = "❎"
active_cell = "🟪"
fps = 120
framerate = 1 / fps


def grab_random_tile(tiles: dict, weights: dict = tile_weightings) -> str:
    weighted_tiles = [int(weight * 10) for weight in weights.values()]
    return tiles[choice(sample(list(tiles), k=1, counts=weighted_tiles))]


def find_neighbors(current_map: list, current_row: int, current_column: int) -> list:
    neighbors = []
    if current_column != 0:
        neighbors.append(current_map[current_row][current_column - 1])
    if current_column != len(current_map[0]) - 1:
        neighbors.append(current_map[current_row][current_column + 1])
    if current_row != 0:
        neighbors.append(current_map[current_row - 1][current_column])
    if current_row != len(current_map) - 1:
        neighbors.append(current_map[current_row + 1][current_column])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = [neighbor for neighbor in neighbors if neighbor != x_mark]
    options.append(grab_random_tile(tiles))
    return choice(options)


def generate_random_neighbor(tiles: dict, grid: list) -> list:
    for r_index, row in enumerate(grid):
        for c_index, _ in enumerate(row):
            if r_index == 0 and c_index == 0:
                grid[r_index][c_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(grid, r_index, c_index)
                grid[r_index][c_index] = select_neighbor(neighbors, tiles)
            print_running_map(grid)
    return grid


def grid_wrapper(x: int, table: list) -> int:
    return x % len(table)


def find_nearest_x(row: int, col: int, grid: list) -> tuple:
    x_row = row
    x_col = col

    while grid[x_row][x_col] != x_mark:
        x_row = grid_wrapper((x_row + choice([1, 0, -1])), grid)
        x_col = grid_wrapper((x_col + choice([1, 0, -1])), grid)
    return x_row, x_col


def generate_wandering_neighbor(tiles: dict, grid: list) -> list:
    new_grid = grid
    cardinality = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    current_row = choice(range(len(new_grid)))
    current_column = choice(range(len(new_grid[0])))
    new_grid[current_row][current_column] = grab_random_tile(tiles)
    visited = [(current_row, current_column)]
    while any(x_mark in column for column in new_grid):
        current_cell = new_grid[current_row][current_column]
        new_grid[current_row][current_column] = active_cell
        print_running_map(new_grid, visited)
        # choose a direction
        options = [
            (
                grid_wrapper((current_row + x), new_grid),
                grid_wrapper((current_column + y), new_grid),
            )
            for x, y in cardinality
            if (
                grid_wrapper(current_row + x, new_grid),
                grid_wrapper(current_column + y, new_grid),
            )
            not in visited
        ]
        next_row, next_column = (
            choice(options)
            if len(options) > 0
            else find_nearest_x(current_row, current_column, new_grid)
        )
        if new_grid[next_row][next_column] == x_mark:
            new_grid[current_row][current_column] = current_cell
            new_grid[next_row][next_column] = select_neighbor(
                find_neighbors(new_grid, next_row, next_column), tiles
            )
            current_row, current_column = next_row, next_column
            visited.append((current_row, current_column))
        print_running_map(new_grid, visited)
    return new_grid


def create_map(
    tiles: dict = map_tiles,
    rows: int = 0,
    columns: int = 0,
    strategy=generate_random_neighbor,
) -> list:
    rows = 5 if rows <= 0 else rows
    columns = rows if columns <= 0 else columns
    grid = [[x_mark for _ in range(rows)] for _ in range(columns)]
    grid = strategy(tiles, grid)
    return grid


def print_map(map: list) -> str:
    res = ""
    for row in map:
        res += "\n"
        for col in row:
            res += col
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
    sleep(framerate)


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
    print(
        f"{print_map(create_map(map_tiles, rows, columns, generate_wandering_neighbor))}"
    )
    print("\n")
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()
    print("thanks for playing! have a nice day 😄")
    exit(0)


if __name__ == "__main__":
    main()
