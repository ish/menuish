from unittest import TestCase
import yaml

from restish import url

from menuish.menu import create_sitemap, Node, Navigation

class MockRequestUrl(object):
    def __init__(self, url):
        self.url = url



class Test(TestCase):

    def setUp(self):
        self.request = MockRequestUrl(url.URL('/gallery'))


    def test_simple(self):
        sitemap = Node('root','Home', 'x1')
        sitemap.add( Node('root.gallery','Gallery','x2'))

        nav = Navigation(showroot=True, item_class=['firstlast','number'], item_id=None)
        html = nav.render_navigation(sitemap, self.request)
        assert html == '<ul><li id="nav-root" class="first-child item-1"><a href="/">Home</a></li><li class="selected last-child item-2" id="nav-gallery"><a href="/gallery">Gallery</a></li></ul>'

    def test_yaml(self):
        sitemap_yaml = """
        - [root, Home, 1, {}]
        - [root.about, About, 2, {}]
        - [root.gallery, Gallery, 3, {}]
        """
        sitemap = create_sitemap(yaml.load(sitemap_yaml))
        html = Navigation(showroot=True, item_class=['firstlast','number'], item_id=None).render_navigation(sitemap, self.request)
        assert html == '<ul><li id="nav-root" class="first-child item-1"><a href="/">Home</a></li><li id="nav-about" class="item-2"><a href="/about">About</a></li><li class="selected last-child item-3" id="nav-gallery"><a href="/gallery">Gallery</a></li></ul>'



