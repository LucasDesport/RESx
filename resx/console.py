#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:20:02 2024

@author: corralien
@author: jpm
"""

import click
import networkx as nx
import sys
import gravis as gv
import pathlib
import pandas as pd
import numpy as np
import re

__version__ = '0.0.2'
default_xml = 'current-RES.xml'
sub_command = ' '.join(sys.argv[1:]) 
MAX_NODES=500

APP_NAME = 'resx'

# VDT and GRAPH processing:   UTILITIES
def clean_vdt(VDTFILE = 'VDT/newlucas.vdt'):
    '''Read a VEDA-TIMES vdt_file(skiprows=3), clean up. 
    Return pandas dataframe vdt, and networkx graph G.    
    From corralien: REWScleaner'''
    
    vdt = pd.read_csv(VDTFILE, skiprows=3, header=None, usecols=[1, 2, 3], 
                      names=['process', 'commodity', 'direction'])
    vdt.head(10)
    
    vdt = vdt.drop_duplicates(['process', 'commodity', 'direction'])
    
    m = np.zeros(len(vdt), dtype=bool)
    m |= vdt['commodity'].isin(['NRGI', 'NRGO', 'DEMO', 'ENVI', 'ENVO', 'MATI', 'MATO'])
    m |= vdt['process'].str.startswith('TU_')
    m |= vdt['process'].str.startswith('NatGrdExt_')
    m |= vdt['process'].str.contains('IMP[A-Z]{3}Z')
    
    vdt = vdt[~m]     
    
    vdt.loc[vdt['commodity'].str.endswith('_'), 'process'].unique() 
    
    G = nx.DiGraph(name='RES')
    
    # resource energy system
    for row in vdt.itertuples():
        prc, com, flow = row.process, row.commodity, row.direction
        G.add_node(com, commodity=com, bipartite=0, color='blue')
        G.add_node(prc, process=prc, bipartite=1, color='red')
        G[prc]['type'] = 'process'
        G[com]['type'] = 'commodity'
        u, v = (com, prc) if row.direction == 'IN' else (prc, com)
        G.add_edge(u, v, direction=flow)  
    
    return vdt, G
    
def get_graph( ):
    err_msg = f"File {default_xml} does not exist. You should init first. See {APP_NAME} init --help"
    # assert pathlib.Path(default_xml).is_file(), err_msg 
    if not pathlib.Path(default_xml).is_file():
        print(err_msg)
        sys.exit(0)

    return nx.read_graphml(default_xml) 

def extract(G, up, down, nodes):
    '''Utility extraction shared by neighbours or sector'''
    GX = nx.DiGraph()
    
    # Recursively callables
    def upWard(layer):
        up_layer = []
        for n in layer:
            for m in G.predecessors(n):
                GX.add_edge(m, n) 
                up_layer.append(m)
        return  up_layer
    
    def downWard(layer):
        down_layer = []
        for n in layer:
            for p in G.successors(n):
                GX.add_edge(n,p) 
                down_layer.append(p)
        return  down_layer        
    
    # Recursions
    for node in nodes:
        layer = [node]
        for count in range(up):
            layer = upWard(layer)
        for count in range(down):
            layer = downWard(layer)
    
    return GX

def out(GX, G):
    nb_nodes = GX.number_of_nodes()
    msg = f'Warning:  many nodes ({nb_nodes}) - process anyway ?[y/n] '
    
    # assert nb_nodes <= MAX_NODES, msg
    if nb_nodes > MAX_NODES and input(msg) != 'y':  sys.exit(0)  
    
    # Inherit attributes from G
    for n in GX.nodes():
        # print(G.nodes[n])
        GX.nodes[n]['type'] =  'process' if 'process' in G.nodes[n].keys() else 'commodity' 
        GX.nodes[n]['color'] =  G.nodes[n]['color']
        GX.nodes[n]['name'] =  n 

    # Add a node title
    GX.add_node("Title")
    GX.nodes["Title"]['name'] =  sub_command   
    GX.nodes["Title"]['type'] =  'title'   

    gv.d3(GX, node_label_size_factor=0.5).display()
    nx.write_graphml(GX, 'GX.xml',  named_key_ids=True)    
    
# CLI SECTION
class OrderCommands(click.Group):
  def list_commands(self, ctx: click.Context) -> list[str]:
    return list(self.commands)

@click.group(cls=OrderCommands)
@click.version_option(__version__) 
def cli():
    '''RES Explorer: build RES from VDT file, extract subgraphs.''' 
    pass

@click.command(name='init', help="""Initialize RES from vdt_file argument. Write to local file 'current-RES.xml'.""")
@click.argument('vdt_file', nargs=1, required=True)
def init(vdt_file):       
    vdt, G = clean_vdt(vdt_file)
    print('Nombre de process    :', vdt['process'].nunique())
    print('Nombre de commodités :', vdt['commodity'].nunique())
    print('Nombre de connexions :', len(vdt)) 
    print(vdt.head(10))
    print('...')
    gv.d3(G, node_label_size_factor=0.5).display()
    nx.write_graphml(G, default_xml)
    print(f"{default_xml} reinitialized with {vdt_file}")
cli.add_command(init)

@cli.command(help="""List parents nodes of argument NODE""")
@click.argument('node', nargs=1, required=True)
def parents(node):    
    G = get_graph() 
    print(sub_command)
    for n in G.predecessors(node):
        print(n)
        
@cli.command(help= """List children nodes of argument NODE""")
@click.argument('node', nargs=1, required=True)
def children(node):       
    G = get_graph()
    print(sub_command)
    for n in G.successors(node):
        print(n)        

@cli.command(help="""Graph shortest path between SOURCE and TARGET""")
@click.argument('source', nargs=1, required=True)
@click.argument('target', nargs=1, required=True)
def path(source, target):                 
    G = get_graph()  
    GX = nx.DiGraph()
    for p in nx.all_shortest_paths(G, source, target):
        for e in zip(p[:-1],p[1:]):
            # print(e)
            GX.add_edge(*e)
    out(GX, G)

@cli.command(help="""Graph neighbours at depths UP,DOWN (default 1,1) of a list of NODES""")
@click.option('--up', nargs=1, default=1)
@click.option('--down', nargs=1, default=1)
@click.argument('nodes', nargs=-1, required=True)
def neighbours(up, down, nodes):           
    G =  get_graph() 
    GX = extract(G, up, down, nodes)
    out(GX, G)
    
@cli.command(help="""Graph all neighbours at depths=(1,1) of nodes matching *REGEXPR*""" )
@click.argument('regexpr', nargs=1, required=True)
def sector(regexpr):             
    G = get_graph()      
    # REGEXP: sublist of nodes
    full_expr = f".*{regexpr}.*$" 
    subnodes = tuple([item for item in G.nodes if re.match(full_expr, item,  re.IGNORECASE )   ])
    up, down  = 1 , 1 
    GX = extract(G, up, down, subnodes)

    out(GX, G)    

cli.epilog = f"Run '{APP_NAME} COMMAND --help' for more information on a command."


if __name__ == '__main__':
    cli()
