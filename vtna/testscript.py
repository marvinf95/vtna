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
#for i in graphs.get_nodes(): print(i[0])
#print(dir(graph_two))
#print(graphs.get_node(634).get_global_attribute('1'))
#graphs.get_node(634).update_global_attribute('1','anders')
#print(graphs.get_node(634).get_global_attribute('1'))
#graphs.get_node(634).update_local_attribute('1',['anders','bla','bla'])
#print(graphs.get_node(634).get_local_attribute('1',1))

#a = graphu.TemporalNode(1,{'bla': 'fu'})
#print(a.get_global_attribute('bla'))
#a.update_global_attribute('bla', 'kacke')
#print(a.get_global_attribute('bla'))
#print(graph_two.get_edges())


#edge = graph_two.Edge(55,202,[1385982040,1385982080,1385982240,1385982260])
edge = graph_two.get_edge(55,202)
print(edge.get_timestamps())

