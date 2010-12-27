#!/usr/bin/env python

"""
KSync - Sync the directory layout with the collections file on a Kindle

Usage:
  ./ksync.py <kindle mount point>
"""

import json
import os
import hashlib
import time
from collections import defaultdict


def kindle_hash(path):
    prefix = "/mnt/us/documents/"
    if not path.startswith(prefix):
        path = os.path.join(prefix, path.strip("/"))
    return hashlib.sha1(path).hexdigest()


class KindleFile(object):
    def __init__(self, path, mount_point=""):
        assert path.startswith(mount_point)
        self.path = path[len(mount_point):].strip(os.path.sep)

    @property
    def collection_name(self):
        parts = self.path.split(os.path.sep)
        if len(parts) > 1:
            return parts[0]
        return None

    @property
    def kindle_path(self):
        return "/mnt/us/documents/" + self.path

    @property
    def kindle_hash(self):
        return "*%s" % kindle_hash(self.kindle_path)
        
    
class KindleCollections(object):
    def __init__(self, root):
        def empty_collection():
            return {"items": [], "lastAccess": int(time.time() * 1000)}
        self.collections = defaultdict(empty_collection)
        
        self.root = os.path.abspath(root)
        assert os.path.isdir(self.root)
        self.load()
        
    def __getitem__(self, k):
        k = k.replace("@", "-")
        k = "%s@en-US" % k
        return self.collections[k]

    @property
    def collections_file(self):
        return os.path.join(self.root, "system/collections.json")
    
    def load(self):
        f = open(self.collections_file)
        self.collections.update(json.load(f))
    
    def write(self):
        f = open(self.collections_file, "w")
        json.dump(self.collections, f)

    def remove_dir_collections(self):
        dir_collections = set()
        for name, collection in self.collections.iteritems():
            if "|DIRCOLLECTION" in collection['items']:
                dir_collections.add(name)
        for collection in dir_collections:
            del self.collections[collection]
        
    def sync_dir_collections(self):
        self.remove_dir_collections()
        
        dir_collections = set()
        doc_root = self.root + "/documents"
        for root, dirs, files in os.walk(doc_root):
            for fn in files:
                path = os.path.join(root, fn)
                kf = KindleFile(path, doc_root)
                _, ext = os.path.splitext(fn)
                
                if ext == ".pdf" and kf.collection_name:
                    dir_collections.add(kf.collection_name)
                    self[kf.collection_name]['items'].append(kf.kindle_hash)
                
        for name in dir_collections:
            self[name]["items"].append("|DIRCOLLECTION")


if __name__ == '__main__':
    import sys
    c = KindleCollections(sys.argv[1])
    c.sync_dir_collections()
    c.write()
