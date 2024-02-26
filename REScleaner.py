#!/usr/bin/env python
# coding: utf-8

# # Reference Energy System

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import graphviz as gv


# In[3]:


VDTFILE = 'VDT/newlucas.vdt'

vdt = pd.read_csv(VDTFILE, skiprows=3, header=None, usecols=[1, 2, 3], names=['process', 'commodity', 'direction'])
vdt.head(10)


# In[4]:


vdt = vdt.drop_duplicates(['process', 'commodity', 'direction'])

m = np.zeros(len(vdt), dtype=bool)
m |= vdt['commodity'].isin(['NRGI', 'NRGO', 'DEMO', 'ENVI', 'ENVO', 'MATI', 'MATO'])
m |= vdt['process'].str.startswith('TU_')
m |= vdt['process'].str.startswith('NatGrdExt_')
m |= vdt['process'].str.contains('IMP[A-Z]{3}Z')

vdt = vdt[~m]


# In[5]:


print('Nombre de process    :', vdt['process'].nunique())
print('Nombre de commodités :', vdt['commodity'].nunique())
print('Nombre de connexions :', len(vdt))


# In[6]:


vdt.loc[vdt['commodity'].str.endswith('_'), 'process'].unique()


# In[7]:


G = nx.DiGraph(name='RES')

# resource energy system
for row in vdt.itertuples():
    prc, com, flow = row.process, row.commodity, row.direction
    G.add_node(com, commodity=com, bipartite=0)
    G.add_node(prc, process=prc, bipartite=1)
    u, v = (com, prc) if row.direction == 'IN' else (prc, com)
    G.add_edge(u, v, direction=flow)


# In[8]:


nx.bipartite.is_bipartite(G)


# In[9]:


for (node, degree) in G.in_degree:
    if degree == 0:
        print(f"{node:<20} : {'com' if G.nodes[node]['bipartite'] == 0 else 'prc'}")


# In[10]:


vdt.to_csv('tiamvdt.csv', index=False)


# In[ ]:





# In[ ]:




