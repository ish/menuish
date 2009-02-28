from unittest import TestCase
import yaml

from restish import url

from menuish.menu import Node, Navigation

class MockRequestUrl(object):
    def __init__(self, url):
        self.url = url


sitemap_yaml = """
- [root, Home, 1, {}]
- [root.about, About, 2, {}]
- [root.gallery, Gallery, 3, {}]
"""

def parse(y):
    rows = yaml.load(y)
    root = rows.pop(0)
    sitemap = Node( *root[:-1], **root[-1])
    for row in rows:
        sitemap.add_node( *row[:-1], **row[-1])
    return sitemap

        

class Test(TestCase):

    def setUp(self):
        self.request = MockRequestUrl(url.URL('/gallery'))


    def test_simple(self):
        sitemap = Node('root','Home', 'x1')
        sitemap.add_child( Node('root.gallery','Gallery','x2'))

        nav = Navigation(showroot=True)
        html = nav.render_navigation(sitemap, self.request)
        assert html == '<ul><li class=" first-child item-1"><a href="/">Home</a></li><li class="selected" class=" last-child item-2"><a href="/gallery">Gallery</a></li></ul>'

    def test_yaml(self):
        sitemap = parse(sitemap_yaml)
        nav = Navigation(showroot=True)
        html = nav.render_navigation(sitemap, self.request)
        assert html == '<ul><li class=" first-child item-1"><a href="/">Home</a></li><li class=" item-2"><a href="/about">About</a></li><li class="selected" class=" last-child item-3"><a href="/gallery">Gallery</a></li></ul>'



