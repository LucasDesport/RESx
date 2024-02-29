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


def clean_vdt(VDTFILE = 'VDT/newlucas.vdt'):
    '''Read a VEDA-TIMES vdt_file, clean up a
    Return pandas dataframe vdt, and networkx graph G.    
    From corralien: REWScleaner'''
    
    vdt = pd.read_csv(VDTFILE, skiprows=3, header=None, usecols=[1, 2, 3], names=['process', 'commodity', 'direction'])
    vdt.head(10)
    
    vdt = vdt.drop_duplicates(['process', 'commodity', 'direction'])
    
    m = np.zeros(len(vdt), dtype=bool)
    m |= vdt['commodity'].isin(['NRGI', 'NRGO', 'DEMO', 'ENVI', 'ENVO', 'MATI', 'MATO'])
    m |= vdt['process'].str.startswith('TU_')
    m |= vdt['process'].str.startswith('NatGrdExt_')
    m |= vdt['process'].str.contains('IMP[A-Z]{3}Z')
    
    vdt = vdt[~m] 
    
    print('Nombre de process    :', vdt['process'].nunique())
    print('Nombre de commodités :', vdt['commodity'].nunique())
    print('Nombre de connexions :', len(vdt)) 
    
    vdt.loc[vdt['commodity'].str.endswith('_'), 'process'].unique() 
    
    G = nx.DiGraph(name='RES')
    
    # resource energy system
    for row in vdt.itertuples():
        prc, com, flow = row.process, row.commodity, row.direction
        G.add_node(com, commodity=com, bipartite=0, color='blue')
        G.add_node(prc, process=prc, bipartite=1, color='red')
        u, v = (com, prc) if row.direction == 'IN' else (prc, com)
        G.add_edge(u, v, direction=flow)  
    
    return vdt, G
    
    
