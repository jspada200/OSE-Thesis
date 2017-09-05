from PyQt4 import QtGui
from PyQt4 import uic
import globalvars as gv
import datatypes


class BaseAttr(QtGui.QWidget):
    """Base class for Attributes displayed in Attr panel."""

    def __init__(self, node, attrobj):
        """Set up base Attr Class used in all attr widgets."""
        super(BaseAttr, self).__init__()

        # Location of the Attribute in the canvas
        self.attrobj = attrobj

        self.node = node
        self.name = attrobj.name
        self.value = attrobj.value

        self.init_ui()

    def init_ui(self):
        """Init Ui."""
        pass


class StandinAttr(BaseAttr):
    """Stand in attribute for testing."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/standin.ui", self)
        for key, value in self.attrobj.extra_info.iteritems():
            print key, ":", value
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)


class FloatAttr(BaseAttr):
    """Widget for Float."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/float_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)
        
        try:
            self.low_range = float(self.attrobj.extra_info['min'])
        except:
            self.low_range = 0.0

        try:
            self.high_range = float(self.attrobj.extra_info['max'])
        except:
            self.high_range = 1.0

        self.default = float(self.attrobj.extra_info['default'])

        self.horizontalSlider.sliderMoved.connect(self.slider_changed)
        # self.lineEdit.setValidator(QtGui.QDoubleValidator())
        self.lineEdit.editingFinished.connect(self.line_updated)

        self.horizontalSlider.setRange(0, 100)
        self.update_line()
        self.update_slider()

    def slider_changed(self):
        """Slot for when the slider is moved."""
        nv = self.horizontalSlider.value()
        new_value = self.slider_convert(nv, to_float=True)
        print "New Val is:", new_value
        if self.parent().mainwin.edit_attribute(self.node,
                                                self.name,
                                                new_value):
            self.value = new_value
            self.update_line()
        else:
            self.update_slider()

    def line_updated(self):
        """Slot for when the line edit is changed."""
        fbv = self.value

        nv = float(self.lineEdit.text())
        if self.parent().mainwin.edit_attribute(self.node, self.name, nv):
            self.value = float(self.lineEdit.text())
            self.update_slider()
        else:
            self.lineEdit.setText(fbv)

    def update_slider(self):
        """Set the sliders value when the line edit is changed or on init."""
        newvalue = self.slider_convert(self.value)
        self.horizontalSlider.setValue(newvalue)

    def update_line(self):
        """Change the line when the slider is changed."""
        self.lineEdit.setText(str(self.value))

    def slider_convert(self, val, to_float=False):
        """Slider widget takes ints so convert back and forth."""
        lr = self.low_range
        hr = self.high_range
        if to_float is False:
            newvalue = (((float(val) - lr) * (100 - 0)) / (hr - lr)) + lr
        else:
            print "To flaot"
            newvalue = (((float(val) - 0) * (hr - lr)) / (100 - 0)) + 0
        return newvalue


class ColorAttr(BaseAttr):
    """Stand in attribute for testing."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/color_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.R_lineEdit.setText(str(self.value.x))
        # self.R_lineEdit.setValidator(QtGui.QDoubleValidator(self))
        self.G_lineEdit.setText(str(self.value.y))
        # self.G_lineEdit.setValidator(QtGui.QDoubleValidator(self))
        self.B_lineEdit.setText(str(self.value.z))
        # self.B_lineEdit.setValidator(QtGui.QDoubleValidator(self))

        self.R_lineEdit.editingFinished.connect(self.line_changed)
        self.G_lineEdit.editingFinished.connect(self.line_changed)
        self.B_lineEdit.editingFinished.connect(self.line_changed)

        self.colorpicker_btn.clicked.connect(self.color_dialog)

        self.colorpicker_btn.setAutoFillBackground(True)
        self.update_cp()

    def line_changed(self):
        """Slot for when any line is chaged in atter."""
        n_r = float(self.R_lineEdit.text())
        n_g = float(self.G_lineEdit.text())
        n_b = float(self.B_lineEdit.text())

        n_v = datatypes.Vec3(n_r, n_g, n_b)

        fbv_r = self.value.x
        fbv_g = self.value.y
        fbv_b = self.value.z

        if self.parent().mainwin.edit_attribute(self.node, self.name, n_v):
            self.value = n_v
            self.update_cp()
        else:
            self.R_lineEdit.setText(str(fbv_r))
            self.G_lineEdit.setText(str(fbv_g))
            self.B_lineEdit.setText(str(fbv_b))

    def update_cp(self):
        """Set the color for the pickers btn."""
        self.colorpicker_btn.setAutoFillBackground(True)
        ss = "background-color: " + self.value.get_hex()
        self.colorpicker_btn.setStyleSheet(ss)

    def color_dialog(self):
        """Get a color from the color picker."""
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            r, g, b, a = col.getRgbF()
            self.R_lineEdit.setText(str(r))
            self.G_lineEdit.setText(str(g))
            self.B_lineEdit.setText(str(b))
            self.line_changed()


class ComboboxAttr(BaseAttr):
    """Stand in attribute for testing."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/dropdown_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.lut = {}
        for x in range(0, len(self.attrobj.extra_info['options'])):
            self.lut[str(x)] = self.attrobj.extra_info['options'][x]
            self.comboBox.addItem(self.lut[str(x)])
            if self.lut[str(x)] in self.attrobj.value:
                self.comboBox.setCurrentIndex(x)

        self.comboBox.currentIndexChanged.connect(self.updateval)

    def updateval(self, nv):
        """Set new value, can support str or int."""
        if self.attrobj.type == "string":
            self.parent().mainwin.edit_attribute(self.node,
                                                 self.name,
                                                 self.lut[str(nv)])

        elif self.attrobj.type == "int":
            self.parent().mainwin.edit_attribute(self.node, self.name, str(nv))


class CheckboxAttr(BaseAttr):
    """Widget for check box attributes."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/checkbox_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.checkBox.setChecked(bool(self.attrobj.value))
        self.checkBox.stateChanged.connect(self.update)

    def update(self, cs):
        """Update value in canvas."""
        self.parent().mainwin.edit_attribute(self.node, self.name, cs)


class IntAttr(BaseAttr):
    """Widget for Int Attr."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/int_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.lineEdit.setText(str(self.attrobj.value))
        # self.lineEdit.setValidator(QtGui.QIntValidator())
        self.lineEdit.editingFinished.connect(self.update)

    def update(self):
        """Line changed, update value."""
        val = int(self.lineEdit.text())
        self.parent().mainwin.edit_attribute(self.node, self.name, val)


class StringAttr(BaseAttr):
    """Widget for String Attr."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/string_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.lineEdit.setText(str(self.attrobj.value))
        self.lineEdit.editingFinished.connect(self.update)

    def update(self):
        """Line changed, update value."""
        val = self.lineEdit.text()
        self.parent().mainwin.edit_attribute(self.node, self.name, val)


class FileAttr(BaseAttr):
    """Widget for File Attr."""

    def init_ui(self):
        """Set up Base UI."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/file_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        self.lineEdit.setText(str(self.attrobj.value))
        self.lineEdit.editingFinished.connect(self.update)
        self.toolButton.clicked.connect(self.file_dialog)

    def file_dialog(self):
        """Select a file to use."""
        file = QtGui.QFileDialog.getOpenFileName(self, 'Open Texture', '')

        if file != '' and file is not None:
            self.lineEdit.setText(file)

        self.update()

    def update(self):
        """Line changed, update value."""
        val = self.lineEdit.text()
        self.parent().mainwin.edit_attribute(self.node, self.name, val)


class ConnectedAttr(BaseAttr):
    """Widget for when a node is connected."""

    def init_ui(self):
        """Init."""
        uic.loadUi(gv.APP_ROOT + "/OSE_Modules/ui/widgets/file_widget.ui",
                   self)
        try:
            self.name_label.setText(self.attrobj.extra_info['label'])
        except:
            self.name_label.setText(self.attrobj.name)

        n = self.attrobj.connection.dest_node
        a = self.attrobj.connection.dest_attr
        self.lineEdit.setText(n + ":" + a)
