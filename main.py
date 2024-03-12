import json
import os
import queue

import numpy as np
import pygame

import settings

FPS = 100
WIDTH, HEIGHT = 700, 700
TILE_WIDTH, TILE_HEIGHT = None, None

TILE = 0
WALL = 1
START = 2
END = 3
BORDER_WALL = 4

COLORS = {
    "BG_COLOR": (255, 255, 255),
    "TILE_COLOR": (210, 210, 210),
    "WALL_TILE_COLOR": (128, 128, 128),
    "TEXT_BG_COLOR": (150, 150, 150),
    "TEXT_COLOR": (0, 0, 0),
    "GREEN": (0, 255, 0),
    "ORANGE": (255, 165, 0),
    "RED": (255, 0, 0),
}

pygame.init()


class DijkstraVertex:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.dist = float("inf")
        self.visited = False
        self.parent = None
        self.edges = []

    def __lt__(self, other):
        return self.dist < other.dist

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def get_pos(self):
        return (self.x, self.y)


class AstarVertex:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.edges = []
        self.distance = float("inf")
        self.heuristic = 0
        self.visited = False
        self.parent = None

    def __lt__(self, other):
        return self.distance + self.heuristic < other.distance + other.heuristic

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def set_heuristic(self, goal):
        self.heuristic = abs(self.x - goal.x) + abs(self.y - goal.y)

    def get_pos(self):
        return (self.x, self.y)


def main_draw(window, board, path, was_here, at_start=False):
    font = pygame.font.SysFont(None, int(min(TILE_WIDTH, TILE_HEIGHT)))

    text_width, text_height = font.size(START)
    align_start_x = TILE_WIDTH / 2 - text_width / 2
    align_start_y = TILE_HEIGHT / 2 - text_height / 2

    text_width, text_height = font.size(END)
    align_end_x = TILE_WIDTH / 2 - text_width / 2
    align_end_y = TILE_HEIGHT / 2 - text_height / 2

    window.fill(COLORS["BG_COLOR"])

    for i, row in enumerate(board):
        for j, col in enumerate(row):
            color = COLORS["TILE_COLOR"]

            if (j, i) in path:
                color = COLORS["GREEN"]

            elif (j, i) in was_here:
                color = COLORS["ORANGE"]

            elif col == WALL:
                color = COLORS["WALL_TILE_COLOR"]

            elif col == END:
                color = COLORS["RED"]

            pygame.draw.rect(
                window,
                color,
                (j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH - 2, TILE_HEIGHT - 2),
            )

            if col == START:
                pygame.draw.rect(
                    window,
                    COLORS["GREEN"],
                    (j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH - 2, TILE_HEIGHT - 2),
                )
                window.blit(
                    font.render(START, True, COLORS["TEXT_COLOR"]),
                    (j * TILE_WIDTH + align_start_x, i * TILE_HEIGHT + align_start_y),
                )

            elif col == END:
                window.blit(
                    font.render(END, True, COLORS["TEXT_COLOR"]),
                    (j * TILE_WIDTH + align_end_x, i * TILE_HEIGHT + align_end_y),
                )

    if not at_start:
        pygame.display.update()


def load_maze_from_file():
    files = os.listdir("maze")
    file = np.random.choice(files)

    with open(f"maze/{file}", "r") as f:
        board = f.readlines()

    for row in range(len(board)):
        board[row] = board[row].rstrip("\n")

    return board


def mouse_pressed(mouse_pos, board, value):
    row, col = int(mouse_pos[1] / TILE_HEIGHT), int(mouse_pos[0] / TILE_WIDTH)

    if board[row, col] != BORDER_WALL:
        board[row, col] = value
        return row, col


def select_pos_text(window, text):
    font = pygame.font.SysFont(None, 40)
    text_width, text_height = font.size(text)

    pygame.draw.rect(
        window,
        COLORS["TEXT_BG_COLOR"],
        (WIDTH / 2 - text_width / 2 - 10, 0, text_width + 20, text_height + 20),
    )
    window.blit(
        font.render(text, True, COLORS["TEXT_COLOR"]), (WIDTH / 2 - text_width / 2, 10)
    )


def start_button(window):
    font = pygame.font.SysFont(None, 60)
    text_width, text_height = font.size("Ready")

    pygame.draw.rect(
        window,
        COLORS["TEXT_BG_COLOR"],
        (WIDTH / 2 - text_width / 2 - 10, 0, text_width + 20, text_height + 20),
    )
    window.blit(
        font.render("Ready", True, COLORS["TEXT_COLOR"]),
        (WIDTH / 2 - text_width / 2, 10),
    )

    return (
        WIDTH / 2 - text_width / 2 - 10,
        0,
        WIDTH / 2 + text_width / 2 + 10,
        text_height + 20,
    )  # x1 y1 x2 y2


def find_neighbors(board, pos, move_diagonally=False):
    neighbors = []
    x, y = pos

    if move_diagonally:
        possibleMoves = [
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
        ]
    else:
        possibleMoves = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    for dx, dy in possibleMoves:
        new_x = x + dx
        new_y = y + dy

        if board[new_y, new_x] != WALL:
            neighbors.append((new_x, new_y))

    return neighbors


def find_value(board, value):
    return np.where(board == value)


def breadth_first_search(window, clock, board, showProcess):
    start_pos = find_value(board, START)
    end_pos = find_value(board, END)

    visited = []
    q = queue.Queue()
    q.put((start_pos, [start_pos]))

    while not q.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_pos, path = q.get()
        if current_pos == end_pos:
            break
        elif current_pos in visited:
            continue
        visited.append(current_pos)

        if showProcess:
            main_draw(window, board, [], visited)
            clock.tick(FPS)

        for neighbor in find_neighbors(board, current_pos):
            new_path = path + [neighbor]
            q.put((neighbor, new_path))

    else:
        main_draw(window, board, [], visited)
        return

    main_draw(window, board, path, visited)


def depth_first_search(window, clock, board, showProcess):
    start_pos = find_value(board, START)
    end_pos = find_value(board, END)

    visited = []
    stack = []
    stack.append((start_pos, [start_pos]))

    while len(stack) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_pos, path = stack.pop()
        if current_pos == end_pos:
            break
        elif current_pos in visited:
            continue
        visited.append(current_pos)

        if showProcess:
            main_draw(window, board, [], visited)
            clock.tick(FPS)

        try:
            neighbors = find_neighbors(board, current_pos)
            neighbors.reverse()
        except:
            pass

        for neighbor in neighbors:
            new_path = path + [neighbor]
            stack.append((neighbor, new_path))

    else:
        main_draw(window, board, [], visited)
        return

    main_draw(window, board, path, visited)


def find_edges(board, vertices, vertex):
    edges = []
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        x = vertex.x + dx
        y = vertex.y + dy
        if 0 <= x < len(board[0]) and 0 <= y < len(board) and board[y][x] != WALL:
            edges.append((x, y))
    return [vertices[y][x] for x, y in edges]


def dijkstra_search(window, clock, board, showProcess):
    start_pos = find_value(board, START)
    end_pos = find_value(board, END)

    rows, cols = len(board), len(board[0])
    vertices = [[DijkstraVertex((x, y)) for x in range(cols)] for y in range(rows)]

    for row in vertices:
        for col in row:
            col.edges = find_edges(board, vertices, col)

    start_vertex = vertices[start_pos[1]][start_pos[0]]
    start_vertex.dist = 0
    end_vertex = vertices[end_pos[1]][end_pos[0]]

    q = queue.Queue()
    q.put(start_vertex)

    path = []
    visited = []
    while not q.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = q.get()

        if current == end_vertex:
            while current.parent:
                path.append(current.get_pos())
                current = current.parent
            path.append(current.get_pos())
            break
        elif current.get_pos() in visited:
            continue
        current.visited = True
        visited.append(current.get_pos())

        if showProcess:
            main_draw(window, board, [], visited)
            clock.tick(FPS)

        for neighbor in current.edges:
            new_dist = current.dist + 1
            if new_dist < neighbor.dist:
                neighbor.dist = new_dist
                neighbor.parent = current
                q.put(neighbor)

    else:
        main_draw(window, board, [], visited)
        return

    main_draw(window, board, path, visited)


def a_star_search(window, clock, board, showProcess):
    start_pos = find_value(board, START)
    end_pos = find_value(board, END)

    rows, cols = len(board), len(board[0])
    vertices = [[AstarVertex((x, y)) for x in range(cols)] for y in range(rows)]

    startVertex = vertices[start_pos[1]][start_pos[0]]
    startVertex.distance = 0
    endVertex = vertices[end_pos[1]][end_pos[0]]

    for row in vertices:
        for col in row:
            col.edges = find_edges(board, vertices, col)
            col.set_heuristic(endVertex)

    pq = queue.PriorityQueue()
    pq.put(startVertex)
    path = []
    visited = []

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = pq.get()

        if current == endVertex:
            while current:
                path.append(current.get_pos())
                current = current.parent
            break
        elif current.get_pos() in visited:
            continue
        current.visited = True
        visited.append(current.get_pos())

        if showProcess:
            clock.tick(FPS)
            main_draw(window, board, [], visited)

        for edge in current.edges:
            cost = current.distance + 1
            heuristic = edge.heuristic
            if cost < edge.distance:
                edge.distance = cost
                edge.parent = current
                edge.heuristic = heuristic
                pq.put(edge)

    else:
        main_draw(window, board, [], visited)

    main_draw(window, board, path, visited)


def randomize_board(board, board_height, board_width):
    num_walls = int(board.shape[0] * board.shape[1] * 0.3)
    interior_indices = [
        (row, col)
        for row in range(1, board_height - 1)
        for col in range(1, board_width - 1)
    ]

    indices_to_set = np.random.choice(
        len(interior_indices), size=num_walls, replace=False
    )
    for idx in indices_to_set:
        row, col = interior_indices[idx]
        board[row, col] = WALL

    start_pos, end_pos = np.random.choice(len(interior_indices), size=2, replace=False)

    board[start_pos] = START
    board[end_pos] = END

    return board


def draw_board(board, window, clock):
    start_pos, end_pos = None, None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        main_draw(window, board, [], [], True)

        if start_pos == None:
            select_pos_text(window, "Select a start tile (O)")
        elif end_pos == None:
            select_pos_text(window, "Select an end tile (X)")
        else:
            button_pos = start_button(window)

        if any(pygame.mouse.get_pressed()):
            mouse_pos = pygame.mouse.get_pos()

            if start_pos == None:
                start_pos = mouse_pressed(mouse_pos, board, START)

            elif end_pos == None:
                end_pos = mouse_pressed(mouse_pos, board, END)

            else:
                if (
                    button_pos[0] < mouse_pos[0] < button_pos[2]
                    and button_pos[1] < mouse_pos[1] < button_pos[3]
                ):
                    break

                if pygame.mouse.get_pressed() == 0:
                    mouse_pressed(mouse_pos, board, WALL)
                elif pygame.mouse.get_pressed() == 2:
                    mouse_pressed(mouse_pos, board, TILE)

        pygame.display.update()
        clock.tick(60)


def get_board(is_draw_maze, window, clock):
    # set board width and height / +2 because I add borders around the board
    board_width, board_height = settings["width"] + 2, settings["height"] + 2
    board = np.full(shape=(board_height, board_height), fill_value=TILE)

    global TILE_WIDTH
    global TILE_HEIGHT
    TILE_WIDTH, TILE_HEIGHT = WIDTH / board_width, HEIGHT / board_height

    # set tiles on edges of the board as walls
    board[0, :] = BORDER_WALL
    board[-1, :] = BORDER_WALL
    board[:, 0] = BORDER_WALL
    board[:, -1] = BORDER_WALL

    # if is_draw_maze is set to "randomize" the random tiles are set as walls
    if is_draw_maze == "randomize":
        board = randomize_board(board, board_height, board_width)

    # if is_draw_maze is set to "draw" the user chooses start -> end -> walls
    elif is_draw_maze == "draw":
        board = draw_board(board, window, clock)

    # if is_draw_maze is set to "file" program chooses a random file to load the maze from
    elif is_draw_maze == "file":
        board = load_maze_from_file()
        board_height, board_width = board.shape
        TILE_WIDTH, TILE_HEIGHT = WIDTH / board_width, HEIGHT / board_height

    return board


def main():
    # tries to load settings from "settings.json", if not found then program ends
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
    except FileNotFoundError:
        print("Settings file not found")
        return

    is_draw_maze = settings["is_draw_maze"]
    is_show_process = settings["is_show_process"]

    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PATHFINDING ALGORITHM")

    # loads the board depending on
    board = get_board(is_draw_maze, window, clock)

    # print the board before algorithms
    main_draw(window, board, [], [])

    match settings["choose_algorithm"]:
        case "breadth_first_search":
            breadth_first_search(window, clock, board, is_show_process)

        case "depth_first_search":
            depth_first_search(window, clock, board, is_show_process)

        case "dijkstra_search":
            dijkstra_search(window, clock, board, is_show_process)

        case "a_star_search":
            a_star_search(window, clock, board, is_show_process)

    # to stop the program from exiting after the algorithm ends
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            break
    pygame.quit()


if __name__ == "__main__":
    # before program starts, settings need to be set and saved to file "settings.json"
    settings.settings()

    main()
