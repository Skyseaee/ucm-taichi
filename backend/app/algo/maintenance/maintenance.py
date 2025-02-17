import copy
import traceback
from concurrent.futures import ProcessPoolExecutor
from typing import List

from app.algo.UCO import uco as UCO
from app.algo import heap
from app.utils.graph_parser import pipeline_read_data
from app.utils.graph_parser  import pipeline_change_map
from app.algo.decorate import wrapper


class prob_of_vertex:
    prob: float
    index: int

    def __init__(self, index):
        self.prob = .0
        self.index = index

    def is_vaild(self) -> bool:
        if not 0 <= self.prob <= 1:
            return False


# used to construct heap
def prob_compare(v1: prob_of_vertex, v2: prob_of_vertex) -> bool:
    return v1.prob <= v2.prob


"""
when the prob of a edge (u, v) changes, we suppose k-prob(u) <= k-prob(v),
recalculate the k-prob of u and maintain the upper bound, which is the max
k-prob of the subset of changed vertex.
"""


def cal_k_probs_when_inserting(graph: List[List[float]], k_probs: List[List[float]], k: int, edge: List[int]):
    """
    cal new k-probs for special k
    :param graph:
    :param k_probs:
    :param k:
    :param edge:
    :return:
    """
    probs = k_probs[k-1]

    u = edge[1]
    # we suppose k-prob(u) <= k-prob(v)
    if probs[edge[0]] <= probs[edge[1]]:
        u = edge[0]
    if k > 2 and k_probs[k-2][u] < .001:
        return probs

    updating_vertexes = find_updating_vertex_when_inserting(u, graph, probs)
    # delete edges
    graph = delete_edges(graph, updating_vertexes)
    temp_vertex = set(updating_vertexes)

    updating_vertexes = [[vertex, False] for vertex in updating_vertexes]
    # we suppose upper_bound is the new k-prob of u
    upper_bound = probs[u] + .01
    temp_k_probs = [UCO.cal_prob(graph, i[0], k) for i in updating_vertexes]

    probs_index = [[prob, i[0]] for i, prob in zip(updating_vertexes, temp_k_probs)]
    heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
    heaps.heapify()

    # should use new judging condition
    cur_thres = probs[u]
    temp_map = copy.deepcopy(graph)
    # vertex_set = set(updating_vertexes)
    while not updating_ended(probs, updating_vertexes, upper_bound):
        temp = heaps.heap_pop()

        current_vertex = -1
        for i, index in enumerate(updating_vertexes):
            if index[0] == temp[1]:
                current_vertex = i
                updating_vertexes[i][1] = True
                break

        cur_thres = max(cur_thres, temp[0])

        if cur_thres > .0001:
            upper_bound = upper_bound_updating(upper_bound, cur_thres)
            probs[updating_vertexes[current_vertex][0]] = cur_thres

        temp_vertex.remove(temp[1])
        for i, neighbor in enumerate(temp_map[temp[1]]):
            if neighbor != 0:
                UCO.remove_edge_from_graph(temp_map, temp[1], i)

        # update k probs
        k_probs = [UCO.cal_prob(temp_map, index, k) for index in temp_vertex]
        probs_index = [[prob, i] for i, prob in zip(temp_vertex, k_probs)]
        heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
        heaps.heapify()

    return probs


def find_updating_vertex_when_inserting(index_of_u: int, graph: List[List[float]], k_probs_of_vertexes: List[float]) -> List[int]:
    """
    use bfs to find which vertex should be updating, the lower_bound is k-probs of u when inserting
    :param index_of_u:
    :param graph:
    :param k_probs_of_vertexes:
    :return: updating vertex
    """
    visited = [False for _ in range(len(graph))]
    visited[index_of_u] = True
    queue = [index_of_u]
    res = [index_of_u]
    while len(queue) != 0:
        temp = queue[0]
        queue = queue[1:]
        for index in find_neighbors(graph, temp):
            if not visited[index] and k_probs_of_vertexes[index] >= k_probs_of_vertexes[index_of_u]:
                visited[index] = True
                queue.append(index)
                res.append(index)

    return res


def find_neighbors(graph: List[List[float]], index: int) -> List[int]:
    res = []
    for i, e in enumerate(graph[index]):
        if i != index and e > 0:
            res.append(i)

    return res


def updating_ended(k_probs: List[float], updating_vertex: List[int], upper_bound: float) -> bool:
    """
    check whether all the updating vertex is updated
    :param k_probs: the probs of k for each vertex
    :param updating_vertex: vertex in updating
    :param upper_bound: the change upper_bound probs
    :return: True to end the while loop
    """
    for up in updating_vertex:
        if up[1]:
            continue
        if k_probs[up[0]] < upper_bound:
            return False
    return True


def upper_bound_updating(ub1: float, ub2: float) -> float:
    """
    omit the tiny change in upper_bound
    :param ub1: old upper_bound
    :param ub2: new upper_bound
    :return: new upper_bound
    """
    if ub2 - ub1 > .0001:
        return ub2
    return ub1


def delete_edges(graph: List[List[float]], updating_vertex: List[int]):
    updating_vertex = set(updating_vertex)
    for i in range(len(graph)):
        for j in range(len(graph)):
            if i not in updating_vertex or j not in updating_vertex:
                graph[i][j] = .0

    return graph


def transpose_matrix(k_probs: List[List[float]]):
    try:
        res = [[] for _ in range(len(k_probs[0]))]
        for i in range(len(k_probs)):
            for j in range(len(k_probs[0])):
                if j < len(k_probs[i]):
                    res[j].append(k_probs[i][j])
                else:
                    res[j].append(0)
        return res
    except IndexError:
        print(i, j, len(k_probs[i]))
        traceback.print_exc()
        exit(-1)


def change_graph(graph: List[List[float]]):
    i, j = 2, 3
    assert i != j, "i can not equal to j"

    new_value = .8
    assert new_value <= 1, "the weight of edge can't larger then 1"

    graph[i][j] = new_value
    graph[j][i] = new_value
    return graph


def reorg_heap(heap: List[List[float]], k_core: int):
    res = [[] for _ in range(k_core)]
    for r in range(k_core):
        for h in heap:
            if len(h) <= r:
                res[r].append(.0)
            else:
                res[r].append(h[r])
    return res


@wrapper
def core_maintenance(k_core, origin_heap, changed_points, graph, filename = 'unknown'):
    final_index = []
    for i in range(1, k_core + 1):
        final_index.append(cal_k_probs_when_inserting(graph, origin_heap, i, changed_points))

    return final_index


def cal_files(filename):
    graph = pipeline_read_data(filename)
    heaps = UCO.UCO_Index(graph, filename=filename)

    k_core = 0
    for h in heaps:
        k_core = max(len(h), k_core)

    temp_heap = reorg_heap(heaps, k_core)

    for h in heaps:
        k_core = max(k_core, len(h))
    for i in range(10):
        indexes_of_changed_points = pipeline_change_map(graph, True)
        # UCO.UCO_Index(graph, filename=filename)
        core_maintenance(k_core, temp_heap, indexes_of_changed_points, copy.deepcopy(graph), filename=filename)


def main():
    files = ['rajat05.mtx', 'chesapeake.mtx.convert', 'inf-euroroad.edges.convert', 'ca-GrQc.mtx.convert']
    # files = ['aves-geese-female-foraging.edges']
    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(cal_files, files)
    # cal_files(files[0])


if __name__ == '__main__':
    main()