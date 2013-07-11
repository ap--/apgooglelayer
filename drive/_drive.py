#!/usr/bin/python

from _utils import unwrap_pages
from _utils import SimpleTree


class GoogleDriveIdHashableDict(dict):
    
    def __init__(self, file_id, *args):
        self.file_id = file_id
        super(GoogleDriveIdHashableDict, self).__init__(*args)

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
        self.user = {}
        self._about = about = self.about()
        self.user['name'] = about['user']['displayName']
        self.user['image'] = about['user']['picture']['url']

    def about(self, **kwargs):
        return self.service.about().get(**kwargs).execute()


    def all_files(self, **kwargs):
        f = lambda x: self.service.files().list(**x).execute()
        return unwrap_pages(f, kwargs)


    def files_in_folder(self, **kwargs):
        f = lambda x : self.service.children().list(**x).execute()
        return unwrap_pages(f, kwargs)


    def folder_structure(self,fields='items(id,mimeType,labels/trashed)'):
        MAP = {}
        for f in self.all_files(fields=fields):
            _id = f.pop('id')
            MAP[_id] = f
        
        def recurse(START, T):
            TRACK = self.files_in_folder(folderId=START,fields='items(id)')
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

    
    def folder_structure_as_gtktreestore(self, fields='items(id,mimeType)'):
        tree = self.folder_structure(fields=fields)
        return tree.as_gtktreestore()


    def files_as_id_dict(self, **kwargs):
        FILES = self.all_files(**kwargs)
        result = {}
        for f in FILES:
            _id = f.pop('id')
            result[_id] = f
        return result
        
