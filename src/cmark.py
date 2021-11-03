import collections as _collections
import ctypes as _ctypes


_nodes = (
    'NONE',
    'DOCUMENT',
    'BLOCK_QUOTE',
    'LIST',
    'ITEM',
    'CODE_BLOCK',
    'HTML_BLOCK',
    'CUSTOM_BLOCK',
    'PARAGRAPH',
    'HEADING',
    'THEMATIC_BREAK',
    'TEXT',
    'SOFTBREAK',
    'LINEBREAK',
    'CODE',
    'HTML_INLINE',
    'CUSTOM_INLINE',
    'EMPH',
    'STRONG',
    'LINK',
    'IMAGE',
)
NodeType = _collections.namedtuple('NodeType', _nodes)(*range(len(_nodes)))
del _nodes

_lists = ('NO_LIST', 'BULLET_LIST', 'ORDERED_LIST')
ListType = _collections.namedtuple('ListType', _lists)(*range(len(_lists)))
del _lists

_events = ('NONE', 'DONE', 'ENTER', 'EXIT')
EventType = _collections.namedtuple('EventType', _events)(*range(len(_events)))
del _events


class Node:
    __slots__ = '_node', '_type'

    def __init__(self, node):
        self._node = node
        self._type = _node_get_type(self._node)

    def __iter__(self):
        return _NodeIterator(self._node)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return _node_get_type_string(self._node).decode('utf-8')

    @property
    def url(self):
        return _get_node_url(self._node)

    @property
    def literal(self):
        return _get_node_literal(self._node)

    @property
    def info(self):
        return _node_get_fence_info(self._node).decode('utf-8')

    @property
    def heading_level(self):
        return _node_get_heading_level(self._node)

    @property
    def list_type(self):
        return _node_get_list_type(self._node)

    @property
    def start_line(self):
        return _node_get_start_line(self._node)


class _NodeIterator:
    __slots__ = '_iter',

    def __init__(self, node):
        self._iter = _iter_new(node)

    def __next__(self):
        event = _iter_next(self._iter)
        if EventType.DONE == event:
            raise StopIteration
        else:
            node = _iter_get_node(self._iter)
            return event, Node(node)

    def __del__(self):
        _iter_free(self._iter)


class _AST(Node):
    __slots__ = ()

    def __del__(self):
        assert NodeType.DOCUMENT == self.type
        _node_free(self._node)


parse_options = 1 << 4


def parse_document(filename):
    with open(filename, 'r') as fh:
        text = fh.read()

    textbytes = text.encode("utf-8")
    textlen = len(textbytes)
    ast = _AST(_parse_document(textbytes, textlen, parse_options))
    return ast





_cmark = _ctypes.CDLL("libcmark.so")


class _Node(_ctypes.Structure):
    __slots__ = ()
_NodePointer = _ctypes.POINTER(_Node)


class _Iter(_ctypes.Structure):
    __slots__ = ()
_IterPointer = _ctypes.POINTER(_Iter)


_iter_free = _cmark.cmark_iter_free
_iter_free.argtypes = _IterPointer,

_iter_get_node = _cmark.cmark_iter_get_node
_iter_get_node.argtypes = _IterPointer,
_iter_get_node.restype = _NodePointer

_iter_next = _cmark.cmark_iter_next
_iter_next.argtypes = _IterPointer,
_iter_next.restype = _ctypes.c_int

_iter_new = _cmark.cmark_iter_new
_iter_new.argtypes = _NodePointer,
_iter_new.restype = _IterPointer

_node_get_fence_info = _cmark.cmark_node_get_fence_info
_node_get_fence_info.argtypes = _NodePointer,
_node_get_fence_info.restype = _ctypes.c_char_p

_node_get_heading_level = _cmark.cmark_node_get_heading_level
_node_get_heading_level.argtypes = _NodePointer,
_node_get_heading_level.restype = _ctypes.c_int

_node_set_heading_level = _cmark.cmark_node_set_heading_level
_node_set_heading_level.argtypes = _NodePointer, _ctypes.c_int
_node_set_heading_level.restype = _ctypes.c_int

_node_get_list_type = _cmark.cmark_node_get_list_type
_node_get_list_type.argtypes = _NodePointer,
_node_get_list_type.restype = _ctypes.c_int

_node_get_literal = _cmark.cmark_node_get_literal
_node_get_literal.argtypes = _NodePointer,
_node_get_literal.restype = _ctypes.c_char_p
_get_node_literal = lambda node: _node_get_literal(node).decode('utf-8')

_node_get_start_line = _cmark.cmark_node_get_start_line
_node_get_start_line.argtypes = _NodePointer,
_node_get_start_line.restype = _ctypes.c_int

_node_get_type = _cmark.cmark_node_get_type
_node_get_type.argtypes = _NodePointer,
_node_get_type.restype = _ctypes.c_int

_node_get_type_string = _cmark.cmark_node_get_type_string
_node_get_type_string.argtypes = _NodePointer,
_node_get_type_string.restype = _ctypes.c_char_p

_node_get_url = _cmark.cmark_node_get_url
_node_get_url.argtypes = _NodePointer,
_node_get_url.restype = _ctypes.c_char_p
_get_node_url = lambda node: _node_get_url(node).decode('utf-8')

_node_free = _cmark.cmark_node_free
_node_free.argtypes = _NodePointer,

_parse_document = _cmark.cmark_parse_document
_parse_document.argtypes = _ctypes.c_char_p, _ctypes.c_ulonglong, _ctypes.c_int
_parse_document.restype = _NodePointer
