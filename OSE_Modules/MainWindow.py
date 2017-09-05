from PyQt4 import QtGui
from PyQt4 import uic
import backend_canvas as canvas
import NodeGraph
import AttrPanel
import datatypes
import globalvars
import json

APP_ROOT = globalvars.APP_ROOT

# --------- APP INFO --------
VERSION = "0.8"
DATE = "July 2017"
NOTES = ""


class MainWindow(QtGui.QMainWindow):
    """Main Win and control for app."""

    def __init__(self, parent=None):
        """Init."""
        # Set up interface layout
        super(MainWindow, self).__init__(parent)
        uic.loadUi(APP_ROOT + "/OSE_Modules/ui/main_interface.ui", self)

        # Canvas Object - Stores and process as operations
        self.canvasobj = canvas.Canvas()

        # Link to settings object on canvas
        self.settings = self.canvasobj.settings

        # node graph - Allows interaction between nodes
        self.node_graph = NodeGraph.NodeGraph(self)

        # Side Panel - Allows the changing of node attributes
        self.attr_panel = AttrPanel.AttrPanel(self)

        # The Currently Selected Node in the graph
        self.selected_node = None

        # Attach widgets to layout objects
        self.nodeGraph_scrollArea.setWidget(self.node_graph)
        self.attrPanel_scrollArea.setWidget(self.attr_panel)

        # Set up listeners
        self.preview_pushButton.clicked.connect(self.preview)

        self.setupmenu()

        self.setupstyle()

        self.ipr_enabled = False
        self.ipr = None
        if self.ipr_enabled:
            self.canvasobj.run_ipr.connect(self.preview)

    # ------------------ Interactions with the Data ------------------

    def edit_attribute(self, node, attr, value):
        """Change Attr Value on Canvas."""
        success = self.canvasobj.edit_attribute(node, attr, value)
        if success is True:
            return True
        else:
            return False

    def make_node(self, identifier, custom=False, name=None):
        """Try to make a new node."""
        print str(identifier)
        node_name = self.canvasobj.add_node(str(identifier), custom=custom, name=None)
        print "Nodename is", node_name
        if node_name is not False:
            self.node_graph.addnode(str(node_name), "None")
            self.preview_comboBox.addItem(str(node_name))

    def connect(self, n1_name, n1_attr, n2_name, n2_attr):
        """Connect 2 node Attributes."""
        success = self.canvasobj.connect_attributes(n1_name,
                                                    n1_attr,
                                                    n2_name,
                                                    n2_attr)
        if success is True:
            print "Adding Connection"
            self.node_graph.addconnection(n1_name,
                                          n1_attr,
                                          n2_name,
                                          n2_attr)
        else:
            print "Could not connect"

    def delete_connection(self, obj):
        """Delete a connection between two attrs."""
        print obj.downstreamconnect
        node_name = obj.downstreamconnect.parentLayoutItem().parentLayoutItem().name
        x = self.canvasobj.disconnect_attributes(node_name,
                                                 obj.downstreamconnect.name)
        if x:
            return True
        else:
            return False

    def delete_node(self, obj):
        """Delete a node from the canvas."""
        n = str(obj.name)
        if self.canvasobj.delete_node(obj.name):
            self.selected_node = None
            index = self.preview_comboBox.findText(n)
            self.preview_comboBox.removeItem(index)
            return True

        else:
            print "Not Deleted"
            return False

    def preview(self):
        """Preview a selected node."""
        # Check to see if the current PRman process is running.
        # If so it needs to be killed first.

        self.canvasobj.export(str(self.preview_comboBox.currentText()),
                              _preview=True)

    def update_attr_panel(self):
        """Update info in attr panel."""
        self.attr_panel.update_layout()

    def helloworld(self):
        """test."""
        print "Main Widget - hello world"

    def setupmenu(self):
        """Set up top menu items with actions."""
        #
        # ------------------- Set up add node menu -----------------
        # Get list of nodes from canvas and add to list
        nodes_to_add = {}
        groups = []
        nodetypes = ['pattern', 'bxdf']
        for name, node in self.canvasobj.avalible_nodes.iteritems():
            nodes_to_add[name] = node.type
            if node.type not in groups:
                if node.type in nodetypes:
                    groups.append(node.type)

        sortednodes = {}
        for grp in groups:
            nlist = []
            for node, n_grp in nodes_to_add.iteritems():
                if n_grp in grp:
                    nlist.append(node)
            nlist.sort()
            sortednodes[grp] = nlist
        self.nodeactlist = {}
        for grp, nodelist in sortednodes.iteritems():
            newmenu = self.menu_addnode.addMenu(grp)
            for node in nodelist:
                self.nodeactlist[node] = datatypes.MakeNodeAction(node, self)
                print "Node is:", node
                newmenu.addAction(self.nodeactlist[node])
                self.nodeactlist[node].triggered.connect(self.nodeactlist[node].make_node)

        #
        # ------------------- Set up custom node menu -------------
        # Gets a list of custom nodes that can be created
        for key, value in self.settings.user_settings['CUSTOM_NODES'].iteritems():
            newaction = QtGui.QAction(value['menuLabel'], self)
            self.menuCustom_Nodes.addAction(newaction)
            newaction.triggered.connect(lambda: self.customnodedig(key))

        for nodename, node in self.canvasobj.avalible_custom_nodes.iteritems():
            self.nodeactlist[nodename] = datatypes.MakeNodeAction(nodename, self, custom=True)
            print "Node is:", nodename
            self.menuCustom_Nodes.addAction(self.nodeactlist[nodename])
            self.nodeactlist[nodename].triggered.connect(self.nodeactlist[nodename].make_node)

        # --------------------- Set up help menu -----------------
        self.actionWiki.triggered.connect(self.actwiki)
        self.actionAbout.triggered.connect(self.actabout)

        # --------------------- Set up Util Menus -----------------
        self.actionSave.triggered.connect(self.save)
        self.actionOpenJson.triggered.connect(self.open)

    def customnodedig(self, nodestyle):
        """Dialog for custom nodes."""
        nodedat = NewCustomNodeDig(self, nodestyle)
        if nodedat.exec_():
            vals = nodedat.GetValue()
            print nodestyle
            if self.canvasobj.create_custom(vals[0], vals[1], vals[0], vals[2]):
                self.make_node(vals[0], custom=True)

    def actwiki(self):
        """Help action."""
        print "Act Help"

    def actabout(self):
        """Act action."""
        AboutDig(self)

    def setupstyle(self):
        """Set up look of main widget."""
        x = 'interface-backgroundcolor'
        bgcolor = self.settings.display_settings['MAINSTYLE'][x]
        style = """
        .QMainWindow {
            background-color: %s
        }

        """ % bgcolor
        self.setStyleSheet(style)

    # ------------------ For Saving and Opening ------------
    def save(self):
        """Save a json file."""
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Save shader Descrition',
                                                     APP_ROOT,
                                                     selectedFilter='*.json')
        self.canvasobj.save_scene(path=fileName)

    def open(self):
        """Open a json discription of the network."""
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Save shader Descrition',
                                                     APP_ROOT,
                                                     selectedFilter='*.json')
        # Based on the incoming json file, create nodes then set attrs.
        if fileName:
            inputdict = json.load(open(fileName, 'r'))
            # Make Nodes
            for node_name, node_info in inputdict.iteritems():
                self.make_node(node_info['STYLE'], name=node_name)
            # Set Attrs
            for node_name, node_info in inputdict.iteritems():
                # If the attr a connection or attr?
                for attrname, attrval in node_info['ATTRIBUTES'].iteritems():
                    if isinstance(attrval, list):
                        if 'connection' in attrval[0]:
                            self.connect(attrval[1],
                                         attrval[2],
                                         node_name,
                                         attrname)


class NewCustomNodeDig(QtGui.QDialog):
    """Interface for getting some info for a new custom node."""

    def __init__(self, p, nodetype):
        """Init."""
        super(NewCustomNodeDig, self).__init__(p)
        uic.loadUi(APP_ROOT + "/OSE_Modules/ui/new_custom_node_dig.ui", self)
        settingsdict = p.settings.user_settings['CUSTOM_NODES'][nodetype]
        for option in settingsdict['_type']:
            self.nodeTypeComboBox.addItem(option)

    def OnCancel(self):
        """Close and do nothing."""
        self.close()

    def OnOk(self):
        """On Ok."""
        self.close()
        return (str(self.nodeNameLineEdit.text()),
                str(self.nodeTypeComboBox.currentText()),
                str(self.helpTextLineEdit.text()))

    def GetValue(self):
        """Get the value."""
        return (str(self.nodeNameLineEdit.text()),
                str(self.nodeTypeComboBox.currentText()),
                str(self.helpTextLineEdit.text()))


class AboutDig(QtGui.QDialog):
    """About Dialog."""

    def __init__(self, p):
        """Init."""
        super(AboutDig, self).__init__(p)
        uic.loadUi(APP_ROOT + "/OSE_Modules/ui/aboutDialog.ui", self)
        self.Version_txt.setText(VERSION)
        self.Date_txt.setText(DATE)
        self.closeButton.clicked.connect(self.btnpressed)
        self.show()

    def btnpressed(self):
        """Close BTN."""
        self.close()