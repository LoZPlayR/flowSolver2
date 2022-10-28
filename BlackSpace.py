class BlackSpace:
    def __init__(self, cn=None, bs=None, nodes=None, hasStart = False, hasEnd=False):
        self.hasEnd = hasEnd
        self.hasStart = hasStart

        if nodes is None:
            nodes = {}
        if cn:
            self.connected_nodes = cn
        else:
            self.connected_nodes = set()

        if bs:
            self.black_spaces = bs
        else:
            self.black_spaces = set()

        self.covered_nodes = set()
        seen = set()

        for node in set(self.connected_nodes):
            if nodes[node] in seen:
                self.covered_nodes.add(nodes[node])
            else:
                seen.add(nodes[node])

    def __len__(self):
        return len(self.black_spaces)

    def get_covered_nodes(self):
        return self.covered_nodes

    def __bool__(self):
        # chokepoints = self.find_chokepoints()

        # For a valid connected space, there must be at least 1 matching set of nodes
        return len(self.covered_nodes) > 0 or (self.hasEnd and self.hasStart)

    def __repr__(self):
        return "BlackSpace containing " + str(self.black_spaces) + " spaces connecting " + \
               str(len(self.connected_nodes)) + " nodes: " + str(self.connected_nodes)
    #
    # def find_chokepoints(self):
    #     print(self.get_heights())

    def get_heights(self):
        seen = set()
        all_heights = []

        def heights(space):
            top_most = space
            num = 1
            seen.add(space)
            up, down = (space[0] - 1, space[1]), (space[0] + 1, space[1])
            if up in self.black_spaces and up not in seen:
                inc, top_most = heights(up)
            if down in self.black_spaces and down not in seen:
                num += heights(down)[0]

            return num, top_most

        for space in self.black_spaces:
            if space not in seen:
                height = heights(space)
                all_heights.append(height)

        return all_heights

    def get_widths(self):
        seen = set()
        all_widths = []

        def widths(space):
            num = 1
            seen.add(space)
            left, right = (space[0], space[1] - 1), (space[0], space[1] + 1)
            if left in self.black_spaces and left not in seen:
                num += widths(left)
            if right in self.black_spaces and right not in seen:
                num += widths(right)

            return num

        for space in self.black_spaces:
            if space not in seen:
                width = widths(space)
                all_widths.append((width, space))

        return all_widths