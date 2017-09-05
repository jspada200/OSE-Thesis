from PyQt4 import QtGui
import attr_widgets
import globalvars as gv
"""
Bugs
-   File "/home/jspadafora/OSE/OSE_Modules/attr_widgets.py", line 64, in init_ui
    self.default = float(self.attrobj.extra_info['default'])
ValueError: invalid literal for float(): 0.75f
"""

class AttrPanel(QtGui.QWidget):
    """Panel for displaying attributes."""

    def __init__(self, mw):
        """Init."""
        super(AttrPanel, self).__init__(mw)

        # Layout to add wigets to
        self.Layout = QtGui.QVBoxLayout(self)
        # self.Layout.addStretch(1)
        self.mainwin = mw
        self.nodename_LineEdit = self.mainwin.nodeName_lineEdit
        self.nodename_LineEdit.editingFinished.connect(self.edit_node_name)
        self.canvasobj = self.mainwin.canvasobj
        print self.canvasobj
        self.setLayout(self.Layout)
        self.show()

    def update_layout(self):
        """Get latest info based on selection."""
        # Clear Layout
        for i in reversed(range(self.Layout.count())):
            self.Layout.itemAt(i).widget().deleteLater()

        self.nodename_LineEdit.setText("")

        # Get seleted node from mainwin
        if self.mainwin.selected_node:
            sn = self.mainwin.selected_node.name
            self.nodename_LineEdit.setText(sn)
            # Get attributes for selected node and create the correct widget
            new_height = 0
            for key, value in self.canvasobj.nodes[sn].in_attributes.iteritems():

                print value.extra_info

                if value.connection is not None:
                    new_attr = attr_widgets.ConnectedAttr(sn, value)
                else:
                    try:
                        if "float" in value.type:
                            new_attr = attr_widgets.FloatAttr(sn, value)
                        elif "color" in value.type:
                            new_attr = attr_widgets.ColorAttr(sn, value)
                        elif "mapper" in str(value.extra_info['widget']):
                            new_attr = attr_widgets.ComboboxAttr(sn, value)
                        elif "checkBox" in str(value.extra_info['widget']):
                            new_attr = attr_widgets.CheckboxAttr(sn, value)
                        elif "fileInput" in str(value.extra_info['widget']):
                            new_attr = attr_widgets.FileAttr(sn, value)
                        elif "int" in value.type:
                            new_attr = attr_widgets.IntAttr(sn, value)
                        elif "string" in value.type:
                            new_attr = attr_widgets.StringAttr(sn, value)
                        else:
                            new_attr = attr_widgets.StandinAttr(sn, value)
                    except Exception, e:
                        print str(e)
                        print key

                self.Layout.addWidget(new_attr)
                new_height = new_height + gv.WIDGET_HEIGHT

            print new_height
            self.setMaximumHeight(new_height)
            self.setMinimumHeight(new_height)

    def edit_node_name(self):
        """Change the node name."""
        in_str = self.nodename_LineEdit.text()
        fallback_value = self.mainwin.selected_node.name
        if fallback_value != in_str:
            print "Updating name"
            if self.canvasobj.rename_node(fallback_value, in_str):
                self.mainwin.node_graph
            self.update_layout()
