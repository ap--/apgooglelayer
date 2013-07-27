#!/usr/bin/python

from _utils import unwrap_pages
from _utils import SimpleTree


class GoogleDriveIdHashableDict(dict):
    
    def __init__(self, file_id, *args, **kwargs):
        self.file_id = file_id
        self.file_name = kwargs.pop('title', '')
        super(GoogleDriveIdHashableDict, self).__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.file_id)

    def __eq__(self, other):
        return self.file_id == other.file_id

    def __repr__(self):
        return '<GoogleDriveFile with id %s>' % self.file_id

    def __str__(self):
        return 'GDF(%s)' % self.file_id


class GoogleDrive(object):
    icon = 'https://developers.google.com/drive/images/drive_icon.png'

    def __init__(self, service):
        self.service = service
        
        # get user info
    def _set_about(self, http=None):
        self.user = {}
        self._about = about = self.about(http=http)
        self.user['name'] = about['user']['displayName']
        self.user['image'] = about['user']['picture']['url']

    def about(self, http=None, **kwargs):
        if http is not None:
            return self.service.about().get(**kwargs).execute(http=http)
        else:
            return self.service.about().get(**kwargs).execute()


    def all_files(self, http=None, **kwargs):
        if http is not None: 
            f = lambda x: self.service.files().list(**x).execute(http=http)
        else: 
            f = lambda x: self.service.files().list(**x).execute()
        return unwrap_pages(f, kwargs)


    def files_in_folder(self, http=None, **kwargs):
        if http is not None: 
            f = lambda x : self.service.children().list(**x).execute(http=http)
        else: 
            f = lambda x : self.service.children().list(**x).execute()
        
        return unwrap_pages(f, kwargs)


    def folder_structure(self, http=None, fields='items(id,mimeType,labels/trashed)'):
        MAP = {}
        for f in self.all_files(http=http, fields=fields):
            _id = f.pop('id')
            MAP[_id] = f
        
        def recurse(START, T):
            TRACK = self.files_in_folder(http=http, folderId=START,fields='items(id)')
            for f in TRACK:
                _id = f['id']
                if bool(MAP[_id]['labels']['trashed']):
                    continue
                Hid = GoogleDriveIdHashableDict(_id, MAP[_id])
                T[Hid] # creates entry through defaultdict
                if 'folder' in MAP[_id]['mimeType']:
                    recurse(START=_id, T=T[Hid])
        
        Tree = SimpleTree()
        recurse('root', Tree)
        return Tree

    def folder_structure2(self, http=None):
        fields = ('items(title,id,mimeType,'
                  'parents/id,parents/isRoot,labels/trashed)')
        
        DATA = []
        for f in self.all_files(http=http, fields=fields):
            if f.pop('labels')['trashed']: continue
            DATA.append(f)
        
        # DATA: all files that are not deleted
        # try to guess root_id:
        GUESS = []
        for d in DATA:
            for p in d['parents']
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
                _id = f.pop('id')
                f.pop('parents')
                Hid = GoogleDriveIdHashableDict(_id, **f)
                T[Hid] # creates entry through defaultdict
                if 'folder' in f['mimeType']:
                    recurse(START=_id, T=T[Hid])
        
        Tree = SimpleTree()
        recurse(root_id, Tree)
        return Tree
    
    def folder_structure_as_gtktreestore(self, http=None, fields='items(id,mimeType)'):
        tree = self.folder_structure(http=http, fields=fields)
        return tree.as_gtktreestore()


    def files_as_id_dict(self, http=None, **kwargs):
        FILES = self.all_files(http=http, **kwargs)
        result = {}
        for f in FILES:
            _id = f.pop('id')
            result[_id] = f
        return result
        
