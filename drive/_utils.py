#!/usr/bin/python
NOGTK = True

from apiclient import errors

def unwrap_pages(func, kwargs):
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            kwargs.update(param)
            part = func(kwargs)
            result.extend(part.get('items', []))
            page_token = part.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print 'An error occured: %s' % error
            break
    return result
            
if not NOGTK:
    from gi.repository import Gtk

import collections

class SimpleTree(collections.defaultdict):
    
    def __init__(self, *args):
        super(SimpleTree, self).__init__(SimpleTree, *args)

    def walkthrough(self):
        def recurse(start, level):
            for k,v in start.iteritems():
                yield level,k
                for x in recurse(v, level+1):
                    yield x
        return recurse(self, 0)

    if not NOGTK:
        def as_gtktreestore(self):
            if len(self) == 0:
                raise Exception('SimpleTree is empty.')
        
            treestore = Gtk.TreeStore(object)

            # first object will always have level 0!
            OLDLEVEL = 0
            PARENT = [None]
            LASTID = None
            for level, value in self.walkthrough():
                if level - OLDLEVEL > 0:
                    PARENT.append(LASTID)
                if level - OLDLEVEL < 0:
                    PARENT.pop()
                LASTID = treestore.append(PARENT[-1],(dict(value),))
                OLDLEVEL = level

            return treestore
        

