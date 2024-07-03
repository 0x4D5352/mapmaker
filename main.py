from random import choice, sample, shuffle
from time import sleep
from datetime import date
from itertools import count
from os import system
from typing import Callable

map_tiles = {
    "land": "🟩",
    "water": "🟦",
    "desert": "🟨",
    "mountain": "🟫",
    "snow": "⬜️",
    "swamp": "🟪",
}

tile_weightings = {
    "land": 0.8,
    "water": 0.9,
    "desert": 0.2,
    "mountain": 0.2,
    "snow": 0.1,
    "swamp": 0.2,
}
# TODO: figure out spacing/sizing for the emojis
numbers = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
}
x_mark = "❎"
active_cell = "❓"
# question_mark = "❓"
lock_framerate = True
fps = 120
framerate = 1 / fps
counter = count()
cardinality = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def grab_random_tile(tiles: dict, weights: dict = tile_weightings) -> str:
    weighted_tiles = [int(weight * 10) for weight in weights.values()]
    return tiles[choice(sample(list(tiles), k=1, counts=weighted_tiles))]


def find_neighbors(current_map: list, current_column: int, current_row: int) -> list:
    neighbors = []
    # orthogonal neighbors
    if current_column != 0:
        neighbors.append(current_map[current_column - 1][current_row])
    if current_column != len(current_map) - 1:
        neighbors.append(current_map[current_column + 1][current_row])
    if current_row != 0:
        neighbors.append(current_map[current_column][current_row - 1])
    if current_row != len(current_map[0]) - 1:
        neighbors.append(current_map[current_column][current_row + 1])
    # diagonal neighbors
    if current_column != 0 and current_row != 0:
        neighbors.append(current_map[current_column - 1][current_row - 1])
    if current_column != len(current_map) - 1 and current_row != 0:
        neighbors.append(current_map[current_column + 1][current_row - 1])
    if current_column != 0 and current_row != len(current_map[0]) - 1:
        neighbors.append(current_map[current_column - 1][current_row + 1])
    if (
        current_column != len(current_map) - 1
        and current_row != len(current_map[0]) - 1
    ):
        neighbors.append(current_map[current_column + 1][current_row + 1])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = [neighbor for neighbor in neighbors if neighbor != x_mark]
    options.append(grab_random_tile(tiles))
    return choice(options)


def grid_wrapper(x: int, table: list) -> int:
    return x % len(table)


def get_random_starting_cell(grid: list) -> tuple:
    return choice(range(len(grid))), choice(range(len(grid[0])))


def find_nearest_x(col: int, row: int, grid: list) -> tuple:
    x_col = col
    x_row = row

    while grid[x_col][x_row] != x_mark:
        x_col = grid_wrapper((x_col + choice([1, 0, -1])), grid)
        x_row = grid_wrapper((x_row + choice([1, 0, -1])), grid[0])
    return x_col, x_row


def generate_scrolling_neighbor_map(tiles: dict, grid: list) -> list:
    new_grid = grid
    for c_index, cols in enumerate(new_grid):
        for r_index, _ in enumerate(cols):
            if c_index == 0 and r_index == 0:
                new_grid[c_index][r_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(new_grid, c_index, r_index)
                new_grid[c_index][r_index] = select_neighbor(neighbors, tiles)
            print_running_map(new_grid)
    return new_grid


def generate_wandering_neighbor_map(tiles: dict, grid: list) -> list:
    new_grid = grid
    current_column, current_row = get_random_starting_cell(new_grid)
    new_grid[current_column][current_row] = grab_random_tile(tiles)
    visited = [(current_column, current_row)]
    while any(x_mark in rows for rows in new_grid):
        current_cell = new_grid[current_column][current_row]
        new_grid[current_column][current_row] = active_cell
        print_running_map(new_grid, visited)
        # choose a direction
        options = [
            (
                grid_wrapper((current_column + x), new_grid),
                grid_wrapper((current_row + y), new_grid[0]),
            )
            for x, y in cardinality
            if (
                grid_wrapper(current_column + x, new_grid),
                grid_wrapper(current_row + y, new_grid[0]),
            )
            not in visited
        ]
        next_column, next_row = (
            choice(options)
            if len(options) > 0
            else find_nearest_x(current_column, current_row, new_grid)
        )
        if new_grid[next_column][next_row] == x_mark:
            new_grid[current_column][current_row] = current_cell
            new_grid[next_column][next_row] = select_neighbor(
                find_neighbors(new_grid, next_column, next_row), tiles
            )
            current_column, current_row = next_column, next_row
            visited.append((current_column, current_row))
        print_running_map(new_grid, visited)
    return new_grid


def generate_wave_function_collapse_map(tiles: dict, grid: list) -> list:
    """
    logic for tile patterns:
    tiles can be next to themselves, otherwise:
    water should only be next to land
    land can be next to anything but snow
    deserts should only be next to mountains or land
    mountains should only be next to land, deserts, or snow.
    snow should only be next to mountains
    swamps should only be next to land, water, and mountains
    """
    tile_patterns = {
        ("land", "land"),
        ("land", "water"),
        ("land", "desert"),
        ("land", "mountain"),
        ("land", "swamp"),
        ("water", "water"),
        ("water", "land"),
        ("water", "swamp"),
        ("desert", "land"),
        ("desert", "desert"),
        ("desert", "mountain"),
        ("mountain", "mountain"),
        ("mountain", "land"),
        ("mountain", "snow"),
        ("mountain", "swamp"),
        ("snow", "snow"),
        ("snow", "mountain"),
        ("swamp", "land"),
        ("swamp", "water"),
        ("swamp", "mountain"),
        ("swamp", "swamp"),
    }

    """
    okay so here's what i need to do:
    - instead of the probability matrix containing the sum of options, it should just contain the options
    - when updating the matrix, it should look into each cell and see if it has a color already.
    - if it does, it should EMIT the patterns are available to any neighbor that is currently an x_mark
    - i need to figure out how to handle intercepts, e.g if opposing neighbors are different colors, the possibilties should be the smallest subset of the two.
    - that way, the lowest entropy cell will be the cell or cells that have the fewest available options.
    - sure it's a bit more expensive, but it will be a more accurate representation of state.

    additional questions:
    - how do i reintroduce weighting?
    - 
    """

    def find_available_patterns(col: int, row: int) -> set:
        available_patterns = set()
        neighbors = find_neighbors(new_grid, col, row)
        for neigbor in neighbors:
            if neigbor != x_mark:
                for pattern in tile_patterns:
                    if pattern[0] == neigbor:
                        available_patterns.add(pattern)
        return available_patterns

    def find_lowest_entropy(possibility_matrix: list) -> tuple:
        lowest_entropy = float("inf")
        lowest_coords = (0, 0)
        for col_index, cols in enumerate(possibility_matrix):
            for row_index, entropy in enumerate(cols):
                if entropy < lowest_entropy:
                    lowest_entropy = entropy
                    lowest_coords = (col_index, row_index)
        return lowest_coords

    def update_possibility_matrix(
        current_column: int, current_row: int, possibility_matrix: list
    ) -> list:
        for col_index, cols in enumerate(possibility_matrix):
            for row_index, entropy in enumerate(cols):
                if new_grid[col_index][row_index] == x_mark:
                    available_patterns = find_available_patterns(col_index, row_index)
                    possibility_matrix[col_index][row_index] = (
                        len(available_patterns),
                        available_patterns,
                    )
        return possibility_matrix

    # TODO: create more tile patterns for larger cell clusters
    new_grid = grid
    observed = set()
    possibility_matrix = [
        [len(tile_patterns) for _ in range(len(new_grid[0]))]
        for _ in range(len(new_grid))
    ]
    current_column, current_row = get_random_starting_cell(new_grid)
    observed.add((current_column, current_row))
    possibility_matrix[current_column][current_row] = 0

    """
    what am i doing after this?
    1. assign the current cell a random tile
    2. update the possibility matrix
    3. find the cell with the lowest entropy
    4. make a choice from the available tile patterns
    5. update the grid
    6. repeat until all cells are observed
    """
    new_grid[current_column][current_row] = grab_random_tile(tiles)
    while len(observed) < len(new_grid) * len(new_grid[0]):
        pass
    return new_grid


def generate_realistic_map(tiles: dict, grid: list) -> list:
    raise NotImplementedError


def generate_random_map(tiles: dict, grid: list) -> list:
    new_grid = grid
    all_coords = [
        (cols, rows)
        for cols in range(len(new_grid))
        for rows in range(len(new_grid[0]))
    ]
    shuffle(all_coords)
    for coordinates in all_coords:
        col, row = coordinates
        new_grid[col][row] = grab_random_tile(tiles)
        print_running_map(new_grid)
    return new_grid


def choose_strategy() -> Callable:
    strategies = [
        generate_scrolling_neighbor_map,
        generate_wandering_neighbor_map,
        generate_wave_function_collapse_map,
        generate_realistic_map,
        generate_random_map,
    ]
    try:
        choice = strategies[
            int(
                input(
                    f"Select your map strategy:\n{", ".join([name.__str__().split(" ")[1] for name in strategies])}\n> "
                )
            )
            - 1
        ]
    except ValueError:
        raise ValueError("Please enter a valid number")
    return choice


def create_map(
    tiles: dict = map_tiles,
    columns: int = 0,
    rows: int = 0,
    strategy: Callable = generate_scrolling_neighbor_map,
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
        except ValueError:
            raise ValueError("Please enter a valid number")
        return value

    columns = get_dimension("wide")
    rows = get_dimension("tall")
    return columns, rows


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
