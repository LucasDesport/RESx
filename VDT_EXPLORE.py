import readers as rd
import networkx as nx
import gravis as gv

# #### Read vdt file

#fname = 'victor.vdt' 
#fname = 'lucas.vdt' 
fname, columns = 'lucas_clean.csv', ['process','commodity','direction']
G, processes, commodities = rd.graph_from_csv(fname, *columns)

G

processes

commodities

# #### Dimensions

nProcesses = len(processes)
nCommodities = len(commodities)
nNodes = len( G.nodes())
nEdges = len( G.edges())
report = f'Data processes={nProcesses} commodities={nCommodities}  Graph nodes={nNodes} edges={nEdges}'
assert nNodes == nProcesses + nCommodities, f'Unexpected {report}'
print(report)

G.is_directed()

nx.is_directed_acyclic_graph(G)

# #### Set type, color, depth=None

for n in processes:
    G.nodes[n]['color']= 'red' 
    G.nodes[n]['type']= 'process' 
    G.nodes[n]['depth']= None 
for n in commodities:
    G.nodes[n]['color']= 'blue' 
    G.nodes[n]['type']= 'commodity'
    G.nodes[n]['depth']= None 

# #### Leaves are out_degree=0 nodes

leaves = [n for n in G.nodes if G.out_degree(n) == 0]

# #### Roots are in_degree=0 nodes

roots = [n for n in G.nodes if G.in_degree(n) == 0]

# #### Check all leaves are commodities, memorize abnormal

funny_leaves = list()
for n in leaves:
    type = G.nodes[n]['type']
    report = f'Leave {n}  {type}'
    try:
        assert type == 'commodity' 
    except:
        print(report)
        funny_leaves.append(n)
print('funny_leaves', funny_leaves)


# #### Check all roots are processes, memorize abnormal

funny_roots = list()
for n in roots:
    type = G.nodes[n]['type']
    report = f'Root {n}  {type}  remove'
    try:
        assert type == 'process' 
    except:
        print(report)
        funny_roots.append(n)
print('funny_roots', funny_roots)


# #### Remove funny, rebuild leaves and roots

for n in funny_leaves + funny_roots:
    G.remove_node(n)
roots = [n for n in G.nodes if G.in_degree(n) == 0]
leaves = [n for n in G.nodes if G.out_degree(n) == 0]
nNodes = len(G.nodes)

# #### Topological sort, more pythonic some day


# +
broken_edges = list()
def set_depth(edge_list, depth):
    next_list = list()
    for e in edge_list:
        n, m = e
        if n in funny_roots or m in funny_leaves :
            continue
        if G.nodes[n]['depth'] == None:
            G.nodes[n]['depth'] = depth
            next_list += [(a, n) for a in G.predecessors(n)]
        else:
            broken_edges.append(e)
    
    return next_list, depth + (1 if next_list else 0)

initial_edge_list = [(n, None) for n in leaves ]
nl = initial_edge_list
depth = 0
while nl:
    print(depth)
    nl, depth  = set_depth(nl, depth)
    
graph_width = depth  
print(f'Sorted graph:  nodes {nNodes}  width   {graph_width}')
# -

# #### Extracted graph 

good_nodes = [n for n in G.nodes if not G.nodes[n]['depth'] is None]
bad_nodes = [n for n in G.nodes if  G.nodes[n]['depth'] is None]
for n in bad_nodes:
    print(G.nodes[n]['type'], n)

# #### Check

# +
print([len(bad_nodes), len(funny_leaves), len(funny_roots)])
print([len(bad_nodes), len(good_nodes), nNodes])

assert len(bad_nodes) == 0 , 'Extracted graph: unexpected dimensions'
# -

GX = G.subgraph(good_nodes)
len(GX.nodes)

# #### Plot

gv.d3(GX, node_label_size_factor=0.3)

print(f'Edges: total {nEdges} - broken {len(broken_edges)}')

roots

leaves

broken_edges

# #### Check depth parity vs node type


for n in G.nodes:
    type = G.nodes[n]['type']
    depth = G.nodes[n]['depth'] 
    if not depth is None :
        try:
            assert depth % 2 == (0 if type == 'commodity'  else 1)
        except:
            print('Parity error' , n, type, depth)
print('Parity check OK')

# #### Check for emissions

for n in bad_nodes:
    print(G.nodes[n]['type'], n, '->' ,  [ f"{G.nodes[s]['type']}:{s}"  for s in list(G.successors(n))  ])

len(GX.nodes)

GX.is_directed()

nx.is_directed_acyclic_graph(GX)

# #### Build bins 

bins = {d:[n for n in GX.nodes if GX.nodes[n]['depth']==d] for d in range(graph_width)}

bins

roots

for num, lst in bins.items():
    print(num, len(lst))

funny_leaves

funny_roots

nx.find_cycle(GX)

path = 'lucas_clean.xml'
nx.write_graphml(GX, path)


