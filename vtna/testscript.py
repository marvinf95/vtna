#!/home/marvin/anaconda3/envs/vtna/bin/python3.6
import vtna.data_import as dimp
import vtna.graph as graphu

print('Start temp import')
edges = dimp.TemporalEdgeTable('vtna/tests/data/highschool_edges.ssv')
print('Start meta import')
meta = dimp.MetadataTable('vtna/tests/data/highschool_meta.tsv')
print('Start building temporal graphs')
graphs = graphu.TemporalGraph(edges, meta, 20)

#i = iter(graphs)
#print(next(i).edges())
#print(next(i).edges())
#print(next(i).edges())


graph_two = graphs[2]
print(graphs.get_nodes())
print(dir(graph_two))

print(graph_two.get_edges())


#edge = graph.Edge(55,202,[1385982040,1385982080,1385982240,1385982260])
#print(edge.get_count())

#import ipywidgets as widgets
import inspect
#print(inspect.getargspec(widgets.Select).args)
#print(list(widgets.Select.keys))
