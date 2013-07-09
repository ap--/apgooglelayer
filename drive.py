#!/usr/bin/python

import utils


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

    def __init__(self, service):
        self.service = service


    def all_files(self, **kwargs):
        f = lambda x: self.service.files().list(**x).execute()
        return utils.unwrap_pages(f, kwargs)


    def files_in_folder(self, **kwargs):
        f = lambda x : self.service.children().list(**x).execute()
        return utils.unwrap_pages(f, kwargs)


    def folder_structure(self):
        MAP = {}
        for f in self.all_files(fields='items(id,mimeType,title)'):
            _id = f.pop('id')
            MAP[_id] = f
        
        def recurse(START, T):
            TRACK = self.files_in_folder(folderId=START,fields='items(id)')
            for f in TRACK:
                _id = f['id']
                Hid = GoogleDriveIdHashableDict(_id, MAP[_id])
                T[Hid] # creates entry through defaultdict
                if 'folder' in MAP[_id]['mimeType']:
                    recurse(START=_id, T=T[Hid])
        
        Tree = utils.SimpleTree()
        recurse('root', Tree)
        return Tree

    
    def folder_structure_as_gtktreestore(self):
        tree = self.folder_structure()
        return tree.as_gtktreestore()


    def files_as_id_dict(self, **kwargs):
        FILES = self.all_files(**kwargs)
        result = {}
        for f in FILES:
            _id = f.pop('id')
            result[_id] = f
        return result
        
