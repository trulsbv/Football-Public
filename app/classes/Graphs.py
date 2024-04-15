import graphviz as gv
import randomcolor as rc
import colorsys as cs
import os
import settings
import shutil


def generate_random_dark_color():
    """
    Generate a single random color with a dark hue.
    """
    random_color = rc.RandomColor()
    while True:
        color = random_color.generate(count=1)[0][1:]  # Generate a single random color
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))  # Convert color to RGB
        hsl = cs.rgb_to_hls(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)  # Convert RGB to HSL
        # Check if the lightness (L) value is less than a threshold (e.g., 0.5 for dark colors)
        if hsl[1] < 0.5 or hsl[2] < 0.5:
            return f"#{color}"  # Return the color if it has a dark hue


class Edge:
    def __init__(self, first, second, weight=0):
        self.first = first
        self.second = second
        self.weight = weight

    def __eq__(self, edge):
        if isinstance(edge, Edge):
            return (self.first == edge.first and self.second == edge.second)
            # above + or (self.second == edge.first and self.first == edge.second)
        return False

    def __str__(self):
        return f"{self.first}, {self.second}"

    def getNodes(self):
        return [self.first, self.second]

    def getOther(self, node):
        if node == self.first:
            return self.second
        return self.first


class Node:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.edges = []

    def display(self) -> None:
        ctr = 0
        for edge in self.edges:
            if self == edge.second:
                continue
            ctr += edge.weight
        return f"{self.name} ({ctr})"

    def __eq__(self, node):
        if isinstance(node, Node):
            return self.name == node.name
        return False

    def __repr__(self) -> str:
        return self.name

    def addEdge(self, edge):
        self.edges.append(edge)


class DirectedCumulativeGraph():
    def __init__(self):
        self.name = ...
        self.nodes = []
        self.edges = []

    def find_edge(self, start: Node, finish: Node):
        for edge in self.edges:
            if edge.first == start and edge.second == finish:
                return edge
        return False

    def add_edge(self, start: str, finish: str):
        start = self.find_node(start)
        finish = self.find_node(finish)
        edge = self.find_edge(start, finish)
        if edge:
            edge.weight += 1
            return
        edge = Edge(start, finish, 1)
        start.addEdge(edge)
        finish.addEdge(edge)
        self.edges.append(edge)

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        n = Node(name, generate_random_dark_color())
        self.nodes.append(n)
        return n

    def export_graph(self, club_name):
        dot = gv.Graph()
        format = "svg"
        for node in self.nodes:
            dot.node(node.name, node.display(), color=node.color)

        for edge in self.edges:
            dot.edge(edge.first.name,
                     edge.second.name,
                     label=str(edge.weight),
                     dir='forward',
                     color=edge.first.color)

        name = f'{club_name}_assists'
        filename = f"{name}.{format}"
        folder = f"{os.getcwd()}/{settings.FOLDER}/{format}"
        dot.render(f'{club_name}_assists', format=format)

        if os.path.exists(name) and not os.path.isdir(name) and not os.path.islink(name):
            os.remove(f'{club_name}_assists')

        folder = f"{os.getcwd()}/{settings.FOLDER}/{format}"
        if not os.path.isdir(folder):
            os.mkdir(folder)

        cur = f"{os.getcwd()}/{filename}"
        new = f"{folder}/{filename}"
        print(f"File:\n{new}")
        shutil.move(cur, new)
