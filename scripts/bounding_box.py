import sys

# bounding box - represents a bounding box in an image
class BoundingBox(object):
    def __init__(self,
                 from_x=(-sys.maxint - 1),
                 to_x=sys.maxint,
                 from_y=(-sys.maxint - 1),
                 to_y=sys.maxint):
        self.from_x = float(from_x)
        self.to_x = float(to_x)
        self.from_y = float(from_y)
        self.to_y = float(to_y)
        if not self.validate():
            raise ValueError("Invalid bounding box values: {0}, {1}, {2}, {3} (should be {0} <= {1}, and {2} <= {3}".format(
                    self.from_x, self.to_y, self.from_y, self.to_y))

    @classmethod
    def fromList(cls, bbox_list):
        return cls(bbox_list[0], bbox_list[1], bbox_list[2], bbox_list[3])

    @classmethod
    def fromStr(cls, bbox_str):
        return cls.fromList(bbox_str.split(" "))

    def validate(self):
        # TODO: check that the bounding box values are valid
        if (self.from_x > self.to_x) or (self.from_y > self.to_y):
            return False
        return True

    def overlap(self, other_bbox):
        # Returns true if there is intersection between the bboxes or a full containment
        if (self.from_x < other_bbox.to_x) and (self.to_x > other_bbox.from_x) and \
           (self.from_y < other_bbox.to_y) and (self.to_y > other_bbox.from_y):
            return True
            return False

    def toStr(self):
        return '{0} {1} {2} {3}'.format(self.from_x, self.to_x, self.from_y, self.to_y)
