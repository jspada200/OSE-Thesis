"""Node - Represents a single node.

Stores input and output attributes
"""


class Node():
    """Represents a single node."""

    def __init__(self,
                 _name,
                 _type,
                 _style,
                 _helptxt,
                 _inattrs=None,
                 _outattrs=None):
        """init."""
        # name - the name of the node. Must be unique
        self.name = _name

        # type - Shader, pattern, volume, custom, ext
        self.type = _type

        # Style - The type of node
        self.style = _style

        # Help - Extra Help text for node
        self.help_txt = _helptxt

        # in_attributes - list of attibutes the user can
        # put in or connect to this node
        if _inattrs is None:
            self.in_attributes = {}
        else:
            self.in_attributes = _inattrs

        # out_attributes - list of attributes that this
        # node outputs
        if _outattrs is None:
            self.out_attributes = {}
        else:
            self.out_attributes = _outattrs

    def edit_attr_value(self, _attr, _value):
        """Change the attributes value based on name."""
        self.in_attributes[_attr].value = _value

        '''
        # try to convert variable into the type that the attr wants
        print "type is:", self.in_attributes[_attr].type
        if self.in_attributes[_attr].type == "string":
            if isinstance(_attr, str):
                self.in_attributes[_attr].value = _value
                print "Value Assigned"
            else:
                print "Attribute type mismatch"
        elif self.in_attributes[_attr].type == "int":
            if isinstance(_attr, int):
                self.in_attributes[_attr].value = _value
                print "Value Assigned"
            else:
                print "Attribute type mismatch - int"
        elif self.in_attributes[_attr].type == "float":
            if isinstance(_attr, float):
                self.in_attributes[_attr].value = _value
                print "Value Assigned"
            else:
                print "Attribute type mismatch"
        elif self.in_attributes[_attr].is_vec3():
            # if isinstance(_attr, vec3)
            self.in_attributes[_attr].value = _value
            print "Value Assigned"
        else:
            print "Attribute type mismatch"
        '''

    def print_node_data(self, verbosity=0):
        """Print out all the data for a node."""
        print "============================="
        print "== Name:", self.name
        print "== Type:", self.type
        print "== Style:", self.style
        print "== Help Text ==============="
        print self.help_txt
        if verbosity > 0:
            print "== Attributes =============="
            for attr_key, attr_val in self.in_attributes.iteritems():
                attr_val.print_attr_data()
            print "== Outputs ================="
            for attr_key, attr_val in self.out_attributes.iteritems():
                attr_val.print_attr_data()
        print " "
