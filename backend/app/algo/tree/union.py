class UnionFindSet:
    def __init__(self, data_list):
        self.father_dict = {}
        self.size_dict = {}

        for node in data_list:
            self.father_dict[node] = node
            self.size_dict[node] = 1
    
    def find(self, node):
        """
        使用递归的方式来查找父节点
        在查找父节点的时候，顺便把当前节点移动到父节点上面
        """
        father = self.father_dict[node]
        if node != father:
            if father != self.father_dict[father]:
                self.size_dict[father] -= 1
            father = self.find(father)
        self.father_dict[node] = father
        return father

    def is_same_set(self, node_a, node_b):
        return self.find(node_a) == self.find(node_b)

    def union(self, node_a, node_b):
        """
        将两个集合合并在一起
        """
        if node_a is None or node_b is None:
            return

        a_head, b_head = self.find(node_a), self.find(node_b)

        if a_head != b_head:
            a_set_size, b_set_size = self.size_dict[a_head], self.size_dict[b_head]
            if a_set_size >= b_set_size:
                self.father_dict[b_head] = a_head
                self.size_dict[a_head] = a_set_size + b_set_size
            else:
                self.father_dict[a_head] = b_head
                self.size_dict[b_head] = a_set_size + b_set_size

