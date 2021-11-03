import collections as _collections
import functools as _functools
import html as _html
import html.parser as _htmlparser
import re as _re


class Html:
    def __init__(self, ids):
        self.allow = _ContentType.NOTEXT
        self.ids = ids
        self.content = []
        self.placeholders = set()
        self.heading_level = 0


class _TemplateBuilder(_htmlparser.HTMLParser):

    def __init__(self, html, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = html
        self.html = html
        self.stack = []


    def handle_starttag(self, tag, attrs):
        element = add_element(self.html, tag)

        for attr, value in attrs:
            set_attribute(element, attr, value)

        if element.content is not None:
            self.stack.append(self.html)
            self.html = element

        if 'h1' == tag:
            heading = 1
        elif 'h2' == tag:
            heading = 2
        elif 'h3' == tag:
            heading = 3
        elif 'h4' == tag:
            heading = 4
        elif 'h5' == tag:
            heading = 5
        elif 'h6' == tag:
            heading = 6
        else:
            heading = 0
        if heading > self.template.heading_level:
            self.template.heading_level = heading


    def handle_endtag(self, tag):
        assert self.html.tag == tag, f'tried to close {tag} but current element is {self.html}'
        assert self.stack, 'Got end tag on an empty document?'
        self.html = self.stack.pop()


    def handle_startendtag(self, tag, attrs):
        assert False, f'got unexpected startend tag: {tag}'


    def handle_data(self, data):
        placeholder = _placeholder_text.match(data)
        if placeholder:
            placeholder = placeholder.group(1)
            assert placeholder not in self.template.placeholders, f'placeholder {placeholder} repeated'
            self.html.content.append(_Placeholder(placeholder))
            self.template.placeholders.add(placeholder)
        else:
            add_text(self.html, data)


    def handle_decl(self, decl):
        assert 'DOCTYPE html' == decl, f"Unexpected declaration: '{decl}'"
        assert isinstance(self.html, Html), f'Trying to add declaration to {self.html}'
        assert not self.html.content, f'Trying to add declaraction to non-empty document: {self.html.content}'
        self.html.content.append(_DocType(f'<!{decl}>'))


    def unknown_decl(self, decl):
        assert False, f"Unknown declaration: '{decl}'"


def build_template(filename):
    with open(filename, 'r') as fh:
        html = fh.read()

    builder = _TemplateBuilder(Html(set()))
    builder.feed(html)
    result = builder.template
    return result


def add_element(parent, tag):
    assert _ContentType.NONE != parent.allow, f'Tried to add element to {parent}'
    element = _Element(parent.ids, tag, **_elements[tag])
    parent.content.append(element)
    return element


def add_html(parent, html):
    assert _ContentType.NONE != parent.allow, f'Tried to add html to {parent}'
    parent.content.append(_RawHtml(html))


def add_text(element, text, omit_if_whitespace=True):
    if _ContentType.ANY != element.allow:
        assert '' == text.strip(), f"{element}: can't accept text '{text}'"
    else:
        prev = element.content[-1] if element.content else None

        if 'pre' == element.tag:
            if isinstance(prev, _PreformattedText):
                prev.content.append(text)
            else:
                element.content.append(_PreformattedText(text))
        else:
            if isinstance(prev, _Text):
                prev.content.append(text)
                prev.omit_if_whitespace = prev.omit_if_whitespace and omit_if_whitespace
            else:
                element.content.append(_Text(text, omit_if_whitespace))


def set_attribute(element, name, value=None):
    assert name not in element.attrs, f'Attribute {name} already set'
    element.attrs[name] = value

    if 'id' == name:
        assert value not in element.ids, f"id '{value}' already exists in document"
        element.ids.add(value)


def render_template(doc, templates):
    assert doc.content, f'document is empty'

    output = []
    it = _Iterator(doc.content)
    stack = []
    while True:
        while it.index < it.end:
            element = it.items[it.index]
            if isinstance(element, _DocType):
                output.append(element.doctype)

            elif isinstance(element, _Element):
                if element.attrs:
                    attrs = []
                    for name, value in element.attrs.items():
                        if value is None:
                            attrs.append(f' {name}')
                        else:
                            attrs.append(' {}="{}"'.format(name, escape_attribute(value)))
                    attrs = ''.join(attrs)
                else:
                    attrs = ''
                output.append(f'<{element.tag}{attrs}>')

                if element.content:
                    stack.append(it)
                    it = _Iterator(element.content)
                    continue
                elif element.content is not None:
                    output.append(f'</{element.tag}>')


            elif isinstance(element, _Placeholder):
                placeholder = element.name
                placeholder = getattr(templates, placeholder)
                it = _Iterator(placeholder.content)
                continue

            elif isinstance(element, _PreformattedText):
                text = ''.join(element.content)
                output.append(escape_text(text))

            elif isinstance(element, _RawHtml):
                output.append(element.html)

            elif isinstance(element, _Text):
                text = ''.join(element.content)
                text = _normalize_whitespace(text)
                if not ((' ' == text) and element.omit_if_whitespace):
                    output.append(escape_text(text))

            else:
                assert False, f'Unexpected element type: {element}'
                output.append(_html.escape(element, False))

            it.index += 1

        if stack:
            it = stack.pop()
            element = it.items[it.index]
            output.append(f'</{element.tag}>')
            it.index +=1
        else:
            break

    result = ''.join(output)
    return result


def escape_attribute(text):
    result = _html.escape(text, True)
    return result


def escape_text(text):
    result = _html.escape(text, False)
    return result


_placeholder_text = _re.compile(r'^\s*\{\{\s*([a-z]+)\s*\}\}\s*$')
_non_id_chars = _re.compile(r'[^\w -]')
def urlify(text):
    result = _non_id_chars.sub('', text).replace(' ', '-').lower()
    return result



_ContentType = _collections.namedtuple(
    'ContentType',
    ('NONE', 'TEXT', 'NOTEXT', 'ANY'))(0, 1, 2, 3)

_elements = {
    'a': {'allow': _ContentType.ANY},
    'article': {'allow': _ContentType.ANY},
    'b': {'allow': _ContentType.ANY},
    'br': {'allow': _ContentType.NONE},
    'body': {'allow': _ContentType.NOTEXT},
    'code': {'allow': _ContentType.ANY},
    'em': {'allow': _ContentType.ANY},
    'footer': {'allow': _ContentType.ANY},
    'h1': {'allow': _ContentType.ANY},
    'h2': {'allow': _ContentType.ANY},
    'h3': {'allow': _ContentType.ANY},
    'h4': {'allow': _ContentType.ANY},
    'h5': {'allow': _ContentType.ANY},
    'h6': {'allow': _ContentType.ANY},
    'head': {'allow': _ContentType.NOTEXT},
    'header': {'allow': _ContentType.ANY},
    'html': {'allow': _ContentType.NOTEXT},
    'img': {'allow': _ContentType.NONE},
    'input': {'allow': _ContentType.NONE},
    'label': {'allow': _ContentType.ANY},
    'li': {'allow': _ContentType.ANY},
    'link': {'allow': _ContentType.NONE},
    'main': {'allow': _ContentType.ANY},
    'meta': {'allow': _ContentType.NONE},
    'nav': {'allow': _ContentType.ANY},
    'ol': {'allow': _ContentType.NOTEXT},
    'p': {'allow': _ContentType.ANY},
    'pre': {'allow': _ContentType.ANY},
    'script': {'allow': _ContentType.TEXT},
    'title': {'allow': _ContentType.ANY},
    'ul': {'allow': _ContentType.NOTEXT},
}


class _DocType:
    __slots__ = 'doctype',

    def __init__(self, doctype):
        self.doctype = doctype


    def __repr__(self):
        return f'DocType({self.doctype})'


class _Element:
    __slots__ = 'ids', 'tag', 'attrs', 'allow', 'content'

    def __init__(self, ids, tag, allow):
        self.ids = ids
        self.tag = tag
        self.attrs = {}
        self.allow = allow
        self.content = None if _ContentType.NONE == allow else []


    def __repr__(self):
        return f'Element({self.tag})'



class _Placeholder:
    __slots__ = 'name',

    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return f'Placeholder({self.name})'


class _PreformattedText:
    __slots__ = 'content',

    def __init__(self, text):
        self.content = [text]


class _RawHtml:
    __slots__ = 'html'

    def __init__(self, html):
        self.html = html


class _Text:
    __slots__ = 'content', 'omit_if_whitespace'

    def __init__(self, text, omit_if_whitespace):
        self.content = [text]
        self.omit_if_whitespace = omit_if_whitespace



class _Iterator:

    def __init__(self, items):
        self.index = 0
        self.end = len(items)
        self.items = items


_normalize_whitespace = _functools.partial(_re.compile('\s+').sub, ' ')
