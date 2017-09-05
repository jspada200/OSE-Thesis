"""Attribute - Stored in a node, this stores a value or connection."""
import datatypes


class Attribute():
    """Attribute - Stored in a node, this stores a value or connection."""

    def __init__(self, in_name, in_type, in_value=None, _extrainfo=None):
        """INIT."""
        # The name of the attribute
        self.name = in_name

        # If the value has a connection store it here
        self.connection = None

        # The type of Attribute
        self.type = in_type

        # Need to handel Vec3s by hand....
        if self.type in ('color', 'point', 'vector'):
            if in_value is not None and type(in_value) is not list:
                in_value = str(in_value).split()

                x = 0
                for val in in_value:

                    if val[len(val) - 1] is ".":
                        in_value[x] = val + "0"
                    x = x + 1
                print self.type
                print in_value
                self.value = datatypes.Vec3(in_value[0],
                                            in_value[1],
                                            in_value[2])
            elif type(in_value) is list:
                self.value = datatypes.Vec3(in_value[0],
                                            in_value[1],
                                            in_value[2])
            else:
                self.value = in_value
        else:
            # The current Value of the Attribute
            self.value = in_value

        # Extra Data Dic - Store here for multiple renderer support
        self.extra_info = _extrainfo

    def connect(self, dest_node, dest_attr):
        """Create a new connection to this attribute."""
        #
        self.connection = None
        self.connection = datatypes.Connection(dest_node, dest_attr)
        pass

    def print_attr_data(self):
        """Print out information about Attr."""
        print "==== Name: ", self.name
        print "==== Connection:", self.connection
        print "==== Type: ", self.type
        print "==== Value: ", self.value

        if self.extra_info != None:
            print "==== Extra Data:"
            for key, value in self.extra_info.iteritems():
                print "======", key, ":", value
        print "--------------------------------------"

    def is_vec3(self):
        """Determin is this attribute can accept a vec3 based on type."""
        if self.type is "vector":
            return True
        elif self.type is "point":
            return True
        elif self.type is "color":
            return True
        else:
            return False
