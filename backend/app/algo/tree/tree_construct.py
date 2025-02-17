# UCF Construct
import sys
import copy
from typing import List

import UCO
import heap
import decorate
from maintenance.maintenance import delete_edges


class TreeNode:
    # nodes: []
    # children: set
    # k: int
    # upper_threshold: float
    # lower_threshold: float
    # father: 'TreeNode'

    def __init__(self, nodes, k, threshold):
        self.nodes = nodes
        self.k = k
        self.upper_threshold = threshold
        self.lower_threshold = threshold
        self.father = None
        self.children = set()

    def set_father(self, father: 'TreeNode', bottom):
        self.father = father
        if not hasattr(father, 'children'):  # 检查father是否有children属性
            father.children = set()
        father.children.add(self)
        if bottom in father.children:
            father.children.remove(bottom)

    def get_threshold(self) -> float:
        return max(self.upper_threshold, self.lower_threshold)

    def merge_node(self, node: 'TreeNode'):
        self.nodes.extend(node.nodes)
        self.nodes = list(set(self.nodes))
        self.children = self.children | node.children

    def __str__(self):
        return ','.join(str(node) for node in self.nodes) \
            + ('->' + '->'.join([str(c) for c in self.children]))


class BottomTreeNode(TreeNode):
    def __init__(self, nodes, k, threshold=1):
        super().__init__(nodes, k, threshold)
        self.father = list()

    def set_father(self, father: 'TreeNode'):
        if father in self.father:
            return
        self.father.append(father)
        father.children.add(self)

    def __str__(self):
        return "buttom" + "|"


@decorate.wrapper
def construct_tree(graph: List[List[float]], threshold=0.01):
    """
    fin function of this proj
    :param graph: the 2-D matrix of graph
    :param threshold: the threshold that set to accelerate the parse of the tree
    :return: TreeNode
    """
    assert threshold <= 0.1, "threshold is too big"
    # compare core
    core = cal_core(copy.deepcopy(graph))
    cores = [[i, c] for i, c in enumerate(core)]

    cores = sorted(cores, key=lambda x: x[1], reverse=True)
    k_max = cores[0][1]
    forest = {}
    for k in range(k_max, 0, -1):        
        temp_graph, vertex = extract_graph(graph, k, cores)
        probs = [UCO.cal_prob(temp_graph, index, k) for index in vertex]
        cur_thres = 0
        S = list() # S is a stack
        eta_threshold = [0 for _ in range(len(graph))]
        probs_index = [[prob, i] for i, prob in enumerate(probs)]
        heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
        heaps.heapify()

        while not UCO.graph_is_empty(temp_graph):
            u = heaps.heap_pop()
            cur_thres = max(cur_thres, u[0])
            eta_threshold[u[1]] = cur_thres
            S.append(u[1])

            # remove v from vertex set
            vertex.remove(u[1])
            for i, neighbor in enumerate(temp_graph[u[1]]):
                if neighbor != 0:
                    # remove neighbor edge from map
                    UCO.remove_edge_from_graph(temp_graph, u[1], i)

                    # update k probs
                    probs = [UCO.cal_prob(temp_graph, index, k) for index in vertex]
                    probs_index = [[prob, i] for i, prob in zip(vertex, probs)]
                    heaps = heap.Heap(probs_index, compare=lambda a, b: a[0] > b[0])
                    heaps.heapify()

        print('cal', k, S, eta_threshold)
        forest[k] = construct_eta_k_tree(copy.deepcopy(graph), k, S, eta_threshold)
    return forest


def cal_core(graph: List[List[float]]):
    n = len(graph)
    core = list(range(n))
    vertex = set(list(range(n)))
    visited = [False for _ in range(n)]
    while len(vertex) != 0:
        degree = degree_certain_graph(graph)
        index = find_min(degree, visited)
        k = degree[index]
        while index != -1 and degree[index] <= k:
            core[index] = k
            # remove edge
            for i in range(n):
                if graph[index][i] != 0:
                    degree[i] -= 1
                    degree[index] -= 1
                    graph[index][i] = .0
                    graph[i][index] = .0

            visited[index] = True
            vertex.remove(index)
            # update index
            index = find_min(degree, visited)

    return core


def find_min(degree, visited):
    index, k = -1, sys.maxsize
    for i, d in enumerate(degree):
        if visited[i]:
            continue
        if d < k:
            k = d
            index = i

    return index


def degree_certain_graph(graph: List[List[float]]):
    """
    calculate the origin degree of the graph
    :param graph:
    :return:
    """
    n = len(graph)
    vertex = [0 for _ in range(n)]
    for i, g in enumerate(graph):
        for p in g:
            if p != 0:
                vertex[i] += 1
    
    return vertex


def extract_graph(graph, k, cores):
    vertex = []
    for core in cores:
        if core[1] >= k:
            vertex.append(core[0])
    
    temp_graph = copy.deepcopy(graph)
    delete_edges(temp_graph, vertex)
    return temp_graph, set(vertex)


def find_connected_component(graph, vertexes, visited: List[int]) -> List[List[int]]:
    """
    find the connected vertexes groups in the graph which the path should take the visited points into consideration.
    :param graph:
    :param vertexes:
    :param visited: the points have already been visited before
    :return: [[]]
    """
    if len(vertexes) <= 1:
        return [vertexes]

    vertex = vertexes.copy()

    for i, v in enumerate(visited):
        if v and i not in vertexes:
            vertexes.append(i)

    node_index, n, group = 0, len(vertexes), 0

    res = [-1 for _ in range(n)]
    res[node_index] = group

    while node_index < n:
        find_more = True
        neighbor = set([i for i, v in enumerate(graph[vertexes[node_index]]) if v != 0])

        while find_more:
            find_more = False
            for k, v in enumerate(vertexes):
                if res[k] == -1 and v in neighbor:
                    res[k] = res[node_index]
                    find_more = True
                    neighbor = neighbor | set([i for i, v in enumerate(graph[v]) if v != 0])
        
        i = 0
        while i < n and res[i] != -1:
            i += 1
        node_index = i
        group += 1
        if node_index < n:
            res[node_index] = group

    ans = [[] for _ in range(group)]
    # print('group', res, vertex)
    for i, r in enumerate(res):
        if vertexes[i] not in vertex:
            continue
        ans[r].append(vertexes[i])

    return [a for a in ans if len(a) != 0]


def find_neighbors(graph, vertexes):
    neighbor = set()
    for v in vertexes:
        neighbor = neighbor | set([i for i, p in enumerate(graph[v]) if p != 0])
    
    return neighbor


def find_node(bottom: TreeNode, v) -> TreeNode:
    """
    find the node where v exists by dfs
    :param bottom: the bottom TreeNode
    :param v:
    :return:
    """
    if not bottom:
        return None
    if v in bottom.nodes:
        return bottom
    elif isinstance(bottom, BottomTreeNode):
        for father in bottom.father:
            node = find_node(father, v)
            if node:
                return node
    else:
        node = find_node(bottom.father, v)
        if node:
            return node


def get_root(node: TreeNode) -> TreeNode:
    if isinstance(node, BottomTreeNode):
        return get_root(node.father[0]) if len(node.father) > 0 else node

    while node.father:
        # print('father: ', node.father)
        node = node.father
    return node


def construct_eta_k_tree(graph: List[List[float]], k: int, stack: List[int], eta_threshold: List[float]):
    bottom = BottomTreeNode([], k, 1)
    visited = [False for _ in range(len(graph))]
    while len(stack) != 0:
        node = stack[-1]
        stack = stack[:-1]
        ct = eta_threshold[node]
        H = [node]
        while len(stack) != 0 and eta_threshold[stack[-1]] == ct:
            H.append(stack[-1])
            stack = stack[:-1]

        # print('H', H, visited)
        for connected in find_connected_component(graph, H, visited):
            # print('connected', connected)
            for c in connected:
                visited[c] = True
            x_treeNode = TreeNode(connected, k, ct)
            bottom.set_father(x_treeNode)
            for v in find_neighbors(graph, connected):
                if v in connected or eta_threshold[v] < ct:
                    continue
                # 1. get the node containing v (Y)
                # print(v, eta_threshold[v], ct, [i.nodes for i in bottom.father])
                y_treeNode = find_node(bottom, v)
                # 2. get the root of Y (Z)
                z_treenode = get_root(y_treeNode)
                # print("get root: ", z_treenode.get_threshold(), 'node is:', x_treeNode.get_threshold())
                if z_treenode.get_threshold() > x_treeNode.get_threshold():
                    z_treenode.set_father(x_treeNode, bottom)
                else:
                    x_treeNode.merge_node(z_treenode)

    return get_root(bottom)


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

    for k, tree in construct_tree(graph).items():
        print(k, tree)
