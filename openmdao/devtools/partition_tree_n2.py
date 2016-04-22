
import os
import sys
import json
from six import iteritems

import webbrowser

from openmdao.core.component import Component


def _system_tree_dict(system):
    """
    Returns a dict representation of the system hierarchy with
    the given System as root.
    """

    def _tree_dict(ss):
        dct = { 'name': ss.name, 'type': 'subsystem' }
        children = [_tree_dict(s) for s in ss.subsystems()]

        if isinstance(ss, Component):
            for vname, meta in ss.unknowns.items():
                dtype=type(meta['val']).__name__
                implicit = False
                if meta.get('state'):
                    implicit = True
                children.append({'name': vname, 'type': 'unknown', 'implicit': implicit, 'dtype': dtype})

            for vname, meta in ss.params.items():
                dtype=type(meta['val']).__name__
                children.append({'name': vname, 'type': 'param', 'dtype': dtype})

        dct['children'] = children

        return dct

    tree = _tree_dict(system)
    if not tree['name']:
        tree['name'] = 'root'
        tree['type'] = 'root'

    return tree

def view_tree(problem, outfile='partition_tree_n2.html', show_browser=False):
    """
    Generates a self-contained html file containing a tree viewer
    of the specified type.  Optionally pops up a web browser to
    view the file.

    Args
    ----
    problem : Problem()
        The Problem (after problem.setup()) for the desired tree.

    outfile : str, optional
        The name of the output html file.  Defaults to 'partition_tree_n2.html'.

    show_browser : bool, optional
        If True, pop up a browser to view the generated html file.
        Defaults to False.
    """
    tree = _system_tree_dict(problem.root)
    viewer = 'partition_tree_n2.template'

    code_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(code_dir, viewer), "r") as f:
        template = f.read()

    treejson = json.dumps(tree)

    myList = []
    for target, (src, idxs) in iteritems(problem._probdata.connections):
        myList.append({'src':src, 'tgt':target})
    connsjson = json.dumps(myList)

    with open(outfile, 'w') as f:
        f.write(template % (treejson, connsjson))

    if show_browser:
        _view(outfile)


def webview(outfile):
    """pop up a web browser for the given file"""
    if sys.platform == 'darwin':
        os.system('open %s' % outfile)
    else:
        webbrowser.get().open(outfile)

def webview_argv():
    """This is tied to a console script called webview.  It just provides
    a convenient way to pop up a browser to view a specified html file(s).
    """
    for name in sys.argv[1:]:
        if os.path.isfile(name):
            webview(name)
