import json
import tkinter as tk

main_font = ("Arial", 14)
smaller_font = ("Arial", 12, "italic")


def start_algorithm(
    root, width, height, is_show_process, choose_algorithm, is_draw_maze
):
    try:
        width = int(width)
        height = int(height)
    except:
        return

    if width < 2 or width > 50 or height < 2 or height > 50:
        return

    height = int(height)
    width = int(width)

    settings = {}
    settings["width"] = width
    settings["height"] = height
    settings["is_show_process"] = is_show_process
    settings["choose_algorithm"] = choose_algorithm
    settings["is_draw_maze"] = is_draw_maze

    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)

    root.destroy()


def settings():
    root = tk.Tk()
    root.title("Settings")
    root.geometry("+200+10")

    # width
    tk.Label(text="Enter width:", font=main_font).grid(
        row=0, column=0, padx=10, pady=10, sticky=tk.W
    )

    width_entry = tk.Entry(root, font=main_font)
    width_entry.grid(row=0, column=1, padx=10, pady=10, ipady=2, sticky=tk.W)

    # height
    tk.Label(text="Enter height:", font=main_font).grid(
        row=1, column=0, padx=10, pady=10, sticky=tk.W
    )

    height_entry = tk.Entry(root, font=main_font)
    height_entry.grid(row=1, column=1, padx=10, pady=10, ipady=2, sticky=tk.W)

    tk.Label(text="").grid(row=2, column=0)

    # algorithm
    tk.Label(text="Choose the algorithm:", font=main_font).grid(
        row=3, column=0, padx=10, pady=10, columnspan=2, sticky=tk.W
    )

    choose_algorithm = tk.StringVar(value="breadth_first_search")

    tk.Radiobutton(
        root,
        text="Breadth first search",
        variable=choose_algorithm,
        value="breadth_first_search",
        font=smaller_font,
    ).grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="Depth first search",
        variable=choose_algorithm,
        value="depth_first_search",
        font=smaller_font,
    ).grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="Dijkstra's algorithm",
        variable=choose_algorithm,
        value="dijkstra_search",
        font=smaller_font,
    ).grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="A* algorithm",
        variable=choose_algorithm,
        value="a_star_search",
        font=smaller_font,
    ).grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)

    # show process
    tk.Label(
        text="Would you like to see the algorithm or just the end result?",
        font=main_font,
    ).grid(row=8, column=0, padx=10, pady=10, columnspan=2, sticky=tk.W)

    is_show_process = tk.BooleanVar(
        value=True
    )  # True - show algorithm, False - show end result

    tk.Radiobutton(
        root,
        text="Show me the algorithm",
        variable=is_show_process,
        value=True,
        font=smaller_font,
    ).grid(row=9, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="Just show me end result",
        variable=is_show_process,
        value=False,
        font=smaller_font,
    ).grid(row=10, column=0, padx=10, pady=10, sticky=tk.W)

    # draw maze
    tk.Label(text="Would you like to draw your own maze?", font=main_font).grid(
        row=11, column=0, padx=10, pady=10, columnspan=2, sticky=tk.W
    )

    is_draw_maze = tk.StringVar(
        value="randomize"
    )  # randomize - random maze, draw - user draws the maze, file - random maze from a file

    tk.Radiobutton(
        root,
        text="Randomize the maze",
        variable=is_draw_maze,
        value="randomize",
        font=smaller_font,
    ).grid(row=12, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="Let me draw the maze",
        variable=is_draw_maze,
        value="draw",
        font=smaller_font,
    ).grid(row=13, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Radiobutton(
        root,
        text="Choose a random maze from file",
        variable=is_draw_maze,
        value="file",
        font=smaller_font,
    ).grid(row=14, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Button(
        text="Start",
        font=main_font,
        command=lambda: start_algorithm(
            root,
            width_entry.get(),
            height_entry.get(),
            is_show_process.get(),
            choose_algorithm.get(),
            is_draw_maze.get(),
        ),
    ).grid(row=15, column=0, columnspan=2, padx=10, pady=10, ipadx=30, ipady=10)

    root.mainloop()
