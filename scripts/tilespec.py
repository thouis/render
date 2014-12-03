import json
from bounding_box import BoundingBox

class Tile(object):
    def __init__(self, **kwargs):
        for field, val in kwargs.iteritems():
            if field == 'bbox':
                val = BoundingBox.fromList(val)
            self.__dict__[field] = val

class Tilespec(object):
    def __init__(self):
        self.tiles = []  # actual tiles added by load() or another function

    @classmethod
    def load(cls, fname):
        tmp = cls()
        js = json.load(open(fname, "r"))
        tmp.tiles.extend([Tile(**info) for info in js])
        return tmp
