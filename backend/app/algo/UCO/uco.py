from typing import List
import copy
from functools import lru_cache

import app.algo.heap as heap
from app.algo.decorate import wrapper


@wrapper
def UCO_Index(graph: List[List[float]], filename: str = 'default'):
    vertex_num = len(graph)
    order = [[] for _ in range(vertex_num)]

    k = 0
    is_end = False
    while not is_end:
        k += 1
        is_end = True
        temp_map = copy.deepcopy(graph)
        cur_thres = 0
        vertex_set = set(range(len(temp_map)))

        k_probs = [cal_prob(temp_map, index, k) for index in vertex_set]
        probs_index = [[prob, i] for i, prob in enumerate(k_probs)]
        heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
        heaps.heapify()

        while not graph_is_empty(temp_map):
            u = heaps.heap_pop()
            cur_thres = max(cur_thres, u[0])
            if cur_thres > 0.001:
                is_end = False
                order[u[1]].append(cur_thres)

            # remove v from vertex set
            vertex_set.remove(u[1])
            for i, neighbor in enumerate(temp_map[u[1]]):
                if neighbor != 0:
                    # remove neighbor edge from map
                    remove_edge_from_graph(temp_map, u[1], i)

                    # update k probs

                    k_probs = [cal_prob(temp_map, index, k) for index in vertex_set]
                    probs_index = [[prob, i] for i, prob in zip(vertex_set, k_probs)]
                    heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
                    heaps.heapify()

    return order


def cal_prob(graph: List[List[float]], index: int, k: int) -> float:
    res = 1
    for i in range(0, k):
        res -= cal_prob_equal(graph, index, i)

    return res


def cal_prob_equal(graph: List[List[float]], index: int, k: int) -> float:
    """
    cal prob of index in new graph
    :param graph: will change when edge removal
    :param index: the index of vertex
    :param k: k number
    :return: the k-prob of vertex index
    """
    edges = []

    # find neighbors of index
    for i, m in enumerate(graph):
        if m[index] != 0:
            edges.append(i)

    # print(edges)
    @lru_cache(maxsize=None)
    def X(h, j) -> float:
        """
        cal prob X(h, j)
        :param h: the len of edges
        :param j: the num of degree we suppose
        :return: the prob
        """
        if j == -1:
            return 0
        elif h == 0 and j == 0:
            return 1
        elif h <= len(edges) and h + 1 <= j <= k:
            return 0
        return graph[index][edges[h - 1]] * X(h - 1, j - 1) + (1 - graph[index][edges[h - 1]]) * X(h - 1, j)

    return X(len(edges), k)


def graph_is_empty(graph: List[List[float]]) -> bool:
    for i in graph:
        for j in i:
            if j != 0:
                return False
    return True


def remove_edge_from_graph(graph: List[List[float]], x: int, y: int):
    graph[x][y] = .0
    # graph[y][x] = .0


def print_res(index: List[List[int]]):
    for i, ins in enumerate(index):
        print('v' + str(i + 1), end=': ')
        for j in ins:
            print(round(j, 2), end='\t')
        print()


if __name__ == '__main__':
    graph = [
        [.0, .5, .2, .0, .0, .0, .0, .0, .0, .0],
        [.5, .0, .8, .2, .6, .0, .0, .0, .0, .0],
        [.2, .8, .0, .5, .8, .0, .0, .0, .0, .0],
        [.0, .2, .5, .0, .4, .0, .0, .0, .0, .0],
        [.0, .6, .8, .4, .0, .2, .0, .0, .0, .0],
        [.0, .0, .0, .0, .2, .0, .5, .0, .0, .0],
        [.0, .0, .0, .0, .0, .5, .0, .8, .5, .8],
        [.0, .0, .0, .0, .0, .0, .8, .0, .0, .0],
        [.0, .0, .0, .0, .0, .0, .5, .0, .0, .8],
        [.0, .0, .0, .0, .0, .0, .8, .0, .8, .0],
    ]
    print_res(UCO_Index(graph))
