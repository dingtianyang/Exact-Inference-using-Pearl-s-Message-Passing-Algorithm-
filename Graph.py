import itertools
import CPD    # CPD is a defined class

class Graph(object):

    def __init__(self, edges=set(), nodes=set()):
        self.edges = edges        # set of tuples : {('A', 'C'), ('D', 'G'), ...}
        self.nodes = nodes        # set of nodes : {'G', 'C', ...}
        self.root = set()
        self.parents = {}         # {node : set of parents}
        self.children = {}        # {node : set of children}
        self.cpd = {}             # {node : class CPD}
        self.lambda_values = {}   # {node : [value0, value1]}
        self.pi_values = {}       # {node : [value0, value1]}
        self.lambda_msg = {}      # {child1 : {parent1 : [parent1_value0, parent1_value1], parent2 : [parent2_value0, parent2_value1]},
                                  #  child2 : {parent1 : [parent1_value0, parent1_value1], parent2 : [parent2_value0, parent2_value1],...}
        self.pi_msg = {}          # {parent1 : {child1 : [parent1_value0, parent1_value1], child2 : [parent2_value0, parent2_value1]},
                                  #  parent2 : {child1 : [parent1_value0, parent1_value1], child2 : [parent2_value0, parent2_value1],...}

        # create self.parents and self.children
        for edge in self.edges:
            pa, ch = edge
            if ch not in self.parents:
                self.parents.update({ch: set(pa)})
            else:
                self.parents[ch].add(pa)
            if pa not in self.children:
                self.children.update({pa: set(ch)})
            else:
                self.children[pa].add(ch)

        # find root nodes
        for node in self.nodes:
            if node not in self.parents:
                self.root.add(node)

        # create self.cpd
        for node in self.nodes:
            num = len(self.find_pa(node)) + 1   # number of parents + 1
            self.cpd[node] = CPD.CPD(num)

    # find parents of given node
    def find_pa(self, node):
        if node in self.parents:
            return self.parents[node]
        else:
            return set()

    # find children of given node
    def find_ch(self, node):
        if node in self.children:
            return self.children[node]
        else:
            return set()

    # find the specific cpd in the cpd table based on input
    def find_cpd(self, X, E=[]):   # format example of input : X = [('A', 1)] E = [['F', 1], ['A', 0]]
        if len(X) == 1:
            p_index = [0 for i in self.cpd[X[0][0]].node_name]
            info = X[:]
            for e in E:
                info.append(e)
            for i in info:
                var, val = i
                var_index = self.cpd[X[0][0]].node_name.index(var)
                p_index[var_index] = val
            p_index = tuple(p_index)
            return self.cpd[X[0][0]].cpd_table[p_index]

    # Pearl's message passing algorithm
    def message_passing(self, X, E=[]):   # format example of input : X = ('A', 1) E = [('F', 1), ('A', 0)]
        self.initialize_network()

        for e in E:
            self.update_network(e[0], e[1])
        alpha = 0
        for x in [0, 1]:
            lambda_value = self.lambda_values[X[0]][x]
            pi_value = self.pi_values[X[0]][x]
            alpha += lambda_value * pi_value
        p = (1 / alpha) * self.lambda_values[X[0]][X[1]] * self.pi_values[X[0]][X[1]]
        return p

    # initialize network
    def initialize_network(self):
        self.instantiated = {}   # {node : value}
        for node in self.nodes:
            self.lambda_values.update({node: [1.0, 1.0]})
            self.pi_values.update({node: [1.0, 1.0]})
            self.lambda_msg.update({node: {}})
            for parent in self.find_pa(node):
                self.lambda_msg[node].update({parent: [1.0, 1.0]})
            self.pi_msg.update({node: {}})
            for child in self.find_ch(node):
                self.pi_msg[node].update({child: [1.0, 1.0]})

        for R in self.root:
            for r in [0, 1]:
                p = self.find_cpd([(R, r)], [])
                self.pi_values[R][r] = p
            for W in self.find_ch(R):
                self.send_pi_msg(R, W)

    # update network
    def update_network(self, V, v_hat):   # input : new instantiated node (E,e)
        self.instantiated.update({V: v_hat})
        for v in [0, 1]:
            if v == v_hat:
                self.lambda_values[V][v] = 1   # update lambda_value
                self.pi_values[V][v] = 1       # update pi_value
            else:
                self.lambda_values[V][v] = 0   # update lambda_value
                self.pi_values[V][v] = 0       # update pi_value
        # send lambda msg and pi msg
        set_Z = self.find_pa(V) - set(self.instantiated.keys())
        for node_Z in set_Z:
            self.send_lambda_msg(V, node_Z)
        for Y in self.find_ch(V):
            self.send_pi_msg(V, Y)

    # send lambda msg
    def send_lambda_msg(self, Y, X):   # Y(child)  -->  X(parent)
        # calculate lambda msg from Y to X and lambda value of X
        for x in [0, 1]:
            set_W = self.find_pa(Y) - {X}
            sum_y = 0                  # marginalize y out
            for y in [0, 1]:
                sum_w = 0              # marginalize w1,w2,.. out
                evidence = [(X, x)]
                for node_W in set_W:
                    evidence.append([node_W, 0])
                w_combinations = itertools.product([0, 1], repeat=len(set_W))
                for w_combination in w_combinations:
                    index = 1
                    for value in w_combination:
                        evidence[index][1] = value
                        index += 1
                    p = self.find_cpd([(Y, y)], evidence)
                    pi_msg_product = 1
                    for entry in evidence[1:]:
                        pi_msg = self.pi_msg[entry[0]][Y][entry[1]]
                        pi_msg_product *= pi_msg
                    sum_w += p * pi_msg_product
                sum_y += sum_w * self.lambda_values[Y][y]
            # update lambda msg
            self.lambda_msg[Y][X][x] = sum_y

            # update lambda value
            lambda_value = 1
            for U in self.find_ch(X):
                lambda_value *= self.lambda_msg[U][X][x]
            self.lambda_values[X][x] = lambda_value

        # send lambda msg
        set_Z = self.find_pa(X)
        for node_Z in set_Z:
            if node_Z in self.instantiated:
                continue
            self.send_lambda_msg(X, node_Z)

        # send pi msg
        set_U = self.find_ch(X) - {Y}
        for node_U in set_U:
            self.send_pi_msg(X, node_U)

    # send pi msg
    def send_pi_msg(self, Z, X):   # Z(parent)  -->  X(child)
        # calculate pi msg from Z to X
        for z in [0, 1]:
            set_U = self.find_ch(Z) - {X}
            lambda_msgs = 1
            for node_U in set_U:
                lambda_msgs *= self.lambda_msg[node_U][Z][z]
            pi_msg = self.pi_values[Z][z] * lambda_msgs
            # update pi msg
            self.pi_msg[Z][X][z] = pi_msg

        # calculate pi value of X
        if X not in self.instantiated:
            for x in [0, 1]:
                sum_z = 0       # marginalize z out
                set_Z = self.find_pa(X)
                z_combinations = itertools.product([0, 1], repeat=len(set_Z))
                evidence = []
                for node_Z in set_Z:
                    evidence.append([node_Z, 0])
                for z_combination in z_combinations:
                    index = 0
                    for value in z_combination:
                        evidence[index][1] = value
                        index += 1
                    p = self.find_cpd([(X, x)], evidence)
                    pi_msg_product = 1
                    for entry in evidence:
                        pi_msg_product *= self.pi_msg[entry[0]][X][entry[1]]
                    sum_z += p * pi_msg_product
                # update pi value
                self.pi_values[X][x] = sum_z

            # send pi msg
            for Y in self.find_ch(X):
                self.send_pi_msg(X, Y)

        # send lambda msg
        lambda_values_of_x = []
        for x in [0, 1]:
            lambda_values_of_x.append(self.lambda_values[X][x])
        if any([i != 1 for i in lambda_values_of_x]):
            set_W = self.find_pa(X) - {Z}
            for W in set_W:
                if W not in self.instantiated:
                    self.send_lambda_msg(X, W)