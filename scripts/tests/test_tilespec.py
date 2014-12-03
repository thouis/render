import os.path

from ..tilespec import Tilespec
from ..bounding_box import BoundingBox

# data file
tilespec_name = "w039_Sec180_Montage.json"
tilespec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), tilespec_name)

def test_loading_tilespec():
    '''Test loading an example tilespec'''
    ts = Tilespec.load(tilespec_path)
    assert ts is not None

def test_tilespec_size():
    '''Check that there are the right number of tiles'''
    ts = Tilespec.load(tilespec_path)
    assert len(ts.tiles) == 16

def test_tilespec_tile_format():
    '''Check that the expected parts of the tilespec are present'''
    ts = Tilespec.load(tilespec_path)
    tile1 = ts.tiles[1]
    assert hasattr(tile1, 'bbox')
    assert type(tile1.bbox) is BoundingBox
    assert tile1.height == 25600
    assert tile1.width == 25600
    assert len(tile1.mipmapLevels.values()) == 1
