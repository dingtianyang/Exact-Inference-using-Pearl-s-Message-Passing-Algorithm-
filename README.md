# Exact-Inference-using-Pearl-s-Message-Passing-Algorithm

The code contains three parts: main.py, Graph.py and CPD.py.

Graph.py contains several graph attributes such as nodes, edges, relationships between nodes as well as attributes and functions of Pearl’s MP algorithm.

CPD.py can be regard as a cpd table that stores the given cpds. The specific cpd can be found according to the index.

main.py contains a read_file function which can read the input file and then generate the graph defined in Graph.py, it can also read the queries. Then, for each query, Pearl’s MP algorithm is used.

You can run the code for different graphs if you follow the same format as shown in part1.txt.
