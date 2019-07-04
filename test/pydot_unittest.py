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

        # 测试多个图
    def test_multiple_graphs(self):
        # 设置图的字符串
        graph_data = 'graph A { a->b };\ngraph B {c->d}'
        # 根据dot_data创造图
        graphs = pydotplus.graph_from_dot_data(graph_data)
        # 验证图的数量是2
        self.assertEqual(len(graphs), 2)
        # 验证图的名称是A 和B
        self.assertEqual([g.get_name() for g in graphs], ['A', 'B'])


        # 测试根据graphviz进行渲染，传入的参数是filename
    def _render_with_graphviz(self, filename):

        # popen的作用是执行系统命令
        p = subprocess.Popen(
            # dot的二进制文件路径，——Tjpe是参数
            (DOT_BINARY_PATH, '-Tjpe'),
            # cwd是设置的昂前路径
            cwd=os.path.dirname(filename),
            # stdin是标准输入
            stdin=open(filename, 'rt'),
            # stderr是标准错误，stdout是标准输出
            stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

        # 将p的标准输出给stdout
        stdout = p.stdout
        # 设置stdout_output是列表
        stdout_output = list()
        while True:
            # 根据stdout读出的数据给data
            data = stdout.read()
            # 如果data为空，则跳出循环
            if not data:
                break
                # 将data添加到stdout_output
            stdout_output.append(data)
            # 关闭标准输出
        stdout.close()

        # 如果输出不为空，那么使用NULL_SEP将列表整合到一个字符串
        if stdout_output:
            stdout_output = NULL_SEP.join(stdout_output)

        # pid, status = os.waitpid(p.pid, 0)
        # this returns a status code we should check
        # 将p进程的状态设为等待
        p.wait()
        # 将标准输出使用sha256加密，hexdigest是
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

        # 验证我的回归测试
    def test_my_regression_tests(self):
        # 调用方法根据dot文件进行渲染和比较函数，参数是我的回归测试目录
        self._render_and_compare_dot_files(MY_REGRESSION_TESTS_DIR)

    def test_graphviz_regression_tests(self):
        self._render_and_compare_dot_files(REGRESSION_TESTS_DIR)

        # 根据dot文件进行渲染和比较
    def _render_and_compare_dot_files(self, directory):

        # 寻找指定目录下，以dot结尾的文件名
        dot_files = [
            fname for fname in os.listdir(directory)
            if fname.endswith('.dot')
        ]  # and fname.startswith('')]

        # 对dot文件列表进行遍历,dot代指每个文件
        for dot in dot_files:
            # 向缓冲区写入内容，这里的内容就是'#'
            os.sys.stdout.write('#')
            # 刷新缓冲区
            os.sys.stdout.flush()
            # 将dot文件的名称和目录拼接起来
            fname = os.path.join(directory, dot)

            try:
                # 使用pydot进行渲染
                parsed_data_hexdigest = self._render_with_pydot(fname)
                # 使用graphviz进行渲染
                original_data_hexdigest = self._render_with_graphviz(fname)
            except Exception:
                # 如果出现异常，打印信息
                print('Failed rendering BAD(%s)' % dot)
                raise
            # 如果根据pydot和graphviz的效果不一致，打印BAD嘻嘻
            if parsed_data_hexdigest != original_data_hexdigest:
                print('BAD(%s)' % dot)
            # 验证根据pydot和graphviz的效果一致
            self.assertEqual(parsed_data_hexdigest, original_data_hexdigest)

            # 测试数字节点id
    def test_numeric_node_id(self):
        # 重设图
        self._reset_graphs()
        # 添加节点
        self.graph_directed.add_node(pydotplus.Node(1))
        # 验证图的节点的第一个元素名称是1
        self.assertEqual(self.graph_directed.get_nodes()[0].get_name(), '1')

        # 测试引用节点id
    def test_quoted_node_id(self):
        # 重设图
        self._reset_graphs()
        # 添加节点，名称是node
        self.graph_directed.add_node(pydotplus.Node('"node"'))
        # 验证图的节点的第一个元素的名称是node
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
