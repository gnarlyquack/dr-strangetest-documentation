import collections as _collections
import http as _http
import os as _os
import shutil as _shutil
import sys as _sys
import urllib.request as _urlrequest

import cmark as _cmark
import htmltools as _htmltools

from pygments import highlight
from pygments.lexers import BashSessionLexer, JsonLexer, PhpLexer
from pygments.formatters import HtmlFormatter


Section = _collections.namedtuple('Section', ('name', 'template', 'index', 'pages'))

sections = (
    Section(
        name = 'Home',
        template = 'page',
        index = 'index',
        pages = (),
    ),
    Section(
        name = 'Documentation',
        template = 'documentation',
        index = 'documentation',
        pages = (
            'getting-started',
            'running-tests',
            'writing-tests',
            'test-fixtures',
            'assertions',
        ),
    ),
    Section(
        name = 'Contributing',
        template = 'page',
        index = 'contributing',
        pages = (),
    ),
    Section(
        name = None,
        template = 'page',
        index = 'sample-code',
        pages = (),
    ),
)


class Site:
    __slots__ = 'index', 'urls', 'remote_urls'

    def __init__(self, remote_urls):
        self.index = {}
        self.urls = []
        self.remote_urls = remote_urls


class Link:
    __slots__ = 'file', 'line', 'url', 'element'

    def __init__(self, file, line, url, element):
        self.file = file
        self.line = line
        self.url = url
        self.element = element


def main():
    remote_urls = False
    if len(_sys.argv) > 1:
        mode = _sys.argv[1]
        if 'dev' == mode:
            remote_urls = False
        elif 'release' == mode:
            remote_urls = True
        else:
            raise Error(f"Unknown release mode: {mode}")

    site = Site(remote_urls)
    nav = {}
    pages = {}
    for section in sections:
        if section.name:
            nav[section.name] = section.index
        build_section(site, pages, section, nav)
    check_urls(site)
    render(pages)

    with open('assets/style.css') as fh:
        style = fh.read();
    highlights = formatter.get_style_defs('div.highlight > pre')
    with open('docs/style.css', 'w') as fh:
        fh.write(highlights)
        fh.write("\n\n\n")
        fh.write(style)


class Template:
    __slots__ = 'ids', 'doc', 'placeholder', 'heading_level'

    def __init__(self, base):
        self.ids = set(base.ids)
        self.heading_level = base.heading_level
        self.placeholder = Placeholders(base.placeholders)
        self.doc = base


class Placeholders:
    def __init__(self, placeholders):
        placeholders = {placeholder: None for placeholder in placeholders}
        object.__setattr__(self, '_placeholders', placeholders)

    def __getattr__(self, name):
        if name in self._placeholders:
            return self._placeholders[name]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self._placeholders:
            self._placeholders[name] = value
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'")


NavBar = _collections.namedtuple('NavBar', ('sections', 'current'))

class TableOfContents:

    def __init__(self, toc, section, heading_level):
        self.toc = toc
        self.section = section
        self.heading_level = heading_level
        self.heading = Heading(section)
        self.stack = []


class Heading:

    def __init__(self, url, name=None):
        self.url = url
        self.name = name
        self.subheadings = []

    def __repr__(self):
        return f'Heading({self.name})'


json_lexer = JsonLexer()
php_lexer = PhpLexer(startinline=True)
shell_lexer = BashSessionLexer()
formatter = HtmlFormatter(style='algol_nu', wrapcode=True)

highlight_php = lambda code: highlight(code, php_lexer, formatter)
highlight_shell = lambda code: highlight(code, shell_lexer, formatter)
highlight_json = lambda code: highlight(code, json_lexer, formatter)


_templates = {}

def get_template(basename):
    if basename not in _templates:
        _templates[basename] = _htmltools.build_template(f'templates/{basename}.html')

    base = _templates[basename]
    template = Template(base)
    return template


_nodes = {
    _cmark.NodeType.EMPH: 'em',
    _cmark.NodeType.ITEM: 'li',
    _cmark.NodeType.PARAGRAPH: 'p',
    _cmark.NodeType.STRONG: 'b',
}


def build_section(site, pages, section, nav):
    toc = [] if section.pages else None
    page = section.index
    pages[page] = build_page(site, section, page, nav, toc, False)
    for page in section.pages:
        pages[page] = build_page(site, section, page, nav, toc, True)



def build_page(site, section, name, nav, toc, include_in_toc):
    assert name not in site.index, f"Page {name} exists multiple times?!"
    site.index[name] = set()

    page = get_template(section.template)
    page.placeholder.navbar = NavBar(nav, section.index)
    if toc is not None:
        page.placeholder.toc = TableOfContents(toc, name, page.heading_level + 1)
    build_article(site, page, name, include_in_toc)
    return page


def set_toc(document, toc, current):
    document.placeholder.toc = TableOfContents(toc, current, document.heading_level + 1)


def build_article(site, template, source, include_in_toc):
    article = _htmltools.Html(template.ids)
    template.placeholder.article = article

    ast = _cmark.parse_document(f'content/{source}.md')
    parent = article
    stack = []
    heading_offset = template.heading_level
    heading = {'level': 0} if include_in_toc else None
    for event, node in ast:
        if _cmark.EventType.ENTER == event:
            child = None
            if _cmark.NodeType.DOCUMENT == node.type:
                pass

            elif _cmark.NodeType.LIST == node.type:
                list_type = node.list_type
                if _cmark.ListType.BULLET_LIST == list_type:
                    child = _htmltools.add_element(parent, 'ul')
                else:
                    assert _cmark.ListType.ORDERED_LIST == list_type, f'Unexpected list type: {list_type}'
                    child = _htmltools.add_element(parent, 'ol')

            elif _cmark.NodeType.HEADING == node.type:
                level = node.heading_level + heading_offset
                child = _htmltools.add_element(parent, f'h{level}')
                if heading is not None:
                    assert \
                        0 == heading['level'], \
                        'Tried to add h{} to h{}'.format(level, heading['level'])
                    heading['level'] = level
                    heading['element'] = child

            elif _cmark.NodeType.LINK == node.type:
                child = _htmltools.add_element(parent, 'a')
                site.urls.append(Link(source, node.start_line, node.url, child))

            elif _cmark.NodeType.TEXT == node.type:
                literal = node.literal
                _htmltools.add_text(parent, literal, False)
                if heading and heading['level']:
                    heading['name'] = literal
                    heading['id'] = _htmltools.urlify(literal)
                    _htmltools.set_attribute(heading['element'], 'id', heading['id'])

            elif _cmark.NodeType.SOFTBREAK == node.type:
                _htmltools.add_text(parent, ' ', False)

            elif _cmark.NodeType.CODE == node.type:
                _htmltools.add_text(_htmltools.add_element(parent, 'code'), node.literal)

            elif _cmark.NodeType.CODE_BLOCK == node.type:
                code = node.literal
                info = node.info
                if 'php' == info:
                    code = highlight_php(code)
                elif 'shell' == info:
                    code = highlight_shell(code)
                elif 'json' == info:
                    code = highlight_json(code)
                else:
                    assert '' == info, f'Unknown code block type: {info}'
                    code = highlight_shell(code)
                _htmltools.add_html(parent, code)

            else:
                assert node.type in _nodes, \
                    f'Unhandled {_cmark.NodeType._fields[node.type]} in {source}.md:{node.start_line}'
                child = _htmltools.add_element(parent, _nodes[node.type])

            if child and child.content is not None:
                stack.append(parent)
                parent = child

        else:
            assert _cmark.EventType.EXIT == event, f'Unexpected event: {event}'
            if _cmark.NodeType.DOCUMENT != node.type:
                parent = stack.pop();

            if (_cmark.NodeType.HEADING == node.type) and heading:
                assert heading['level'], "Popped a heading but we weren't in one?"
                add_toc_entry(template.placeholder.toc, heading['level'], heading['name'], heading['id'])
                site.index[source].add(heading['id'])
                heading['level'] = 0

    assert not stack, f'Unpopped elements: {stack}'


def add_toc_entry(toc, level, name, url):
    if toc.heading.name is None:
        assert level == toc.heading_level, f'Never set name for initial heading'
        heading = toc.heading
        heading.name = name
    else:
        heading = Heading(url, name)

    if level > toc.heading_level:
        assert (toc.heading_level + 1) == level, f'Heading level skipped from {toc.heading_level} to {level}'
        toc.heading_level += 1
        toc.stack.append(toc.toc)
        toc.toc = toc.heading.subheadings
    elif level < toc.heading_level:
        while level < toc.heading_level:
            assert toc.stack
            toc.heading_level -= 1
            toc.toc = toc.stack.pop()
        assert toc.stack

    toc.heading = heading
    toc.toc.append(heading)


def check_urls(site):
    checked = {}
    for link in site.urls:
        if link.url in checked:
            url = checked[link.url]
        elif link.url.startswith('@'):
            parts = link.url[1:].split('#')
            assert len(parts) <= 2, f"Unexpected url: {link.url}"
            path = parts[0]

            if path:
                if '.' == path:
                    page = 'index'
                else:
                    page = path
                assert page in site.index, \
                    "File {}:{} links to {}, but this page doesn't exist".format(
                        link.file, link.line, path)

            if 2 == len(parts):
                fragment = parts[1]
                page = path if path else link.file
                assert fragment in site.index[page], \
                    "File {}:{} links to {}#{}, but there is no matching id on that page".format(
                        link.file, link.line, page, fragment)
                fragment = f'#{fragment}'
            else:
                fragment = ''

            url = f'{path}{fragment}'
        else:
            url = link.url
            if site.remote_urls:
                request = _urlrequest.Request(link.url, method='HEAD')
                response = _urlrequest.urlopen(request)
                assert 200 == response.status, \
                    "url {} got response {} {}".format(
                        link.url, reponse.status, _http.HTTPStatus(response.status).name)
                if response.url != link.url:
                    print(f"{link.url} resolved to:\n{response.url}")

        _htmltools.set_attribute(link.element, 'href', url)
        if link.url not in checked:
            checked[link.url] = url


def render(templates):
    with _os.scandir('docs') as it:
        for entry in it:
            if entry.is_file():
                _os.remove(entry)
            elif entry.is_dir():
                _shutils.rmtree(entry)
            else:
                assert False, f"Don't know how to handle file {entry.path}"

    for filename, template in templates.items():
        template.placeholder.navbar = build_navbar(template.placeholder.navbar)
        if hasattr(template.placeholder, 'toc'):
            template.placeholder.toc = build_toc(template.placeholder.toc)

        output = _htmltools.render_template(template.doc, template.placeholder)
        with open(f'docs/{filename}.html', 'w') as fh:
            fh.write(output)


def build_navbar(nav):
    html = _htmltools.Html(set())
    for section, name in nav.sections.items():
        li = _htmltools.add_element(html, 'li')
        a = _htmltools.add_element(li, 'a')
        url = '.' if 'index' == name else f'{name}.html'
        _htmltools.set_attribute(a, 'href', url)
        if nav.current == name:
            _htmltools.set_attribute(a, 'class', 'active')
        _htmltools.add_text(a, section)
    return html


def build_toc(toc):
    section = toc.section
    while toc.stack:
        toc.toc = toc.stack.pop()
    html = _htmltools.Html(set())
    ol = _htmltools.add_element(html, 'ol')

    class _Iterator:
        def __init__(self, parent, toc):
            self.index = 0
            self.max = len(toc)
            self.parent = parent
            self.toc = toc
    stack = []
    it = _Iterator(ol, toc.toc)
    page = ''
    current = False
    while True:
        while it.index < it.max:
            entry = it.toc[it.index]
            if not stack:
                page = entry.url

            li = _htmltools.add_element(it.parent, 'li')

            if section == entry.url:
                current = True

            if entry.subheadings:
                _htmltools.set_attribute(li, 'class', 'collapsible')
                button = _htmltools.add_element(li, 'input')
                _htmltools.set_attribute(button, 'type', 'checkbox')
                if current:
                    _htmltools.set_attribute(button, 'checked')

            if section == entry.url:
                _htmltools.add_text(li, entry.name)
            else:
                a = _htmltools.add_element(li, 'a')
                if stack:
                    if page == section:
                        url = f'#{entry.url}'
                    else:
                        url = f'{page}.html#{entry.url}'
                else:
                    url = f'{entry.url}.html'
                _htmltools.set_attribute(a, 'href', url)
                _htmltools.add_text(a, entry.name)

            if entry.subheadings:
                stack.append(it)
                it = _Iterator(_htmltools.add_element(li, 'ol'), entry.subheadings)
                continue

            it.index += 1
        if stack:
            it = stack.pop()
            it.index += 1
            current = current and stack
        else:
            break

    return html


if __name__ == '__main__':
    main()
