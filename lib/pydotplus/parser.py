# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Carlos Jenkins <carlos@jenkins.co.cr>
# Copyright (c) 2014 Lance Hepler
# Copyright (c) 2004-2011 Ero Carrera <ero@dkbza.org>
# Copyright (c) 2004-2007 Michael Krause <michael@krause-software.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Graphviz's dot language parser.

The dotparser parses graphviz files in dot and dot files and transforms them
into a class representation defined by pydotplus.
"""

from __future__ import division, print_function

# sys模块提供对解释器使用或维护的一些变量的访问，以及与解释器强烈交互的函数。它始终可用。
import sys
import pydotplus
# codecs是处理编码格式
import codecs

# pyparsing模块可以被用来解析简单的名字字符串或代数表达式，同时也可以从复杂格式文本报告中提取数据。
# 然后你定义的匹配模式也可能会接收到一个无效的格式输入。pyparsing用来从定义良好的数据格式中进行数据提取。
from pyparsing import __version__ as pyparsing_version

from pyparsing import (
    nestedExpr, Literal, CaselessLiteral, Word, OneOrMore,
    Forward, Group, Optional, Combine, nums, restOfLine,
    cStyleComment, alphanums, printables, ParseException,
    ParseResults, CharsNotIn, QuotedString
)

# 判断python版本是否是3.0.0
PY3 = not sys.version_info < (3, 0, 0)

# 如果是python3版本，basestring = str
if PY3:
    basestring = str

# 定义P_AttrList类
class P_AttrList:

# 定义初始化函数，传入参数toks
    def __init__(self, toks):
        # 定义attrs属性，性质是字典
        self.attrs = {}
        # i=0
        i = 0

        # 当i小于toks的长度
        while i < len(toks):
            # attrname是toks的第i个元素
            attrname = toks[i]
            # 如果i+2小于toks的长度，并且，toks的第i+1个元素是=
            if i + 2 < len(toks) and toks[i + 1] == '=':
                # 那么attrvalue 是toks的第i+2个元素
                attrvalue = toks[i + 2]
                # i自加3
                i += 3
            else:
                # 否则，attrvalue是None
                attrvalue = None
                # i自加1
                i += 1
            # attrs的key是attrname，值是attrvalue
            self.attrs[attrname] = attrvalue

    # 魔方方法__repr__。在调用repr函数的时候被调用
    def __repr__(self):
        # 返回字符串，返回类的name和attrs属性
        return "%s(%r)" % (self.__class__.__name__, self.attrs)

# 定义类DefaultStatement，继承自P_AttrList
class DefaultStatement(P_AttrList):

    # 初始化函数，参数是default_type,attrs
    def __init__(self, default_type, attrs):
        self.default_type = default_type
        self.attrs = attrs

    # 重写repr魔方方法
    def __repr__(self):
        return "%s(%s, %r)" % (
            self.__class__.__name__,
            self.default_type, self.attrs
        )

# 定义top_graphs是列表
top_graphs = list()

# 定义push_top_grah_stmt函数，参数是str,loc和toks
def push_top_graph_stmt(str, loc, toks):
    # attrs是字典
    attrs = {}
    # g初始化为None
    g = None

    # 对toks进行遍历，元素用element代替
    for element in toks:
        # 如果element是parseresults,tuple,list之一，并且，element的长度是1 并且elment的第0个元素是basestring
        if (isinstance(element, (ParseResults, tuple, list)) and
                len(element) == 1 and isinstance(element[0], basestring)):
        # 将element的第0个元素给element
            element = element[0]

        # 如果element==strict
        if element == 'strict':
            # 那么attrs['strict'] 是True
            attrs['strict'] = True

        # 否则如果element在graph,digraph中的一个
        elif element in ['graph', 'digraph']:
            # attrs是空字典
            attrs = {}

            g = pydotplus.Dot(graph_type=element, **attrs)
            attrs['type'] = element

            top_graphs.append(g)

        elif isinstance(element, basestring):
            g.set_name(element)

        elif isinstance(element, pydotplus.Subgraph):
            g.obj_dict['attributes'].update(element.obj_dict['attributes'])
            g.obj_dict['edges'].update(element.obj_dict['edges'])
            g.obj_dict['nodes'].update(element.obj_dict['nodes'])
            g.obj_dict['subgraphs'].update(element.obj_dict['subgraphs'])
            g.set_parent_graph(g)

        elif isinstance(element, P_AttrList):
            attrs.update(element.attrs)

        elif isinstance(element, (ParseResults, list)):
            add_elements(g, element)

        else:
            raise ValueError("Unknown element statement: %r " % element)

    for g in top_graphs:
        update_parent_graph_hierarchy(g)

    if len(top_graphs) == 1:
        return top_graphs[0]

    return top_graphs


def update_parent_graph_hierarchy(g, parent_graph=None, level=0):
    if parent_graph is None:
        parent_graph = g

    for key_name in ('edges',):
        if isinstance(g, pydotplus.frozendict):
            item_dict = g
        else:
            item_dict = g.obj_dict

        if key_name not in item_dict:
            continue

        for key, objs in item_dict[key_name].items():
            for obj in objs:
                if 'parent_graph' in obj and \
                        obj['parent_graph'].get_parent_graph() == g:
                    if obj['parent_graph'] is g:
                        pass
                    else:
                        obj['parent_graph'].set_parent_graph(parent_graph)

                if key_name == 'edges' and len(key) == 2:
                    for idx, vertex in enumerate(obj['points']):
                        if isinstance(
                            vertex,
                            (
                                pydotplus.Graph,
                                pydotplus.Subgraph,
                                pydotplus.Cluster
                            )
                        ):
                            vertex.set_parent_graph(parent_graph)
                        if isinstance(vertex, pydotplus.frozendict):
                            if vertex['parent_graph'] is g:
                                pass
                            else:
                                vertex['parent_graph'].set_parent_graph(
                                    parent_graph
                                )


def add_defaults(element, defaults):
    d = element.__dict__
    for key, value in defaults.items():
        if not d.get(key):
            d[key] = value


def add_elements(g, toks,
                 defaults_graph=None,
                 defaults_node=None,
                 defaults_edge=None):
    if defaults_graph is None:
        defaults_graph = {}
    if defaults_node is None:
        defaults_node = {}
    if defaults_edge is None:
        defaults_edge = {}

    for elm_idx, element in enumerate(toks):
        if isinstance(element, (pydotplus.Subgraph, pydotplus.Cluster)):
            add_defaults(element, defaults_graph)
            g.add_subgraph(element)

        elif isinstance(element, pydotplus.Node):
            add_defaults(element, defaults_node)
            g.add_node(element)

        elif isinstance(element, pydotplus.Edge):
            add_defaults(element, defaults_edge)
            g.add_edge(element)

        elif isinstance(element, ParseResults):
            for e in element:
                add_elements(
                    g, [e], defaults_graph, defaults_node, defaults_edge
                )

        elif isinstance(element, DefaultStatement):
            if element.default_type == 'graph':
                default_graph_attrs = pydotplus.Node('graph', **element.attrs)
                g.add_node(default_graph_attrs)

            elif element.default_type == 'node':
                default_node_attrs = pydotplus.Node('node', **element.attrs)
                g.add_node(default_node_attrs)

            elif element.default_type == 'edge':
                default_edge_attrs = pydotplus.Node('edge', **element.attrs)
                g.add_node(default_edge_attrs)
                defaults_edge.update(element.attrs)

            else:
                raise ValueError(
                    "Unknown DefaultStatement: %s " % element.default_type
                )

        elif isinstance(element, P_AttrList):
            g.obj_dict['attributes'].update(element.attrs)

        else:
            raise ValueError("Unknown element statement: %r" % element)


def push_graph_stmt(str, loc, toks):
    g = pydotplus.Subgraph('')
    add_elements(g, toks)
    return g


def push_subgraph_stmt(str, loc, toks):
    g = pydotplus.Subgraph('')

    for e in toks:
        if len(e) == 3:
            e[2].set_name(e[1])
            if e[0] == 'subgraph':
                e[2].obj_dict['show_keyword'] = True
            return e[2]
        else:
            if e[0] == 'subgraph':
                e[1].obj_dict['show_keyword'] = True
            return e[1]

    return g


def push_default_stmt(str, loc, toks):
    # The pydot class instances should be marked as
    # default statements to be inherited by actual
    # graphs, nodes and edges.
    default_type = toks[0][0]
    if len(toks) > 1:
        attrs = toks[1].attrs
    else:
        attrs = {}

    if default_type in ['graph', 'node', 'edge']:
        return DefaultStatement(default_type, attrs)
    else:
        raise ValueError("Unknown default statement: %r " % toks)


def push_attr_list(str, loc, toks):
    p = P_AttrList(toks)
    return p


def get_port(node):
    if len(node) > 1:
        if isinstance(node[1], ParseResults):
            if len(node[1][0]) == 2:
                if node[1][0][0] == ':':
                    return node[1][0][1]
    return None


def do_node_ports(node):
    node_port = ''

    if len(node) > 1:
        node_port = ''.join([str(a) + str(b) for a, b in node[1]])

    return node_port


def push_edge_stmt(str, loc, toks):
    tok_attrs = [a for a in toks if isinstance(a, P_AttrList)]
    attrs = {}

    for a in tok_attrs:
        attrs.update(a.attrs)

    e = []

    if isinstance(toks[0][0], pydotplus.Graph):
        n_prev = pydotplus.frozendict(toks[0][0].obj_dict)
    else:
        n_prev = toks[0][0] + do_node_ports(toks[0])

    if isinstance(toks[2][0], ParseResults):
        n_next_list = [[n.get_name()] for n in toks[2][0]]
        for n_next in [n for n in n_next_list]:
            n_next_port = do_node_ports(n_next)
            e.append(pydotplus.Edge(n_prev, n_next[0] + n_next_port, **attrs))

    elif isinstance(toks[2][0], pydotplus.Graph):
        e.append(
            pydotplus.Edge(
                n_prev,
                pydotplus.frozendict(toks[2][0].obj_dict),
                **attrs
            )
        )

    elif isinstance(toks[2][0], pydotplus.Node):
        node = toks[2][0]

        if node.get_port() is not None:
            name_port = node.get_name() + ":" + node.get_port()
        else:
            name_port = node.get_name()

        e.append(pydotplus.Edge(n_prev, name_port, **attrs))

    elif isinstance(toks[2][0], type('')):
        for n_next in [n for n in tuple(toks)[2::2]]:
            if isinstance(n_next, P_AttrList) or \
                    not isinstance(n_next[0], type('')):
                continue

            n_next_port = do_node_ports(n_next)
            e.append(pydotplus.Edge(n_prev, n_next[0] + n_next_port, **attrs))

            n_prev = n_next[0] + n_next_port

    else:
        # UNEXPECTED EDGE TYPE
        pass

    return e


def push_node_stmt(s, loc, toks):

    if len(toks) == 2:
        attrs = toks[1].attrs
    else:
        attrs = {}

    node_name = toks[0]
    if isinstance(node_name, list) or isinstance(node_name, tuple):
        if len(node_name) > 0:
            node_name = node_name[0]

    n = pydotplus.Node(str(node_name), **attrs)
    return n


graphparser = None


# 接下来要看的代码
def graph_definition():
    global graphparser

    if not graphparser:
        # punctuation
        colon = Literal(":")
        lbrace = Literal("{")
        rbrace = Literal("}")
        lbrack = Literal("[")
        rbrack = Literal("]")
        lparen = Literal("(")
        rparen = Literal(")")
        equals = Literal("=")
        comma = Literal(",")
        # dot = Literal(".")
        # slash = Literal("/")
        # bslash = Literal("\\")
        # star = Literal("*")
        semi = Literal(";")
        at = Literal("@")
        minus = Literal("-")

        # keywords
        strict_ = CaselessLiteral("strict")
        graph_ = CaselessLiteral("graph")
        digraph_ = CaselessLiteral("digraph")
        subgraph_ = CaselessLiteral("subgraph")
        node_ = CaselessLiteral("node")
        edge_ = CaselessLiteral("edge")

        # token definitions
        identifier = Word(alphanums + "_.").setName("identifier")

        # dblQuotedString
        double_quoted_string = QuotedString(
            '"', multiline=True, unquoteResults=False
        )

        noncomma_ = "".join([c for c in printables if c != ","])
        alphastring_ = OneOrMore(CharsNotIn(noncomma_ + ' '))

        def parse_html(s, loc, toks):
            return '<%s>' % ''.join(toks[0])

        opener = '<'
        closer = '>'
        html_text = nestedExpr(
            opener, closer,
            (CharsNotIn(opener + closer))
        ).setParseAction(parse_html).leaveWhitespace()

        ID = (
            identifier | html_text |
            double_quoted_string |  # .setParseAction(strip_quotes) |
            alphastring_
        ).setName("ID")

        float_number = Combine(
            Optional(minus) +
            OneOrMore(Word(nums + "."))
        ).setName("float_number")

        righthand_id = (float_number | ID).setName("righthand_id")

        port_angle = (at + ID).setName("port_angle")

        port_location = (
            OneOrMore(Group(colon + ID)) |
            Group(colon + lparen + ID + comma + ID + rparen)
        ).setName("port_location")

        port = (
            Group(port_location + Optional(port_angle)) |
            Group(port_angle + Optional(port_location))
        ).setName("port")

        node_id = (ID + Optional(port))
        a_list = OneOrMore(
            ID + Optional(equals + righthand_id) + Optional(comma.suppress())
        ).setName("a_list")

        attr_list = OneOrMore(
            lbrack.suppress() + Optional(a_list) + rbrack.suppress()
        ).setName("attr_list")

        attr_stmt = (Group(graph_ | node_ | edge_) + attr_list).setName(
            "attr_stmt"
        )

        edgeop = (Literal("--") | Literal("->")).setName("edgeop")

        stmt_list = Forward()
        graph_stmt = Group(
            lbrace.suppress() + Optional(stmt_list) +
            rbrace.suppress() + Optional(semi.suppress())
        ).setName("graph_stmt")

        edge_point = Forward()

        edgeRHS = OneOrMore(edgeop + edge_point)
        edge_stmt = edge_point + edgeRHS + Optional(attr_list)

        subgraph = Group(
            subgraph_ + Optional(ID) + graph_stmt
        ).setName("subgraph")

        edge_point << Group(subgraph | graph_stmt | node_id).setName(
            'edge_point'
        )

        node_stmt = (
            node_id + Optional(attr_list) + Optional(semi.suppress())
        ).setName("node_stmt")

        assignment = (ID + equals + righthand_id).setName("assignment")
        stmt = (
            assignment | edge_stmt | attr_stmt |
            subgraph | graph_stmt | node_stmt
        ).setName("stmt")
        stmt_list << OneOrMore(stmt + Optional(semi.suppress()))

        graphparser = OneOrMore((
            Optional(strict_) + Group((graph_ | digraph_)) +
            Optional(ID) + graph_stmt
        ).setResultsName("graph"))

        singleLineComment = Group("//" + restOfLine) | Group("#" + restOfLine)

        # actions
        graphparser.ignore(singleLineComment)
        graphparser.ignore(cStyleComment)

        assignment.setParseAction(push_attr_list)
        a_list.setParseAction(push_attr_list)
        edge_stmt.setParseAction(push_edge_stmt)
        node_stmt.setParseAction(push_node_stmt)
        attr_stmt.setParseAction(push_default_stmt)

        subgraph.setParseAction(push_subgraph_stmt)
        graph_stmt.setParseAction(push_graph_stmt)
        graphparser.setParseAction(push_top_graph_stmt)

    return graphparser


# 解释dot数据，传入的参数是data
def parse_dot_data(data):

    # 定义全局变量，top_graphs
    global top_graphs

    # 定义top_graphs为一个空列表
    top_graphs = list()

    # 如果使用的版本是Python3
    if PY3:
        # 判断data是否是bytes
        if isinstance(data, bytes):
            # this is extremely hackish
            try:
                # 寻找idx，先找到charset开始的位置，并将这个位置索引添加7,7是charset的长度
                idx = data.index(b'charset') + 7
                # 如果idx的元素在\t\n\r=中的任一个元素，idx自加1
                while data[idx] in b' \t\n\r=':
                    idx += 1
                # 将此时的idx赋值给fst
                fst = idx
                # 如果idx不在\t\n\r];,中的任意一个，那么idx自加1
                while data[idx] not in b' \t\n\r];,':
                    idx += 1
                # 定义charset,它的值是fst:idx中的数据，使用"\分离，使用ascii编码
                charset = data[fst:idx].strip(b'"\'').decode('ascii')
                # 使用charset重新对data编码
                data = data.decode(charset)
            except:
                # 如果出现异常，那么直接将数据使用utf-8重新编码
                data = data.decode('utf-8')
    else:
        # 如果不是python3版本，那么如果data是从codes.UTF_8开始的，那么使用utf-8重新对data进行编码
        if data.startswith(codecs.BOM_UTF8):
            data = data.decode('utf-8')

    try:
        # 将grapharser定义为graph_definition方法
        graphparser = graph_definition()

        # 如果解释的版本大于1.2，那么调用parseWithtabs()方法
        if pyparsing_version >= '1.2':
            graphparser.parseWithTabs()

        # 调用parseString方法对data进行处理，返回tokens
        tokens = graphparser.parseString(data)

        # 如果tokens的长度等于1，返回tokens的第0个数据，否则，遍历tokens的所有元素组成的列表
        if len(tokens) == 1:
            return tokens[0]
        else:
            return [g for g in tokens]
            # 如果出现ParseException
    except ParseException:
        # exc_info用来在对异常进行捕获时，获得异常的详尽信息
        err = sys.exc_info()[1]
        # 打印err的line，line不知道是什么意思，下面都不知道什么意思
        print(err.line)
        print(" " * (err.column - 1) + "^")
        print(err)
        # 返回空
        return None
