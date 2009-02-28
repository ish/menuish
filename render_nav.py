class R(object):
    def __init__(self, url):
        self.url = url


from restish import url
r = R(url.URL('/gallery'))

from navigation import NavigationItem as N
a = N('x12','Home', 'root')
a.add_child( N('x234','Gallery','gallery'))

from navigation import Navigation
n = Navigation()
print 'repr(nav) = ',repr(n.render_navigation(a, r))

