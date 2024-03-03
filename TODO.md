# jeu. 08 févr. 2024 13:26:29 CET

## documentation
 - DOCSTRINGS
 - rewrite README
 - write HOWTO, EXAMPLES
 - speak of yEd

## RES-Explorer
 - clean code, factorize neighbours and sector
 - resx sector BIO
 - bug if no current-RES.xml implement followings ...
 - resx --graph=PREFIX COMMAND ARGS  
 - rebuild if PREFIX.vdt newer than PREFIX.xml
 - check path
 - poetry

## DONE
 - merge existing bricks
 - parents list  = neighbours --up=1 --down=0
 - children list = neighbours --up=0 --down=1
 - neighbours --up= --down= list_of_nodes

## gshow
 - --Graph=  memorize
 - --output=
 - clean 
 - add attributes
 - git
 - deploy
 - doc, presentation
 - GX.graphml, title

## vdt2xml
 - cli
 - if __name__ 

#========== OLDIES =========

# Reparer
 - bug courant

# Functions   csv_to_graph vdt_to_graph
 - edit under spyder

# Use large.vdt again with same code as CSV_EXPLORE
 - terminal leaves of type process produce terminal leave EXPNRGZ
 - assert all input roots are processes
 - assert all terminal leaves are commodities


## Drawing links
 - https://networkx.org/documentation/stable/reference/drawing.html
 
# Try
 - suppress exchange processes
 - check is_dag on remaining graph 

# Find terminal leaves by yourself
 - length(successors) == 0
 
# Make more check:
  - all depths assigned, compute max == last ?? 
 
# nx.Graph to excel
