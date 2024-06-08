from random import choice

map_tiles = {"land": "🟩", "water": "🟦", "desert": "🟨", "mountain": "🟫"}


def grab_random_tile(tiles: dict) -> str:
    return tiles[choice(list(tiles))]


def find_neighbors(current_map: list, current_row: int, current_column: int) -> list:
    neighbors = []
    # modulo = len(current_map)
    if current_column != 0:
        neighbors.append(current_map[current_row][current_column - 1])
    if current_row != 0:
        neighbors.append(current_map[current_row - 1][current_column])
    return neighbors


def select_neighbor(neighbors: list, tiles: dict) -> str:
    options = neighbors
    options.append(grab_random_tile(tiles))
    return choice(options)


def create_map(tiles: dict = map_tiles, size: int = 50) -> list:
    grid = [["X" for _ in range(size)] for _ in range(size)]
    for r_index, row in enumerate(grid):
        # no need to reference the column, but this feels yucky
        for c_index, _ in enumerate(row):
            if r_index == 0 and c_index == 0:
                grid[r_index][c_index] = grab_random_tile(tiles)
            else:
                neighbors = find_neighbors(grid, r_index, c_index)
                grid[r_index][c_index] = select_neighbor(neighbors, tiles)
    return grid


def main() -> None:
    print(f"{create_map()}")
    print("\n")
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()
    print("thanks for playing! have a nice day 😄")
    exit(0)


if __name__ == "__main__":
    main()
