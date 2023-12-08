#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 18:00:00 2023

@author: jpm

SHOULD PYTHONIZE
"""

# +
import pandas as pd
import networkx as nx
from pathlib import Path

def df_to_graph(df):
    cname = 'commodity_id'
    pname = 'process_id'
    sname = 'direction'
    
    commodities = df[cname].unique()    
    processes = df[pname].unique()

    # #### Build edge list
    out_list = df[df[sname]=='OUT']    
    in_list = df[df[sname]=='IN']    
    edgelist = in_list[[cname, pname]].values.tolist() \
        + out_list[[pname, cname]].values.tolist()
    G = nx.from_edgelist(edgelist, create_using=nx.DiGraph)
    return G, processes, commodities

# generic csv read
def graph_from_csv(fname, pname='process_id', cname='commodity_id', 
                   sname='direction'): 
    csv_file = Path('.') / 'VDT' / fname
    df = pd.read_csv(csv_file)
    G, processes, commodities = df_to_graph(df)
    return G, processes, commodities

# Just columns renaming
def graph_from_vdt(fname):
    vdt_file = Path('.') / 'VDT' / fname
    df = pd.read_csv(vdt_file,  skiprows=3, 
        names = ['zone', 'process_id', 'commodity_id', 'direction'])
    G, processes, commodities = df_to_graph(df[[ 'process_id', 'commodity_id', 'direction']])
    return G, processes, commodities

if __name__ == '__main__':
    G1, p1, c1 = graph_from_csv('res.csv')
    print(G1,p1,c1)
    G2, p2, c2 = graph_from_vdt('large.vdt')
    print(G2,p2,c2)