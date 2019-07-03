# coding=iso-8859-1
#  编码格式是iso-8895-1
# TODO:
# -test graph generation APIs (from adjacency, etc..)
# 将要做的是测试图像产生APi，测试删除节点，删除边的方法，测试公共类的set的方法
# -test del_node, del_edge methods
# -test Common.set method

from __future__ import division, print_function
# 导入division和print_function，division是新的除法特性，原来的除号对于分子分母是整数的情况会取整，但新特性中在此情况下除法不会取整，取整使用//
# print_function是新的print函数，如果导入此特性，那么之前的print语句不能用了

import os
# 导入os模块
try:
    # 从hashlib模块中导入sha256部分，sha256是一个加密算法
    from hashlib import sha256
    # 如果带入失败，则导入sha包，使用里面的new方法作为sha256算法
except ImportError:
    import sha
    sha256 = sha.new

import subprocess
# subprocess最早在2.4版本引入，用来生成子进程，并且可以通过管道连接诶他们的输入/输出/错误，以及获得他们的返回值。
import sys
# 导入sys模块，是系统模块

import pydotplus
# 导入pydotplus模块
import unittest
# 导入test模块

# sys.version_info会返回使用的版本信息，这里的含义是如果版本是2.X版本，PY3为True,否则是False
PY3 = not sys.version_info < (3, 0, 0)

if PY3:
    # 如果是python3版本，则Null_SEP=b'',xrange是range
    NULL_SEP = b''
    xrange = range
else:
    # 否则NULL_SEP是'',bytes是str
    NULL_SEP = ''
    bytes = str

# find_graphviz方法返回相关exe软件的地址，完整返回如下所示，dot是其中的一个软件
# {'dot': 'D:\\program\\Graphviz\\bin\\dot.exe',
#  'twopi': 'D:\\program\\Graphviz\\bin\\twopi.exe',
#  'neato': 'D:\\program\\Graphviz\\bin\\neato.exe',
#  'circo': 'D:\\program\\Graphviz\\bin\\circo.exe',
#  'fdp': 'D:\\program\\Graphviz\\bin\\fdp.exe',
#  'sfdp': 'D:\\program\\Graphviz\\bin\\sfdp.exe'}

DOT_BINARY_PATH = pydotplus.find_graphviz()['dot']
# 测试的路径，位于当前目录的子目录
TEST_DIR = './'
# 回归测试文件夹，图像地址
REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, 'graphs')
# 我的测试地址
MY_REGRESSION_TESTS_DIR = os.path.join(TEST_DIR, 'my_tests')


# 定义测试图像API类，继承自测试模块中的TestCase
class TestGraphAPI(unittest.TestCase):
# 每次方法之前执行
    def setUp(self):
    # 调用_reset_graphs方法，字面意思是重置图像
        self._reset_graphs()

    def _reset_graphs(self):
        # 重置图像，定义图像类，名称是testGraph，图像类型是digraph
        self.graph_directed = pydotplus.Graph(
            'testgraph', graph_type='digraph'
        )
        # 测试保持图像类型
    def test_keep_graph_type(self):
        # 定义点类型，名称是Test，图像类型是graph,点类型的名称是g
        g = pydotplus.Dot(graph_name='Test', graph_type='graph')

        # 确定相等，确定g的类型是graph
        self.assertEqual(g.get_type(), 'graph')

        # 定义点的类型，图像类型是digraph
        g = pydotplus.Dot(graph_name='Test', graph_type='digraph')
        # 确认图像的类型是digraph
        self.assertEqual(g.get_type(), 'digraph')
    # 测试添加类型
    def test_add_style(self):
        # 定义节点名称是mynode
        node = pydotplus.Node('mynode')
        # 节点添加类型，名称是abc
        node.add_style('abc')
        # 确定节点的类型是abc
        self.assertEqual(node.get_style(), 'abc')
        # 添加节点类型是def
        node.add_style('def')
        # 确定节点类型是abc,def
        self.assertEqual(node.get_style(), 'abc,def')
        # 添加节点类型是ghi
        node.add_style('ghi')
        # 确定节点类型是abc,def,ghi
        self.assertEqual(node.get_style(), 'abc,def,ghi')

        # c测试根据节点创造简单图像
    def test_create_simple_graph_with_node(self):
        # 定义点类型数据，名称是g
        g = pydotplus.Dot()
        # 设置点数据的类型是digraph
        g.set_type('digraph')
        # 设置节点legend
        node = pydotplus.Node('legend')
        # 设置节点shape是box
        node.set("shape", 'box')
        # 图像添加节点node
        g.add_node(node)
        # 设置节点label是mine
        node.set('label', 'mine')

        self.assertEqual(
            # 确定点数据是'digraph G {\nlegend [label=mine, shape=box];\n}\n'
            g.to_string(),
            'digraph G {\nlegend [label=mine, shape=box];\n}\n'
        )

    def test_attribute_with_implicit_value(self):

        d = 'digraph {\na -> b[label="hi", decorate];\n}'
        g = pydotplus.graph_from_dot_data(d)
        attrs = g.get_edges()[0].get_attributes()

        self.assertEqual('decorate' in attrs, True)

    def test_subgraphs(self):

        g = pydotplus.Graph()
        s = pydotplus.Subgraph("foo")

        self.assertEqual(g.get_subgraphs(), [])
        self.assertEqual(g.get_subgraph_list(), [])

        g.add_subgraph(s)

        self.assertEqual(g.get_subgraphs()[0].get_name(), s.get_name())
        self.assertEqual(g.get_subgraph_list()[0].get_name(), s.get_name())

        # 测试图像序列化
    def test_graph_pickling(self):

        import pickle

        g = pydotplus.Graph()
        s = pydotplus.Subgraph("foo")
        g.add_subgraph(s)
        g.add_edge(pydotplus.Edge('A', 'B'))
        g.add_edge(pydotplus.Edge('A', 'C'))
        g.add_edge(pydotplus.Edge(('D', 'E')))
        g.add_node(pydotplus.Node('node!'))

        self.assertEqual(type(pickle.dumps(g)), bytes)

    def test_unicode_ids(self):

        node1 = '"aánñoöüé€"'
        node2 = '"îôø®çßΩ"'

        g = pydotplus.Dot()
        g.set_charset('latin1')
        g.add_node(pydotplus.Node(node1))
        g.add_node(pydotplus.Node(node2))
        g.add_edge(pydotplus.Edge(node1, node2))

        self.assertEqual(g.get_node(node1)[0].get_name(), node1)
        self.assertEqual(g.get_node(node2)[0].get_name(), node2)

        self.assertEqual(g.get_edges()[0].get_source(), node1)
        self.assertEqual(g.get_edges()[0].get_destination(), node2)

        g2 = pydotplus.graph_from_dot_data(g.to_string())

        self.assertEqual(g2.get_node(node1)[0].get_name(), node1)
        self.assertEqual(g2.get_node(node2)[0].get_name(), node2)

        self.assertEqual(g2.get_edges()[0].get_source(), node1)
        self.assertEqual(g2.get_edges()[0].get_destination(), node2)

    def test_graph_with_shapefiles(self):

        shapefile_dir = os.path.join(TEST_DIR, 'from-past-to-future')
        dot_file = os.path.join(shapefile_dir, 'from-past-to-future.dot')

        pngs = [
            os.path.join(shapefile_dir, fname)
            for fname in os.listdir(shapefile_dir)
            if fname.endswith('.png')
        ]

        f = open(dot_file, 'rt')
        graph_data = f.read()
        f.close()

        g = pydotplus.graph_from_dot_data(graph_data)

        g.set_shape_files(pngs)

        jpe_data = g.create(format='jpe')

        hexdigest = sha256(jpe_data).hexdigest()

        hexdigest_original = self._render_with_graphviz(dot_file)

        self.assertEqual(hexdigest, hexdigest_original)

    def test_multiple_graphs(self):

        graph_data = 'graph A { a->b };\ngraph B {c->d}'

        graphs = pydotplus.graph_from_dot_data(graph_data)

        self.assertEqual(len(graphs), 2)

        self.assertEqual([g.get_name() for g in graphs], ['A', 'B'])


    def _render_with_graphviz(self, filename):

        p = subprocess.Popen(
            (DOT_BINARY_PATH, '-Tjpe'),
            cwd=os.path.dirname(filename),
            stdin=open(filename, 'rt'),
            stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

        stdout = p.stdout

        stdout_output = list()
        while True:
            data = stdout.read()
            if not data:
                break
            stdout_output.append(data)
        stdout.close()

        if stdout_output:
            stdout_output = NULL_SEP.join(stdout_output)

        # pid, status = os.waitpid(p.pid, 0)
        # this returns a status code we should check
        p.wait()

        return sha256(stdout_output).hexdigest()

    def _render_with_pydot(self, filename):
        # f = open(filename, 'rt')
        # graph_data = f.read()
        # f.close()

        # g = pydotplus.parse_from_dot_data(graph_data)
        # 根据filename绘制总图
        g = pydotplus.graph_from_dot_file(filename)

        # 如果总图的类型不是list，将其改变为list
        if not isinstance(g, list):
            g = [g]

            # 使用NULL_SEP将总图的元素进行处理后添加到一起
        jpe_data = NULL_SEP.join([_g.create(format='jpe') for _g in g])

        # 使用sha256对jpe_data进行加密，hexdigest的含义是返回十六进制的摘要
        return sha256(jpe_data).hexdigest()

    def test_my_regression_tests(self):
        self._render_and_compare_dot_files(MY_REGRESSION_TESTS_DIR)

    def test_graphviz_regression_tests(self):
        self._render_and_compare_dot_files(REGRESSION_TESTS_DIR)

    def _render_and_compare_dot_files(self, directory):

        dot_files = [
            fname for fname in os.listdir(directory)
            if fname.endswith('.dot')
        ]  # and fname.startswith('')]

        for dot in dot_files:
            os.sys.stdout.write('#')
            os.sys.stdout.flush()

            fname = os.path.join(directory, dot)

            try:
                parsed_data_hexdigest = self._render_with_pydot(fname)
                original_data_hexdigest = self._render_with_graphviz(fname)
            except Exception:
                print('Failed rendering BAD(%s)' % dot)
                raise

            if parsed_data_hexdigest != original_data_hexdigest:
                print('BAD(%s)' % dot)

            self.assertEqual(parsed_data_hexdigest, original_data_hexdigest)

    def test_numeric_node_id(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node(1))

        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(), '1')

    def test_quoted_node_id(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node('"node"'))

        self.assertEqual(
            self.graph_directed.get_nodes()[0].get_name(), '"node"'
        )

    def test_quoted_node_id_to_string_no_attributes(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node('"node"'))

        self.assertEqual(
            self.graph_directed.get_nodes()[0].to_string(), '"node";'
        )

    def test_keyword_node_id(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node('node'))

        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(), 'node')

    def test_keyword_node_id_to_string_no_attributes(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node('node'))

        self.assertEqual(self.graph_directed.get_nodes()[0].to_string(), '')

    def test_keyword_node_id_to_string_with_attributes(self):

        self._reset_graphs()

        self.graph_directed.add_node(pydotplus.Node('node', shape='box'))

        self.assertEqual(
            self.graph_directed.get_nodes()[0].to_string(), 'node [shape=box];'
        )

    def test_names_of_a_thousand_nodes(self):

        self._reset_graphs()

        names = set(['node_%05d' % i for i in xrange(10 ** 4)])

        for name in names:

            self.graph_directed.add_node(pydotplus.Node(name, label=name))

        self.assertEqual(
            set([n.get_name() for n in self.graph_directed.get_nodes()]), names
        )

    def test_executable_not_found_exception(self):
        paths = {'dot': 'invalid_executable_path'}

        graph = pydotplus.Dot('graphname', graph_type='digraph')

        graph.set_graphviz_executables(paths)

        self.assertRaises(pydotplus.InvocationException, graph.create)

    def test_graph_add_node_argument_type(self):

        self._reset_graphs()

        self.assertRaises(TypeError, self.graph_directed.add_node, 1)
        self.assertRaises(TypeError, self.graph_directed.add_node, 'a')

    def test_graph_add_edge_argument_type(self):

        self._reset_graphs()

        self.assertRaises(TypeError, self.graph_directed.add_edge, 1)
        self.assertRaises(TypeError, self.graph_directed.add_edge, 'a')

    def test_graph_add_subgraph_argument_type(self):

        self._reset_graphs()

        self.assertRaises(TypeError, self.graph_directed.add_subgraph, 1)
        self.assertRaises(TypeError, self.graph_directed.add_subgraph, 'a')

    def test_quoting(self):
        import string
        g = pydotplus.Dot()
        g.add_node(pydotplus.Node("test", label=string.printable))
        data = g.create(format='jpe')
        self.assertEqual(len(data) > 0, True)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraphAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)
