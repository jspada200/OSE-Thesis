"""This mod provides classes for exporting the node graph."""
import os
import shutil
import subprocess
import globalvars
import datatypes
import json

"""
The Exporter class is a super class for setting up a new renderer or export
sceme for an exisiting renderer.
"""


class Exporter():
    """Super class for exporting a node graph."""

    """
    Init function
    Inputs
        _settings - The settings object from the canvas
        _nodes - The dicunary of nodes from the cavnas
        _source - The name of the node that is being exported
                  Should be a shader that is connected to other
                  nodes
        _loc - The location the output rib file should be sent to

    Returns
        None

    """
    def __init__(self, _settings, _nodes, _source, _loc=None):
        """INIT."""
        self.loc = None
        self.out_stream = None

        # The main node graph to Exporter
        self.settings = _settings
        self.nodes = _nodes
        self.source = _source

        self.rerender_interface = None

        # use the env temp directory if no temp file is set
        if _loc is None:
            self.loc = os.path.join(_settings.path_settings["TEMP"], "tmp.rib")
        else:
            self.loc = _loc

    def save(self):
        """Save the out stream to file."""
        try:
            target = open(self.loc, 'w')
            target.seek(0)
            target.truncate()

            for line in self.out_stream:
                target.write(line)
                print(line)

            target.close()

            print "File Written to", self.loc
            print "Export compleated successfully"

        except:
            print "Unable to write file", self.loc

    def update(self, _settings, _nodes, _source, _loc=None):
        """Update settings on this exporter."""
        self.settings = _settings
        self.nodes = _nodes
        self.source = _source
        if _loc is None:
            self.loc = os.path.join(_settings.path_settings["TEMP"], "tmp.rib")
        else:
            self.loc = _loc

    def export(self):
        """Gen the node graph in a specific way."""
        pass

    def preview(self, _scenepath):
        """Preview the node graph render."""
        pass

    def save_image(self, _image_path):
        """Save an image."""
        pass

"""
Exporter for RIS
Can generate a RIB file and renderer it to IT or another
frame buffer.
"""


class RISExporter(Exporter):
    """Export a RIS RIB file."""

    def export(self):
        """Export a RIS RIB file to loc."""
        print 'Starting Export'
        # The node network output stream. Every item is a line
        self.out_stream = []

        # Find the node that is specified as the source (a shader)
        # and recursivly build out node network
        for key, value in self.nodes.iteritems():
            if key == self.source:
                self.stream_me(key)

        self.out_stream = reversed(self.out_stream)

        self.save()

    def preview(self, _scenepath):
        """Launche render of RIB to IT."""
        self.export()
        # First gather shader paths from settings
        # shader_path = self.settings.path_settings['SHADERPATHS']
        print "Starting Preview"

        # ------------ Set up Render Rib ---------------------------
        # Next make a copy of the rib file for the test scene
        shader_rib_file = self.loc
        source_file = _scenepath.replace(os.path.basename(_scenepath),
                                         "tmp.rib")

        shutil.copy(_scenepath, source_file)

        _scenepath_f = open(_scenepath, 'r+')
        source_file_f = open(source_file, 'r+')

        # Search for custom tags in the rib file and replace the correct items
        for line in _scenepath_f:
            newline = str(line)
            newline = newline.replace("#RRG_inset_ReadArchive 'spath'",
                                      "ReadArchive '" + shader_rib_file.replace("\\", "/") + "'")
            arch = os.path.join(globalvars.APP_ROOT, "OSE_Modules", "exportschemes", "lightrig.rib")
            newline = newline.replace("#RRG_inset_lightrig",
                                      "ReadArchive '" + arch.replace("\\", "/") + "'")

            osl = os.path.join(globalvars.APP_ROOT, "Custom", "osl").replace("\\", "/")
            print 'Option "searchpath" "shader" ":' + osl + ':@"'

            newline = newline.replace("#RRG_inset_PATHSHADER", 'Option "searchpath" "string shader" ["' + osl + ':@"]')
            newline = newline.replace("#RRG_inset_PATHTEX", 'Option "searchpath" "string texture" ["' + osl + ':@"]')
            newline = newline.replace("#RRG_inset_PATHPROC", 'Option "searchpath" "string procedural" ["' + osl + ':@"]')
            newline = newline.replace("#RRG_inset_PATHRIX", 'Option "searchpath" "string rixplugin" ["' + osl + ':@"]')
            arch = os.path.join(globalvars.APP_ROOT, "OSE_Modules", "exportschemes")
            # newline = newline.replace(old, new)
            source_file_f.write(newline)

        # ------------------ Render it to IT ----------------------
        prman_path = '"' + str(os.path.join(self.settings.path_settings['RMANTREE'], 'bin', 'prman')) + '" '
        # subprocess.call([prman_path, source_file], shell=True)
        rndr_cmd = prman_path + source_file
        print "Running:", rndr_cmd
        my_env = os.environ
        proc = subprocess.Popen(rndr_cmd, env=my_env, shell=True)

    def save_img(self):
        """Save an image of the render."""
        pass
    """
    Recursive function that dose the heavy lifting. Starting from
    the source node (a shader normally) it will go through all
    the in_attributes. If there is a connection it will then add
    the connected node to a list and run this function again on it
    """
    def stream_me(self, _nodename):
        """Recursive func that loops over nodes."""
        more_nodes = []

        node = self.nodes[_nodename]

        # Need to fix lower case letters comming in from XML source
        nodefunction = None
        if str(node.type[0]) == 'p':
            nodefunction = 'Pattern'
        elif str(node.type[0]) == 'b':
            nodefunction = "Bxdf"
        else:
            nodefunction = str(node.type)

        my_string = nodefunction + ' "' + str(node.style) + '" ' + '"' + str(node.name) + '" \n '

        for key, attr in node.in_attributes.iteritems():
            # Check to see if it is connected
            if attr.connection == None:

                # Check to see what type the value is.
                # This will govern the export scheme
                if str(attr.type) == "int":
                    my_string = my_string + '"' + str(attr.type) + " " + str(attr.name) + '" [' + str(attr.value).replace('f', '') + '] \n '

                elif str(attr.type) == "float":
                    my_string = my_string + '"' + str(attr.type) + ' ' + str(attr.name) + '" [' + str(attr.value).replace('f', '') + '] \n '

                elif str(attr.type) == "color":
                    my_string = my_string + '"' + str(attr.type) + ' ' + str(attr.name) + '" [' + str(attr.value.x).replace('f', '') + ' ' + str(attr.value.y).replace('f', '') + ' ' + str(attr.value.z).replace('f', '') + '] \n '

                elif str(attr.type) == "string":
                    my_string = my_string + '"' + str(attr.type) + ' ' + str(attr.name) + '" [' + str(attr.value) + '] \n '

            else:
                # Use this to create a refrence to another node.
                # Also add to array to be exported
                my_string = my_string + '"reference ' + str(attr.type) + ' ' + str(attr.name) + '"' + '["' + str(attr.connection.dest_node) + ':' + attr.connection.dest_attr + '"] \n '

                # Need to make sure I am not outputting the same data twice if
                # same node is connected to multiple imputs

                if str(attr.connection.dest_node) not in more_nodes:
                    more_nodes.append(str(attr.connection.dest_node))

        self.out_stream.append(my_string)

        for ids in more_nodes:
            self.stream_me(ids)
        pass


class MayaExporter(Exporter):
    """Generate a maya scene File"""
    # There is currently a maya script that will let you pull in a json shading network
    # This currently is not needed
    pass


class JsonExporter(Exporter):
    """Export to a json file, for use with file saves."""

    def export(self):
        """Export a RIS RIB file to loc."""
        print 'Starting Export'
        # The node network output stream. Every item is a line

        self.out_stream = {}

        for nodekey, node in self.nodes.iteritems():
            self.out_stream[nodekey] = {}
            self.out_stream[nodekey]['STYLE'] = node.style
            if hasattr(node, 'src'):
                if 'osl' in node.src:
                    self.out_stream[nodekey]['TYPE'] = 'texture'
                    self.out_stream[nodekey]['STYLE'] = node.style
            else:
                self.out_stream[nodekey]['TYPE'] = node.type

            self.out_stream[nodekey]['ATTRIBUTES'] = {}
            for key, attr in node.in_attributes.iteritems():
                if attr.connection:
                    e_val = ["connection",
                             attr.connection.dest_node,
                             attr.connection.dest_attr]
                elif isinstance(attr.value, datatypes.Vec3):
                    e_val = [attr.value.x, attr.value.y, attr.value.z]
                else:
                    e_val = attr.value

                self.out_stream[nodekey]['ATTRIBUTES'][key] = e_val

        self.save()

    def save(self):
        """Save the out stream to file."""

        try:
            target = open(self.loc, 'w')
            target.seek(0)
            target.truncate()

            json.dump(self.out_stream, target)

            target.close()

            print "File Written to", self.loc
            print "Export compleated successfully"

        except:
            print "Unable to write file", self.loc
