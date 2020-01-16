import numpy as np

class CPD(object):

    def __init__(self, num):
        size = [2] * num
        self.cpd_table = np.zeros(size)  # create a table to store the given cpds
        self.node_name = []

    def input_cpd(self, cpd):       # format example of input : [('C', 1, 0.1), ('A', 0), ('B', 0)]
        self.node_name = [info[0] for info in cpd]
        node_value = [0] * len(cpd)
        for info in cpd:
            index = self.node_name.index(info[0])
            node_value[index] = info[1]

        cmp_node_value = node_value[:]
        cmp_node_value[0] = 1 - cmp_node_value[0]  # complementary event
        node_value = tuple(node_value)             # index of cpd to update  e.x. (1,0,0)
        cmp_node_value = tuple(cmp_node_value)     # index of complementary cpd to update  e.x. (0,0,0)

        p = cpd[0][2]
        self.cpd_table[node_value] = p
        self.cpd_table[cmp_node_value] = np.round(1 - p, 4)