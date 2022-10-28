import tkinter
from tkinter import *


class LevelBuilder:
    SCREEN_SIZE = 600
    COLORS = ["red", "green", "blue", "yellow", "orange", "cyan", "magenta", "brown", "purple", "white", "gray", "lime",
              "dark khaki", "navy", "teal", "pink"]
    MID_POS = [[8], [6, 10], [4, 8, 12], [2, 6, 10, 14], [0, 4, 8, 12, 16], [0, 16/5, 32/5, 48/5, 64/5, 16],
               [0, 8/3, 16/3, 8, 32/3, 40/3, 16], [0, 16/7, 32/7, 48/7, 64/7, 80/7, 96/7, 16]]

    def __init__(self):
        # Creates Window
        self.window = Tk()
        self.window.title("Flow Solver 2.0")
        self.window.geometry("750x950")

        self.window.minsize(750, 950)
        self.window.maxsize(750, 950)

        # Initializes Variables for board size and number of nodes
        self.height = IntVar(self.window)
        self.height.set(5)
        self.width = IntVar(self.window)
        self.width.set(5)
        self.numNodes = IntVar(self.window)
        self.numNodes.set(3)

        # Records variables for tracking nodes (Color, (0 or 1))
        self.used_nodes = {}
        self.unused_nodes = {(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)}

        # Uses set screen size to measure the size of the board
        self.wwidth = self.SCREEN_SIZE
        self.wheight = self.SCREEN_SIZE
        self.cellSize = self.SCREEN_SIZE / 5

        # Creates Canvas
        self.canvas = Canvas(self.window, width=self.wwidth, height=self.wheight + 2 * self.cellSize, bg='black')
        self.canvas.pack(padx=0, pady=0)

        # Initializes Frame for Size Menus
        self.sizeMenuFrame = Frame(self.window)
        self.sizeMenuFrame.pack()

        # Initializes Size and Node Menus
        self.heightMenu = OptionMenu(self.sizeMenuFrame, self.height, *[i for i in range(5, 19)])
        self.widthMenu = OptionMenu(self.sizeMenuFrame, self.width, *[i for i in range(5, 19)])
        self.numNodeMenu = OptionMenu(self.sizeMenuFrame, self.numNodes, *[i for i in range(3, 17)])
        self.heightMenu.pack(side="left")
        self.widthMenu.pack(side="left")
        self.numNodeMenu.pack(side='left')

        # Initializes Size Apply button
        self.update_button = Button(self.window, text="APPLY", command=self.update_canvas)
        self.update_button.pack()

        self.canvas.tag_bind("node", "<B1-Motion>", self.drag_object)
        self.canvas.tag_bind("node", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("node", "<ButtonRelease-1>", self.drag_stop)

        self.drag_info = {"x": 0, "y": 0, "item": None, "prev": ()}

        self.solveButton = Button(self.window, text="SOLVE", command=self.destroy)
        self.solveButton.pack()

        self.update_canvas()

        self.window.mainloop()

    def drag_start(self, event):
        self.drag_info["item"] = self.canvas.find_closest(event.x, event.y)[0]

        if 'node' in self.canvas.gettags(self.drag_info['item']):
            c = self.canvas.coords(self.drag_info['item'])
            self.drag_info['prev'] = (((c[0] + c[2]) / (self.cellSize * 2) - 0.5,
                                       ((c[1] + c[3]) / (self.cellSize * 2)) - 0.5)) if event.y < self.wheight else (
                -1, -1)
            self.canvas.moveto(self.drag_info['item'], event.x - self.cellSize / 2, event.y - self.cellSize / 2)
            self.drag_info["x"] = event.x
            self.drag_info['y'] = event.y
        else:
            self.drag_info['item'] = None

    def drag_stop(self, event):
        if self.drag_info['item']:
            # Drop on board
            if event.y < self.wheight:
                self.add_to_board(self.drag_info['item'], event.x // self.cellSize, event.y // self.cellSize)
            # Drop off board
            else:
                self.remove_from_board(self.drag_info['item'])

            self.drag_info["item"] = None
            self.drag_info["x"] = 0
            self.drag_info['y'] = 0

    def drag_object(self, event):
        if self.drag_info['item']:
            if 0 <= event.x < self.wwidth and 0 <= event.y < self.wheight + 2 * self.cellSize:
                dx = event.x - self.drag_info['x']
                dy = event.y - self.drag_info['y']

                self.canvas.move(self.drag_info['item'], dx, dy)

                self.drag_info['x'] = event.x
                self.drag_info['y'] = event.y

    def make_node(self, c_x, c_y, color, number):
        x, y = self.cellSize * c_x, self.cellSize * c_y
        return self.canvas.create_oval(x + self.cellSize * 1 / 8, y + self.cellSize * 1 / 8, x + self.cellSize * 7 / 8,
                                       y + self.cellSize * 7 / 8, fill=self.COLORS[color],
                                       tags=("node", (color, number)), outline="")

    def add_to_board(self, node, x, y):
        # explain = ""
        # Gets the color and number (0 or 1) for the node
        n_col, number = self.canvas.gettags(node)[1].split(" ")
        # explain += "Found node " + number + " of color " + self.COLORS[int(n_col)]
        n_col, number = int(n_col), int(number)

        # Gets the coordinates to move the node to
        move_x = self.cellSize * x
        move_y = self.cellSize * y

        # explain += ". Wanted to move it to (" + str(x) + ", "+str(y) + ")."

        # Checks if on board
        isOffScreen = False
        if not (0 <= x < self.width.get() and 0 <= y < self.height.get()):
            # explain += "It was offscreen."
            isOffScreen = True

        # Space is occupied
        if (x, y) in self.used_nodes.values() or isOffScreen:
            # explain += " But it was occupied, so it "
            # Moved from board to board
            if (n_col, number) in self.used_nodes and self.used_nodes[(n_col, number)] != (x, y) and self.drag_info[
                'prev'] != (-1, -1):
                # explain += "was moved back to its previous position on the board."
                move_x = self.cellSize * self.drag_info['prev'][0]
                move_y = self.cellSize * self.drag_info['prev'][1]
            # Moved from extra to board
            elif (n_col, number) in self.unused_nodes:
                # explain += "Moved back to being unused."
                move_x, move_y = self.remove_from_board(node)
            # Screen resize caused it to be cut offx
            elif x >= self.width.get() or y >= self.height.get():
                # explain += "was cut off and returned to unused."
                move_x, move_y = self.remove_from_board(node)
            else:
                pass
                # explain += "was probably already there."
        # Space is not occupied
        else:
            # explain += " Moved it to (" + str(x) + ", "+str(y) + ") and updated location."
            self.used_nodes[(n_col, number)] = (x, y)
            if (n_col, number) in self.unused_nodes:
                self.unused_nodes.remove((n_col, number))
                # explain += " " + str((n_col, number)) + " is no longer unused."

        # Snap node in place
        # print(explain + " Moved to " + str((move_x, move_y)))
        self.canvas.moveto(node, move_x + self.cellSize / 8, move_y + self.cellSize / 8)

    def remove_from_board(self, node):
        # explain = ""
        # Gets the color and number (0 or 1) for the node
        n_col, number = self.canvas.gettags(node)[1].split(" ")
        # explain += "Found node " + number + " of color " + self.COLORS[int(n_col)]
        n_col, number = int(n_col), int(number)

        # Checks if node is being used
        if (n_col, number) in self.used_nodes:
            # explain += " being used"
            self.used_nodes.pop((n_col, number))
        self.unused_nodes.add((n_col, number))
        # explain += ". Added it to unused nodes."

        temp_width = (self.wwidth - (5 * self.cellSize / 4)) / 16

        move_x = self.cellSize / 4
        move_y = self.wheight

        # top
        if n_col <= (self.numNodes.get() - 1) // 2:
            move_x += temp_width * self.MID_POS[((self.numNodes.get() // 2) + (self.numNodes.get() % 2)) - 1][n_col]
            move_y += self.cellSize / 8
        # bottom
        else:
            move_x += temp_width * self.MID_POS[(self.numNodes.get() // 2) - 1][n_col % (self.numNodes.get() // 2)]
            move_y += 9 * self.cellSize / 8

        # print(explain)
        self.canvas.moveto(node, move_x, move_y)

        return move_x, move_y

    def update_nodes(self):
        self.canvas.delete('node')
        # Sums up total current nodes
        total_nodes = len(self.used_nodes) / 2 + len(self.unused_nodes) / 2
        node_diff = int(self.numNodes.get() - total_nodes)

        # Nodes were added
        if node_diff > 0:
            for i in range(node_diff):
                for number in range(2):
                    self.unused_nodes.add((int(total_nodes) + i, number))

        # Nodes were removed
        elif node_diff <= 0:
            remove_nodes = set()  # set of nodes to be removed

            # Gets nodes that are on the board that need to be deleted
            for node in self.used_nodes.keys():
                if node[0] > self.numNodes.get() - 1:
                    remove_nodes.add(node)
            # Gets nodes that are not on the board that need to be deleted
            for node in self.unused_nodes:
                if node[0] > self.numNodes.get() - 1:
                    remove_nodes.add(node)
            # Deletes nodes
            for node in remove_nodes:
                if node in self.used_nodes:
                    self.used_nodes.pop(node)
                else:
                    self.unused_nodes.remove(node)

        # Readds unused nodes
        for node in self.unused_nodes:
            temp_node = self.make_node(-10, -10, node[0], node[1])
            self.remove_from_board(temp_node)

        # Readds used nodes
        temp = set(self.used_nodes.keys())
        for node in temp:
            temp_node = self.make_node(-10, -10, node[0], node[1])
            self.add_to_board(temp_node, self.used_nodes[node][0], self.used_nodes[node][1])

    def update_canvas(self):
        self.canvas.delete("bg")

        # Im lazy and copy/pasting code lmao
        size = (self.width.get(), self.height.get())

        # Determines canvas size for rectangles
        largerIndex = 0 if size[0] >= size[1] else 1

        self.cellSize = self.SCREEN_SIZE / size[largerIndex]
        self.wwidth = self.SCREEN_SIZE if largerIndex == 0 else self.SCREEN_SIZE * size[0] / size[1]
        self.wheight = self.SCREEN_SIZE if largerIndex == 1 else self.SCREEN_SIZE * size[1] / size[0]

        # Resizes Canvas
        self.canvas.config(width=self.wwidth, height=self.wheight + 2 * self.cellSize)

        # Draws gridlines
        for dist in range(int(self.height.get()) + 1):
            # Horizontal
            self.canvas.create_line(0, dist * self.wheight / self.height.get() + 1, self.wwidth,
                                    dist * self.wheight / self.height.get() + 1, tag='bg', width=2)

        for dist in range(self.width.get() + 1):
            # Vertical
            self.canvas.create_line(dist * self.wwidth / self.width.get() + 1, 0,
                                    dist * self.wwidth / self.width.get() + 1,
                                    self.wheight, tag='bg', width=2)
        self.update_nodes()
        self.canvas.update()

    def destroy(self):
        # Closes window
        if len(self.unused_nodes) == 0:
            self.window.destroy()
        else:
            print("Not all nodes used")

    def solve(self):
        # Returns nodes and size of board
        if len(self.unused_nodes) == 0:
            return {(int(self.used_nodes[node][1]), int(self.used_nodes[node][0])): node[0] for node in
                    self.used_nodes}, \
                   (self.width.get(), self.height.get())
        print("WINDOW EXITED")
        return None, 0
