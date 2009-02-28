from restish import url
from breve.tags.html import tags as T


class SiteMapItem(object):
    """I represent a site map item aka a menu item.
    """

    def __init__(self, manager, id, label, path, level, app, item_id, children=None):
        self.manager = manager
        self.id = id
        self.path = path
        self.level = level
        self.app = app
        self.item_id = item_id
        self.label = label
        self._item = None
        if children is not None:
            self.children = children
        else:
            self.children = []

    def name():
        def get(self):
            return self.path.split('.')[-1]
        def set(self, new_name):
            self.path = '.'.join(self.path.split('.')[:-1]+[new_name,])
        return property(get, set)
    name = name()

    def find_child_by_id(self, childId):
        """Search all the children of this node for a child with the specified
        id.
        """
        for child in self.children:
            if child.id == childId:
                return child
            child = child.find_child_by_id(childId)
            if child is not None:
                return child

    def find_child_by_name(self, name):
        """Find an immediate child with the specified name.
        """
        for child in self.children:
            if child.name == name:
                return child

    def getItem(self):
        return self._item

    def hasItem(self):
        return self._item is not None

    def setItem(self, item):
        self._item = item


    def get_node_from_url(self,child_url):
        if child_url.startswith('/'):
            child_url = child_url[1:]
        segments = child_url.split('/')
        node = self
        for segment in segments:
            for n in node.children:
                if n.path.split('.')[-1] == segment:
                    node = n
                    break
            else:
                return None
        if n != self:
            return n
        else:
            return None


class NestedListNavigationFragment(objct):

    def __init__(self, type=None, maxdepth=None, showroot=False, openall=False,
            openallbelow=0, startdepth=0,force_url=None):
        """

        Parameters
        ----------

        type    
            If set, filters the navigation items in sitemap to be of the given
            type only. Otherwise, all navigation items (not necessarily the
            same as all sitemap items) are rendered.

        startdepth
            Depth at which to start showing navigation items. Can be an
            absolute or relative depth (see below).

        maxdepth
            Maximum depth of navigation items to show. Can be an absolute or
            relative depth (see below).

        showroot
            Flag to say whether the 'root' of the current tree should be shown
            (e.g. home for a general menu)

        openallbelow
            Open every submenu below the given depth (good for leaving top
            level closed but showing all submenus within a section).

        openall
            Flag to override the openallbelow to expand every menu.

        force_url
            render as if you are here



        URL Depth Specification
        -----------------------

        The startdepth and maxdepth can be specified in a number of ways,
        either absolute to the root URL or relative from a symbolic location or
        a named navigation level.

            <int>   
                Absolute depth from the root of the site.

            here+<int>
                Relative to the current URL.

            startdepth+<int>
                Relative to the startdepth. (Don't use for startdepth itself!)

            <navigation>+<int>
                Relative to the deepest item in the given navigation level.
        """
        self.navigation_type = type
        self.startdepth = startdepth
        self.maxdepth= maxdepth
        self.showroot = showroot
        self.openall = openall
        self.openallbelow = openallbelow
        if force_url is not None:
            self.force_url_path = ['root'] + force_url.split('/')
        else:
            self.force_url_path = None


    def initialise_args(self, sitemap, request):
        """
        Resolve the args passed to __init__ to have real meaning in the context
        of the navigation and current location in the URL.
        
        We also perform some type checking at the same time to ensure later
        comparisons work correctly.
        """

        if self.navigation_type is not None:
            self.navigation_type = int(self.navigation_type)
        if self.maxdepth is not None:
            self.maxdepth = self.resolve_depth_arg(self.maxdepth, sitemap, request)
        self.startdepth = self.resolve_depth_arg(self.startdepth, sitemap, request)
        self.showroot = resolve_boolean(self.showroot)
        self.openall = resolve_boolean(self.openall)
        self.openallbelow = int(self.openallbelow)


    def resolve_depth_arg(self, depth_spec, sitemap, request):
        """
        Resolve a depth arg.
        """
        # Convert to a string to test, even though we may simply turn it back
        # into an integer.
        depth_spec = str(depth_spec)

        # If there is no '+' then it's just an integer.
        if '+' not in depth_spec:
            return int(depth_spec)

        # Split the spec
        relative_to, relative_offset = depth_spec.split('+', 1)
        relative_offset = int(relative_offset)

        if relative_to == 'here':
            # Relative to the current url
            relative_depth = len(self.get_current_path(sitemap, request)) - 1

        elif relative_to == 'startdepth':
            # Relative to the start depth
            relative_depth = self.resolve_depth_arg(self.startdepth, sitemap, request)

        else:
            # Relative to the navigation level
            navigation_level = int(relative_to)
            relative_depth = len(self.get_current_path(sitemap, request, navigation_level)) - 1

        return relative_depth + relative_offset
        
    
    def render_navigation(self, sitemap, request):
        self.initialise_args(sitemap, request)
        return self.build_menu(sitemap, request)

    def get_current_path_segments(self, request):
        path = ['root'] + request.url.path_segments
        return path


    def get_current_path(self, sitemap, request, navigation_level=None):
        path = self.get_current_path_segments(request)
        # Rebuild path to reference the deepest path within the given
        # navigation level (if any).
        if navigation_level is not None:
            path, rest = path[:1], path[1:]
            node = sitemap
            for segment in rest:
                node = node.find_child_by_name(segment)
                if node.level == navigation_level:
                    path.append(segment)
                else:
                    break

        return path


    def build_menu(self, sitemap, request):

        # Highlighting of navigation is driven by the request.
        request_path = self.get_current_path_segments(request)
        # Filter out empty segments
        request_path = [ r for r in request_path if r ]
        if self.force_url_path is not None:
            force_url_path = [ r for r in self.force_url_path if r ]
        else:
            force_url_path = request_path


        def url_for_node(node):
            u = url.root
            for segment in node.path.split('.')[1:]:
                u = u.child(segment)
            return u

        def add_root_menu(tag):

            nodepath = node.path.split('.')
            nodedepth = len(nodepath)

            label = node.label

            t = T.li()[T.a(href=url_for_node(node))[label]]
            tag[t]
            
            if request_path == nodepath:
                t = t(class_="selected")            


        def add_child_menus(tag, node, urlpath):

            nodepath = node.path.split('.')
            nodedepth = len(nodepath)

            label = node.label

            # If we're not showing submenus (apart from the selected item)
            # then loop through our urlpath and check that the node matches each segment.
            # If it doesn't then return our result so far
            if not self.openall:
                for n, segment in enumerate(urlpath[:self.openallbelow]):
                    if n+1>=nodedepth or segment != nodepath[n+1]:
                        return

            t = T.li()[T.a(href=url_for_node(node))[label]]
            tag[t]

            # Mark selected item
            if request_path[:nodedepth] == nodepath[:nodedepth]:
                t = t(class_="selectedpath")
            if request_path == nodepath:
                t = t(class_="selected")

            # only show up to a set depth
            if self.maxdepth is not None and nodedepth > self.maxdepth:
                return

            # If we have more children and we're showing them all or we're considered to be in the right location - then add them
            if node.children and (self.openall or force_url_path[:nodedepth] == nodepath[:nodedepth]):

                s = T.ul()
                t[s]
                add_children(s, node, urlpath,is_root=False)


        def add_children(tag, node, urlpath, is_root=True):
            """ The root node is the top level segment (e.g. for an absolute url
                /a/b/c, root node is 'a'
                node is the sitemap root node (with path 'root')
            """

            # if this is the root node of our tree, and we have 'showroot' set
            # then add this as a top level list item
            if node is not None and is_root is True and self.showroot is True:
                add_root_menu(tag)

            if node is None or node.children is None:
                return tag


            # for each child of the node, (i.e. for each top level menu item) 
            for child in node.children:
                # as long as a level is defined, otherwise continue
                if self.navigation_type is not None and child.level != self.navigation_type:
                    continue
                add_child_menus(tag, child, urlpath)

            return tag

        def menu_built(tag):

            def appendClassAttribute(tag, attribute, value):
                tag.attrs[attribute] = "%s %s"%(tag.attrs.get('class', ''),value)

            
            try:
                appendClassAttribute(tag.children[0], 'class', 'first-child')
                appendClassAttribute(tag.children[-1], 'class', 'last-child')
            except IndexError:
                pass
            
            for n,child in enumerate(tag.children):
                appendClassAttribute(tag.children[n], 'class', 'item-%s'%(n+1))
            return tag


        # Render from the root of the sitemap by default
        node = sitemap

        # Adjust the root node for the start depth.
        urlpath = list(url.URL(context.IRequest(ctx).path).pathList())
        if urlpath == ['']:
            urlpath = []

        if len(urlpath) < self.startdepth:
            # We've not reached this section of the site yet.
            node = None
        else:
            # Traverse the sitemap to find the root node at the given start depth.
            for segment in urlpath[:self.startdepth]:
                node = node.find_child_by_name(segment)


        # We always start with a menu
        tag = T.ul()
        

        # Take the rootnode and add children given the navigation level as
        # context (navlevel is primary secondary but coded as integers)
        tag = add_children(tag, node, urlpath)
        return menu_built(tag)
    


def labelForMenu(ctx, item, node):
    """
    Return the best label to use in the navigation. This is either the label
    assigned to the sitemap item or a title obtained from the content item.
    """
    if node.label:
        return node.label



def items_to_display(sitemap, current_path, navigation_type):

    # root is always displayed
    items = [sitemap]

    current_pathDepth = len(current_path)

    def visit_children(node):

        if node is None or node.children is None:
            return

        # Add the children of the node
        for child in node.children:
            if child.level is not None:
                items.append(child)

        nodepath = node.path.split('.')
        nodedepth = len(nodepath)

        if nodedepth == current_pathDepth:
            return

        child = current_path[nodedepth]
        visit_children(node.find_child_by_name(child))

    visit_children(sitemap)

    return items
    


def resolve_boolean(value):
    """
    Map a boolean-like value to a Python bool instance.
    """

    # Maybe it's an integer value
    try:
        return bool(int(value))
    except ValueError:
        pass

    # Common strings
    value = value.lower()
    if value in ['true', 'yes']:
        return True
    elif value in ['false', 'no']:
        return False

    raise ValueError("Unrecognised boolean-like value %r" % value)

