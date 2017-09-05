"""Datatypes - contains classes for utility data types."""
import math
from PyQt4 import QtGui


class Vec3():
    """Vec3 class stores 3 values for a 3d vector."""

    def __init__(self, _x, _y, _z):
        """INIT."""
        self.x = _x
        self.y = _y
        self.z = _z

    def print_vec3(self):
        """Print the vector."""
        print "<", self.x, ",", self.y, ",", self.z, ">"

    def get_hex(self):
        """Convert a vec3 to hex for color."""
        try:
            return "#%02x%02x%02x" % (math.floor(float(self.x) * 255),
                                      math.floor(float(self.y) * 255),
                                      math.floor(float(self.z) * 255))
        except Exception, e:
            print str(e)
            print self.x
            print self.y
            print self.z
            return 0

    def get_QColor(self):
        """Return a QColor object."""
        newqtcolor = QtGui.QColor()
        newqtcolor.setRgbF(float(self.x), float(self.y), float(self.z))
        return newqtcolor


class Connection():
    """Represents a connection to another node."""

    def __init__(self, _destnode, _destattr):
        """INIT."""
        self.dest_node = _destnode
        self.dest_attr = _destattr


class MakeNodeAction(QtGui.QAction):
    """An Qt action with extra val."""

    def __init__(self, txt, p, custom=False):
        """Init."""
        super(MakeNodeAction, self).__init__(str(txt), p)
        self.node = txt
        self.custom = custom

    def make_node(self):
        """Make a node on the main win."""
        self.parent().make_node(self.node, custom=self.custom)
