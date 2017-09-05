"""NodeImporter - Super class for importing new nodes."""
import os
import glob
import backend_node as node
import customnodes as cn
import backend_attribute as attribute
from xml.etree import ElementTree
import re
from PyQt4 import QtCore
# from subprocess import check_output


"""This class serves as a framework for other moduals to
import nodes to the canvas."""


class NodeImporter(QtCore.QObject):
    """NodeImporter - Super class for importing new nodes."""

    def __init__(self, _path_settings, _parentobj):
        """INIT."""
        super(NodeImporter, self).__init__(_parentobj)
        self.path_settings = _path_settings
        self.node_list = {}
        self.custom_node_list = {}
        self.get_nodes()
        print len(self.node_list), "Nodes have been found!"

    def get_nodes(self):
        """Gen a node list that can be returned to the canvas."""
        pass

    def get_list(self):
        """Return a list of nodes to the canvas."""
        return self.node_list


class RmanNodeImporter(NodeImporter):
    """Import renderman Nodes."""

    def get_nodes(self):
        """Gen a node list that can be returned to the canvas."""
        self.installDir = os.path.join(self.path_settings['RMANTREE'] , "lib", "plugins")

        for filename in glob.glob(os.path.join(self.installDir, 'Args', '*.args')):
            self.get_node_data(filename)

        # Scan local custom OSL dir
        for filename in glob.glob(os.path.join(self.path_settings['current_dir'], 'Custom', 'osl', 'args', '*.args')):
            self.get_node_data(filename, ctype='RISOSLNode')

        '''
        # Renderman 20.11 had a differnt folder struct then 21.2
        # Place holder
        # self.installDir = os.environ['RMANTREE'] + '/lib/RIS/'
        current_type = None
        # check each dir for args folder
        for x in os.listdir(self.installDir):
            current_type = x
            if current_type == 'pattern' or current_type == 'bxdf':
                ck_dir = self.installDir + x
                if len(os.listdir(ck_dir)) > 0:
                    for x in os.listdir(ck_dir):
                        if x == 'Args':
                            for filename in glob.glob(os.path.join((ck_dir + '/Args/'), '*.args')):
                                self.get_node_data(filename)
        '''

    def get_node_data(self, filename, ctype='' ,get_single=False):
        """Get a single Node."""
        f = open(filename, 'rt')
        tree = ElementTree.parse(f)

        shader_type = None
        # first Get the shader Type
        for item in tree.findall('.//shaderType/tag'):
            shader_type = item.attrib.get('value')

        node_help = None

        node_help_stuff = tree.findall("help")

        for node_help_item in node_help_stuff:
            node_help = node_help_item.text

        style = None
        m = re.match(r'(.+?)(\.[^.]*$|$)', (os.path.basename(filename)))
        if m != None:
            style = m.group(1)

        # Create a new Node object
        if 'RISOSLNode' in ctype:
            # Do some checks to see whats on disk....
            # Check to see if there is a source file, if not we are going to abort this build.
            osldir = os.path.join(self.path_settings['current_dir'], 'Custom', 'osl')
            srcfile = os.path.join(osldir, 'src', os.path.basename(filename).replace('.args', '.osl'))
            print 'filename', filename
            print 'osldir', osldir
            print 'srcfile', srcfile
            if os.path.isfile(srcfile):
                print "SRC FOUND!"
                # check to see if there is a compled node.
                new_node = cn.RISOSLNode(self.parent(),
                                         style,
                                         shader_type,
                                         style,
                                         node_help,
                                         self,
                                         _srcfile = srcfile,
                                         _argsfile = os.path.join(osldir, 'args', filename))
            else:
                return 0
        else: 
            new_node = node.Node(style, shader_type, style, node_help)

        # Next Get the Args and outputs using the get Arg List Function
        attr_list = []
        attr_list = self.get_attrs(tree)

        out_list = []
        out_list = self.get_outputs(tree)

        new_node.in_attributes = attr_list
        new_node.out_attributes = out_list

        if get_single:
            tree = None
            f.close()
            return new_node
        else:
            # new_node.print_node_data()
            if ctype is not '':
                self.custom_node_list[new_node.name] = new_node
            else:
                self.node_list[new_node.name] = new_node
            tree = None
            new_node = None
            f.close()

    def get_attrs(self, _tree):
        """Get all the arguments and add them to this node."""
        name = None
        label = None
        arg_type = None
        default = None
        widget = None
        tag_value = []
        help = None
        options = []

        return_list = {}

        for arg in _tree.findall(".//param"):
            name = arg.attrib.get('name')
            label = arg.attrib.get('label')
            arg_type = arg.attrib.get('type')
            default = arg.attrib.get('default')
            widget = arg.attrib.get('widget')

            output_dict = {}

            if arg_type == "float":
                min_val = arg.attrib.get('min')
                max_val = arg.attrib.get('max')
                output_dict['min'] = min_val
                output_dict['max'] = max_val

            for tagItem in arg.findall('tags/tag'):
                tag_value = tagItem.attrib.get('value')

            for helpItem in arg.findall('args/help'):
                help = helpItem.text

            options = []
            if widget == "mapper":
                hintdicts = arg.find('hintdict')

                for option in hintdicts.findall('string'):
                    options.append(option.attrib.get('name'))

            output_dict['label'] = label
            output_dict['default'] = default
            output_dict['widget'] = widget
            output_dict['tag_value'] = tag_value
            output_dict['help'] = help
            output_dict['options'] = options

            return_list[name] = attribute.Attribute(name,
                                                    arg_type,
                                                    default,
                                                    output_dict)
        return return_list

    def get_outputs(self, tree):
        """Get a list of outputs for a node."""
        name = None
        arg_type = []

        return_list = {}

        for output_item in tree.findall('output'):
            name = output_item.attrib.get('name')

            for tag_item in output_item.findall('tags/tag'):
                arg_type = tag_item.attrib.get('value')

            return_list[name] = attribute.Attribute(name, arg_type)

        return return_list

# This is a work in progress to explore importing arnold nodes into OSE
# Not needed for thesis submission
'''
class ArnoldNodeImporter(NodeImporter):
    """NodeImporter - Super class for importing new nodes."""

    def get_nodes(self):
        """Gen a node list that can be returned to the canvas."""
        # Three posible Methods, Try to pull from mtoa_shaders, Katana Args, or Kick
        # ----------------- mtoa_shaders ----------------------------
        # Get the mtoa_shaders.mtd file, Contains args for shaders

        # Arnold File contains info for all the built in nodes.
        # [declatationtype name] = new declaration
        #   Node
        #   Attr

        # -------------- Katana Args --------------------------------
        # Since Katana May not be installed, Will include a folder of 
        # Args files included in the katana Plugin Install. 
        # Will be stored in approot/ArnoldRscrs/Args

        # Get a list of all the args files.

        Argspath = os.path.join(self.path_settings['current_dir'], 'ArnoldRscrs', 'Args', '*.args')
        print Argspath
        for file in glob.glob(Argspath):
            print file
            self.get_node_data(os.path.join(Argspath, file))

        # -------------- Kick --------------------------------------
        # Kick is a utility that allows you to get info and render with Arnold
        out = check_output([os.path.join(self.path_settings['ARNOLD'],
                                         "bin",
                                         self.path_settings['KICK']), "-nodes"])
        nodes = {}
        print "Parsing Nodes"
        # Types of args supported. 
        argtypes = ["RGB", "FLOAT", "BOOL", "ENUM", "STRING", "INT"]

        for line in out.split("\n"):
            l = line.split()
            if len(l) == 2 and l[1] == "shader":
                nodes[l[0]] = self.get_node_data(l[0], argtypes)   
        
        for nodename, nodedata in nodes.iteritems():
            new_node = node.Node(nodename, 'shader', nodename, "")

            name = None
            label = None
            arg_type = None
            default = None
            widget = None
            help = None

            attrs = {}
            for attrname, attrvals in nodedata['attributes'].iteritems():
                

                widget = None
                attrType = None
                # Find the widget and type
                if attrvals['type'] == 'RGB':
                    attrType = 'color'
                    widget = 'color'
                    x = float(attrvals['default'][0].replace(",", ""))
                    y = float(attrvals['default'][1].replace(",", ""))
                    z = float(attrvals['default'][2].replace(",", ""))
                    attrvals['default'] = [x, y, z]
                
                elif attrvals['type'] == 'FLOAT':
                    attrType = 'float'
                    widget = 'float'
                elif attrvals['type'] == 'BOOL':
                    attrType = 'int'
                    widget = 'checkbox'
                elif attrvals['type'] == 'ENUM':
                    attrType = 'string'
                    widget = 'string'
                elif attrvals['type'] == 'INT':
                    attrType = 'int'
                    widget = 'float'                

                extrainfo = {'label':attrname, 
                             'default': attrvals['default'],
                             'help': "",
                             'widget': widget
                             }


                newattr = attribute.Attribute(attrname,
                                              attrType,
                                               in_value=attrvals['default'],
                                               _extrainfo=extrainfo)
                attrs[attrname] = newattr

            new_node.in_attributes = attrs

            self.node_list[nodename] = new_node

    def get_node_data(self, nodename, argtypes):
        """Using Kick, return more detailed info from kick."""
        cmd = os.path.join(self.path_settings['ARNOLD'],
                           "bin",
                           self.path_settings['KICK'])
        print cmd
        out = check_output([cmd, "-info", nodename])
        nodedata = {}
        nodedata['attributes'] = {}
        for line in out.split("\n"):
            line = line.split()
            if len(line) > 0:
                if line[0] == "node:":
                    nodedata['name'] = line[1]
                
                elif line[0] == "output:":
                    nodedata['output'] = line[1]
                
                elif line[0] in argtypes:
                    try:
                        if line[0] == "RGB":
                            print line
                            d = []
                            d.append(line[2])
                            d.append(line[3])
                            d.append(line[4])
                            nodedata['attributes'][line[1]] = {'default': d,
                                                               'type':line[0]}  
                        else:
                            nodedata['attributes'][line[1]] = {'default':line[2],'type':line[0]}
                    except Exception, e:
                        print str(e)
                        print "Could not add attribute", line[1]                  
        return nodedata

    # Kept this method for ref just in case Katana Args files are needed.
    def get_node_data_argsfiles(self, file):
        """Build a node from the args data."""
        f = open(file, 'rt')
        tree = ElementTree.parse(f)
        nodename = os.path.basename(file).replace('.args', '')
        root = tree.getroot()
        nodehelp = root[0].text

        in_attributes = {}
        for child in root:
            if child.tag == 'param':
                print child.attribmaya
                in_attributes[child.attrib['name']] = child.attrib
'''
