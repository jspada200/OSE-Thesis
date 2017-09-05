"""Provides interface to create custom nodes."""

# import backend_canvas as canvas
import backend_node as node
import backend_nodeimporter as importer
import os
from PyQt4 import QtCore
import subprocess
import time
from shutil import copyfile
import xml.etree.ElementTree as ET
from random import randint
import globalvars
import re


class UpdateChecker(QtCore.QThread):
    """Object that searches for update to a specific file."""

    file_changed = QtCore.pyqtSignal()

    def __init__(self, p, filepath):
        """Init."""
        super(UpdateChecker, self).__init__(p)
        self.lastupdate = None
        self.filepath = filepath
        print "Init update checker:", self.filepath

        if os.path.isfile(self.filepath):
            self.lastupdate = os.stat(self.filepath)[8]
        else:
            f = open(self.filepath, "wb")
            del f
            self.lastupdate = os.stat(self.filepath)[8]

    def run(self):
        """Main Thread, check for updates."""
        running = True
        while running:
            try:
                new_update = os.stat(self.filepath)[8]
                if new_update != self.lastupdate:
                    self.lastupdate = new_update
                    self.file_changed.emit()
            except:
                continue
            time.sleep(1)


class CustomNode(QtCore.QObject, node.Node):
    """Super class for any custom nodes."""
    update_visual = QtCore.pyqtSignal()
    
    def __init__(self,
                 _parent,
                 _name,
                 _type,
                 _style,
                 _helptxt,
                 _importer,
                 _srcfile=None,
                 _argsfile=None,
                 _compiled=None):
        """Init."""

        QtCore.QObject.__init__(self, _parent)
        node.Node.__init__(self,
                           _name=_name,
                           _type=_type,
                           _style=_style,
                           _helptxt=_helptxt)

        self.EXPORT_PATH = os.path.join(globalvars.APP_ROOT, "Custom")
        self.settings = self.parent().settings
        self.nodeimporter = _importer
        # Paths for relevent files
        self.src = _srcfile
        if self.src is None:
            if self.cksrc() is False:
                self.createsrc()

        self.ntype = _type

        self.compiled = _compiled
        if self.compiled is None:
            self.compilenode()

        self.argsfile = _argsfile
        if self.argsfile is None:
            self.generateargs()

        # Text stating the status (compled, errors, ext)
        self.status = "None"

        # Create update trackers and link.
        self.src_update_checker = UpdateChecker(self, self.src)
        self.src_update_checker.file_changed.connect(self.compilenode)
        self.src_update_checker.start()
        print self.src_update_checker
        # Custom setup for specific nodes
        self.initnode()

    def initnode(self):
        """Entery point for custom nodes."""
        pass

    def createsrc(self):
        """Create a file to act as the main file."""
        # Copy a templeate file depending on what node it is.
        pass
    # ---------- Change functions ----------------------

    def srcupdated(self):
        """Function called when src is updated."""
        pass

    def generateargs(self):
        """Create args or modify args based on src."""
        pass

    def compilenode(self, qstr):
        """Compile the given src file."""
        pass

    def cksrc(self):
        """Check to see if the source file exist."""
        return False


class RISOSLNode(CustomNode):
    """OSL node class."""

    def createsrc(self):
        """Copy a src file to use as a templet."""
        p = os.path.join(self.EXPORT_PATH, 'osl', 'src')
        copyfile(os.path.join(p, 'test.osl'), os.path.join(p, self.style + '.osl'))
        self.src = os.path.join(p, self.style + '.osl')

    def compilenode(self):
        """Use OSLC from renderman complie our osl node."""
        osopath = os.path.join(self.EXPORT_PATH, "osl", self.style + ".oso ")
        oslc = '"' + os.path.join(self.settings.path_settings['RMANTREE'], 'bin', 'oslc') + '"'
        oslc_process = oslc + " -v -o " + osopath + self.src

        p = subprocess.Popen(oslc_process, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.stdout.read()
        err = p.stderr.read()

        print output
        print err

        self.status = output.split()[0]
        if self.status == 'FAILED':
            print "Failed to compile!"
            print err
        else:
            print output
            self.compiled = str(osopath)
            self.generateargs()

    def generateargs(self):
        """Create args or modify args based on src."""
        # run oslinfo
        # Todo - Run in verbos to get all the meta data - ! 
        osopath = os.path.join(self.EXPORT_PATH, "osl", self.style + ".oso")
        self.argsfile = os.path.join(self.EXPORT_PATH, "osl", "args", self.style + ".args")
        oslinfo = '"' + os.path.join(self.settings.path_settings['RMANTREE'], 'bin', 'oslinfo') + '" -v'
        proc = oslinfo + " " + osopath
        p = subprocess.Popen(proc,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()

        oslinfo_inattributes = {}
        oslinfo_outattributes = {}
        attrs = {"in":{}, "out":{}}
        # TODO - Run OSL Info in verbose mode to get more data!
        currentkey = ""
        currenttype = ""
        print "OSLINFO OUTPUT:"
        print out
        print "======================================"
        for line in out.split('\n'):
            # Attrubute Defanition= \s{4}["] 
            # Attrubute setting = (\s{16})\w
            if re.match(r'\s{4}["]', line) is not None:
                line = line.replace('"', '').split()
                print "Attribute Def! :", line
                if len(line) == 2:
                    currenttype = "in"
                    currentkey = line[0]
                    attrs[currenttype][line[0]] = {"type" : line[1]}
                elif len(line) == 3:
                    currenttype = "out"
                    currentkey = line[0]
                    attrs[currenttype][line[0]] = {"type" : line[2]}

            elif 'Default value' in line or 'metadata' in line:
                line = line.split(":")
                if "Default value" in line[0]:
                    if attrs[currenttype][currentkey]["type"] == "color":
                        attrs[currenttype][currentkey]["default"] = line[1].split()[1:4]

                    else:
                        attrs[currenttype][currentkey]["default"] = line[1]
                    print attrs[currenttype][currentkey]["default"]
                elif "metadata" in line[0]:
                    line = line[1].split()
                    vartype = line[0]
                    varname = line[1]
                    varval = line[3:len(line)]

                    if vartype == "string":
                        varval = varval.join().replace('"', '')
                    elif len(varval) <= 1:
                        varval = varval[0].replace('"', '')
                    elif len(varvel) > 5:
                        varval = varval[1:4]
                    print varval
                    attrs[currenttype][currentkey][varname] = varval

        oslinfo_inattributes = attrs['in']
        oslinfo_outattributes = attrs['out']

        print oslinfo_inattributes
        print oslinfo_outattributes


        '''
        line = line.split()
        # Check to see if it is an attribute
        # Regular float, int, or str input
        if len(line) == 3:
            oslinfo_inattributes[line[1]] = [line[0], line[2]]
        # Regular float, int, or str output
        elif len(line) == 4:
            oslinfo_outattributes[line[2]] = [line[1], line[3]]
        # Regular vec3 input
        elif len(line) == 7:
            oslinfo_inattributes[line[1]] = [line[0], [line[3], line[4], line[5]]]
        # Regular vec3 output
        elif len(line) == 8:
            oslinfo_outattributes[line[2]] = [line[1], [line[4], line[5], line[6]]]
        '''
        # Check to see if an args file exists

        
        # Build a brand new basic args file
        # copy default templet and fill in data
        copyfile(os.path.join(self.EXPORT_PATH, 'osl', 'args', 'PxrDefault.args'),
                 self.argsfile)

        # Set inital information
        # on the defualt templet
        tree = ET.parse(self.argsfile)
        root = tree.getroot()
        # Set shader type
        root[0][0].set('value', self.ntype)

        # Gen a unique ID
        root[2].set('nodeid', str(randint(1, 524288)))

        parmsandouts = []
        for key, data in oslinfo_outattributes.iteritems():
            parmsandouts.append(self.build_xml_args(key, data, 'output'))

        for key, data in oslinfo_inattributes.iteritems():
            parmsandouts.append(self.build_xml_args(key, data, 'param'))
        
        for i in parmsandouts:
            root.insert(2, i)

        tree._setroot(root)
        tree.write(self.argsfile)

        newnode = self.nodeimporter.get_node_data(self.argsfile, get_single=True)
        self.in_attributes = newnode.in_attributes
        self.out_attributes = newnode.out_attributes
        self.update_visual.emit()


    def build_xml_args(self, key, data, elemtag):
        """Build a new element for arguments."""
        # Now we need to add in the in and out args ----
        net = None
        if type(data['default']) is list:
            l = data['default']
            default = str(l[0]) + ". " + str(l[1]) + ". " + str(l[2]) + "."
        else:
            default = str(data['default'])
        minmax = None
        if 'float' in data['type']:
            if 'min' in data.keys():
                minv = data['min']
            else:
                minv = '-1'
            if 'max' in data.keys():
                maxv = data['max']
            else:
                maxv = '1'
            minmax = [minv, maxv]

        helptxt = None
        if 'help' in data.keys():
            helptxt = data['help']
        

        if 'param' in elemtag:
            if 'widget' in data.keys():
                if data['widget'] == "null":
                    data['widget'] = "default"
            else:
                data['widget'] = "defualt"

            if 'label' in data.keys():
                label = data['label']
            else:
                label = key

            if minmax:
                net = ET.Element('param', attrib={'name': key,
                                                  'label': label,
                                                  'type': data['type'],
                                                  'default': default,
                                                  'min': minmax[0],
                                                  'max': minmax[1],
                                                  'widget': data['widget']})
            else:
                net = ET.Element('param', attrib={'name': key,
                                                  'label': label,
                                                  'type': data['type'],
                                                  'default': default,
                                                  'widget': data['widget']})
            ET.SubElement(net, 'help').text = helptxt
        
        else:
            net = ET.Element('output', attrib={'name': key})

        tags = ET.SubElement(net, 'tags')
        vec3types = ['color', 'vector', 'normal', 'point']

        if data['type'] in vec3types:
            for t in vec3types:
                ET.SubElement(tags, 'tag', attrib={'value': t})
        else:
            ET.SubElement(tags, 'tag', attrib={'value': data['type']})

        return net

    def cksrc(self):
        """Check the osl dir for a file by the same name, link if it exists."""
        p = os.path.join(self.EXPORT_PATH, 'osl', 'src')
        src = os.path.join(p, self.style + '.osl')
        if os.path.isfile(src):
            self.src = src
            return True
        else:
            return False
