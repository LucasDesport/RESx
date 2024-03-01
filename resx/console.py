#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 13:20:02 2024

@author: jpm
"""

import click
import networkx as nx
import sys
import gravis as gv
import pathlib
import pandas as pd
import numpy as np

# from resx.REScleaner import clean_vdt

__version__ = '0.0.1'
default_xml = 'current-RES.xml'
sub_command = ' '.join(sys.argv[1:]) 
MAX_NODES=200

APP_NAME = 'resx'

CONFIG_DIR = pathlib.Path(click.get_app_dir(APP_NAME))
DATA_DIR = pathlib.Path.home() / APP_NAME

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
    
def get_graph( ):
    err_msg = f"File {default_xml} does not exist. See {APP_NAME} init --help"
    assert pathlib.Path(default_xml).is_file(), err_msg
    return nx.read_graphml(default_xml) 

def out(GX, G):
    nb_nodes = GX.number_of_nodes()
    assert nb_nodes <= MAX_NODES, f'Too many nodes: {nb_nodes}'
    
    # Inherit attributes from G
    for n in GX.nodes():
        print(n)
        GX.nodes[n]['color'] =  G.nodes[n]['color']
        # GX.nodes[n]['type'] =  G.nodes[n]['type'] 
        GX.nodes[n]['name'] =  n    

    gv.d3(GX, node_label_size_factor=0.5).display()
    
    # Add a node title
    # attr = ["Fill Color"="No Color", "Fill Color 2"="No Color", "Line Color"="No Color"  ]
    GX.add_node("Title")
    GX.nodes["Title"]['name'] =  sub_command   
    GX.nodes["Title"]['type'] =  'title'   

    nx.write_graphml(GX, 'GX.xml',  named_key_ids=True)    
    
@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option(__version__)
# @click.pass_context
def cli():
    # ctx.ensure_object(dict)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)    
    # ctx.obj['graph'] =  get_graph( )

@click.command(name='init')
@click.argument('vdt_file')
# @click.pass_context
def init(vdt_file):
    """Initialize local file current-RES.xml from vdt_file argument."""   
    vdt, G = clean_vdt(vdt_file)
    click.echo(vdt.head(10))
    click.echo('...')
    gv.d3(G, node_label_size_factor=0.5).display()
    nx.write_graphml(G, default_xml)
    click.echo(f"{default_xml} reinitialized with {vdt_file}")
    # ctx.obj['graph'] = G 

@cli.command(name='parents')
# @click.pass_context
@click.argument('node', nargs=1, required=True)
def parents(node):
    G = get_graph() 
    click.echo(sub_command)
    for n in G.predecessors(node):
        click.echo(n)
        
@cli.command(name='children')
# @click.pass_context
@click.argument('node', nargs=1, required=True)
def children(node):
    G = get_graph()
    click.echo(sub_command)
    for n in G.successors(node):
        click.echo(n)        

@cli.command(name='neighbours')
# @click.pass_context
@click.option('--up', nargs=1, default=0)
@click.option('--down', nargs=1, default=0)
@click.argument('nodes', nargs=-1, required=True)
def neighbours(up, down, nodes):
    G =  get_graph() 
    GX = nx.DiGraph()
    
    # Recursions
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
    
    for node in nodes:
        layer = [node]
        for idx in range(int(up)):
            layer = upWard(layer)
            
        layer = [node]
        for idx in range(int(down)):
            layer = downWard(layer)

    # Inherit attributes from G
    for n in GX.nodes():
        print(n)
        GX.nodes[n]['color'] =  G.nodes[n]['color']
        # GX.nodes[n]['type'] =  G.nodes[n]['type'] 
        GX.nodes[n]['name'] =  n 

    out(GX, G)
    
@cli.command(name='path')
# @click.pass_context
@click.argument('source', nargs=1, required=True)
@click.argument('target', nargs=1, required=True)
def path(source, target):    
    G = get_graph()  
    GX = nx.DiGraph()
    for p in nx.all_shortest_paths(G, source, target):
        for e in zip(p[:-1],p[1:]):
            print(e)
            GX.add_edge(*e)            
    out(GX, G)

cli.add_command(init)
cli.add_command(parents)
cli.add_command(children)
cli.add_command(neighbours)
cli.add_command(path)
cli.epilog = f"Run '{APP_NAME} COMMAND --help' for more information on a command."


if __name__ == '__main__':
    cli()
