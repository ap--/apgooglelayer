# import from this module
from .extras import SimpleTree, HashableIdDict

from apiclient import errors
import functools

__all__ = ['GoogleDrive', 'GoogleDriveError']


class GoogleDriveError(Exception):
    pass


def unwrap_pages(func):
    def wrapper(self, **kwargs):
        result = []
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                kwargs.update(param)
                lkwargs = kwargs.copy()
                part = func(self, **lkwargs)
                result.extend(part.get('items', []))
                page_token = part.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError as error:
                raise GoogleDriveError('%s(): HttpError while '
                            'unwrapping %s' % (func.func_name, error))
        return result
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper
            

class GoogleDrive(object):
    icon = 'https://developers.google.com/drive/images/drive_icon.png'

    def __init__(self, service):
        self.service = service
        
    def about(self, **kwargs):
        http = kwargs.pop('http', None)
        return self.service.about().get(**kwargs).execute(http=http)

    @unwrap_pages
    def all_files(self, **kwargs):
        http = kwargs.pop('http', None)
        return self.service.files().list(**kwargs).execute(http=http)

    @unwrap_pages
    def files_in_folder(self, **kwargs):
        http = kwargs.pop('http', None)
        return self.service.children().list(**kwargs).execute(http=http)

    
    def folder_structure(self, http=None, fields=None):
        _fields = ('items(title,id,mimeType,parents/id,'
                   'parents/isRoot,labels/trashed)')
        if fields is not None:
            _fields += ',%s' % fields
        #XXX: TODO: check for required fields      

        DATA = []
        for f in self.all_files(http=http, fields=_fields):
            if f['labels']['trashed']: continue
            DATA.append(f)
        
        # DATA: all files that are not deleted
        # try to guess root_id:
        GUESS = []
        for d in DATA:
            for p in d['parents']:
                if p['isRoot']:
                    GUESS.append(p['id'])
        GUESS = set(GUESS) # if there's only one possible solution, we're done.
        if len(GUESS) == 1:
            root_id, = GUESS
        else:
            root_id = self.about(http=http, 
                    fields='rootFolderId').pop('rootFolderId')

        # sort'em
        def recurse(START, T):
            # get all files, that have START as a parent
            TRACK = []
            N = len(DATA)
            for i,d in enumerate(reversed(DATA)):
                if any(p['id'] == START for p in d['parents']):
                    TRACK.append(DATA.pop(N-i-1))
            
            for f in TRACK:
                Hid = HashableIdDict(**f)
                T[Hid] # creates entry through defaultdict
                if 'folder' in f['mimeType']:
                    recurse(START=f['id'], T=T[Hid])

        Tree = SimpleTree()
        recurse(root_id, Tree)
        return Tree


    def files_as_id_dict(self, http=None, **kwargs):
        FILES = self.all_files(http=http, **kwargs)
        return {f['id']: f for f in FILES}
        
