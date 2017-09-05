"""Node graph and related classes."""

from PyQt4 import QtGui
from PyQt4 import QtCore
# import canvas

'''
TODO

Look
- Use look information from settings
    - nodes
    - connections
    - canvas
- Connections
    - Line Width
'''
# ----------------------------- NodeGFX Class --------------------------------#
# Provides a visual repersentation of a node in the node interface. Requeres
# canvas interface. Added to main scene
#


class NodeGFX(QtGui.QGraphicsItem):
    """Display a node."""

    # --------------------------- INIT ---------------------------------------#
    #
    # Initlize the node
    #   n_x - Where in the graphics scene to position the node. x cord
    #   n_y - Where in the graphics scene to position the node. y cord
    #   n_node - Node object from Canvas. Used in construction of node
    #   n_scene - What is the parent scene of this object
    #
    def __init__(self, n_x, n_y, n_node, n_scene, init=True):
        """INIT."""
        super(NodeGFX, self).__init__()
        # Colection of input and output AttributeGFX Objects
        self.gscene = n_scene
        self.inputs = {}
        self.outputs = {}

        # An identifier for selections
        self.io = "node"

        self.base_node = n_node
        # Use information from the passed in node to build
        # this object.
        self.name = self.base_node.name

        # Check to see if this emiter exists on the node. if so connect it
        try:
            self.base_node.update_visual.connect(self.checkvars)
        except Exception, e:
            print "Not a custom node"
            print str(e)

        # Get the node color for styling
        self.nodeMeta = self.base_node.type

        # Load display settings
        self.settings = self.gscene.settings

        self.disp_set = {}
        if self.nodeMeta not in self.settings.display_settings['NODES'].keys():
            self.disp_set = self.settings.display_settings['NODES']['default']
        else:
            self.disp_set = self.settings.display_settings['NODES'][self.nodeMeta]

        # The width of a node
        self.width = self.disp_set['min-width']
        self.height = self.disp_set['min-height']

        # Inputs and outputs
        node_inputs = self.base_node.in_attributes
        node_outputs = self.base_node.out_attributes

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)

        # ------------------------ Set up Node Title --------------------
        f = self.disp_set['fontcolor']
        self.lable = QtGui.QGraphicsTextItem(self.name,
                                             self)
        self.lable.setDefaultTextColor(QtGui.QColor(f[0], f[1], f[2]))

        off = self.disp_set['boarderWidth'] / 2
        self.lable.setPos(off, off)

        # ------------------------ Set up layouts for attrs --------------------
        self.inputslayout = _GraphicsLayout(self.disp_set['attribute_offset'], self)
        self.inputslayout.translate(0, 35)

        self.outputslayout = _GraphicsLayout(self.disp_set['attribute_offset'], self)
        self.outputslayout.translate(self.disp_set['min-width'], 35)

        self.checkvars()

        # Bools for drawing options.
        self._over = False
        self._selected = False
        self.setGraphicsEffect(QtGui.QGraphicsDropShadowEffect())
        self.setAcceptHoverEvents(True)

    # ---------------- Utility Functions -------------------------------------#
    def canv(self):
        """Link to the canvas object."""
        return self.scene().parent().parent().canvasobj

    def __del__(self):
        """Destory a node and all child objects."""
        # Remove self from GFX scene
        try:
            self.scene().removeItem(self)
        except:
            pass

    def boundingRect(self):
        """Bounding."""
        return QtCore.QRectF(-.5,
                             -.5,
                             self.width + .5,
                             self.height + .5)

    # ------------- Event Functions ------------------------------------------#

    def mouseReleaseEvent(self, event):
        if event.pos().x() > 10 and event.pos().x() < (self.width - 50):
            self.update()
            super(NodeGFX, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Update connections when nodes are moved."""
        self.scene().updateconnections()
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)
        self.gscene.update()

    def mousePressEvent(self, event):
        """Select a node."""
        if event.pos().x() > 10 and event.pos().x() < (self.width - 50):
            self.scene().selection(self)
        # QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)

    def hoverEnterEvent(self, event):
        """Set flag for mouse over."""
        try:
            self.scene().parent().node_graph.setDragMode(QtGui.QGraphicsView.NoDrag)
            self._over = True
        except:
            pass

    def hoverLeaveEvent(self, event):
        """Set flag for mouse over."""
        try:
            self.scene().parent().node_graph.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self._over = False
        except:
            pass

    def checkvars(self):
        """Check all the inputs and outputs for this var name. If it is new add it.
        If it is deleted, remove it."""
        print "Updating node visuals"
        # ----------------- Add new inputs and outputs ------------------
        # Add new inputs
        for key, value in self.base_node.in_attributes.iteritems():
            if key not in self.inputs.keys():
                # Set up input
                new_attr_gfx = AttributeGFX(0,
                                            0,
                                            self.scene(),
                                            self.settings,
                                            key,
                                            value.type,
                                            "input")
                self.inputs[key] = new_attr_gfx
                self.inputslayout.add_item(new_attr_gfx)
        # Add new outputs
        for key, value in self.base_node.out_attributes.iteritems():
            if key not in self.outputs.keys():
                # Set up input
                new_attr_gfx = AttributeGFX(0,
                                            0,
                                            self.scene(),
                                            self.settings,
                                            key,
                                            value.type,
                                            "output")
                self.outputs[key] = new_attr_gfx
                self.outputslayout.add_item(new_attr_gfx)

        # ---------- Remove deleted inputs and outputs ---------------

        for key, value in self.inputs.iteritems():
            if key not in self.base_node.in_attributes.keys():
                self.inputslayout.remove_items(key)

        for key, value in self.outputs.iteritems():
            if key not in self.base_node.out_attributes.keys():
                self.outputslayout.remove_items(key)

    # ----------- Paint Functions -------------------------------------------#
    def paint(self, painter, option, widget):
        """Paint the node."""
        # Will need to pull from settings instead of what is being done here

        # Get large layout height

        if self.inputslayout.height() > self.outputslayout.height():
            self.height = self.inputslayout.height()
        else: 
            self.height = self.outputslayout.height()

        if self.disp_set['attribute_offset'] > self.height:
            self.height = self.disp_set['attribute_offset']
        self.height += 75
        print "Drawing node height:", self.height
        bg = self.disp_set['bgcolor']
        color = QtGui.QColor(bg[0], bg[1], bg[2])

        boarderwidth = self.disp_set['boarderWidth']

        # Background
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(color)

        rectangle = QtCore.QRectF(0,
                                  0,
                                  self.width,
                                  self.height)
        painter.drawRoundedRect(rectangle, 15.0, 15.0)

        # Inner Area
        painter.setPen(QtCore.Qt.NoPen)

        if self._selected:
            bc = self.disp_set['selbgcolor']
        else:
            bc = self.disp_set['boarderColor']

        color = QtGui.QColor(bc[0], bc[1], bc[2])

        painter.setBrush(color)
        w = self.width - boarderwidth
        h = self.height - boarderwidth

        showfx = self.graphicsEffect()

        if self._over:
            showfx.setColor(QtGui.QColor(1,0,0))
        else:
            showfx.setColor(QtGui.QColor(0,0,0))



        rectangle = QtCore.QRectF(0 + boarderwidth / 2,
                                  0 + boarderwidth / 2,
                                  w,
                                  h)

        painter.drawRoundedRect(rectangle, 15.0, 15.0)


# -------------------------- ConnectionGFX Class -----------------------------#
# Using two attributes draw a line between them. When
# Set up, a connection is also made on the canvas. unlike the canvas which
# stores connections on attributes, connectionGFX objects are stored in a
# list on the scene object
#


class ConnectionGFX (QtGui.QGraphicsLineItem):
    """A connection between two nodes."""

    # ---------------------- Init Function -----------------------------------#
    #
    # Inits the Connection.
    #   n_scene - The scene to add these connections to
    #   n_upsteam - a ref to an upstream attributeGFX object.
    #   n_downstream - a ref to a downstream attributeGFX object.
    #

    def __init__(self, n_scene, n_upstream, n_downstream):
        """INIT."""
        # Links to the AttributeGFX objs
        self.upstreamconnect = n_upstream
        self.downstreamconnect = n_downstream
        self.io = 'connection'
        self.disp_settings = n_scene.settings.display_settings
        super(ConnectionGFX, self).__init__()
        self.setPen(QtGui.QPen(QtCore.Qt.black, 3, QtCore.Qt.SolidLine))
        n_scene.addItem(self)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.update()

    # ----------------- Utility functions -------------------------------

    # When nodes are moved update is called. This will change the line
    def update(self):
        """Called when new Draw."""
        super(ConnectionGFX, self).update()
        x1, y1, x2, y2 = self.updatepos()
        self.setLine(x1, y1, x2, y2)

    # Called by update calculate the new line points
    def updatepos(self):
        """Get new position Data to draw line."""
        up_pos = QtGui.QGraphicsItem.scenePos(self.upstreamconnect.gitem)
        dn_pos = QtGui.QGraphicsItem.scenePos(self.downstreamconnect.gitem)

        x1 = up_pos.x()
        y1 = up_pos.y() + (self.upstreamconnect.gitem.height / 2)

        x2 = dn_pos.x()
        y2 = dn_pos.y() + (self.upstreamconnect.gitem.height / 2)

        return x1, y1, x2, y2

    # -------------------------- Event Overides ------------------------------#
    def mousePressEvent(self, event):
        """Select a connection."""
        self.scene().selection(self)
        QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)

# ------------------------ AttributeGFX Class --------------------------------#
# Provides a visual repersentation of an attribute. Used for both input and
# output connections. Stored on nodes themselves. They do not hold any of
# the attribute values. This info is stored and modded in the canvas.
#

class AttributeGFX(QtGui.QGraphicsLayoutItem):
    """Wrapper."""

    def __init__(self,
                 n_x,
                 n_y,
                 n_scene,
                 n_settings,
                 n_name,
                 n_type,
                 n_io):
        """Init."""
        super(AttributeGFX, self).__init__()
        self.io = n_io
        self.name = n_name

        # Use same object for inputs and outputs
        self.is_input = True
        if "output" in n_io:
            self.is_input = False

        if self.is_input:
            self.disp_settings = n_settings.display_settings['INPUTS']
        else:
            self.disp_settings = n_settings.display_settings['OUTPUTS']

        if n_type not in self.disp_settings.keys():
            self.disp_settings = self.disp_settings['default']
        else:
            self.disp_settings = self.disp_settings[n_type]


        self.gitem = _AttributeGFX(n_x,
                                   n_y,
                                   n_scene,
                                   n_settings,
                                   n_name,
                                   n_type,
                                   n_io)
        self.setGraphicsItem(self.gitem)
        self.setMinimumHeight(3)

    def sizeHint(self, z, sizeh):
        """Get the size."""
        boundingrec = self.gitem.boundingRect()
        r = QtCore.QSizeF()
        r.setHeight(boundingrec.height())
        r.setWidth(boundingrec.width())
        return r

    def setGeometry(self, x):
        """Set geo size."""
        self.gitem.setPos(x.topLeft())


class _AttributeGFX (QtGui.QGraphicsEllipseItem):
    """An attribute on a node."""

    # ---------------- Init -------------------------------------------------#
    #
    # Init the attributeGFX obj. This object is created by the nodeGFX obj
    #   n_x - Position x
    #   n_y - Position y
    #   n_scene - The scene to add this object to
    #   n_parent - The patent node of this attribute. Used to link
    #   n_name - The name of the attribute, must match whats in canvas
    #   n_type - The data type of the attribute
    #   n_io - Identifier for selection

    def __init__(self,
                 n_x,
                 n_y,
                 n_scene,
                 n_settings,
                 n_name,
                 n_type,
                 n_io):
        """INIT."""
        self.io = n_io
        self.name = n_name
        # Use same object for inputs and outputs
        self.is_input = True
        if "output" in n_io:
            self.is_input = False

        if self.is_input:
            self.disp_settings = n_settings.display_settings['INPUTS']
        else:
            self.disp_settings = n_settings.display_settings['OUTPUTS']

        if n_type not in self.disp_settings.keys():
            self.disp_settings = self.disp_settings['default']
        else:
            self.disp_settings = self.disp_settings[n_type]

        self.width = self.disp_settings['radius']
        self.height = self.disp_settings['radius']

        QtGui.QGraphicsEllipseItem.__init__(self,
                                            float(n_x - 5),
                                            float(n_y + self.height / 4),
                                            float(self.width),
                                            float(self.height),
                                            scene=n_scene)
        # QtGui.QGraphicsLayoutItem.__init__(self)

        self.fc = self.disp_settings.get('fillcolor', [66, 134, 244])
        self.sc = self.disp_settings.get('hovercolor', [212, 175, 55])
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.fc[0],
                                                self.fc[1],
                                                self.fc[2]),
                                   QtCore.Qt.SolidPattern))

        f = self.disp_settings['fontcolor']
        self.lable = QtGui.QGraphicsTextItem(n_name, self, n_scene)
        self.lable.setDefaultTextColor(QtGui.QColor(f[0], f[1], f[2]))

        # TODO - Need a more procedual way to place the outputs...
        if self.is_input is False:
            n_x = n_x - 100

        self.lable.setPos(self.width + n_x, n_y)
        self.setAcceptHoverEvents(True)

    # ----------------------------- Event Overides -------------------------- #
    def mousePressEvent(self, event):
        """Select and attribute."""
        self.scene().selection(self)
        QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)

    def hoverEnterEvent(self, event):
        """Set flag for mouse over."""
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.sc[0],
                                                self.sc[1],
                                                self.sc[2]),
                      QtCore.Qt.SolidPattern))

    def hoverLeaveEvent(self, event):
        """Set flag for mouse over."""
        self.setBrush(QtGui.QBrush(QtGui.QColor(self.fc[0],
                                                self.fc[1],
                                                self.fc[2]),
                      QtCore.Qt.SolidPattern))

# ------------------------ SceneGFX Class --------------------------------#
# Provides tracking of all the elements in the scene and provides all the
# functionality. Is a child of the NodeGraph object. Commands for editing the
# node network byond how they look in the node graph are passed up to the
# canvas. If the functions in the canvas return true then the operation is
# permitted and the data in the canvas has been changed.
#

class SceneGFX(QtGui.QGraphicsScene):
    """Stores grapahic elems."""

    # -------------------------- init -------------------------------------- #
    #
    #   n_x - position withing the node graph widget x cord
    #   n_y - position withing the node graph widget y cord
    def __init__(self, n_x, n_y, n_width, n_height, n_parent):
        """INIT."""
        # Dict of nodes. Must match canvas
        self.nodes = {}

        # list of connections between nodes
        self.connections = []

        # The currently selected object
        self.cur_sel = None

        # how far to off set newly created nodes. Prevents nodes from
        # being created ontop of each other
        self.node_creation_offset = 100

        super(SceneGFX, self).__init__(n_parent)
        self.width = n_width
        self.height = n_height

        self.settings = self.parent().settings

    def addnode(self, node_name, node_type, br):
        """Forward node creation calls to scene."""
        x = br.x() + (br.width() / 2)
        y = br.y() + (br.height() / 2)
        new_node = NodeGFX(x,
                           y,
                           self.canv().nodes[node_name],
                           self)
        self.addItem(new_node)
        self.nodes[node_name] = new_node

    def addconnection(self, n1_node, n1_attr, n2_node, n2_attr):
        """Add a new connection."""
        new_connection = ConnectionGFX(self,
                                       self.nodes[n1_node].outputs[n1_attr],
                                       self.nodes[n2_node].inputs[n2_attr])
        self.connections.append(new_connection)
        self.parent().update_attr_panel()

    def helloworld(self):
        """test."""
        print "Scene - hello world"

    def updateconnections(self):
        """Update connections."""
        for con in self.connections:
            con.update()

    def canv(self):
        """Link to the canvas object."""
        return self.parent().canvasobj

    def mainwidget(self):
        """Link to the main widget obj."""
        return self.parent()

    def delselection(self):
        """Delete the selected obj."""
        if "connection" in self.cur_sel.io:
            if self.mainwidget().delete_connection(self.cur_sel):
                self.removeItem(self.cur_sel)
                for x in range(0, len(self.connections) - 1):
                    if self.cur_sel == self.connections[x]:
                        del self.connections[x]
                        break
                self.cur_sel = None

        elif "node" in self.cur_sel.io:
            if self.mainwidget().delete_node(self.cur_sel):
                node_name = self.cur_sel.name

                # First search for all connections assosiated with this node
                # and delete

                # Create Dic from list
                connection_dict = {}
                for x in range(0, len(self.connections)):
                    connection_dict[str(x)] = self.connections[x]

                new_connection_list = []

                for key, con in connection_dict.iteritems():

                    print con.upstreamconnect.parentLayoutItem().parentLayoutItem().name
                    print con.downstreamconnect.parentLayoutItem().parentLayoutItem().name

                    up_node = con.upstreamconnect.parentLayoutItem().parentLayoutItem().name
                    down_node = con.downstreamconnect.parentLayoutItem().parentLayoutItem().name

                    if up_node == node_name or down_node == node_name:
                        self.removeItem(connection_dict[key])
                    else:
                        new_connection_list.append(con)

                self.connections = new_connection_list
                del connection_dict

                self.removeItem(self.nodes[node_name])
                del self.nodes[node_name]
        self.parent().update_attr_panel()
        self.update(self.sceneRect())

    def keyPressEvent(self, event):
        """Listen for key presses on scene obj."""
        if event.key() == QtCore.Qt.Key_Delete:
            self.delselection()

        super(SceneGFX, self).keyPressEvent(event)

    def selection(self, sel):
        """Function to handel selections and connections."""
        last_sel = self.cur_sel
        self.cur_sel = sel

        if "node" in sel.io:
            # set selection to none on all nodes.
            print "sel name:", self.cur_sel.name

            for nodekey, node in self.nodes.iteritems():

                if nodekey == self.cur_sel.name: 
                    node._selected = True
                else:
                    node._selected = False
                node.update()
            
            self.mainwidget().selected_node = sel
            self.mainwidget().attr_panel.update_layout()

        # Need to compaire the current and last selections to see
        # if a connection has been made
        if last_sel != None:
            if "input" in last_sel.io and "output" in self.cur_sel.io:
                lspn = last_sel.parentItem().name
                cspn = self.cur_sel.parentItem().name
                if lspn is not cspn:
                    self.mainwidget().connect(last_sel.parentItem().name,
                                              last_sel.name,
                                              self.cur_sel.parentItem().name,
                                              self.cur_sel.name)
                last_sel = None
                self.cur_sel = None

            elif "output" in last_sel.io and "input" in self.cur_sel.io:
                lspn = last_sel.parentItem().parentItem().name
                cspn = self.cur_sel.parentItem().parentItem().name
                if lspn is not cspn:
                    self.mainwidget().connect(last_sel.parentItem().name,
                                              last_sel.name,
                                              self.cur_sel.parentItem().name,
                                              self.cur_sel.name)
                last_sel = None
                self.cur_sel = None


class NodeGraph (QtGui.QGraphicsView):
    """Main Wrapper for node network."""

    def __init__(self, p):
        """INIT."""
        QtGui.QGraphicsView.__init__(self, p)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.mainwin = p
        self.initui()

    def initui(self):
        """Set up the UI."""
        s = self.mainwin.settings.display_settings['SCENESTYLE']['stylesheet']
        self.setStyleSheet(s)
        self._zoom = 0
        self.scene = SceneGFX(0, 0, 25, 1000, self.mainwin)
        self.setScene(self.scene)

        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtGui.QFrame.NoFrame)

    # ---------- UI interaction ---------------------------------------------
    def zoomFactor(self):
        return self._zoom
    '''
    def fitInView(self):
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.scene().transform().mapRect(rect)
        facv
    '''

    def wheelEvent(self, event):
        if event.delta() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        self.scale(factor, factor)


    # ---------- network interaction ----------------------------------------
    def addnode(self, node_name, node_type):
        """Forward node creation calls to scene."""
        br = self.mapToScene(self.viewport().geometry()).boundingRect()
        self.scene.addnode(node_name, node_type, br)

    def addconnection(self, n1_node, n1_attr, n2_node, n2_attr):
        """Add a connection between 2 nodes."""
        self.scene.addconnection(n1_node, n1_attr, n2_node, n2_attr)

    def helloworld(self):
        """test."""
        print "Node graph - hello world"

    def canv(self):
        """Link to the canvas object."""
        return self.mainwin.canvasobj

    def change_name_accepted(self, old_name, new_name):
        """Update the node graph to accept new names"""
        pass


# ------------------------ Graphic Layout Class ---------------------------#
# Provides a class organizing Qgraphics items in a vertical layout

class _GraphicsLayout (QtGui.QGraphicsWidget):
    """Provide structure for organizing elements."""

    def __init__(self, spacing, parent):
        """Init."""
        super(_GraphicsLayout, self).__init__(parent)
        self.setLayout(QtGui.QGraphicsLinearLayout(QtCore.Qt.Vertical))
        self.layout().setSpacing(spacing)
        self.name = self.parentItem().name
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.MinimumExpanding)
        self.items = {}
        self.spacing = spacing

    def add_item(self, item):
        """Add a new item to the layout and transform it into position."""
        '''
        trans = self.spacing * len(self.items) - 1 + item.height
        item.setParentItem(self)
        item.translate(0, trans)
        '''
        self.items[item.name] = item
        self.layout().addItem(self.items[item.name])

    def height(self):
        """Return the height of this object."""
        height = 0.0
        for x in range(0, self.layout().count()):
            height += self.layout().itemAt(x).gitem.boundingRect().height()

        return height + (self.spacing * self.layout().count())
        '''
        if len(self.items) > 0:
            height = self.layout().count() * self.spacing
        else:
            height = 0.0
        print "Height:", height
        return height
        '''
    def remove_items(self, item_index):
        """Remove a bunch of items based on the index then adjust transforms."""
        # Remove from list
        self.layout().removeItem(self.items[item_index])
        del self.items[item_index]
        '''
        try:
            self.items.pop(item_index)
            self.scene().removeItem(self.items[item_index])
        except Exception, e:
            print str(e)
        space = 0
        for key in self.items.keys():
            self.items[key].setY(0)
            trans = ((self.spacing + self.items[key].height))
            self.items[key].translate(0, trans)
            space += 1
        '''
