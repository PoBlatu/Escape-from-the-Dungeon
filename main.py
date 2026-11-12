SYMBOLS = {
    "in": ">",
    "empty": " ",
    "monster": "&",
    "weapon": "/",
    "health": "+",
    "out": "<",
    "player": "@",
}

MOVES = {
    "w": (0, -1), "ц": (0, -1),   # вверх
    "s": (0, 1),  "ы": (0, 1),    # вниз
    "a": (-1, 0), "ф": (-1, 0),   # влево
    "d": (1, 0),  "в": (1, 0),    # вправо
}

# один уровень: комнаты (позиция на сетке + содержимое) и связи между ними
LEVELS = [
    {
        "rooms": {
            "A": {"coords": (0, 0), "content": "in"},
            "B": {"coords": (1, 0), "content": "empty"},
            "C": {"coords": (2, 0), "content": "monster"},
            "D": {"coords": (1, 1), "content": "weapon"},
            "E": {"coords": (2, 1), "content": "health"},
            "F": {"coords": (2, 2), "content": "out"},
        },
        "links": [("A", "B"), ("B", "C"), ("B", "D"),
                  ("C", "E"), ("D", "E"), ("E", "F")],
    },
    {
        "rooms": {
            "A": {"coords": (0, 0), "content": "in"},
            "B": {"coords": (1, 0), "content": "empty"},
            "C": {"coords": (2, 0), "content": "monster"},
            "D": {"coords": (3, 0), "content": "health"},
            "E": {"coords": (0, 1), "content": "monster"},
            "F": {"coords": (1, 1), "content": "empty"},
            "G": {"coords": (2, 1), "content": "weapon"},
            "H": {"coords": (3, 1), "content": "monster"},
            "I": {"coords": (1, 2), "content": "empty"},
            "J": {"coords": (2, 2), "content": "monster"},
            "K": {"coords": (3, 2), "content": "monster"},
            "L": {"coords": (3, 3), "content": "out"},
        },
        "links": [("A", "B"), ("A", "E"), ("B", "C"), ("B", "F"),
                  ("C", "D"), ("C", "G"), ("D", "H"), ("E", "F"),
                  ("F", "I"), ("G", "J"), ("H", "K"), ("I", "J"),
                  ("J", "K"), ("K", "L")],
    }
]

MAX_HP = 6
MONSTER_HP = 3
DAMAGE = 1
MONSTER_DAMAGE = 2
POTION = 5
LOW_HP = MAX_HP / 3

def new_game(level):
    game = {
        "level": level,
        "room": "A",
        "hp": MAX_HP,
        "attack": DAMAGE,
        "seen": {"A"},
        "finished": False,
        "bag": [],
        "messages": []
    }
    game["seen"].update(neighbors(game))
    return game

def neighbors(game):
    res = []
    for a, b in game["level"]["links"]:
        if a == game["room"]:
            res.append(b)
        elif b == game["room"]:
            res.append(a)
    return res

def move(game, key):
    rooms = game["level"]["rooms"]
    x, y = rooms[game["room"]]["coords"]
    dx, dy = MOVES.get(key, (0, 0))
    for room in neighbors(game):
        if rooms[room]["coords"] == (x + dx, y + dy):
            game["room"] = room
            game["seen"].update(neighbors(game))
            room_content(game)
            return
    game["messages"].append("Прохода нет!")

def fight(hp, attack, monster_hp=MONSTER_HP, monster_damage=MONSTER_DAMAGE):
    while monster_hp > 0 and hp > 0:
        monster_hp -= attack
        if monster_hp > 0:
            hp -= monster_damage
    return max(hp, 0), monster_hp <=0

def room_content(game):
    room = game["level"]["rooms"][game["room"]]
    content = room["content"]
    if content == "monster":
        game["hp"], won = fight(game["hp"], game["attack"])
        if won:
            game["messages"].append("Монстр побеждён!")
            room["content"] = "empty"
        else:
            game["messages"].append("Вы погибли.")
            game["finished"] = True
    elif content == "weapon":
        game["attack"] += 1
        game["messages"].append("Нашли оружие!")
        room["content"] = "empty"
    elif content == "health":
        game["hp"] = min(MAX_HP, game["hp"] + POTION)
        game["messages"].append("Зелье здоровья!") 
        room["content"] = "empty"
    elif content == "out":
        game["messages"].append("Вы дошли до выхода. Победа!")
        game["finished"] = True

def health_bar(hp, max_hp=MAX_HP, low_hp=LOW_HP):
    hp = max(0, min(hp, max_hp)) # защита от выхода за границы
    bar = "+" * hp + "-" * (max_hp - hp)
    warning = "  ВНИМАНИЕ: мало здоровья!" if 0 < hp <= low_hp else ""
    return f"Здоровье: [{bar}]{warning}"

def show_screen(game):
    render(game["level"], game["room"], game["seen"])
    print(health_bar(game["hp"])) 
    for msg in game["messages"]:
        print(msg)
    game["messages"].clear()

def ask_move():
    return input("Куда идти (W вверх, S вниз, A влево, D вправо)? ").strip().lower()

def render(level, player_position, seen):
    rooms, links = level["rooms"], level["links"]
    w = max(r["coords"][0] for r in rooms.values()) + 1
    h = max(r["coords"][1] for r in rooms.values()) + 1

    # комната занимает 3 символа "[X]", между комнатами по 1 символу на связь
    canvas = [[" "] * (w * 4 - 1) for _ in range(h * 2 - 1)]

    for key, room in rooms.items():
        if key not in seen:
            continue
        x, y = room["coords"]
        cx, cy = x * 4, y * 2
        sym = SYMBOLS["player"] if player_position == key else SYMBOLS[room["content"]]
        canvas[cy][cx:cx + 3] = ["[", sym, "]"]

    for a, b in links:
        if a not in seen or b not in seen:
            continue
        ax, ay = rooms[a]["coords"]
        bx, by = rooms[b]["coords"]
        if ay == by: # соседи по горизонтали
            canvas[ay * 2][min(ax, bx) * 4 + 3] = "-"
        elif ax == bx: # соседи по вертикали
            canvas[min(ay, by) * 2 + 1][ax * 4 + 1] = "|"
        else:
            raise ValueError(f"Комнаты {a} и {b} не соседние")

    print("\n".join("".join(row).rstrip() for row in canvas))


def run(level):
    print("Добро пожаловать на уровень!")
    game = new_game(level)
    while not game["finished"]:
        show_screen(game)
        choice = ask_move()
        move(game, choice)
    show_screen(game)

if __name__ == "__main__":
    run(LEVELS[1])