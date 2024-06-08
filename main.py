from random import choice, sample

map_tiles = {"land": "🟩", "water": "🟦", "desert": "🟨", "mountain": "🟫"}
tile_weightings = {"land": 0.3, "water": 0.5, "desert": 0.1, "mountain": 0.1}


def grab_random_tile(tiles: dict, weights: dict = tile_weightings) -> str:
    weighted_tiles = [int(weight * 10) for weight in weights.values()]
    return tiles[choice(sample(list(tiles), k=1, counts=weighted_tiles))]


def find_neighbors(current_map: list, current_row: int, current_column: int) -> list:
    neighbors = []
    if current_column != 0:
        neighbors.append(current_map[current_row][current_column - 1])
    if current_row != 0:
        neighbors.append(current_map[current_row - 1][current_column])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = neighbors
    options.append(grab_random_tile(tiles))
    return choice(options)


def create_map(tiles: dict = map_tiles, width: int = 50, height: int = 0) -> list:
    rows = width
    columns = rows if height <= 0 else height
    grid = [["X" for _ in range(columns)] for _ in range(rows)]
    for r_index, row in enumerate(grid):
        for c_index, _ in enumerate(row):
            if r_index == 0 and c_index == 0:
                grid[r_index][c_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(grid, r_index, c_index)
                grid[r_index][c_index] = select_neighbor(neighbors, tiles)
    return grid


def print_map(map: list) -> str:
    res = ""
    for row in map:
        for col in row:
            res += col
        res += "\n"
    return res


def main() -> None:
    print(f"{print_map(create_map())}")
    print("\n")
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()
    print("thanks for playing! have a nice day 😄")
    exit(0)


if __name__ == "__main__":
    main()
