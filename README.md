# VDT files postprocessing with RES-Explorer (resx)

The VDT file is a VEDA Topology File. VEDA (VErsatile Data Analyst) is a powerful yet user friendly set of tools geared to facilitate the creation, maintenance, browsing, and modification of the large data bases required by complex mathematical and economic models [ref](https://www.filesuffix.com/fr/extension/vdt). 

Processes and commodities in a VEDA-TIMES model are organized in a directed bi-colored graph interpreted as the RES of the model,  in general too big to be displayed.

RES-Explorer allows to request different extractions from the whole RES graph,   resulting in sub-graphs 
sufficiently small to be drawn. 

Extractions are put in a graphml formatted local file  GX.xml, which can be processed by the yEd application.  yEd offers many nice layouts for graphs.

Note that  local file  GX.xml always contains the last extraction. It is the user responsability to possibly archive it.


## The resx command

Usage: resx [OPTIONS] COMMAND [ARGS]...

 - resx --help
 - resx --version

## Sub commands
### Convert a vdt file to a networkx graph, output to xml file:  command init_res
 - resx init_res  vdt_file 
 
Output in file 'current-RES.xml'
Resulting graph can be interpreted as a RES, in general too big to be displayed.

### Explore graph sub commands 
 - resx node_parents <node>
 - resx node_children <node>
 - resx path <source_node> <target_node>
 - resx neighbours --up=up_depth --down=down_depth <node_list>
 - resx sector <reg_expr nodelist>
 
Extract sub-graphs, sufficiently small to be displayed

### Examples

<figure>   
   <img src="Figures/gshow+path.png" alt="gshow+path" />
    <figcaption  class="figure-caption text-center">resx path ELCNUC INMFUEL</figcaption>
</figure>
<figure>
   <img src="Figures/gshow+neighbours.png" alt="gshow+neighbours" />   
    <figcaption  class="figure-caption text-center">resx neighbours INMFUEL 3 3</figcaption>
</figure>
