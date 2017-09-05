"""Canvas - Part of Shader Editor Core backend.

Stores all nodes.
Handels all the node creation, deletions, and interaction.
"""
# This module deals with getting paths, system specific settings, ext.
import backend_setting as setting

# Brings in nodes from an external renderer. To add support for a new renderer, 
# the object with can be extended.
import backend_nodeimporter as nodeimporter

# The object used for interaction and storage of a single node
import backend_node as node

# Inherating node object, this uses event listeners to update and 
# deals with any complining needed
import customnodes as cn

# Writes out the resulting scene files or storage formats
import backend_exporter as exporter

# Extra data types
import datatypes

# globals
import globalvars

# External imports
import os
from PyQt4 import QtCore


class Canvas(QtCore.QObject):
    """Canvas Class - Controls Nodes in Scene."""
    # Emited whenever somthing is changed, may run ipr
    # if enabled
    run_ipr = QtCore.pyqtSignal()

    def __init__(self):
        """INIT."""
        super(Canvas, self).__init__()
        # Settings object - Stores path, user, and display info
        self.settings = setting.Settings()

        # Stores nodes in Canvas
        # Dic with -> Name : Node Object
        self.nodes = {}

        # Stores all the node types a user can make
        self.avalible_nodes = {}
        self.gen_avalible_nodes()

        # Custom nodes - Hold custom nodes
        self.custom_nodes = {}

        # Export object holder
        self.exporter = None

    # ---------- Main interface ------------ #
    # GUI Interface use these functions for canvas interaction
    # Avoid changing data members of this class directly as
    # these functions have checking to make sure an interaction
    # is allowed

    # Adds a new node to the nodes dics
    # Inputs
    #   _node_type - The desiered node type from availible nodes dict
    #   _name - Custom name for a node. If none provided come up with one
    #           from the node type
    #
    # Returns
    #   None
    def add_node(self, _node_type, name=None, custom=False):
        """Create a new node in canvas."""
        # Find the node we want to create
        print "==========================================="
        print "Adding Node"

        searchnodes = dict(self.avalible_nodes.items() + self.avalible_custom_nodes.items())
        for key, value in searchnodes.iteritems():
            if key == _node_type:

                # Get all the values from the node templet
                node_type = value.type
                node_style = value.style
                node_help = value.help_txt
                node_in = value.in_attributes
                node_out = value.out_attributes

                # We need to make sure the name is unique
                # and has no spaces. to Do this ittrate an
                # int on the end of the node name
                loop = True
                ittr = 0

                if name is None:
                    name = str(node_style) + str(ittr)
                else:
                    name.replace(" ", "")

                if self.check_name(name) is False:
                    base_name = name
                    while loop:
                        name = base_name + str(ittr)
                        if self.check_name(name):
                            loop = False
                        else:
                            ittr = ittr + 1
                node_name = name

                print "=== node name:", node_name
                nn = str(node_name)
                print "nn is", nn

                if custom:
                    self.nodes[node_name] = cn.RISOSLNode(self,
                                                          node_name,
                                                          node_type,
                                                          node_style,
                                                          node_help,
                                                          self.node_maker)
                else:
                    # create a new node and append to our list
                    self.nodes[node_name] = node.Node(node_name,
                                                      node_type,
                                                      node_style,
                                                      node_help,
                                                      node_in,
                                                      node_out)
                print "Node created"
                return nn

        print "Could not create node", str(node_name)
        print "No such node exists in avalible nodes"
        return None

    # Change a node name. Checks to see if it already exists and
    # is alowed
    # Inputs
    #   _oldname - The original name for a node
    #   _newname - The new name for a node
    def rename_node(self, _oldname, _newname):
        """Change a nodes name if it is already node used."""
        _newname = _newname.replace(" ", "")
        if self.check_name(_newname):
            self.nodes[_newname] = self.nodes[_oldname]
            self.nodes[_newname].name = _newname
            del self.nodes[_oldname]
            print "======================="
            print "Node Name Changed!"
            print " "
        else:
            print "======================="
            print "Unable to change name!"
            print "Node with the name", _newname
            print "already exists."
            print " "

    # Deletes a node from the node dic and from connected Attrs
    # Inputs
    #       _name - The name of the node you wish to remove
    # Returns
    #   None
    def delete_node(self, _name):
        """Using a node name, Delete node from canvas."""
        # Need to remove the node then search attrs on all nodes
        # for connections. If one exists remove it
        # Delete Connections that use this node
        for nodekey, value in self.nodes.iteritems():
            for attrkey, attr in value.in_attributes.iteritems():
                if attr.connection is not None:
                    print attr.connection.dest_node 
                    if attr.connection.dest_node == _name:
                        attr.connection = None
                    
        del self.nodes[_name]

        print "======================="
        print _name, "Deleted"
        print " "
        self.run_ipr.emit()
        return True

    # Create a connection object on an attribute to another node and Attr,
    # Check to see if node and attrs exist. If so check that they can be
    # connected. If so create a new connecyion object on the Dest node
    # Inputs
    #   src_node - Where the connection is comming from up stream
    #   src_attr - Where the connection is comming from up stream
    #   dest_node - Where the connection is stored
    #   dest_attr - Attribute that is getting the connection attached
    def connect_attributes(self, src_node, src_attr, dest_node, dest_attr):
        """Create a connection between 2 nodes."""
        try:
            # Check to see if the attrs are compatable then connect
            src_type = self.nodes[src_node].out_attributes[src_attr].type
            print "src node", src_node
            print "src attr", src_attr
            dest_type = self.nodes[dest_node].in_attributes[dest_attr].type
            print "dest node", dest_node
            print "dest attr", dest_attr

            print "src_type:", src_type
            print "dest_type:", dest_type

            self.nodes[dest_node].in_attributes[dest_attr].connect(src_node,
                                                                   src_attr)
            self.run_ipr.emit()
            return True
        except:
            return False

    def disconnect_attributes(self, _node, _attr):
        """Disconnect an attribute on one node from another."""
        print "============"
        print "Delete connection on", _node, " ", _attr
        try:
            self.nodes[_node].in_attributes[_attr].connection = None
            self.run_ipr.emit()
            return True
        except:
            print "Unable to disconnect Attribute"
            return False

    def list_avalible_nodes(self):
        """Return a list of all the nodes a user can make."""
        for key, nodeobj in self.avalible_nodes.iteritems():
            nodeobj.print_node_data()

    def list_node_list(self):
        """List all the nodes that currently exist."""
        for key, nodeobj in self.nodes.iteritems():
            nodeobj.print_node_data(verbosity=1)

    # Edit and Attribute on a node
    # Inputs
    #   _nodename - The name of the node that the attrubute is part of
    #   _attr - The attribute you wish to change the value of
    #   _value - The new value. Must match type of attr
    # return
    #   None
    def edit_attribute(self,
                       _nodename,
                       _attr,
                       _value):
        """Edit an attribute on a node."""
        try:
            self.nodes[_nodename].edit_attr_value(_attr, _value)
            self.run_ipr.emit()
            return True
        except:
            print "Something went wrong"
            return False

    def create_custom(self, _name, _type, _style, _helptxt):
        """Create a custom node that can be used in the network."""
        if _name not in self.avalible_nodes.keys() and _name not in self.custom_nodes.keys():
            new_custom_node = cn.RISOSLNode(self,
                                            _name,
                                            _type,
                                            _style,
                                            _helptxt,
                                            self.node_maker)
            self.node_maker.get_node_data(new_custom_node.argsfile)
            self.avalible_nodes = self.node_maker.node_list
            return True
        else:
            return False

    # ------ Rendering interfaces ------ #

    def export(self, _srcnode, _loc=None, _preview=False):
        """Based on renderer export the SDF."""
        if self.settings.user_settings['RENDERER'] == "rman":
            print "===================="
            print "Export called - Rman"

            if self.exporter is None:
                self.exporter = exporter.RISExporter(self.settings,
                                                     self.nodes,
                                                     _srcnode,
                                                     _loc)
            else:
                self.exporter.update(self.settings,
                                     self.nodes,
                                     _srcnode,
                                     _loc)

            if _preview is False:
                self.exporter.export()
            elif _preview is True:

                # ToDo - Make Relative in settings
                cd = globalvars.APP_ROOT
                pfile = self.settings.user_settings['PREVIEWSCENEFILE']
                x = os.path.join(str(cd), "OSE_Modules", "exportschemes" , pfile)
                self.exporter.preview(x)

        else:
            print "========================================="
            print "Renderer Not Found! Please check settings"

    # ---------- Save Scene ------------- #
    def save_scene(self, path=None):
        """Write out scene information."""
        # Json formatting
        # - Nodename
        #   - Node Type
        #   - Attributes
        #       - Connection
        #       - Value
        export = exporter.JsonExporter(self.settings,
                                       self.nodes,
                                       None,
                                       path)
        export.export()


    # --------- Init functions ---------- #
    # Functions used to inilize the Canvas object

    def gen_avalible_nodes(self):
        """Create node objects the user can use to make new nodes."""
        # Which modual to use to gen the nodes
        node_mod = self.settings.user_settings['RENDERER']
        ps = self.settings.path_settings
        if node_mod == "rman":
            self.node_maker = nodeimporter.RmanNodeImporter(ps, self)
        elif node_mod == "arnold":
            self.node_maker = nodeimporter.ArnoldNodeImporter(ps, self)

        self.avalible_nodes = self.node_maker.node_list
        self.avalible_custom_nodes = self.node_maker.custom_node_list

    def getstyle(self, type, search_term):
        """Get a dic of style information from setting modual."""
        return None

    # ------ Utility Functions ---------- #

    def check_name(self, _name):
        """Check to see if a name exists, if so return False."""
        for key, value in self.nodes.iteritems():
            if key == _name:
                return False
        return True

    def check_connections(self):
        """Since attributes can be added and removed, we need to refresh connections from time to time."""
        pass

if __name__ == "__main__":
    x = Canvas()
    x.add_node('PxrFacingRatio', 'facingRat')
    x.add_node('PxrMix', 'mixer')
    x.add_node('PxrDisney', 'disney')

    x.edit_attribute('mixer', 'color1', datatypes.Vec3(1, 1, 0))
    x.edit_attribute('mixer', 'color2', datatypes.Vec3(0, 0, 1))

    x.connect_attributes("mixer", "resultRGB", "disney", "baseColor")
    x.connect_attributes("facingRat", "resultF", "mixer", "mix")

    x.export('disney', _preview=True)
