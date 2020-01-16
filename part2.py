import Graph   # Graph is a defined class

def read_file(file_name):
    edges, nodes = set(), set()
    cpds, queries = [], []
    with open(file_name) as file:
        for line in file:
            line = line.split()

            # read edges
            if all([x.isalpha() for x in line]):
                pa, ch = line
                edges.add((pa, ch))

            # read nodes
                if pa not in nodes:
                    nodes.add(pa)
                if ch not in nodes:
                    nodes.add(ch)

            # read the given cpds
            elif '=' in line:
                cpd = []
                p = float(line[-1])   # the given probability
                cpd.append((line[0][0], int(line[0][1]), p))
                for x in line[2:]:
                    if x[0].isalpha() and x[1].isdigit():
                        cpd.append((x[0], int(x[1])))
                    if x == '=':
                        break
                cpds.append(cpd)   # format example: [('C', 1, 0.1), ('A', 0), ('B', 0)]

            # read queries
            else:
                y = []
                e = []
                for x in line:
                    if line.index(x) < line.index('|'):
                        y.append((x[0], int(x[1])))
                    if x == '|':
                        continue
                    if line.index(x) > line.index('|'):
                        e.append((x[0], int(x[1])))
                queries.append((y,'|', e))   # format example: [([('A', 1)], '|', [('B', 0)])]

            # create Graph object and input the given cpds
            graph = Graph.Graph(edges=edges, nodes=nodes)
            for cpd in cpds:
                node = cpd[0][0]
                graph.cpd[node].input_cpd(cpd)

    return graph, queries

file_name = "part2.txt"
graph, queries = read_file(file_name)
for query in queries:

    # part of the print (describe the query)
    str = " ".join('%s' % id for id in query)
    for i in str:
        if i != '|' and not i.isalnum():
            str = str.replace(i, '')
    print("P(" + str + ") = ", end=' ')

    # divide query into interested nodes and given evidence
    x = []
    e = []
    for entry in query:
        if query.index(entry) < query.index('|'):
            x.append(entry)
        if entry == '|':
            continue
        if query.index(entry) > query.index('|'):
            e.append(entry)
    X = x[0]   # format example: [('A', 1)]
    E = e[0]   # format example: [('B', 0)]
    # Pearl's message passing algorithm
    p = 1
    while X:
        X_1st = X.pop(0)   # the first interested node
        p *= graph.message_passing(X_1st, E)
        E.append(X_1st)    # add the first node to evidence for computing joint distribution
    print(round(p,4))