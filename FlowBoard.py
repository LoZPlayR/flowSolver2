import math
from tkinter import *
from BlackSpace import BlackSpace
import time
from pynput.mouse import Listener
import threading


DIRECTIONS = {(1, 0), (0, -1), (-1, 0), (0, 1)}
t = time.time()

class FlowBoard:
    COLORS = ["red", "green", "blue", "yellow", "orange", "cyan", "magenta", "brown", "purple", "white", "gray", "lime",
              "dark khaki", "navy", "teal", "pink"]
    SCREEN_SIZE = 740

    def __init__(self, nodes, size, holes=None):
        self.filled_spaces = {}
        self.showState = 2
        # 0 = nothing, 1 = lines, 2 = segments

        if holes:
            self.filled_spaces = {hole: -1 for hole in holes}
        self.BS_seen = set()
        self.nodes = nodes
        self.remaining_nodes = set(nodes.keys())

        self.curr_color = 0
        # self.seg_number = 0

        if type(size) is int:
            self.height = size
            self.width = size

            self.wwidth = self.SCREEN_SIZE
            self.wheight = self.SCREEN_SIZE
            self.cellSize = self.SCREEN_SIZE / size

        elif type(size) is tuple:
            if len(size) != 2:
                raise ValueError("Size should be a tuple of length 2. (Given tuple of length " + str(len(size)) + ").")
            self.height = size[1]
            self.width = size[0]

            largerIndex = 0 if size[0] >= size[1] else 1

            self.cellSize = self.SCREEN_SIZE / size[largerIndex]
            self.wwidth = self.SCREEN_SIZE if largerIndex == 0 else self.SCREEN_SIZE * size[0] / size[1]
            self.wheight = self.SCREEN_SIZE if largerIndex == 1 else self.SCREEN_SIZE * size[1] / size[0]

        else:
            raise TypeError("Invalid value for size (should be list or tuple)")

        # Creates heat map
        self.pos_vals = {(r, c): [0] * int(len(self.remaining_nodes)/2) for r in range(self.height) for c in range(self.width)}

        # self.make_heat_maps()

        print(self.pos_vals)

        # Creates Window
        self.window = Tk()
        self.window.title("Flow Solver 2.0")
        self.window.geometry("750x900")


        # Creates Canvas
        self.canvas = Canvas(self.window, width=self.wwidth, height=self.wheight, bg='black')
        self.canvas.pack(padx=0, pady=0)

        # Draws gridlines
        for dist in range(self.height + 1):
            # Horizontal
            self.canvas.create_line(0, dist * self.wheight / self.height + 1, self.wwidth,
                                    dist * self.wheight / self.height + 1, tag='bg', width=2)

        for dist in range(self.width + 1):
            # Vertical
            self.canvas.create_line(dist * self.wwidth / self.width + 1, 0, dist * self.wwidth / self.width + 1,
                                    self.wheight, tag='bg', width=2)

        # Adds nodes to screen
        eighth_cell = self.cellSize / 8
        for node in enumerate(nodes):
            self.canvas.create_oval(node[1][1] * self.cellSize + eighth_cell, node[1][0] * self.cellSize + eighth_cell,
                                    (node[1][1] + 1) * self.cellSize - eighth_cell,
                                    (node[1][0] + 1) * self.cellSize - eighth_cell, tag="NODE",
                                    fill=self.COLORS[nodes[node[1]]],
                                    outline="")
        self.canvas.update()

        # Initialize Threads
        # self.listenerThread = threading.Thread(target=self.next_state, args=())
        #
        # self.listenerThread.start()


    def next_state(self):
        def on_click(x, y, button, pressed):
            if not pressed:
                self.showState += 1
                self.showState = self.showState % 3

                print('State: ' + ("None" * (self.showState == 0)) + ("Lines" * (self.showState == 1)) +
                      ("Segments" * (self.showState == 2)))

        with Listener(on_click=on_click) as listener:
            listener.join()

    def make_line(self, start, end):
        # time.sleep(10)

        if time.time() % 10 < 0.001:
            self.canvas.update()
        if start == end:
            yield [end]
        else:
            children = [(start[0] + direction[0], start[1] + direction[1]) for direction in DIRECTIONS]
            children.sort(key=lambda x: math.sqrt((x[0]-end[0])**2+(x[1]-end[1])**2))
            # children.sort(key=lambda x: self.pos_vals[x][self.curr_color] if x in self.pos_vals else float('inf'))
            for child in children:
                #child = (start[0] + direction[0], start[1] + direction[1])
                if self.isEmptySpace(child):
                    self.filled_spaces[child] = self.curr_color
                    child_tag = str(start[0]) + "_" + str(start[1]) + 'to' + str(child[0]) + "_" + str(child[1])
                    self.draw_segment(start, child, child_tag)
                    # Show Segment
                    if self.showState == 2:
                        self.canvas.update()
                    # Check for Valid board
                    if self.valid_board(child, end):
                        for line in self.make_line(child, end):
                            yield [start] + line

                    self.filled_spaces.pop(child)
                    self.canvas.delete(child_tag)

    def draw_segment(self, start, end, tag):
        line_width = self.cellSize / 3
        half_cell = self.cellSize / 2

        self.canvas.create_line(start[1] * self.cellSize + half_cell, start[0] * self.cellSize + half_cell,
                                end[1] * self.cellSize + half_cell, end[0] * self.cellSize + half_cell,
                                width=line_width, tag=tag, fill=self.COLORS[self.curr_color])

        self.canvas.create_oval(end[1] * self.cellSize + self.cellSize / 3 + 1,
                                end[0] * self.cellSize + self.cellSize / 3 + 1,
                                end[1] * self.cellSize + 2 * self.cellSize / 3,
                                end[0] * self.cellSize + 2 * self.cellSize / 3,
                                outline="", fill=self.COLORS[self.curr_color], tag=tag)

    def valid_board(self, start, end):
        self.BS_seen = set()
        all_BS = []
        for row in range(self.height):
            for col in range(self.width):
                # Looking at a Node
                if (row, col) in self.remaining_nodes:
                    obs = 0 # Things blocking a node
                    for direction in DIRECTIONS:
                        # looking around node
                        child = (row + direction[0], col + direction[1])
                        if not self.isEmptySpace(child) or child == end:
                            obs += 1
                    if obs == 4:
                        return False

                # Looking at an Empty Space
                elif self.isEmptySpace((row, col)):
                    # change this - check if end is next to filled space of same color
                    # if (row, col) == end:
                    #     continue
                    obs = 0  # Things around the space
                    node_adj = False
                    start_adj = False
                    for direction in DIRECTIONS:
                        # looking around space
                        child = (row + direction[0], col + direction[1])
                        if child in self.remaining_nodes:
                            node_adj = True
                        if child == start:
                            start_adj = True
                        if not self.isEmptySpace(child):
                            if (row, col) == end and child in self.filled_spaces and \
                                    self.filled_spaces[child] == self.curr_color and not start_adj:
                                return False
                            obs += 1

                    if not node_adj and obs >= 3 and not start_adj and (row, col) != end:
                        return False
                else:
                    num_loc_col = 0
                    for direction in DIRECTIONS:
                        # looking around line
                        child = (row + direction[0], col + direction[1])
                        if child in self.filled_spaces and self.filled_spaces[(row, col)] == self.filled_spaces[child]:
                            num_loc_col += 1

                    if num_loc_col > 2:
                        return False
                bs = self.BS(row, col, start, end)
                if bs is not None:
                    all_BS.append(bs)

        covered_nodes = set()

        for bs in all_BS:
            if not bs:
                # print("Invalid BlackSpace!")
                return False
            covered_nodes.update(bs.get_covered_nodes())

        if len(covered_nodes) < len(self.remaining_nodes)/2:
            # print("not all nodes are covered!")
            return False

        return True

    def isEmptySpace(self, child):
        return 0 <= child[0] < self.height and 0 <= child[1] < self.width and child not in self.filled_spaces and child not in self.remaining_nodes

    def BS(self, row, col, start, end):
        hasEnd = False
        hasStart = False

        if not self.isEmptySpace((row, col)) or (row, col) in self.BS_seen or (row, col) == end:
            return None

        queue = [(row, col)]
        nodes_found = set()
        seen = {(row, col)}

        while queue:
            curr = queue.pop(0)
            for direction in DIRECTIONS:
                child = (curr[0] + direction[0], curr[1] + direction[1])
                if child == end:
                    hasEnd = True
                    continue
                if child == start:
                    hasStart = True
                    continue
                if child in seen or child in self.BS_seen:
                    continue
                if self.isEmptySpace(child) and child != end:
                    seen.add(child)
                    self.BS_seen.add(child)
                    queue.append(child)
                elif child in self.remaining_nodes:
                    seen.add(child)
                    nodes_found.add(child)
        return BlackSpace(nodes_found, seen.difference(nodes_found), self.nodes, hasStart, hasEnd)

    def solve(self):
        def solve_helper():
            if len(self.remaining_nodes) == 0:
                print(time.time() - t)
                self.canvas.update()
                while True:
                    continue
            start, end = (node for node in self.nodes if self.nodes[node] == self.curr_color)
            if start[0] > end[0] or (start[0] == end[0] and start[1] < end[1]):
                start, end = end, start

            self.remaining_nodes.remove(start)
            self.remaining_nodes.remove(end)

            self.filled_spaces[start] = self.curr_color

            for line in self.make_line(start, end):
                if self.showState == 1:
                    self.canvas.update()
                self.curr_color += 1
                solve_helper()
                self.curr_color -= 1
            self.filled_spaces.pop(start)
            self.remaining_nodes.add(start)
            self.remaining_nodes.add(end)

        solve_helper()

    def make_heat_maps(self):
        # start with just red
        DIRECT8 = {(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)}
        for curr_node in self.remaining_nodes:
            curr_col = self.nodes[curr_node]
            for node in self.remaining_nodes:
                if self.nodes[node] != curr_col:
                    node_dist = max(abs(curr_node[0] - node[0]), abs(curr_node[1] - node[1]))

                    # Construct heat map
                    h_map = []
                    for row in range(self.height):
                        temp = []
                        for col in range(self.width):
                            temp.append(0)
                        h_map.append(temp)

                    h_map[node[0]][node[1]] = node_dist
                    power = 0

                    fill_queue = [(node, node_dist)]
                    seen = {node}

                    while fill_queue:
                        next_node, level = fill_queue.pop(0)
                        h_map[next_node[0]][next_node[1]] = abs(level)
                        power += abs(level)

                        for direction in DIRECT8:
                            child = next_node[0] + direction[0], next_node[1] + direction[1]
                            if child not in seen and 0 <= child[0] < self.height and 0 <= child[1] < self.width:
                                seen.add(child)
                                fill_queue.append((child, level-1))

                    for row in range(len(h_map)):
                        for col in range(len(h_map[row])):
                            self.pos_vals[(row, col)][curr_col] += h_map[row][col] / power * 10

                    for line in h_map:
                        print(line)
                    print("POWER", power)
                    print("______________")
