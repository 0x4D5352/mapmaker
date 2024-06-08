from random import choice

map_tiles = {"green": "🟩", "blue": "🟦", "yellow": "🟨"}


def select_neighbor(neighbor, tiles):
    return choice([neighbor, tiles[choice(list(tiles))]])


def create_map(tiles=map_tiles, size=50):
    res = ""
    for _ in range(size):
        for _ in range(size):
            if len(res) == 0:
                res += f"{tiles[choice(list(tiles))]}"
            else:
                neighbor = res[-1] if res[-1] != "\n" else res[-2]
                res += f"{select_neighbor(neighbor, tiles)}"
        res += "\n"
    return res


def main():
    print(f"{create_map()}")
    print("\n")
    response = input("go again? Y for yes, anything else is no\n> ")
    if len(response) > 0:
        if response[0].upper() == "Y":
            main()


if __name__ == "__main__":
    main()
