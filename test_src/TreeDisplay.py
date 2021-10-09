import graphviz
from graphviz import nohtml
from copy import deepcopy
from test_src.Node import Node

class TreeDisplay:

    def __init__(self):
        self.g = graphviz.Digraph('g', filename='tree.gv',
                    node_attr={'shape': 'record', 'height': '.1'})


    def __create_graph_nodes(self, node):
        self.g.node(
            f'node{str(node.depth)}.{str(node.action)}',
            f'''<
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    <TR PORT="f0">
                        <TD>type:</TD>
                        <TD>{str(node.type)}</TD>
                    </TR>
                    <TR>
                        <TD>depth:</TD>
                        <TD>{str(node.depth)}</TD>
                    </TR>
                    <TR>
                        <TD>value:</TD>
                        <TD>{str(node.value)}</TD>
                    </TR>
                </TABLE>
            >'''
        )
        if node.parent is not None:
            self.g.edge(f'node{str(node.parent.depth)}.{str(node.parent.action)}',
                f'node{str(node.depth)}.{str(node.action)}')
            print('depth: ', node.depth)
            print('parent depth: ', node.parent.depth)
        if len(node.children) > 0:
            for child in node.children:
                self.__create_graph_nodes(child)


    def create_frame(self, node: Node):
        self.__create_graph_nodes(node)
        self.g.view()
