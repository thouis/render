import sys
from itertools import combinations

from tilespec import Tilespec
from matchspec import Matchspec

def find_overlap_correspondences(tile1, tile2):
    url1 = tile1.url
    url2 = tile2.url
    


if __name__ == "__main__":
    tilespec = Tilespec.load(sys.argv[1])
    matchspec = Matchspec()

    for t1, t2 in combinations(tilespec.tiles(), 2):
        ov12 = find_overlap_correspondences(t1, t2)
        ov21 = find_overlap_correspondences(t2, t1)
        matchspec.add_matches(ov12)
        matchspec.add_matches(ov21)

    matchspec.save(sys.argv[2])
