from collections import defaultdict


class Graph:
    def __init__(self):
        self.vertices = set()
        self.edges = defaultdict(dict)

    def add_vertex(self, vertex):
        self.vertices.add(vertex)

    def add_edge(self, vertex1, vertex2, weight):
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        self.edges[vertex1][vertex2] = weight
        self.edges[vertex2][vertex1] = weight

    def shortest_path(self, source, destination):
        unvisited = set(self.vertices)
        distance = {vertex: float("inf") for vertex in self.vertices}
        previous = {vertex: None for vertex in self.vertices}
        distance[source] = 0

        while unvisited:
            current = min(unvisited, key=lambda vertex: distance[vertex])
            unvisited.remove(current)

            for neighbor in self.edges[current]:
                new_distance = distance[current] + self.edges[current][neighbor]
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current

        path = []
        while destination != source:
            path.append(destination)
            destination = previous[destination]
        path.append(source)

        return path[::-1]
